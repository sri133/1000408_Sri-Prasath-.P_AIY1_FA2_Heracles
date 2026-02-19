import streamlit as st
import google.generativeai as genai
import sqlite3
import hashlib
import pandas as pd
import matplotlib.pyplot as plt
import time
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet

# ---------------------------
# PAGE CONFIG
# ---------------------------
st.set_page_config(page_title="HERACLES 🏛", layout="wide")

# ---------------------------
# GEMINI API
# ---------------------------
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# ---------------------------
# DATABASE
# ---------------------------
conn = sqlite3.connect("heracles.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    xp INTEGER DEFAULT 0,
    goal TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS workouts(
    user TEXT,
    goal TEXT,
    content TEXT,
    date TEXT,
    pinned INTEGER DEFAULT 0
)
""")

conn.commit()

# ---------------------------
# UTIL FUNCTIONS
# ---------------------------
def hash_pass(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_badge(xp):
    if xp >= 1000:
        return "🏆 Consistency King"
    elif xp >= 500:
        return "🔥 Fat Burner"
    elif xp >= 250:
        return "💪 Muscle Builder"
    return "👶 Beginner"

def generate_plan(prompt, temperature):
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        generation_config={"temperature": temperature}
    )
    response = model.generate_content(prompt)
    return response.text

def export_pdf(text, username):
    file_name = f"{username}_progress.pdf"
    doc = SimpleDocTemplate(file_name)
    styles = getSampleStyleSheet()
    story = []
    story.append(Paragraph(text, styles["Normal"]))
    doc.build(story)
    return file_name

# ---------------------------
# AUTH
# ---------------------------
if "user" not in st.session_state:
    st.session_state.user = None

if not st.session_state.user:
    st.title("🏛 HERACLES")

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Login"):
            c.execute("SELECT * FROM users WHERE username=? AND password=?",
                      (u, hash_pass(p)))
            data = c.fetchone()
            if data:
                st.session_state.user = u
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab2:
        new_u = st.text_input("New Username")
        new_p = st.text_input("New Password", type="password")
        if st.button("Register"):
            try:
                c.execute("INSERT INTO users(username,password) VALUES(?,?)",
                          (new_u, hash_pass(new_p)))
                conn.commit()
                st.success("Registered! Please login.")
            except:
                st.error("Username already exists")

else:

    user = st.session_state.user

    st.sidebar.title(f"Welcome {user}")

    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.rerun()

    # XP + Badge
    c.execute("SELECT xp FROM users WHERE username=?", (user,))
    xp = c.fetchone()[0]
    badge = get_badge(xp)

    st.sidebar.write(f"XP: {xp}")
    st.sidebar.write(f"Badge: {badge}")
    st.sidebar.progress(min(xp/1000,1.0))

    # Leaderboard
    st.sidebar.subheader("🏆 Leaderboard")
    df = pd.read_sql_query("SELECT username,xp FROM users ORDER BY xp DESC", conn)
    st.sidebar.dataframe(df)

    # ---------------------------
    # MAIN UI
    # ---------------------------
    st.title("🏋️ HERACLES – Elite Fitness Engine")

    goal = st.selectbox("Goal",
                        ["Muscle Building","Fat Burning","Stamina","Recovery"])

    level = st.selectbox("Level",
                         ["Beginner","Intermediate","Advanced"])

    difficulty = st.slider("Difficulty",1,10,5)

    temperature = st.slider("AI Creativity",0.1,0.9,0.3)

    if st.button("Generate Workout"):
        prompt = f"""
        Create a {goal} workout.
        Level: {level}
        Difficulty: {difficulty}/10
        Safe and structured.
        """
        plan = generate_plan(prompt, temperature)

        st.session_state.last_plan = plan
        st.write(plan)

        c.execute("INSERT INTO workouts VALUES(?,?,?,?,?)",
                  (user,goal,plan,str(datetime.now()),0))
        c.execute("UPDATE users SET xp = xp + 50 WHERE username=?",(user,))
        conn.commit()

    if "last_plan" in st.session_state:
        if st.button("🔄 Regenerate"):
            st.rerun()

        if st.button("📌 Pin Workout"):
            c.execute("UPDATE workouts SET pinned=1 WHERE user=? ORDER BY date DESC LIMIT 1",(user,))
            conn.commit()
            st.success("Pinned!")

    # Workout History
    st.subheader("📆 Workout History")

    filter_goal = st.selectbox("Filter by Goal",
                               ["All","Muscle Building","Fat Burning","Stamina","Recovery"])

    if filter_goal == "All":
        history = pd.read_sql_query(
            "SELECT goal,date FROM workouts WHERE user=?",
            conn, params=(user,))
    else:
        history = pd.read_sql_query(
            "SELECT goal,date FROM workouts WHERE user=? AND goal=?",
            conn, params=(user,filter_goal))

    if not history.empty:
        st.line_chart(history.groupby("date").count())

    # BMI
    st.subheader("🧮 BMI Calculator")
    w = st.number_input("Weight (kg)")
    h = st.number_input("Height (cm)")
    if h>0:
        bmi = w / ((h/100)**2)
        st.write(f"BMI: {round(bmi,2)}")

    st.subheader("⏱ Rest Timer")

if st.button("Start 30s Rest"):
    timer_placeholder = st.empty()

    for i in range(30, 0, -1):
        timer_placeholder.markdown(f"## ⏳ {i} sec")
        time.sleep(1)

    timer_placeholder.markdown("### ✅ Rest Complete!")


    # Form Tips
    st.subheader("🧠 AI Form Check")
    ex = st.text_input("Exercise name")
    if st.button("Get Form Tips"):
        tips = generate_plan(f"Give safe form tips for {ex}",0.3)
        st.write(tips)

    # Goal Completion %
    st.subheader("📊 Goal Completion")
    total = len(history)
    completion = min(total/20,1.0)
    st.progress(completion)
    st.write(f"{round(completion*100)}% Completed")

    # Export PDF
    if st.button("💾 Export Progress PDF"):
        text = f"{user} XP: {xp}"
        file = export_pdf(text,user)
        with open(file,"rb") as f:
            st.download_button("Download PDF",f,file_name=file)

    # Change Password
    st.subheader("🔐 Account Settings")
    newpass = st.text_input("New Password",type="password")
    if st.button("Change Password"):
        c.execute("UPDATE users SET password=? WHERE username=?",
                  (hash_pass(newpass),user))
        conn.commit()
        st.success("Password Updated")

    if st.button("🗑 Delete Account"):
        c.execute("DELETE FROM users WHERE username=?",(user,))
        conn.commit()
        st.session_state.user=None
        st.rerun()

