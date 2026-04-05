# Git Shred — Adaptive Diet Adjustment Engine

A Python-based diet planning and adjustment tool that combines exercise science domain knowledge with software development. Built as a portfolio project to demonstrate the intersection of health analytics and programming.

## What It Does

- Generates a personalized diet plan based on user inputs like sex, height, weight, goals, etc.
- Offers weekly check-ins that track metrics including bodyweight, steps, strength, fatigue, and adherence
    - This weekly check-in model imitates the format of many human health and fitness coaching services
- Runs a two-bucket scoring engine (deficit score + recovery score) to produce data-driven recommendations
- Stores all user data in a relational SQLite database across three normalized tables

## Tech Stack

- Python
- SQLite
- Pandas (planned)
- Streamlit (planned web interface)

## How To Run

1. Clone the repo
2. Create a virtual environment: `python3 -m venv venv`
3. Activate it: `source venv/bin/activate`
4. Run the program: `python3 main.py`

## Project Structure

- `main.py` — entry point, user login, initial plan creation
- `checkin.py` — weekly check-in inputs and calculations
- `engine.py` — two-bucket scoring and recommendation engine
- `database.py` — SQLite connection, table creation, all data functions
- `test.py` — scenario testing for engine validation

## Background

Built by a kinesiology student and personal trainer with 4 years of coaching experience and 6 years of training and dieting experience. The recommendation logic is grounded in exercise science principles along with personal coaching experience and domain knowledge.