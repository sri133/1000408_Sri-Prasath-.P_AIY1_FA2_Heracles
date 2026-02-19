import streamlit as st
import google.generativeai as genai
from datetime import datetime

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="CoachBot AI 🏆",
    page_icon="💪",
    layout="centered"
)

# --------------------------------------------------
# LOAD GEMINI API FROM SECRETS
# --------------------------------------------------
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except KeyError:
    st.error("⚠️ Gemini API key not found in Streamlit secrets.")
    st.stop()

# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.title("🏃‍♂️ CoachBot AI – Smart Fitness Assistant")
st.caption("AI-powered virtual coach for youth athletes")

st.markdown("---")

# --------------------------------------------------
# USER INPUT SECTION
# --------------------------------------------------
st.subheader("👤 Athlete Profile")

sport = st.selectbox(
    "Sport",
    ["Football", "Cricket", "Basketball", "Athletics",
     "Badminton", "Hockey", "Calisthenics"]
)

position = st.text_input(
    "Player Position (e.g., Striker, Bowler, Goalkeeper)"
)

injury = st.text_area(
    "Injury History / Risk Zone",
    placeholder="e.g., Knee strain, ankle sprain, none"
)

goal = st.selectbox(
    "Primary Goal",
    ["Build Stamina",
     "Increase Strength",
     "Post-Injury Recovery",
     "Speed & Agility",
     "Tactical Improvement"]
)

diet = st.selectbox(
    "Diet Preference",
    ["Vegetarian", "Non-Vegetarian", "Eggetarian", "Vegan"]
)

intensity = st.selectbox(
    "Training Intensity",
    ["Low", "Moderate", "High"]
)

# --------------------------------------------------
# MODEL TUNING
# --------------------------------------------------
st.markdown("---")
st.subheader("🧪 AI Tuning")

temperature = st.slider(
    "Creativity Level",
    min_value=0.1,
    max_value=0.9,
    value=0.3
)

# --------------------------------------------------
# PROMPT BUILDER
# --------------------------------------------------
def build_prompt():
    return f"""
You are CoachBot AI, a certified youth sports coach and fitness scientist.

Athlete Details:
- Sport: {sport}
- Position: {position}
- Injury History: {injury}
- Goal: {goal}
- Diet: {diet}
- Training Intensity: {intensity}

Instructions:
- Be safety-first and injury-aware.
- Avoid medical diagnosis.
- Avoid extreme or unsafe exercises.
- Use simple, youth-friendly language.
- Provide structured sections.

Generate:

1. Safe position-specific workout plan
2. Injury-aware precautions & recovery advice
3. Tactical / skill coaching tips
4. Nutrition & hydration guidance
5. Warm-up & cooldown routine
"""

# --------------------------------------------------
# GENERATE BUTTON
# --------------------------------------------------
st.markdown("---")

if st.button("🚀 Generate Training Plan"):

    if not position:
        st.warning("Please enter the player position.")
        st.stop()

    with st.spinner("CoachBot AI is thinking like a real coach..."):

        try:
            model = genai.GenerativeModel(
                model_name="gemini-2.5-flash",
                generation_config={
                    "temperature": temperature
                }
            )

            response = model.generate_content(build_prompt())

            st.success("✅ Personalized Coaching Plan Ready!")
            st.markdown(response.text)

        except Exception as e:
            st.error("⚠️ Something went wrong while generating the plan.")
            st.exception(e)

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.markdown("---")
st.caption(
    "⚠️ Educational use only. Consult a certified coach or doctor for medical concerns.\n"
    f"Session Time: {datetime.now().strftime('%d %b %Y %H:%M')}"
)

