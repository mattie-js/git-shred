from database import update_plan


def run_engine(checkin_data, calculated_data, plan_data, user_data):


    ## calls all neccesary variables
    target_rol         = plan_data["rate_of_loss_pct"]
    slow_rol_small     = target_rol * 0.80   # below 80% of target = a little slow
    slow_rol_large     = target_rol * 0.50   # below 50% of target = very slow
    fast_rol_small     = target_rol * 1.20   # above 120% of target = a little fast
    fast_rol_large     = target_rol * 1.50   # above 150% of target = way too fast

    bmr               = calculated_data["recalculated_bmr"]
    cal_rx            = plan_data["cal_rx"]
    baseline_steps    = user_data["activity_level"] * 2500  # rough step baseline from activity level
    current_steps     = checkin_data["avg_step_count"] #acutal avg steps per day post checkin

    cal_lower_bound   = bmr * 0.85 # threshold for low calorie diet
    cal_upper_bound   = bmr * 1.33 #if cals above this --> cutting cals is an option
    steps_high        = baseline_steps * 1.5

    ## specific recommendation magnitudes
    cal_cut_moderate   = int(cal_rx * 0.08)
    cal_cut_aggressive = int(cal_rx * 0.125)
    cal_bump           = int(cal_rx * 0.08)
    step_increase_moderate   = int(baseline_steps * 0.15)
    step_increase_aggressive = int(baseline_steps * 0.25)


    weeks_in_deficit  = calculated_data["total_weeks_in_deficit"]
    weekly_rol        = calculated_data["weekly_rol"]  #acutal ROL from checkin
    fatigue           = checkin_data["fatigue_subj"] #1-10 rating
    strength          = checkin_data["strength_subj"]   # 1=increasing 2=maintaining 3=declining
    days_adherent     = checkin_data["days_adherent"]   #x/7 days stickign to plan
    calories_over     = checkin_data["calories_over"]   #total calories across all non-adherant days
    off_the_rails     = checkin_data["off_the_rails"] #0 = no, 1= yes
    user_id           = checkin_data["user_id"]
    plan_id           = plan_data.get("plan_id")


    ## ── first check-in guard ─────────────────────────────────────────
    if weeks_in_deficit < 1: ## first week of diet
        print("\nNot enough data yet — keep following your plan and check back next week!")
        return

    ## ── pull last two weeks ROL from database ────────────────────────
    ## for now we use current weekly_rol as proxy
    ## TODO: get last 2 check_ins and confirm trend before scoring ROL
    rol_slow_small_flag  = weekly_rol < slow_rol_small   # losing less than 80% of target
    rol_slow_large_flag  = weekly_rol < slow_rol_large   # losing less than 50% of target
    rol_fast_large_flag  = weekly_rol > fast_rol_large   # losing more than 150% of target
    
    ## above is boolean variables for positive flags

    ## ── adherence checkpoint ───────────────────────────────────────────────
    adherence_blocked = False
    adherence_note    = ""

    if days_adherent < 5:
        adherence_blocked = True
        adherence_note = "⚠️  Adherence is below 5/7 days — focus on sticking to your plan before making any adjustments."

    elif off_the_rails == 1:
        adherence_blocked = True
        adherence_note = "⚠️  You reported going off the rails this week — no diet changes until adherence improves."

    elif days_adherent in [5, 6] and calories_over and calories_over > (cal_rx * 0.5): ##total calories over across exceed 1/2 of daily cal_rx
        adherence_blocked = True
        adherence_note = "⚠️  Calories over on off days exceeded half your daily target — no changes this week."

    ## ── deficit score ────────────────────────────────────────────────
    deficit_score = 0

    if rol_slow_large_flag:
        deficit_score += 3
        if weeks_in_deficit < 4:
            deficit_score += 2
        elif weeks_in_deficit <= 10:
            deficit_score += 1 
    ## if ROL is slow and early in the deficit, increase points

    elif rol_slow_small_flag:
        deficit_score += 1
        if weeks_in_deficit < 4:
            deficit_score += 2
        elif weeks_in_deficit <= 10:
            deficit_score += 1

    if rol_fast_large_flag:
        deficit_score -= 2

    if days_adherent == 7 and (rol_slow_large_flag or rol_slow_small_flag) and weeks_in_deficit <= 8:
        deficit_score += 1


    ## ── recovery score ───────────────────────────────────────────────
    recovery_score = 0

    ## fatigue
    if fatigue > 7:
        fatigue_points = 3
    elif fatigue >= 5:
        fatigue_points = 1
    else:
        fatigue_points = 0

    if weeks_in_deficit < 6:
        fatigue_points *= 2  ##high fatigue early on double fatigue points due to higher concern

    recovery_score += fatigue_points #adds points from fatigue to total recovery score

    ## strength - gym performance is a major metric
    if strength == 3:        # declining
        recovery_score += 3
    elif strength == 2:      # maintaining
        recovery_score += 0
    elif strength == 1:      # increasing
        recovery_score -= 3 

    ## weeks in deficit 
    if weeks_in_deficit > 20:
        recovery_score += 2
    elif weeks_in_deficit >= 10:
        recovery_score += 1

    ## ROL too fast AND high fatigue bonus
    if rol_fast_large_flag and fatigue > 7:
        recovery_score += 2

    ## cardio and calorie points simply for being agressive outside of subjectivity
    if current_steps >= steps_high:
        recovery_score += 1
    if cal_rx <= bmr:
        recovery_score += 1


    ## ── resolution logic ─────────────────────────────────────────────
    print("\n=== WEEKLY RECOMMENDATION ===")


    def ask_implement(new_cal=None, new_steps=None): ##TODO confirm I understand
        confirm = input("\nWill you implement this change? (y/n): ").strip().lower()
        if confirm == "y":
            update_plan(plan_id, new_cal, new_steps)
            print("✅ Plan updated successfully.")
        else:
            print("Got it — no changes made. Keep it in mind for next week.")

## recovery assessed first
    if recovery_score >= 8:  ##user needs adjustment
        ## determine deload vs diet break vs refeed
        activity_multipliers = {1: 1.2, 2: 1.375, 3: 1.55, 4: 1.725, 5: 1.9}
        multiplier = activity_multipliers[user_data["activity_level"]]
        current_tdee = int(bmr * multiplier)

        if strength == 3 and fatigue > 7: ##strength down + fatigue high
            print("🔴 DELOAD RECOMMENDED")
            print("Your strength is declining and fatigue is very high. Take a deload week — reduce training volume and intensity significantly.")
            if cal_rx < cal_lower_bound or current_steps > steps_high:
                print("Your calories are also very low and/or cardio is high. Consider a full diet break (1-2 weeks at maintenance).")
                new_cals = current_tdee
                print(f"Suggested calorie target during diet break: ~{new_cals} kcal")
                ask_implement(new_cal=new_cals)


        elif strength == 1 and fatigue > 7:
            print("🟡 REFEED RECOMMENDED")
            print("Strength is still going up but fatigue is high — a 1-2 day refeed at maintenance calories (prioritize carbs) should help.")
            new_cals = current_tdee
            print(f"Suggested refeed calorie target: ~{new_cals} kcal")
            ask_implement(new_cal=new_cals)


    
        elif strength == 2 and fatigue > 7: #strength maintaining + fatigue high
            print("🟡 MONITOR CLOSELY")
            print("Fatigue is high but strength is holding. Keep pushing for now.")
            if cal_rx <= bmr and current_steps > steps_high:
                print("⚠️  Warning: calories are at/below BMR and cardio is very high. Adjustments will likely be coming soon.")
    
        else: ##check for strenght values != 1,2,3
            print("⚠️  Unable to determine recommendation — check your inputs.")


    elif recovery_score >= 4: ## moderate recovery score
        print("🟡 RECOVERY WARNING")
        print("Your recovery score is elevated. No deficit increases this week.")

        if strength == 1 and fatigue > 7: ##strength increase + moderate fatigue
            print("Your strength is increasing, but fatigue is high. Keep an eye on fatigue levels but keep pushing!")

        elif strength == 3: ##strength decreasing + moderate recovery TODO how to handle strength decrease while fatigue is low
            if cal_rx < cal_lower_bound:
                new_cals = int(cal_rx + cal_bump)
                print(f"Strength declining and calories are low — 🟡 Calories may be too low.")
                print(f"Suggested calorie bump: ~{new_cals} kcal")
                ask_implement(new_cal=new_cals)
            if current_steps > steps_high:
                new_steps = int(current_steps - step_increase_moderate)
                print(f"Strength declining and cardio is high — consider reducing step count.")
                print(f"Suggested step target: ~{new_steps} steps/day")
                ask_implement(new_steps=new_steps)

        ## moderate recovery and high deficit score TODO add tangible small bump
        if deficit_score >= 5: 
            print("Despite recovery warning, deficit score is high — consider a small moderate adjustment only.")

## recovery is ok, move on to evaluate deficit score--------------------------------------------------
    else: 
        if adherence_blocked:
            print(adherence_note)

        elif rol_fast_large_flag and fatigue <= 4:
            new_cals = int(cal_rx + cal_bump)
            print("✅ Rate of loss is faster than target but fatigue is low.")
            print(f"Small calorie bump recommended. New target: ~{new_cals} kcal")
            ask_implement(new_cal=new_cals)

        elif deficit_score >= 5:
            print("🔴 AGGRESSIVE DEFICIT INCREASE RECOMMENDED")
            if cal_rx > cal_upper_bound:
                new_cals = int(cal_rx - cal_cut_aggressive)
                print(f"Cut calories by {cal_cut_aggressive} kcal. New target: ~{new_cals} kcal")
                ask_implement(new_cal=new_cals)
            elif current_steps < steps_high:
                new_steps = int(current_steps + step_increase_aggressive)
                print(f"Increase daily steps by {step_increase_aggressive}. New target: ~{new_steps} steps/day")
                ask_implement(new_steps=new_steps)
            else:
                new_cals = int(cal_rx - cal_cut_aggressive)
                print(f"Cut calories by {cal_cut_aggressive} kcal. New target: ~{new_cals} kcal")
                ask_implement(new_cal=new_cals)

        elif deficit_score >= 2:
            print("🟠 MODERATE DEFICIT INCREASE RECOMMENDED")
            if cal_rx > cal_upper_bound:
                new_cals = int(cal_rx - cal_cut_moderate)
                print(f"Cut calories by {cal_cut_moderate} kcal. New target: ~{new_cals} kcal")
                ask_implement(new_cal=new_cals)
            elif current_steps < steps_high:
                new_steps = int(current_steps + step_increase_moderate)
                print(f"Increase daily steps by {step_increase_moderate}. New target: ~{new_steps} steps/day")
                ask_implement(new_steps=new_steps)
            else:
                new_cals = int(cal_rx - cal_cut_moderate)
                print(f"Cut calories by {cal_cut_moderate} kcal. New target: ~{new_cals} kcal")
                ask_implement(new_cal=new_cals)


        elif deficit_score <= -2:
            new_cals = int(cal_rx + cal_bump)
            print("✅ ROL is faster than target.")
            print(f"Small calorie bump recommended. New target: ~{new_cals} kcal")
            ask_implement(new_cal=new_cals)
        else:
            print("✅ YOU'RE ON TRACK — no changes needed this week. Keep it up!")

    ## always print strength declining low fatigue notice
    if strength == 3 and fatigue <= 4 and recovery_score < 4:
        print("\n📋 Note: Strength declined this week despite low fatigue.")
        print("This could be a one-off — check sleep quality, stress levels, training intensity, and protein intake before drawing conclusions.")
        print("If this continues next week, we'll reassess.")