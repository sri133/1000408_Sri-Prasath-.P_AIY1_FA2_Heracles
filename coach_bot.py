import streamlit as st
import google.generativeai as genai
import sqlite3
import hashlib
import pandas as pd
import time
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

# --------------------------------------------------
# CONFIG
# --------------------------------------------------
st.set_page_config(page_title="HERACLES 🏛", layout="wide")

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# --------------------------------------------------
# DATABASE
# --------------------------------------------------
conn = sqlite3.connect("heracles.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    xp INTEGER DEFAULT 0
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS workouts(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT,
    goal TEXT,
    content TEXT,
    date TEXT,
    pinned INTEGER DEFAULT 0,
    completed INTEGER DEFAULT 0
)
""")

conn.commit()

# --------------------------------------------------
# UTILITIES
# --------------------------------------------------
def hash_pass(p):
    return hashlib.sha256(p.encode()).hexdigest()

def badge(xp):
    if xp >= 1000:
        return "🏆 Consistency King"
    elif xp >= 500:
        return "🔥 Fat Burner"
    elif xp >= 250:
        return "💪 Muscle Builder"
    return "👶 Beginner"

def generate_ai(prompt, temp):
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        generation_config={"temperature": temp}
    )
    return model.generate_content(prompt).text

def export_pdf(text, user):
    file = f"{user}_progress.pdf"
    doc = SimpleDocTemplate(file)
    styles = getSampleStyleSheet()
    story = [Paragraph(text, styles["Normal"])]
    doc.build(story)
    return file

# --------------------------------------------------
# AUTH SYSTEM
# --------------------------------------------------
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
            if c.fetchone():
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
                st.success("Registered successfully")
            except:
                st.error("Username exists")

else:

    user = st.session_state.user

    # Sidebar
    st.sidebar.title(f"Welcome {user}")

    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.rerun()

    # XP + Badge
    c.execute("SELECT xp FROM users WHERE username=?", (user,))
    xp = c.fetchone()[0]

    st.sidebar.write(f"XP: {xp}")
    st.sidebar.write(f"Badge: {badge(xp)}")
    st.sidebar.progress(min(xp/1000, 1.0))

    # Leaderboard
    st.sidebar.subheader("🏆 Leaderboard")
    lb = pd.read_sql_query("SELECT username,xp FROM users ORDER BY xp DESC", conn)
    st.sidebar.dataframe(lb, use_container_width=True)

    # --------------------------------------------------
    # MAIN APP
    # --------------------------------------------------
    st.title("🏋️ HERACLES Fitness Engine")

    goal = st.selectbox("Goal",
        ["Muscle Building","Fat Burning","Stamina","Recovery"])

    level = st.selectbox("Level",
        ["Beginner","Intermediate","Advanced"])

    difficulty = st.slider("Difficulty",1,10,5)

    temp = st.slider("AI Creativity",0.1,0.9,0.3)

    # Generate Workout
    if st.button("Generate Workout"):
        prompt = f"""
        Create a safe {goal} workout.
        Level: {level}
        Difficulty: {difficulty}/10.
        Structured format.
        """

        plan = generate_ai(prompt, temp)
        st.session_state.last_plan = plan
        st.markdown(plan)

        c.execute("""
        INSERT INTO workouts(user,goal,content,date,pinned,completed)
        VALUES(?,?,?,?,?,?)
        """,(user,goal,plan,str(datetime.now()),0,0))
        conn.commit()

    # Regenerate
    if "last_plan" in st.session_state:
        if st.button("🔄 Regenerate"):
            st.rerun()

        # Mark completed
        c.execute("""
        SELECT id FROM workouts
        WHERE user=? ORDER BY date DESC LIMIT 1
        """,(user,))
        last_id = c.fetchone()[0]

        if st.button("✅ Mark Workout Completed"):
            c.execute("UPDATE workouts SET completed=1 WHERE id=?",(last_id,))
            c.execute("UPDATE users SET xp=xp+50 WHERE username=?",(user,))
            conn.commit()
            st.success("+50 XP Earned!")
            st.rerun()

        if st.button("📌 Pin Workout"):
            c.execute("UPDATE workouts SET pinned=1 WHERE id=?",(last_id,))
            conn.commit()
            st.success("Workout Pinned!")

    # --------------------------------------------------
    # PROGRESS TRACKING
    # --------------------------------------------------
    st.subheader("📊 Progress Tracking")

    filter_goal = st.selectbox("Filter Goal",
        ["All","Muscle Building","Fat Burning","Stamina","Recovery"])

    if filter_goal == "All":
        df = pd.read_sql_query(
            "SELECT * FROM workouts WHERE user=? AND completed=1",
            conn, params=(user,))
    else:
        df = pd.read_sql_query(
            "SELECT * FROM workouts WHERE user=? AND goal=? AND completed=1",
            conn, params=(user,filter_goal))

    if not df.empty:
        chart_data = df.groupby("date").count()["goal"]
        st.line_chart(chart_data)

    # Goal Completion %
    target = 20
    total_completed = len(df)
    completion = min(total_completed/target,1.0)
    st.progress(completion)
    st.write(f"{round(completion*100)}% Goal Completed")

    # --------------------------------------------------
    # BMI
    # --------------------------------------------------
    st.subheader("🧮 BMI Calculator")
    w = st.number_input("Weight (kg)")
    h = st.number_input("Height (cm)")
    if h > 0:
        bmi = w / ((h/100)**2)
        st.write(f"BMI: {round(bmi,2)}")

    # --------------------------------------------------
    # REST TIMER
    # --------------------------------------------------
    st.subheader("⏱ Rest Timer")

    if st.button("Start 30s Rest"):
        placeholder = st.empty()
        for i in range(30,0,-1):
            placeholder.markdown(f"## ⏳ {i} sec")
            time.sleep(1)
        placeholder.markdown("### ✅ Rest Complete!")

    # --------------------------------------------------
    # FORM TIPS
    # --------------------------------------------------
    st.subheader("🧠 AI Form Tips")
    ex = st.text_input("Exercise Name")
    if st.button("Get Tips"):
        tips = generate_ai(f"Give safe form tips for {ex}",0.3)
        st.write(tips)

    # --------------------------------------------------
    # EXPORT PDF
    # --------------------------------------------------
    if st.button("💾 Export Progress PDF"):
        text = f"{user} XP: {xp}"
        file = export_pdf(text,user)
        with open(file,"rb") as f:
            st.download_button("Download PDF",f,file_name=file)

    # --------------------------------------------------
    # ACCOUNT SETTINGS
    # --------------------------------------------------
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
