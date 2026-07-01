import os
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# ==========================================================
# 1. SECURITY CONTROL (Must run BEFORE importing google SDK)
# ==========================================================
# Force your key into the environment memory to fix the 401 OAuth token bug
if "GOOGLE_API_KEY" in st.secrets:
    os.environ["GEMINI_API_KEY"] = st.secrets["GOOGLE_API_KEY"]

from google import genai
from google.genai import types

# ==========================================================
# 2. PREMIUM UI & PAGE CONFIGURATION
# ==========================================================
st.set_page_config(
    page_title="HERO R&D - 2-Wheeler Engineering Copilot",
    page_icon="🏍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium Hero MotoCorp Branding Palette
st.markdown(
    """
    <style>
    .stApp {
        background-color: #0f1115;
        color: #e2e8f0;
    }
    .hero-header {
        background: linear-gradient(90deg, #d32f2f 0%, #1e2025 100%);
        padding: 25px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 25px;
        border-left: 6px solid #ffffff;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .hero-title {
        color: #ffffff;
        font-family: 'Impact', 'Arial Black', sans-serif;
        letter-spacing: 1.5px;
        margin: 0;
        font-size: 32px;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1a1d24;
        border: 1px solid #2d3139;
        border-radius: 6px 6px 0px 0px;
        padding: 10px 20px;
        color: #a0aec0;
    }
    .stTabs [aria-selected="true"] {
        background-color: #d32f2f !important;
        color: white !important;
        border-color: #d32f2f !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Branding Header Bar
st.markdown(
    """
    <div class="hero-header">
        <div>
            <h1 class="hero-title">HERO MOTOCORP R&D</h1>
            <p style="margin:5px 0 0 0; color:#ffcccc; font-size:14px; font-weight:600; letter-spacing:0.5px;">
                INTELLIGENT TWO-WHEELER DESIGN & ENGINEERING CORE
            </p>
        </div>
        <div style="text-align: right;">
            <span style="background-color:#ffffff; color:#d32f2f; padding:6px 16px; font-weight:bold; border-radius:6px; font-size:13px; box-shadow: 0 2px 5px rgba(0,0,0,0.2);">
                ENGINEERING AGENT v2.5
            </span>
        </div>
    </div>
    """, 
    unsafe_allow_html=True
)

# ==========================================================
# 3. ENGINE INITIALIZATION (Locked in Session Memory)
# ==========================================================
if "robo" not in st.session_state:
    # Initializing blank forces the SDK to securely pull the environment key 
    # we injected at the top, bypassing argument parsing bugs.
    st.session_state.robo = genai.Client()
    st.session_state.messages = []

# Technical Knowledge System Instructions
automotive_persona = (
    "You are the Principal Simulation and Design Engineer at Hero MotoCorp R&D. "
    "Your core focus is exclusively two-wheeler dynamics, powertrain engineering, "
    "chassis topology, aerodynamics, and advanced structural mechanics.\n\n"
    "Strict Boundaries:\n"
    "1. Focus purely on motorcycles, scooters, and performance EV bikes.\n"
    "2. Present engineering data utilizing Markdown Tables for structured parameters.\n"
    "3. Incorporate LaTeX equations when presenting fluid formulas, torque transitions, or stress profiles.\n"
    "4. Reject unrelated non-automotive/non-engineering queries firmly but professionally."
)

# ==========================================================
# 4. INTERACTIVE SIDEBAR & TELEMETRY MODULE
# ==========================================================
with st.sidebar:
    if os.path.exists("assets/hero_logo.png"):
        st.image("assets/hero_logo.png", use_container_width=True)
    else:
        st.markdown("<h2 style='color:#d32f2f; text-align:center;'>HERO</h2>", unsafe_allow_html=True)
        
    st.markdown("<hr style='margin:10px 0; border-color:#2d3139;'>", unsafe_allow_html=True)
    st.markdown("<h4 style='color:#d32f2f;'>📊 Live Math & Telemetry Sim</h4>", unsafe_allow_html=True)
    
    tool_select = st.selectbox(
        "Select Active Telemetry View", 
        ["Powertrain Torque Curve", "Suspension Ride Dynamics"]
    )
    
    if tool_select == "Powertrain Torque Curve":
        st.write("Brake Power Formulation:")
        st.latex(r"P = \frac{2 \pi N T}{60,000}")
        
        rpm = np.linspace(1000, 9500, 100)
        torque = 18 * np.sin(rpm / 3500) + 14 - (rpm / 1500)**1.2
        df = pd.DataFrame({"Engine RPM": rpm, "Torque (Nm)": torque})
        
        fig = px.line(df, x="Engine RPM", y="Torque (Nm)", title="Target Powertrain Map", template="plotly_dark")
        fig.update_traces(line_color='#d32f2f', line_width=3)
        st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# 5. INDUSTRIAL WORKSPACE DASHBOARD
# ==========================================================
tab1, tab2 = st.tabs(["🌐 R&D Engineering Copilot", "📊 Baseline Parameter Matrix"])

with tab1:
    st.caption("Perform stress distribution checks, geometry modifications, or thermal management planning:")
    
    # Render historical chat log items from page refresh state
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Anchor standard chat input interface
    if question := st.chat_input("Ask about trellis frame triangulation, trail configuration, or rake adjustments..."):
        with st.chat_message("user"):
            st.markdown(question)
        st.session_state.messages.append({"role": "user", "content": question})

        # BUILD THE MESSAGE HISTORY PAYLOAD MANUALLY FOR THE MODEL
        contents_payload = []
        for msg in st.session_state.messages:
            # Map roles to match Google's native API layout rules ('user' and 'model')
            api_role = "user" if msg["role"] == "user" else "model"
            contents_payload.append(
                types.Content(role=api_role, parts=[types.Part(text=msg["content"])])
            )

        # Run direct content generation safely on default pipeline setup
        with st.chat_message("assistant"):
            with st.spinner("Processing dynamic engine simulation arrays..."):
                try:
                    response = st.session_state.robo.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=contents_payload,
                        config=types.GenerateContentConfig(
                            system_instruction=automotive_persona,
                            temperature=0.15
                        )
                    )
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as error_context:
                    st.error(f"Core Interface Connection Error: {error_context}")

with tab2:
    st.subheader("📋 Structural Geometry Benchmarks")
    st.write("Baseline engineering architectural targets for variant development:")
    
    matrix_specs = {
        "Engineering Value Metric": ["Rake Angle Geometry", "Mechanical Trail", "Wheelbase Matrix", "Unsprung Mass Ratio Target", "CoG Relative Height"],
        "Commuter Architecture": ["26.0°", "90 mm", "1245 mm", "0.14", "515 mm"],
        "Premium Performance (Karizma Core)": ["24.2°", "98 mm", "1375 mm", "0.11", "480 mm"],
        "EV Architecture (Vida Platform Type)": ["25.5°", "93 mm", "1310 mm", "0.16", "435 mm"]
    }
    st.table(pd.DataFrame(matrix_specs))
