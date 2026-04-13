from database import create_connection
from datetime import date


def get_checkin_inputs(user_id, plan_data):
    print("\n=== WEEKLY CHECK-IN ===")
    
    check_in_date = date.today()

    while True:
        try:
            avg_weight_lbs = float(input("What was your average weight this week?(lbs): "))
            if avg_weight_lbs < 80 or avg_weight_lbs > 600:
                print("Please enter a valid weight in lbs.")
                continue
            break
        except ValueError:
            print("Please enter a valid number.")

    while True:
        try:
            days_tracked = int(input("How many days did you track your weight this week? (1-7): "))
            if days_tracked < 1 or days_tracked > 7:
                print("Please enter a number between 1 and 7.")
                continue
            break
        except ValueError:
            print("Please enter a valid number.")

    while True:
        try:
            avg_step_count = int(input("What was your average daily step count this week?: "))
            if avg_step_count < 0 or avg_step_count > 100000:
                print("Please enter a valid step count.")
                continue
            break
        except ValueError:
            print("Please enter a valid number.")
    
    print("""
    Strength this week:
    1 - Getting stronger
    2 - Maintaining
    3 - Getting weaker
    """)

    while True:
        try:
            strength_subj = int(input("Select 1, 2, or 3: "))
            if strength_subj < 1 or strength_subj > 3:
                print("Please enter a number between 1 and 3.")
                continue
            break
        except ValueError:
            print("Please enter a valid number.")

    while True:
        try:
            fatigue_subj = int(input("Rate your fatigue this week (1-10, 10 being most fatigued): "))
            if fatigue_subj < 1 or fatigue_subj > 10:
                print("Please enter a number between 1 and 10.")
                continue
            break
        except ValueError:
            print("Please enter a valid number.")

    while True:
        try:
            days_adherent = int(input("How many days did you stick to your plan this week?(0-7): "))
            if days_adherent < 0 or days_adherent > 7:
                print("Please enter a number between 0 and 7.")
                continue
            break
        except ValueError:
            print("Please enter a valid number.")
    
    calories_over = None
    off_the_rails = 0
    if days_adherent < 7:
        print("For the days you were off plan: ")
        rails_yn = input("Do you know roughly how many calories over you went? (y/n): ")
        if rails_yn.lower() == "y":
            while True:
                try:
                    calories_over = float(input("How many calories over were you (total across off days)?: "))
                    if calories_over < 0:
                        print("Please enter a positive number.")
                        continue
                    break
                except ValueError:
                    print("Please enter a valid number.")
        else:
            off_the_rails = 1

    ## calculated variables
    goal_weight = plan_data["goal_weight"]
    lbs_to_go = avg_weight_lbs - goal_weight
    
    return {
        "user_id": user_id,
        "check_in_date": check_in_date,
        "avg_weight_lbs": avg_weight_lbs,
        "days_tracked": days_tracked,
        "avg_step_count": avg_step_count,
        "strength_subj": strength_subj,
        "fatigue_subj": fatigue_subj,
        "days_adherent": days_adherent,
        "calories_over": calories_over,
        "off_the_rails": off_the_rails,
        "lbs_to_go": round(lbs_to_go, 2),
    }

def calculate_checkin(checkin_data, user_data, plan_data):
    from datetime import date
    
    ## calculate total weeks in deficit
    start_date = user_data["start_date"]
    if isinstance(start_date, str): ## converts all incoming data to "date" type yyyy, mm, dd
        from datetime import datetime
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date() 
    today = date.today()
    total_weeks_in_deficit = (today - start_date).days // 7 

    ## recalculate bmr at current weight, calls data needed form user_data
    current_week_bw_avg = checkin_data["avg_weight_lbs"]
    age = user_data["age"]
    height_in = user_data["height_in"]
    sex = user_data["sex"]

    if sex == 1: ##new bmr calc, M=1, F=2
        recalculated_bmr = (10 * (current_week_bw_avg / 2.205)) + (6.25 * (height_in * 2.54)) - (5 * age) + 5
    else:
        recalculated_bmr = (10 * (current_week_bw_avg / 2.205)) + (6.25 * (height_in * 2.54)) - (5 * age) - 161

    ## get last weeks avg weight from database
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT avg_weight_lbs FROM check_ins WHERE user_id = %s ORDER BY check_in_date DESC LIMIT 1", (checkin_data["user_id"],))
    result = cursor.fetchone() ##result = last weeks bw
    conn.close()

    if result:
        last_week_weight = result[0]
        weekly_rol = ((last_week_weight - checkin_data["avg_weight_lbs"])/last_week_weight) *100 
    else:
        ## first check in, compare against starting weight from users table
        last_week_weight = user_data["weight"]
        weekly_rol = ((last_week_weight - checkin_data["avg_weight_lbs"])/last_week_weight)*100

    ## cumulative rol - rate of loss over whole diet /week
    total_lbs_lost = user_data["weight"] - checkin_data["avg_weight_lbs"]
    if total_weeks_in_deficit > 0:
        cumulative_rol = (total_lbs_lost / user_data["weight"]) / total_weeks_in_deficit * 100
    else:
        cumulative_rol = 0

    return {
        "total_weeks_in_deficit": total_weeks_in_deficit,
        "recalculated_bmr": round(recalculated_bmr, 2),
        "weekly_rol": round(weekly_rol, 2),
        "cumulative_rol": round(cumulative_rol, 2),
        "total_lbs_lost": round(total_lbs_lost, 2)
    }