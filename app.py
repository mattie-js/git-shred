import streamlit as st
from database import create_tables, get_user_by_email, get_plan_by_user_id, get_last_checkin

## styling
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background-color: #F8F9FA;
    }
    
    [data-testid="stHeader"] {
        background-color: #F8F9FA;
    }

    h1 {
        color: #1A1A1A !important;
        font-weight: 700 !important;
    }
    
    h2, h3 {
        color: #2D5016 !important;
        font-weight: 600 !important;
    }

    [data-testid="stMetricValue"] {
        font-size: 1.4rem !important;
        font-weight: 700 !important;
        color: #1A1A1A !important;
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.85rem !important;
        color: #6B7280 !important;
        font-weight: 500 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }
    </style>
""", unsafe_allow_html=True)

## initialize database
## initialize database once per session
if "db_initialized" not in st.session_state:
    create_tables()
    st.session_state["db_initialized"] = True

## page config
st.set_page_config(
    page_title="Git Shred",
    page_icon="💪",
    layout="centered",
    initial_sidebar_state="collapsed"
)

## title
st.title("💪 Git Shred")
st.subheader("Adaptive Diet Coaching System")

## login
st.divider()
email = st.text_input("Enter your email address to get started:")

if email:
    email = email.strip().lower()
    user = get_user_by_email(email)

    if user: ##session_state
        user_id = user[0]
        st.session_state["user_id"] = user_id
        st.session_state["user"] = user
        plan_data = get_plan_by_user_id(user_id)  ## fetch plan data for all menu options
        st.divider()

        ## initialize menu choice in session state
        if "menu_choice" not in st.session_state:
            st.session_state["menu_choice"] = None

        ## two buttons side by side
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("📋 Weekly Check-in", use_container_width=True):
                st.session_state["menu_choice"] = "checkin"
        with col_btn2:
            if st.button("📊 View Current Plan", use_container_width=True):
                st.session_state["menu_choice"] = "plan"

        choice = st.session_state["menu_choice"]

        if choice == "checkin": ## check in form
            from checkin import calculate_checkin
            from database import insert_checkin, update_plan
            from engine import run_engine

            ## build user_data dict from database tuple
            user_data = {
                "age": user[3],
                "sex": user[4],
                "height_in": user[5],
                "weight": user[6],
                "activity_level": user[7],
                "start_date": user[2],
                "checkin_day": user[8]
            }

            st.subheader("Weekly Check-in")
            st.divider()

            from datetime import date, timedelta
            ## day mapping
            day_names = {1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday", 5: "Friday", 6: "Saturday", 7: "Sunday"}
            today = date.today()
            today_day_num = today.isoweekday()  ## 1=Monday, 7=Sunday
            checkin_day_num = user[8]  ## stored checkin day from users table
            scheduled_day_name = day_names[checkin_day_num]
            today_name = day_names[today_day_num]

            ## initialize override states
            if "override_day" not in st.session_state:
                st.session_state["override_day"] = False
            if "override_weekly" not in st.session_state:
                st.session_state["override_weekly"] = False

            ## check if today is their checkin day
            if today_day_num != checkin_day_num and not st.session_state["override_day"]:
                st.warning(f"Your scheduled check-in day is **{scheduled_day_name}**. Today is **{today_name}**.")
                if st.button("Check in anyway", key="btn_override_day"):
                    st.session_state["override_day"] = True
                    st.rerun()
                st.stop()

            ## check if they already checked in this week
            last_checkin = get_last_checkin(user[0])
            if last_checkin:
                last_date = last_checkin[0]
                if isinstance(last_date, str):
                    from datetime import datetime
                    last_date = datetime.strptime(last_date, "%Y-%m-%d").date()
                days_since_last = (today - last_date).days
                if days_since_last < 6 and not st.session_state["override_weekly"]:
                    st.warning(f"You checked in {days_since_last} days ago. Check-ins are once weekly.")
                    if st.button("Check in anyway", key="btn_override_weekly"):
                        st.session_state["override_weekly"] = True
                        st.rerun()
                    st.stop()

            with st.form("checkin_form"):
                avg_weight_lbs = st.number_input("Average weight this week (lbs)", min_value=80, max_value=600, step=1, value=None, placeholder="Enter your average weight")
                days_tracked = st.number_input("How many days did you track your weight? (1-7)", min_value=1, max_value=7, step=1, value=None, placeholder="Enter number of days")
                avg_step_count = st.number_input("Average daily step count this week", min_value=0, max_value=100000, step=100, value=None, placeholder="Enter average steps")

                strength_subj = st.selectbox("Strength this week", [
                    "1 - Getting stronger",
                    "2 - Maintaining strength",
                    "3 - Getting weaker"
                ])

                fatigue_subj = st.slider("Fatigue this week (1-10, 10 being most fatigued)", min_value=1, max_value=10, value=5)

                days_adherent = st.number_input("How many days did you stick to your plan? (0-7)", min_value=0, max_value=7, step=1, value=None, placeholder="Enter number of days")

                if_off_plan = st.selectbox("Were you off plan any days?", ["No — fully adherent", "Yes — I know roughly how many calories over", "Yes — I went completely off the rails"])

                calories_over_input = None
                if if_off_plan == "Yes — I know roughly how many calories over":
                    calories_over_input = st.number_input("Total calories over across off days", min_value=0, max_value=10000, step=50, value=None, placeholder="Enter total calories over")

                checkin_submitted = st.form_submit_button("Submit Check-in")

            calories_over = None
            off_the_rails = 0
        
            if checkin_submitted:
                ## override contradictory adherence answers
                if int(days_adherent) == 7:
                    if_off_plan = "No — fully adherent"
                    calories_over = None
                    off_the_rails = 0

                from datetime import date

                ## parse selectbox
                strength_int = int(strength_subj[0])

                ## handle off plan logic
                if if_off_plan == "Yes — I know roughly how many calories over":
                    calories_over = float(calories_over_input) if calories_over_input else None
                elif if_off_plan == "Yes — I went completely off the rails":
                    off_the_rails = 1

                ## build checkin_data dictionary
                checkin_data = {
                    "user_id": user[0],
                    "check_in_date": date.today(),
                    "avg_weight_lbs": float(avg_weight_lbs),
                    "days_tracked": int(days_tracked),
                    "avg_step_count": int(avg_step_count),
                    "strength_subj": strength_int,
                    "fatigue_subj": int(fatigue_subj),
                    "days_adherent": int(days_adherent),
                    "calories_over": calories_over,
                    "off_the_rails": off_the_rails,
                    "lbs_to_go": round(float(avg_weight_lbs) - plan_data["goal_weight"], 2)
                }

                ## run calculations
                calculated_data = calculate_checkin(checkin_data, user_data, plan_data)

                ## save to database
                insert_checkin(checkin_data, calculated_data)

                ## run engine
                messages = run_engine(checkin_data, calculated_data, plan_data, user_data)

                ## display messages
                st.divider()
                st.subheader("Your Weekly Recommendation")
                for msg_type, msg_text in messages:
                    if msg_type == "error":
                        st.error(msg_text)
                    elif msg_type == "warning":
                        st.warning(msg_text)
                    elif msg_type == "success":
                        st.success(msg_text)
                    elif msg_type == "info":
                        st.info(msg_text)

        elif choice == "plan":
            plan = get_plan_by_user_id(user[0])
            if plan:
                st.subheader("Your Current Plan")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"""
                        <div style="background:white; border:1px solid #E5E7EB; border-radius:12px; padding:1.5rem; margin-bottom:0.5rem;">
                            <p style="color:#6B7280; font-size:0.8rem; text-transform:uppercase; letter-spacing:0.05em; margin:0 0 0.3rem 0;">Daily Calories</p>
                            <p style="font-size:1.6rem; font-weight:700; color:#1A1A1A; margin:0;">{int(plan['cal_rx'])} kcal</p>
                        </div>
                        <div style="background:white; border:1px solid #E5E7EB; border-radius:12px; padding:1.5rem; margin-bottom:0.5rem;">
                            <p style="color:#6B7280; font-size:0.8rem; text-transform:uppercase; letter-spacing:0.05em; margin:0 0 0.3rem 0;">Protein</p>
                            <p style="font-size:1.6rem; font-weight:700; color:#1A1A1A; margin:0;">{int(plan['protein_rx'])}g</p>
                        </div>
                        <div style="background:white; border:1px solid #E5E7EB; border-radius:12px; padding:1.5rem; margin-bottom:0.5rem;">
                            <p style="color:#6B7280; font-size:0.8rem; text-transform:uppercase; letter-spacing:0.05em; margin:0 0 0.3rem 0;">Carbs</p>
                            <p style="font-size:1.6rem; font-weight:700; color:#1A1A1A; margin:0;">{int(plan['carb_rx'])}g</p>
                        </div>
                        <div style="background:white; border:1px solid #E5E7EB; border-radius:12px; padding:1.5rem; margin-bottom:0.5rem;">
                            <p style="color:#6B7280; font-size:0.8rem; text-transform:uppercase; letter-spacing:0.05em; margin:0 0 0.3rem 0;">Fat</p>
                            <p style="font-size:1.6rem; font-weight:700; color:#1A1A1A; margin:0;">{int(plan['fat_rx'])}g</p>
                        </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.markdown(f"""
                        <div style="background:white; border:1px solid #E5E7EB; border-radius:12px; padding:1.5rem; margin-bottom:0.5rem;">
                            <p style="color:#6B7280; font-size:0.8rem; text-transform:uppercase; letter-spacing:0.05em; margin:0 0 0.3rem 0;">TDEE</p>
                            <p style="font-size:1.6rem; font-weight:700; color:#1A1A1A; margin:0;">{int(plan['tdee'])} kcal</p>
                        </div>
                        <div style="background:white; border:1px solid #E5E7EB; border-radius:12px; padding:1.5rem; margin-bottom:0.5rem;">
                            <p style="color:#6B7280; font-size:0.8rem; text-transform:uppercase; letter-spacing:0.05em; margin:0 0 0.3rem 0;">Rate of Loss</p>
                            <p style="font-size:1.6rem; font-weight:700; color:#1A1A1A; margin:0;">{round(plan['rate_of_loss_pct'], 2)}% BW/week</p>
                        </div>
                        <div style="background:white; border:1px solid #E5E7EB; border-radius:12px; padding:1.5rem; margin-bottom:0.5rem;">
                            <p style="color:#6B7280; font-size:0.8rem; text-transform:uppercase; letter-spacing:0.05em; margin:0 0 0.3rem 0;">Goal Weight</p>
                            <p style="font-size:1.6rem; font-weight:700; color:#1A1A1A; margin:0;">{int(plan['goal_weight'])} lbs</p>
                        </div>
                        <div style="background:white; border:1px solid #E5E7EB; border-radius:12px; padding:1.5rem; margin-bottom:0.5rem;">
                            <p style="color:#6B7280; font-size:0.8rem; text-transform:uppercase; letter-spacing:0.05em; margin:0 0 0.3rem 0;">Timeframe</p>
                            <p style="font-size:1.6rem; font-weight:700; color:#1A1A1A; margin:0;">{plan['weeks_to_goal']} weeks</p>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.error("No plan found.")
    else:
        st.warning("No account found. Let's create your plan!")
        st.divider()
        st.subheader("Create Your Plan")

        with st.form("plan_creation"): ##runs form as multiple inputs at once. st is reactive so no submitting inputs one by one
            email_create = st.text_input("Email address")
            age = st.number_input("Age", min_value=10, max_value=100, step=1, value=None, placeholder="Enter your age")
            sex = st.selectbox("Sex", ["Male", "Female"])
            height_in = st.number_input("Height (inches)", min_value=50, max_value=84, step=1, value=None, placeholder="Enter your height in inches", format="%d")
            weight = st.number_input("Current weight (lbs)", min_value=80, max_value=600, step=1, value=None, placeholder="Enter your weight in pounds", format="%d")

            st.write("**Activity Level**")
            activity_level = st.selectbox("Select your activity level", [
                "1 - Sedentary (< 5,000 steps/day)",
                "2 - Lightly active (5,000 - 7,500 steps/day)",
                "3 - Moderately active (7,500 - 10,000 steps/day)",
                "4 - Very active (10,000 - 12,500 steps/day)",
                "5 - Extremely active (12,500+ steps/day)"
            ])

            goal_weight = st.number_input("Goal weight (lbs)", min_value=80, max_value=600, step=1, value=None, placeholder="Enter your goal weight in pounds", format="%d")
            weeks_to_goal = st.number_input("Timeframe (weeks) — enter 0 if no timeframe", min_value=0, max_value=104, step=1, value=None, placeholder="Enter your timeframe in weeks.")

            st.write("**Check-in Day**")
            checkin_day = st.selectbox("Select your weekly check-in day", [
                "1 - Monday",
                "2 - Tuesday",
                "3 - Wednesday",
                "4 - Thursday",
                "5 - Friday",
                "6 - Saturday",
                "7 - Sunday"
            ])

            submitted = st.form_submit_button("Create My Plan") ##submits form and creates plan

        if submitted:
            from datetime import date
            from main import calculate_tdee, calculate_plan
            from database import insert_user, insert_plan

            ## parse selectbox values to integers
            sex_int = 1 if sex == 'Male' else 2
            activity_int = int(activity_level[0]) ## [0 calls the first part of string, "1-sedentary"]
            checkin_int = int(checkin_day[0])

            user_data = {
                "email": email_create.strip().lower(),
                "age": int(age),
                "sex": sex_int,
                "height_in": int(height_in),
                "weight": float(weight),
                "activity_level": activity_int,
                "goal_weight": float(goal_weight),
                "weeks_to_goal": int(weeks_to_goal),
                "checkin_day": checkin_int,
                "start_date": date.today()
            }

            tdee = calculate_tdee(user_data)
            plan_data = calculate_plan(user_data, tdee)
            user_id = insert_user(user_data)
            insert_plan(plan_data, user_id)

            st.success("Plan created successfully!")
            st.divider()
            st.subheader("Your Diet Plan")

            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                    <div style="background:white; border:1px solid #E5E7EB; border-radius:12px; padding:1.5rem; margin-bottom:0.5rem;">
                        <p style="color:#6B7280; font-size:0.8rem; text-transform:uppercase; letter-spacing:0.05em; margin:0 0 0.3rem 0;">Daily Calories</p>
                        <p style="font-size:1.6rem; font-weight:700; color:#1A1A1A; margin:0;">{int(plan_data['cal_rx'])} kcal</p>
                    </div>
                    <div style="background:white; border:1px solid #E5E7EB; border-radius:12px; padding:1.5rem; margin-bottom:0.5rem;">
                        <p style="color:#6B7280; font-size:0.8rem; text-transform:uppercase; letter-spacing:0.05em; margin:0 0 0.3rem 0;">Protein</p>
                        <p style="font-size:1.6rem; font-weight:700; color:#1A1A1A; margin:0;">{int(plan_data['protein_rx'])}g</p>
                    </div>
                    <div style="background:white; border:1px solid #E5E7EB; border-radius:12px; padding:1.5rem; margin-bottom:0.5rem;">
                        <p style="color:#6B7280; font-size:0.8rem; text-transform:uppercase; letter-spacing:0.05em; margin:0 0 0.3rem 0;">Carbs</p>
                        <p style="font-size:1.6rem; font-weight:700; color:#1A1A1A; margin:0;">{int(plan_data['carb_rx'])}g</p>
                    </div>
                    <div style="background:white; border:1px solid #E5E7EB; border-radius:12px; padding:1.5rem; margin-bottom:0.5rem;">
                        <p style="color:#6B7280; font-size:0.8rem; text-transform:uppercase; letter-spacing:0.05em; margin:0 0 0.3rem 0;">Fat</p>
                        <p style="font-size:1.6rem; font-weight:700; color:#1A1A1A; margin:0;">{int(plan_data['fat_rx'])}g</p>
                    </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                    <div style="background:white; border:1px solid #E5E7EB; border-radius:12px; padding:1.5rem; margin-bottom:0.5rem;">
                        <p style="color:#6B7280; font-size:0.8rem; text-transform:uppercase; letter-spacing:0.05em; margin:0 0 0.3rem 0;">TDEE</p>
                        <p style="font-size:1.6rem; font-weight:700; color:#1A1A1A; margin:0;">{int(plan_data['tdee'])} kcal</p>
                    </div>
                    <div style="background:white; border:1px solid #E5E7EB; border-radius:12px; padding:1.5rem; margin-bottom:0.5rem;">
                        <p style="color:#6B7280; font-size:0.8rem; text-transform:uppercase; letter-spacing:0.05em; margin:0 0 0.3rem 0;">Rate of Loss</p>
                        <p style="font-size:1.6rem; font-weight:700; color:#1A1A1A; margin:0;">{round(plan_data['rate_of_loss_pct'], 2)}% BW/week</p>
                    </div>
                    <div style="background:white; border:1px solid #E5E7EB; border-radius:12px; padding:1.5rem; margin-bottom:0.5rem;">
                        <p style="color:#6B7280; font-size:0.8rem; text-transform:uppercase; letter-spacing:0.05em; margin:0 0 0.3rem 0;">Goal Weight</p>
                        <p style="font-size:1.6rem; font-weight:700; color:#1A1A1A; margin:0;">{int(plan_data['goal_weight'])} lbs</p>
                    </div>
                    <div style="background:white; border:1px solid #E5E7EB; border-radius:12px; padding:1.5rem; margin-bottom:0.5rem;">
                        <p style="color:#6B7280; font-size:0.8rem; text-transform:uppercase; letter-spacing:0.05em; margin:0 0 0.3rem 0;">Timeframe</p>
                        <p style="font-size:1.6rem; font-weight:700; color:#1A1A1A; margin:0;">{plan_data['weeks_to_goal']} weeks</p>
                    </div>
                """, unsafe_allow_html=True)