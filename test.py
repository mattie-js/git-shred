from engine import run_engine

## ── shared plan data ─────────────────────────────────────────────
base_plan = {
    "plan_id": 1,
    "rate_of_loss_pct": 0.75,
    "cal_rx": 2100,
    "tdee": 2800,
    "goal_weight": 170.0,
    "weeks_to_goal": 15,
    "protein_rx": 190,
    "carbs_g": 200,
    "fat_rx": 60
}

## ── shared user data ─────────────────────────────────────────────
base_user = {
    "age": 21,
    "sex": 1,
    "height_in": 72,
    "weight": 190.0,
    "activity_level": 3,
    "start_date": "2026-01-01",
    "checkin_day": 1
}

## ── scenario runner ──────────────────────────────────────────────
def run_scenario(name, checkin_data, calculated_data, plan_data=base_plan, user_data=base_user):
    print(f"\n{'='*50}")
    print(f"SCENARIO: {name}")
    print(f"{'='*50}")
    run_engine(checkin_data, calculated_data, plan_data, user_data)

## ── scenario 1 ───────────────────────────────────────────────────
## ROL slow, good adherence, moderate fatigue, 6 weeks in
run_scenario(
    "1 - Slow ROL, good adherence, moderate fatigue",
    checkin_data={
        "user_id": 1,
        "check_in_date": "2026-02-12",
        "avg_weight_lbs": 188.5,
        "days_tracked": 6,
        "avg_step_count": 8000,
        "strength_subj": 2,
        "fatigue_subj": 4,
        "days_adherent": 7,
        "calories_over": None,
        "off_the_rails": 0,
        "lbs_to_go": 18.5
    },
    calculated_data={
        "total_weeks_in_deficit": 6,
        "weekly_rol": 0.3,
        "recalculated_bmr": 1800.0,
        "cumulative_rol": 0.4,
        "total_lbs_lost": 1.5
    }
)

## ── scenario 2 ───────────────────────────────────────────────────
## ROL too fast, low fatigue, strength increasing, 3 weeks in
run_scenario(
    "2 - ROL too fast, low fatigue, strength increasing",
    checkin_data={
        "user_id": 1,
        "check_in_date": "2026-01-22",
        "avg_weight_lbs": 187.2,
        "days_tracked": 7,
        "avg_step_count": 8000,
        "strength_subj": 1,
        "fatigue_subj": 3,
        "days_adherent": 7,
        "calories_over": None,
        "off_the_rails": 0,
        "lbs_to_go": 17.2
    },
    calculated_data={
        "total_weeks_in_deficit": 3,
        "weekly_rol": 1.4,
        "recalculated_bmr": 1850.0,
        "cumulative_rol": 1.2,
        "total_lbs_lost": 2.8
    }
)

## ── scenario 3 ───────────────────────────────────────────────────
## High fatigue, strength declining, low cals, high cardio, 14 weeks in
run_scenario(
    "3 - High fatigue, strength declining, low cals, high cardio",
    checkin_data={
        "user_id": 1,
        "check_in_date": "2026-04-01",
        "avg_weight_lbs": 180.0,
        "days_tracked": 6,
        "avg_step_count": 11000,
        "strength_subj": 3,
        "fatigue_subj": 8,
        "days_adherent": 6,
        "calories_over": 300,
        "off_the_rails": 0,
        "lbs_to_go": 10.0
    },
    calculated_data={
        "total_weeks_in_deficit": 14,
        "weekly_rol": 0.6,
        "recalculated_bmr": 1750.0,
        "cumulative_rol": 0.65,
        "total_lbs_lost": 10.0
    },
    plan_data={**base_plan, "cal_rx": 1700}
)

## ── scenario 4 ───────────────────────────────────────────────────
## ROL on track, low adherence, moderate fatigue, 8 weeks in
run_scenario(
    "4 - ROL on track, low adherence",
    checkin_data={
        "user_id": 1,
        "check_in_date": "2026-02-26",
        "avg_weight_lbs": 184.0,
        "days_tracked": 5,
        "avg_step_count": 9000,
        "strength_subj": 2,
        "fatigue_subj": 6,
        "days_adherent": 5,
        "calories_over": 600,
        "off_the_rails": 0,
        "lbs_to_go": 14.0
    },
    calculated_data={
        "total_weeks_in_deficit": 8,
        "weekly_rol": 0.8,
        "recalculated_bmr": 1800.0,
        "cumulative_rol": 0.75,
        "total_lbs_lost": 6.0
    }
)

## ── scenario 5 ───────────────────────────────────────────────────
## 18 weeks in, slow ROL, high fatigue, cals low, cardio high
run_scenario(
    "5 - 18 weeks in, slow ROL, high fatigue, cals and cardio maxed",
    checkin_data={
        "user_id": 1,
        "check_in_date": "2026-04-01",
        "avg_weight_lbs": 178.0,
        "days_tracked": 7,
        "avg_step_count": 11500,
        "strength_subj": 2,
        "fatigue_subj": 7,
        "days_adherent": 7,
        "calories_over": None,
        "off_the_rails": 0,
        "lbs_to_go": 8.0
    },
    calculated_data={
        "total_weeks_in_deficit": 18,
        "weekly_rol": 0.4,
        "recalculated_bmr": 1720.0,
        "cumulative_rol": 0.55,
        "total_lbs_lost": 12.0
    },
    plan_data={**base_plan, "cal_rx": 1650}
)

## ── scenario 6 ───────────────────────────────────────────────────
## 5 weeks in, ROL on track, low fatigue, strength increasing, slight non adherence
run_scenario(
    "6 - On track, low fatigue, strength up, slight non adherence",
    checkin_data={
        "user_id": 1,
        "check_in_date": "2026-02-05",
        "avg_weight_lbs": 186.0,
        "days_tracked": 6,
        "avg_step_count": 7800,
        "strength_subj": 1,
        "fatigue_subj": 2,
        "days_adherent": 6,
        "calories_over": 200,
        "off_the_rails": 0,
        "lbs_to_go": 16.0
    },
    calculated_data={
        "total_weeks_in_deficit": 5,
        "weekly_rol": 0.7,
        "recalculated_bmr": 1900.0,
        "cumulative_rol": 0.72,
        "total_lbs_lost": 4.0
    }
)