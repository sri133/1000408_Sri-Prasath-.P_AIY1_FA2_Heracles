import streamlit as st
import google.generativeai as genai
from datetime import datetime

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Heracles Coach AI 🏆",
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

MODEL_NAME = "gemini-2.5-flash"

# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.title("🏃‍♂️ Heracles CoachBot AI – Smart Fitness Assistant")
st.caption("AI-powered virtual coach for youth athletes & fitness enthusiasts")

st.markdown("---")

# --------------------------------------------------
# USER INPUT SECTION
# --------------------------------------------------
st.subheader("👤 Athlete Profile")

sport = st.selectbox(
    "Sport",
    [
        "Football",
        "Cricket",
        "Basketball",
        "Athletics",
        "Badminton",
        "Hockey",
        "Calisthenics",
        "General Fitness"
    ]
)

position = st.text_input(
    "Player Position / Focus Area (e.g., Striker, Bowler, Upper Body)"
)

injury = st.text_area(
    "Injury History / Risk Zone",
    placeholder="e.g., Knee strain, ankle sprain, none"
)

goal = st.selectbox(
    "Primary Goal",
    [
        "Build Stamina",
        "Increase Strength",
        "Post-Injury Recovery",
        "Speed & Agility",
        "Tactical Improvement",
        "Bodybuilding (Muscle Gain)",
        "Fat Burning (Weight Loss)"
    ]
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

    special_instructions = ""

    if goal == "Bodybuilding (Muscle Gain)":
        special_instructions = """
        Focus on hypertrophy-based training.
        Include sets, reps, rest time.
        Mention progressive overload.
        Add protein-rich diet advice.
        Keep training sustainable.
        """

    elif goal == "Fat Burning (Weight Loss)":
        special_instructions = """
        Focus on safe fat loss.
        Combine strength training and cardio.
        Avoid crash diets.
        Mention calorie awareness (no extreme restriction).
        Promote consistency and recovery.
        """

    return f"""
You are CoachBot AI, a certified youth sports coach and fitness scientist.

Athlete Details:
- Sport: {sport}
- Position / Focus: {position}
- Injury History: {injury}
- Goal: {goal}
- Diet: {diet}
- Training Intensity: {intensity}

Special Instructions:
{special_instructions}

Rules:
- Be safety-first and injury-aware.
- Avoid medical diagnosis.
- Avoid unsafe or extreme exercises.
- Use clear, structured sections.
- Keep language simple and motivating.

Generate:

1. Weekly Workout Structure
2. Exercise Plan (sets, reps, rest)
3. Injury-Aware Recovery Guidance
4. Nutrition & Hydration Plan
5. Warm-up & Cooldown Routine
"""

# --------------------------------------------------
# GENERATE BUTTON
# --------------------------------------------------
st.markdown("---")

if st.button("🚀 Generate Training Plan"):

    if not position:
        st.warning("Please enter the player position or focus area.")
        st.stop()

    with st.spinner("CoachBot AI is generating your personalized plan..."):

        try:
            model = genai.GenerativeModel(
                model_name=MODEL_NAME,
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

