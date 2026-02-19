# 1000408_Sri-Prasath-.P_AIY1_FA2_Heracles
🏃‍♂️ Heracles CoachBot AI – Smart Fitness Assistant

AI-powered virtual fitness coach built with Streamlit and Google Gemini (Generative AI).

CoachBot AI generates personalized workout plans, injury-aware recovery guidance, tactical advice, and nutrition strategies for young athletes based on their sport, position, and goals.

🚀 Live Demo

🔗 https://1000408sri-prasath-paiy1fa2heracles-hogkefpvitd5jjttsm8z3h.streamlit.app/

📌 Project Overview

Many youth athletes do not have access to professional coaching or personalized training plans.
This project solves that by building a Generative AI-based coaching assistant that:

Creates position-specific workout plans

Adjusts training for injury history

Provides safe muscle gain / fat loss routines

Suggests nutrition guidance based on diet type

Promotes structured and sustainable development

The assistant is safety-focused and avoids extreme or medical advice.

🧠 Tech Stack

Frontend: Streamlit

AI Model: Gemini 2.5 Flash

API Integration: google-generativeai

Language: Python

⚙️ Features
👤 Athlete Profile Inputs

Sport selection

Player position / focus area

Injury history

Primary goal

Diet preference

Training intensity

🧪 AI Tuning

Temperature slider (controls creativity level)

📋 AI Output Includes

Weekly Workout Structure

Exercise Plan (sets, reps, rest)

Injury-Aware Recovery Guidance

Nutrition & Hydration Plan

Warm-up & Cooldown Routine

🔥 Prompt Engineering Strategy

The app dynamically builds structured prompts using:

Sport-specific context

Position awareness

Injury adaptation logic

Goal-based special instructions

Safety-first constraints

Special goal logic implemented:

🏋️ Muscle Gain Mode

Hypertrophy-based training

Progressive overload mention

Protein-rich diet advice

Sustainable intensity

🔥 Fat Loss Mode

Strength + cardio balance

Calorie awareness guidance

Avoid crash dieting

Recovery emphasis

The AI is instructed to:

Avoid medical diagnosis

Avoid unsafe exercises

Keep language simple and motivating

Use structured formatting

🎛️ Model Configuration
MODEL_NAME = "gemini-2.5-flash"

generation_config = {
    "temperature": temperature
}

Temperature Behavior
Temperature	Output Style
0.2 – 0.3	Safe, structured, conservative
0.5 – 0.6	Balanced
0.7 – 0.9	Creative & tactical

Default: 0.3 (Safety-first output)

📂 Project Structure
Heracles-CoachBot-AI/
│
├── app.py
├── requirements.txt
└── README.md

📦 Installation (Local Run)
1️⃣ Clone Repository
git clone https://github.com/yourusername/yourrepo.git
cd yourrepo

2️⃣ Install Dependencies
pip install -r requirements.txt

3️⃣ Add Gemini API Key

Create .streamlit/secrets.toml:

GEMINI_API_KEY = "your_api_key_here"

4️⃣ Run App
streamlit run app.py

🌐 Deployment (Streamlit Cloud)

Push project to GitHub

Go to https://streamlit.io/cloud

Connect GitHub repo

Add GEMINI_API_KEY in Secrets

Deploy

🛡️ Safety Design

No medical diagnosis

Injury-aware recommendations

No extreme dieting

Sustainable training focus

Clear disclaimer footer

📊 Example Use Case

Input:

Sport: Cricket
Position: Fast Bowler
Injury: Knee strain
Goal: Build Stamina
Intensity: Moderate


Output:

Low-impact conditioning

Resistance band drills

Pool-based cardio

Hamstring mobility work

Structured weekly schedule

🎯 Why This Project Matters

Democratizes access to coaching

Promotes safe youth athletic development

Demonstrates real-world generative AI integration

Shows structured prompt engineering and model control

Deployable, scalable web solution

⚠️ Disclaimer

Educational use only.
Consult certified coaches or medical professionals for injury treatment.
