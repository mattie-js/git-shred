from database import create_connection, create_tables, insert_user, insert_plan, get_user_by_email, get_plan_by_user_id
from datetime import date


def get_user_inputs():
    email = input("What is your email adress? (user ID) ")
    age =int(input("How old are you? "))
    sex = int(input("Are you male or female? ")) ## M = 1, F = 2
    height_in = int(input('How tall are you (in)? '))
    weight = float(input('What is your weight? '))
    start_date = date.today()
    print('''
          What is your activity level?
          1 - Sedentary (< 5,000 steps/ day)
          2 - Lightly active (5,000 - 7,500 steps/ day)
          3 - Moderately active (7,500 - 10,000 steps/ day)
          4 - Very active (10,000 - 12,500 steps/ day)
          5 - Extremely active (12,500+ steps/ day) 

        ''')
    activity_level = int(input('What is your daily activity level? '))
    goal_weight = float(input('What is your goal weight(lbs):? '))
    weeks_to_goal = int(input('''How many weeks would you like to diet: 
                              Note: If no timeframe type "0"'''))
    print("""
    Select your check-in day:
    1 - Monday
    2 - Tuesday
    3 - Wednesday
    4 - Thursday
    5 - Friday
    6 - Saturday
    7 - Sunday
    """)
    checkin_day = int(input("Enter the number for your check-in day: "))

    return { ##returns data as dictionary
        "age": age,
        "sex": sex,
        "height_in": height_in,
        "weight": weight,
        "activity_level": activity_level,
        "start_date": start_date,
        "goal_weight": goal_weight,
        "weeks_to_goal": weeks_to_goal,
        "checkin_day": checkin_day,
        "email": email

    }

def calculate_tdee(user_data):
    bmr = 0
    weight = user_data["weight"]
    age = user_data["age"]
    height_in = user_data["height_in"]
    sex = user_data["sex"]
    if sex == 1: ## is male
        bmr = (10*(weight/2.205))+(6.25*(height_in*2.54))-(5*age)+5
    else: ## is woman
        bmr = (10*(weight/2.205))+(6.25*(height_in*2.54))-(5*age)-161
    activity_multipliers = {
        1: 1.2,
        2: 1.375,
        3: 1.55,
        4: 1.725,
        5: 1.9
    }
    multiplier = activity_multipliers[user_data["activity_level"]]
    tdee = bmr*multiplier
    return round(tdee, 2)


def calculate_plan(user_data, tdee):
    weight = user_data["weight"]
    goal_weight = user_data["goal_weight"]
    weeks_to_goal = user_data["weeks_to_goal"]
    sex = user_data["sex"]
    lbs_to_lose = weight - goal_weight                    ## rate of loss is lbs/week
    if weeks_to_goal > 0:
        rate_of_loss_pct = ((lbs_to_lose / weeks_to_goal)/weight)*100 ## % bodyweight to lose per week
        print('You need to lose', round((weight - goal_weight) / weeks_to_goal, 2), 'lbs per week to reach your goal!')

    else:
        agressive_rate = int(input('''How agressive would you like to diet: 
                               Type: 1 for easy
                                     2 for moderate
                                     3 for agressive'''))
        if agressive_rate == 1:
            rate_of_loss_pct = .5
        elif agressive_rate == 2:
            rate_of_loss_pct = .75
        elif agressive_rate == 3:
            rate_of_loss_pct = 1
        else:
            rate_of_loss_pct = .75
        print('You should try to lose', round(weight*(rate_of_loss_pct/100), 2), 'lbs per week to reach your goal!')
    
    weekly_deficit = (rate_of_loss_pct/100) *weight*3500
    cal_rx = tdee-(weekly_deficit/7)
    protein_rx = weight
    fat_rx = weight * .33
    carb_rx = (cal_rx - (protein_rx * 4)-(fat_rx*9)) / 4
    
## flag for too agressive of diet 
    if sex == 1 and rate_of_loss_pct > 1:
        print('Warning! This is a very agressive rate of loss and may lead to negative side effects.')
    elif sex == 2 and rate_of_loss_pct > .8:
        print('Warning! This is a very agressive rate of loss and may lead to negative side effects.')


    return {
    "goal_weight": round(goal_weight, 2),
    "weeks_to_goal": weeks_to_goal,
    "tdee": round(tdee, 0),
    "rate_of_loss_pct": round(rate_of_loss_pct, 3),
    "protein_rx": round(protein_rx, 0),
    "fat_rx": round(fat_rx, 0),
    "carb_rx": round(carb_rx, 0),
    "cal_rx": round(cal_rx, 0)
    }
    
    

if __name__ == "__main__":
    create_tables()
    
    email = input("Enter your email address: ").strip().lower()
    user = get_user_by_email(email)

    if user:
        user_id = user[0]
        plan_data = get_plan_by_user_id(user_id)
        print(f"\nWelcome back!")
        print("""
What would you like to do?
1 - Weekly check-in
2 - View current plan
        """)
        choice = int(input("Enter 1 or 2: "))

        if choice == 1: ## imports needed variables 
            from checkin import get_checkin_inputs, calculate_checkin
            from database import insert_checkin
            from engine import run_engine

            user_data = {
                "age": user[3],
                "sex": user[4],
                "height_in": user[5],
                "weight": user[6],
                "activity_level": user[7],
                "start_date": user[2],
                "checkin_day": user[8]
            }

            checkin_data = get_checkin_inputs(user_id, plan_data)
            calculated_data = calculate_checkin(checkin_data, user_data, plan_data)
            insert_checkin(checkin_data, calculated_data)
            run_engine(checkin_data, calculated_data, plan_data, user_data)
        elif choice == 2:
            plan = get_plan_by_user_id(user_id)
            if plan:
                print(f"""
{'='*30}
        YOUR CURRENT PLAN
{'='*30}
Daily Calories:       {plan_data['cal_rx']} kcal
Protein:              {plan_data['protein_rx']}g
Carbs:                {plan_data['carb_rx']}g
Fat:                  {plan_data['fat_rx']}g
{'─'*30}
TDEE:                 {plan_data['tdee']} kcal
Rate of Loss:         {plan_data['rate_of_loss_pct']}% BW/week
Goal Weight:          {plan_data['goal_weight']} lbs
Timeframe:            {plan_data['weeks_to_goal']} weeks
{'='*30}
                """)
            else:
                print("No plan found.")
    else:
        print("\nNo account found. Let's create your plan!")
        user_data = get_user_inputs()
        tdee = calculate_tdee(user_data)
        plan_data = calculate_plan(user_data, tdee)
        user_id = insert_user(user_data)
        insert_plan(plan_data, user_id)
        print(f"""
{'='*30}
        YOUR DIET PLAN
{'='*30}
Daily Calories:       {plan_data['cal_rx']} kcal
Protein:              {plan_data['protein_rx']}g
Carbs:                {plan_data['carb_rx']}g
Fat:                  {plan_data['fat_rx']}g
{'─'*30}
TDEE:                 {plan_data['tdee']} kcal
Rate of Loss:         {round(plan_data['rate_of_loss_pct'], 2)}% BW/week
Timeframe:            {plan_data['weeks_to_goal']} weeks
Goal Weight:          {plan_data['goal_weight']} lbs
{'='*30}
        """)