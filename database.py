import psycopg2
import os
from datetime import date
import json

from dotenv import load_dotenv
load_dotenv()


def create_connection():
    conn = psycopg2.connect(
        host=os.environ.get("DB_HOST"),
        port=os.environ.get("DB_PORT"),
        database=os.environ.get("DB_NAME"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD")
    )
    return conn


def create_tables():
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id SERIAL PRIMARY KEY,
            email TEXT UNIQUE,
            start_date DATE,
            age INTEGER,
            sex INTEGER,
            height_in INTEGER,
            weight_lbs FLOAT,
            activity_level INTEGER,
            checkin_day INTEGER
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS plans (
            plan_id SERIAL PRIMARY KEY,
            user_id INTEGER,
            goal_weight_lbs FLOAT,
            timeframe_weeks INTEGER,
            tdee FLOAT,
            rate_of_loss FLOAT,
            calories INTEGER,
            protein_g FLOAT,
            carbs_g FLOAT,
            fat_g FLOAT,
            prescribed_steps INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS check_ins (
            check_in_id SERIAL PRIMARY KEY,
            user_id INTEGER,
            check_in_date DATE,
            avg_weight_lbs FLOAT,
            total_weeks_in_deficit INTEGER,
            days_adherent INTEGER,
            avg_step_count INTEGER,
            strength_subj INTEGER,
            fatigue_subj INTEGER,
            lbs_to_go FLOAT,
            weekly_rol FLOAT,
            cumulative_rol FLOAT,
            calories_over FLOAT,
            off_the_rails INTEGER,
            recalculated_bmr FLOAT,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    """)

    conn.commit()
    conn.close()

def insert_user(user_data):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (start_date, age, sex, height_in, weight_lbs, activity_level, checkin_day, email)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING user_id
    """, (
        user_data["start_date"],
        user_data["age"],
        user_data["sex"],
        user_data["height_in"],
        user_data["weight"],
        user_data["activity_level"],
        user_data["checkin_day"],
        user_data["email"]
    ))
    user_id = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    return user_id

def get_user_by_email(email):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM users WHERE email = %s
    """, (email,))
    result = cursor.fetchone()
    conn.close()
    return result

def get_plan_by_user_id(user_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM plans WHERE user_id = %s
        ORDER BY plan_id DESC
        LIMIT 1
    """, (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "plan_id": row[0],
            "user_id": row[1],
            "goal_weight": row[2],
            "weeks_to_goal": row[3],
            "tdee": row[4],
            "rate_of_loss_pct": row[5],
            "cal_rx": row[6],
            "protein_rx": row[7],
            "carb_rx": row[8],
            "fat_rx": row[9],
            "prescribed_steps": row[10],
            # is_active is row[11]
            "created_at": str(row[12]),
        }
    return None

def insert_plan(plan_data, user_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO plans (user_id, goal_weight_lbs, timeframe_weeks, tdee, rate_of_loss, calories, protein_g, carbs_g, fat_g)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        user_id,
        plan_data["goal_weight"],
        plan_data["weeks_to_goal"],
        plan_data["tdee"],
        plan_data["rate_of_loss_pct"],
        plan_data["cal_rx"],
        plan_data["protein_rx"],
        plan_data["carb_rx"],
        plan_data["fat_rx"]
    ))
    conn.commit()
    conn.close()

def update_plan(plan_id, new_cal=None, new_steps=None):
    conn = create_connection()
    cursor = conn.cursor()
    if new_cal:
        cursor.execute("""
            UPDATE plans SET calories = %s WHERE plan_id = %s
        """, (new_cal, plan_id))
    if new_steps:
        cursor.execute("""
            UPDATE plans SET prescribed_steps = %s WHERE plan_id = %s
        """, (new_steps, plan_id))
    conn.commit()
    conn.close()

def insert_checkin(checkin_data, calculated_data):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO check_ins (
            user_id, check_in_date, avg_weight_lbs, total_weeks_in_deficit,
            days_adherent, avg_step_count, strength_subj, fatigue_subj,
            lbs_to_go, weekly_rol, cumulative_rol, calories_over,
            off_the_rails, recalculated_bmr
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        checkin_data["user_id"],
        checkin_data["check_in_date"],
        checkin_data["avg_weight_lbs"],
        calculated_data["total_weeks_in_deficit"],
        checkin_data["days_adherent"],
        checkin_data["avg_step_count"],
        checkin_data["strength_subj"],
        checkin_data["fatigue_subj"],
        checkin_data["lbs_to_go"],
        calculated_data["weekly_rol"],
        calculated_data["cumulative_rol"],
        checkin_data["calories_over"],
        checkin_data["off_the_rails"],
        calculated_data["recalculated_bmr"]
    ))
    conn.commit()
    conn.close()

def get_last_two_checkins(user_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT weekly_rol FROM check_ins
        WHERE user_id = %s
        ORDER BY check_in_date DESC
        LIMIT 2
    """, (user_id,))
    results = cursor.fetchall()
    conn.close()
    return results

def get_last_checkin(user_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT check_in_date FROM check_ins
        WHERE user_id = %s
        ORDER BY check_in_date DESC
        LIMIT 1
    """, (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def get_user_by_id(user_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def get_or_create_daily_log(user_id):
    plan = get_plan_by_user_id(user_id)
    if not plan:
        return None

    conn = create_connection()
    cursor = conn.cursor()

    today = date.today()

    cursor.execute("""
        SELECT * FROM daily_logs WHERE user_id = %s AND date = %s
    """, (user_id, today))
    row = cursor.fetchone()

    if row:
        conn.close()
        return {
            "id": row[0],
            "user_id": row[3],
            "plan_id": row[4],
            "date": str(row[5]),
            "status": row[6],
            "target_calories": row[7],
            "target_protein": row[8],
            "actual_calories": row[9],
            "actual_protein": row[10],
            "step_count": row[11],
            "cardio_minutes": row[12],
            "cardio_type": row[13],
            "training_session": row[14],
            "notes": row[15],
            "is_adherent": row[16],
            "training_complete": row[17],
            "nutrition_complete": row[18],
            "cardio_complete": row[19],
            "steps_complete": row[20],
            "supplements_complete": row[21],
            "bodyweight_lbs": row[22],
        }

    cursor.execute("""
        SELECT schedule FROM training_templates WHERE user_id = %s
    """, (user_id,))
    template_row = cursor.fetchone()

    day_name = today.strftime("%A").lower()
    training_session = None
    if template_row:
        schedule = template_row[0]
        training_session = schedule.get(day_name)

    cursor.execute("""
        INSERT INTO daily_logs (
            user_id, plan_id, date, status,
            target_calories, target_protein, training_session
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING *
    """, (
        user_id,
        plan["plan_id"],
        today,
        "open",
        plan["cal_rx"],
        plan["protein_rx"],
        training_session
    ))
    new_row = cursor.fetchone()
    conn.commit()
    conn.close()

    return {
        "id": new_row[0],
        "user_id": new_row[3],
        "plan_id": new_row[4],
        "date": str(new_row[5]),
        "status": new_row[6],
        "target_calories": new_row[7],
        "target_protein": new_row[8],
        "actual_calories": new_row[9],
        "actual_protein": new_row[10],
        "step_count": new_row[11],
        "cardio_minutes": new_row[12],
        "cardio_type": new_row[13],
        "training_session": new_row[14],
        "notes": new_row[15],
        "is_adherent": new_row[16],
        "training_complete": new_row[17],
        "nutrition_complete": new_row[18],
        "cardio_complete": new_row[19],
        "steps_complete": new_row[20],
        "supplements_complete": new_row[21],
        "bodyweight_lbs": new_row[22],
    }

def update_daily_log(log_id, updates):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE daily_logs
        SET
            actual_calories = %s,
            actual_protein = %s,
            step_count = %s,
            cardio_minutes = %s,
            cardio_type = %s,
            training_session = %s,
            notes = %s,
            status = %s,
            is_adherent = %s,
            training_complete = %s,
            nutrition_complete = %s,
            cardio_complete = %s,
            steps_complete = %s,
            supplements_complete = %s,
            bodyweight_lbs = %s,
            updated_at = now()
        WHERE id = %s
        RETURNING *
    """, (
        updates.get("actual_calories"),
        updates.get("actual_protein"),
        updates.get("step_count"),
        updates.get("cardio_minutes"),
        updates.get("cardio_type"),
        updates.get("training_session"),
        updates.get("notes"),
        updates.get("status", "open"),
        updates.get("is_adherent"),
        updates.get("training_complete"),
        updates.get("nutrition_complete"),
        updates.get("cardio_complete"),
        updates.get("steps_complete"),
        updates.get("supplements_complete"),
        updates.get("bodyweight_lbs"),
        log_id
    ))
    row = cursor.fetchone()
    conn.commit()
    conn.close()
    if row:
        return {
            "id": row[0],
            "user_id": row[3],
            "plan_id": row[4],
            "date": str(row[5]),
            "status": row[6],
            "target_calories": row[7],
            "target_protein": row[8],
            "actual_calories": row[9],
            "actual_protein": row[10],
            "step_count": row[11],
            "cardio_minutes": row[12],
            "cardio_type": row[13],
            "training_session": row[14],
            "notes": row[15],
            "is_adherent": row[16],
            "training_complete": row[17],
            "nutrition_complete": row[18],
            "cardio_complete": row[19],
            "steps_complete": row[20],
            "supplements_complete": row[21],
            "bodyweight_lbs": row[22],
        }
    return None

def save_training_template(user_id, schedule):
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id FROM training_templates WHERE user_id = %s
    """, (user_id,))
    existing = cursor.fetchone()
    
    if existing:
        cursor.execute("""
            UPDATE training_templates
            SET schedule = %s
            WHERE user_id = %s
            RETURNING *
        """, (json.dumps(schedule), user_id))
    else:
        cursor.execute("""
            INSERT INTO training_templates (user_id, schedule)
            VALUES (%s, %s)
            RETURNING *
        """, (user_id, json.dumps(schedule)))
    
    row = cursor.fetchone()
    conn.commit()
    conn.close()
    
    return {
        "id": row[0],
        "user_id": row[1],
        "schedule": row[2]
    }

def get_training_template(user_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM training_templates WHERE user_id = %s
    """, (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "id": row[0],
            "user_id": row[1],
            "schedule": row[2]
        }
    return None

def save_supplement_template(user_id, supplements):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id FROM supplement_templates WHERE user_id = %s
    """, (user_id,))
    existing = cursor.fetchone()

    if existing:
        cursor.execute("""
            UPDATE supplement_templates
            SET supplements = %s
            WHERE user_id = %s
            RETURNING *
        """, (json.dumps(supplements), user_id))
    else:
        cursor.execute("""
            INSERT INTO supplement_templates (user_id, supplements)
            VALUES (%s, %s)
            RETURNING *
        """, (user_id, json.dumps(supplements)))

    row = cursor.fetchone()
    conn.commit()
    conn.close()

    return {
        "id": row[0],
        "user_id": row[1],
        "supplements": row[2]
    }

def get_supplement_template(user_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM supplement_templates WHERE user_id = %s
    """, (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "id": row[0],
            "user_id": row[1],
            "supplements": row[2]
        }
    return None

if __name__ == "__main__":
    create_tables()
    print("Tables created successfully")