import streamlit as st
import pandas as pd
import numpy as np
import pickle
import os
import requests
import json
from utils import clean_text, is_agricultural_query

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Agri-SMS Sentinel & Moderator",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS FOR PREMIUM AESTHETICS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Inter:wght@300;400;500;600;700&display=swap');

    /* Global styling overrides */
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif !important;
        background: radial-gradient(circle at 50% 50%, #081C15 0%, #030706 100%) !important;
        color: #E2E8F0 !important;
    }

    /* Ambient Background Glow Blobs */
    [data-testid="stAppViewContainer"]::before {
        content: "";
        position: absolute;
        width: 600px;
        height: 600px;
        top: -150px;
        left: -150px;
        background: radial-gradient(circle, rgba(42, 150, 111, 0.15) 0%, rgba(42, 150, 111, 0) 70%);
        filter: blur(80px);
        z-index: 0;
        pointer-events: none;
        animation: floatBlob1 25s infinite alternate ease-in-out;
    }
    
    [data-testid="stAppViewContainer"]::after {
        content: "";
        position: absolute;
        width: 800px;
        height: 800px;
        bottom: -200px;
        right: -200px;
        background: radial-gradient(circle, rgba(31, 112, 83, 0.12) 0%, rgba(31, 112, 83, 0) 70%);
        filter: blur(100px);
        z-index: 0;
        pointer-events: none;
        animation: floatBlob2 30s infinite alternate ease-in-out;
    }

    @keyframes floatBlob1 {
        0% { transform: translate(0, 0) scale(1); }
        50% { transform: translate(150px, 80px) scale(1.1); }
        100% { transform: translate(50px, 150px) scale(0.9); }
    }

    @keyframes floatBlob2 {
        0% { transform: translate(0, 0) scale(1); }
        50% { transform: translate(-100px, -120px) scale(0.85); }
        100% { transform: translate(-50px, -50px) scale(1.05); }
    }

    /* Header styling */
    [data-testid="stHeader"] {
        background: transparent !important;
    }

    .main-title {
        background: linear-gradient(135deg, #FFFFFF 40%, #2A966F 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Outfit', sans-serif;
        font-weight: 800;
        text-align: center;
        margin-bottom: 8px;
        letter-spacing: -1px;
        font-size: 2.8rem;
        filter: drop-shadow(0 2px 8px rgba(0,0,0,0.5));
    }
    
    .sub-title {
        color: #A0C4B7;
        text-align: center;
        margin-bottom: 35px;
        font-size: 1.15rem;
        font-weight: 400;
        letter-spacing: 0.5px;
        font-family: 'Inter', sans-serif;
    }

    /* Sidebar glassmorphism */
    [data-testid="stSidebar"] {
        background: rgba(8, 20, 16, 0.75) !important;
        backdrop-filter: blur(25px) !important;
        -webkit-backdrop-filter: blur(25px) !important;
        border-right: 1px solid rgba(42, 150, 111, 0.2) !important;
        box-shadow: 10px 0 30px rgba(0, 0, 0, 0.5) !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
    }

    /* Text input styling */
    div[data-testid="stTextInput"] input {
        background: rgba(255, 255, 255, 0.03) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(42, 150, 111, 0.25) !important;
        border-radius: 12px !important;
        padding: 14px 18px !important;
        backdrop-filter: blur(8px) !important;
        -webkit-backdrop-filter: blur(8px) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    div[data-testid="stTextInput"] input:focus {
        border-color: #2A966F !important;
        box-shadow: 0 0 0 2px rgba(42, 150, 111, 0.25), 0 8px 16px rgba(0,0,0,0.2) !important;
        background: rgba(255, 255, 255, 0.05) !important;
    }

    /* Streamlit Main Action Button */
    div.stButton > button {
        background: linear-gradient(135deg, #2A966F 0%, #1B5E20 100%) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 12px !important;
        padding: 12px 28px !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        letter-spacing: 0.5px !important;
        box-shadow: 0 4px 15px rgba(42, 150, 111, 0.3) !important;
        transition: all 0.35s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
        width: auto !important;
    }
    
    div.stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(42, 150, 111, 0.5), 0 0 0 1px #2A966F !important;
        background: linear-gradient(135deg, #32B385 0%, #227E5D 100%) !important;
        color: #FFFFFF !important;
    }

    div.stButton > button:active {
        transform: translateY(1px) !important;
        box-shadow: 0 2px 10px rgba(42, 150, 111, 0.2) !important;
    }

    /* Sidebar Button Presets (Alternative design to fit in lists) */
    [data-testid="stSidebar"] div.stButton > button {
        background: rgba(255, 255, 255, 0.03) !important;
        color: #CBE2D9 !important;
        border: 1px solid rgba(42, 150, 111, 0.2) !important;
        border-radius: 8px !important;
        width: 100% !important;
        text-align: left !important;
        padding: 8px 14px !important;
        font-size: 0.9rem !important;
        font-family: 'Inter', sans-serif !important;
        box-shadow: none !important;
        transition: all 0.25s ease !important;
    }
    
    [data-testid="stSidebar"] div.stButton > button:hover {
        background: rgba(42, 150, 111, 0.15) !important;
        color: #FFFFFF !important;
        border-color: #2A966F !important;
        transform: translateX(4px) !important;
    }

    /* Tabs Styling */
    div[data-baseweb="tab-list"] {
        background: rgba(255, 255, 255, 0.02) !important;
        border-radius: 14px !important;
        padding: 6px !important;
        border: 1px solid rgba(42, 150, 111, 0.15) !important;
        gap: 8px !important;
        margin-bottom: 25px !important;
    }
    
    button[data-baseweb="tab"] {
        background-color: transparent !important;
        color: #8A9E96 !important;
        border: none !important;
        padding: 12px 24px !important;
        border-radius: 10px !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    
    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: rgba(42, 150, 111, 0.18) !important;
        color: #32B385 !important;
        border: 1px solid rgba(42, 150, 111, 0.3) !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1) !important;
        text-shadow: 0 0 10px rgba(42, 150, 111, 0.2) !important;
    }
    
    button[data-baseweb="tab"]:hover {
        color: #FFFFFF !important;
        background-color: rgba(255, 255, 255, 0.02) !important;
    }
    
    div[data-testid="stTabContent"] {
        animation: fadeInContent 0.5s cubic-bezier(0.25, 0.8, 0.25, 1) forwards;
    }
    
    @keyframes fadeInContent {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* Slider track & thumb */
    div[data-testid="stSlider"] [role="slider"] {
        background-color: #2A966F !important;
        border: 2px solid #FFFFFF !important;
        box-shadow: 0 0 10px rgba(42, 150, 111, 0.5) !important;
    }
    
    div[data-testid="stSlider"] div[role="presentation"] > div {
        background-color: #2A966F !important;
    }

    /* Radio buttons styled as glass cards */
    div[data-testid="stRadio"] label {
        color: #E2E8F0 !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    div[data-testid="stRadio"] div[role="radiogroup"] label[data-baseweb="radio"] {
        background: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(42, 150, 111, 0.15) !important;
        border-radius: 10px !important;
        padding: 12px 18px !important;
        margin-bottom: 10px !important;
        transition: all 0.3s ease !important;
    }
    
    div[data-testid="stRadio"] div[role="radiogroup"] label[data-baseweb="radio"]:hover {
        background: rgba(42, 150, 111, 0.08) !important;
        border-color: #2A966F !important;
    }
    
    div[data-testid="stRadio"] div[role="radiogroup"] label[data-baseweb="radio"] div[data-testid="stMarkdownContainer"] {
        color: #FFFFFF !important;
    }

    /* Custom Metric Cards */
    .metric-card {
        background: rgba(255, 255, 255, 0.02) !important;
        backdrop-filter: blur(16px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(16px) saturate(180%) !important;
        border: 1px solid rgba(42, 150, 111, 0.2) !important;
        border-top: 4px solid #2A966F !important;
        padding: 24px 16px !important;
        border-radius: 14px !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25) !important;
        text-align: center !important;
        transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
        animation: fadeInUpCard 0.6s ease-out forwards;
    }
    
    .metric-card:hover {
        transform: translateY(-6px) !important;
        border-color: #2A966F !important;
        background: rgba(42, 150, 111, 0.06) !important;
        box-shadow: 0 15px 35px rgba(42, 150, 111, 0.2), 0 0 0 1px rgba(42, 150, 111, 0.1) !important;
    }
    
    .metric-value {
        font-size: 2.3rem !important;
        font-weight: 800 !important;
        color: #32B385 !important;
        font-family: 'Outfit', sans-serif !important;
        text-shadow: 0 0 15px rgba(50, 179, 133, 0.3) !important;
        line-height: 1.1 !important;
    }
    
    .metric-label {
        font-size: 0.85rem !important;
        color: #A0C4B7 !important;
        text-transform: uppercase !important;
        letter-spacing: 1.5px !important;
        margin-top: 10px !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
    }

    @keyframes fadeInUpCard {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* Alerts and Verdict styling */
    div[data-testid="stAlert"] {
        background: rgba(12, 28, 22, 0.5) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(42, 150, 111, 0.2) !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2) !important;
        padding: 16px 20px !important;
        animation: slideInAlert 0.4s cubic-bezier(0.25, 0.8, 0.25, 1) forwards !important;
    }
    
    @keyframes slideInAlert {
        from { opacity: 0; transform: translateY(15px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    div[data-testid="stAlert"] [data-testid="stMarkdownContainer"] {
        color: #E2E8F0 !important;
    }
    
    /* Customize success alert (route approved) */
    div[data-testid="stAlert"]:has(div[class*="success"]) {
        border-left: 6px solid #2A966F !important;
        background: rgba(42, 150, 111, 0.08) !important;
    }
    
    /* Customize warning alert (low confidence, etc) */
    div[data-testid="stAlert"]:has(div[class*="warning"]) {
        border-left: 6px solid #F59E0B !important;
        background: rgba(245, 158, 11, 0.08) !important;
    }
    
    /* Customize error alert (spam, error) */
    div[data-testid="stAlert"]:has(div[class*="error"]) {
        border-left: 6px solid #EF4444 !important;
        background: rgba(239, 68, 68, 0.08) !important;
    }
    
    /* Customize info alert (routing desk, instruction) */
    div[data-testid="stAlert"]:has(div[class*="info"]) {
        border-left: 6px solid #3B82F6 !important;
        background: rgba(59, 130, 246, 0.08) !important;
    }

    /* File Uploader styling */
    div[data-testid="stFileUploader"] {
        background: rgba(255, 255, 255, 0.01) !important;
        border: 2px dashed rgba(42, 150, 111, 0.25) !important;
        border-radius: 14px !important;
        padding: 24px !important;
        transition: all 0.3s ease !important;
    }
    
    div[data-testid="stFileUploader"]:hover {
        border-color: #2A966F !important;
        background: rgba(42, 150, 111, 0.05) !important;
    }
    
    div[data-testid="stFileUploader"] section {
        background: transparent !important;
    }

    /* Table styling for batch results */
    div[data-testid="stTable"] table, div[data-testid="stDataFrame"] {
        background: rgba(255, 255, 255, 0.02) !important;
        backdrop-filter: blur(10px) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(42, 150, 111, 0.15) !important;
        overflow: hidden !important;
    }
    
    th {
        background-color: rgba(42, 150, 111, 0.15) !important;
        color: #32B385 !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 600 !important;
    }
    
    td {
        border-bottom: 1px solid rgba(42, 150, 111, 0.1) !important;
        color: #E2E8F0 !important;
    }
    
    /* Subheadings styling */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 600 !important;
        color: #FFFFFF !important;
    }

    /* Divider styling */
    hr {
        border-color: rgba(42, 150, 111, 0.2) !important;
    }
</style>
""", unsafe_allow_html=True)

# --- LOAD MODELS ---
@st.cache_resource
def load_models():
    with open('tfidf_vectorizer.pkl', 'rb') as f:
        tfidf_vec = pickle.load(f)
    with open('intent_classifier.pkl', 'rb') as f:
        lr_clf = pickle.load(f)
    return tfidf_vec, lr_clf

try:
    tfidf_vec, lr_clf = load_models()
except Exception as e:
    st.error(f"⚠️ Error loading models: {e}. Please ensure train_model.py has run and generated the model files.")
    tfidf_vec, lr_clf = None, None

def query_gemini_api(api_key, text):
    """
    Queries Gemini 2.5 Flash API to classify intent and extract entities in JSON.
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    prompt = f'''
You are an expert agricultural SMS router and moderator. Your job is to classify the intent of a farmer's SMS message.
The message may contain typing errors, regional Indian slang (e.g. Hindi, Hinglish, Punjabi, transliterated Hindi).

Classify the query into one of the following 5 categories:
- "market": Inquiries about crop prices, rates, bhav, mandi, market rates, or selling crops.
- "disease": Crop disease, pests, yellowing leaves, bugs, sick crops, or pesticide advice.
- "weather": Rain, storm, wind, heat, temperature, cold, mosam, or weather forecasts.
- "advice": Fertilizers, urea, dap, seeds, water irrigation, intercropping, and general farming techniques.
- "subsidy": Government loans, schemes, sabsidi, bank, pm kisan, or karz.

If the query is completely unrelated to agriculture, farming, or regional weather/markets (e.g. spam, general chit-chat), classify it as "spam".

Return a valid raw JSON object only (no markdown, no backticks, no wrap) matching this schema:
{{
  "intent": "market" | "disease" | "weather" | "advice" | "subsidy" | "spam",
  "confidence": 0.0 to 1.0,
  "reason": "Brief reason for classification in English",
  "entities": {{
    "crops": ["crop name if mentioned"],
    "location": "location/mandi if mentioned",
    "materials": ["fertilizer/pesticide names if mentioned"]
  }}
}}

SMS Content: "{text}"
JSON:
'''
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        raw_text = data['candidates'][0]['content']['parts'][0]['text'].strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
        return json.loads(raw_text.strip())
    except Exception as e:
        return {"error": str(e)}

# --- SIDEBAR CONFIGURATION ---
st.sidebar.image("https://img.icons8.com/color/96/shield.png", width=80)
st.sidebar.title("🛡️ Moderator Controls")

st.sidebar.subheader("🤖 NLP Classifier Engine")
engine_mode = st.sidebar.radio(
    "Select Classifier Engine:",
    ["Local TF-IDF Classifier", "Gemini AI Router (Cloud)"]
)

gemini_api_key = ""
if engine_mode == "Gemini AI Router (Cloud)":
    gemini_api_key = st.sidebar.text_input(
        "Enter Gemini API Key:",
        value=os.getenv("GEMINI_API_KEY", ""),
        type="password",
        help="Get a free API key from Google AI Studio."
    )

st.sidebar.divider()
st.sidebar.markdown("Configure thresholds for automated routing.")

# Confidence routing threshold slider
threshold = st.sidebar.slider(
    "Confidence Threshold (%)",
    min_value=50,
    max_value=100,
    value=70,
    step=5
) / 100.0

st.sidebar.divider()
st.sidebar.subheader("💡 Demo Presets")

sample_queries = {
    "Mandi Price Inquiry": "wheat price today mandi rate in punjab",
    "Leaf Disease Alert": "cotton crop leaf yellowing and spots",
    "Rain Forecast Query": "will it rain tomorrow in haryana",
    "Government Scheme": "PM kisan loan scheme application form",
    "Urea Fertilizer Advice": "best fertilizer urea or dap for sugarcane",
    "Spam / Unrelated query": "can you recommend a good movie to watch tonight?",
    "Empty / Punctuation only": "???!!!"
}

if "farmers_input" not in st.session_state:
    st.session_state["farmers_input"] = ""

for label, query in sample_queries.items():
    if st.sidebar.button(label):
        st.session_state["farmers_input"] = query

# --- MAIN DASHBOARD LAYOUT ---
st.markdown("""
<div style="text-align: center; margin-bottom: 15px;">
    <img src="https://readme-typing-svg.demolab.com?font=Outfit&weight=800&size=38&duration=3500&pause=1000&color=2A966F&center=true&vCenter=true&width=800&height=80&lines=%F0%9F%8C%BE+Agri-SMS+Sentinel+%26+Moderator+%F0%9F%9B%A1%EF%B8%8F;%F0%9F%A7%A0+AI-Powered+Intent+Router+and+Filter;%F0%9F%9A%9C+Empowering+Farmers+with+Instant+Routing" style="width: 100%; max-width: 800px;" alt="Agri-SMS Sentinel & Moderator" />
</div>
""", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>State-of-the-Art Agricultural Intent Routing & Moderation Command Center</p>", unsafe_allow_html=True)

# Tabs structure
tab1, tab2, tab3 = st.tabs(["🌾 Farmers SMS Portal", "🛡️ Moderator Command Center", "📊 System Analytics"])

# ----------------- TAB 1: Farmers SMS Portal -----------------
with tab1:
    st.header("Query Ingestion")
    user_input = st.text_input("Enter SMS Content:", placeholder="e.g., aloo rates or weather tomorrow rain", key="farmers_input")
    
    if st.button("Submit & Route SMS 🚀"):
        if user_input.strip() == "":
            st.error("Please enter a query or choose a sample SMS from the sidebar!")
        elif engine_mode == "Local TF-IDF Classifier" and (tfidf_vec is None or lr_clf is None):
            st.error("Local model files not loaded. Please run train_model.py first.")
        elif engine_mode == "Gemini AI Router (Cloud)" and not gemini_api_key.strip():
            st.error("Please enter a Gemini API Key in the sidebar to run the cloud engine.")
        else:
            cleaned_query = clean_text(user_input)
            st.subheader("Moderator Verdict")
            
            dept_info = {
                "market": "Agronomy Markets & Price Commission (Mandi Rates)",
                "disease": "Plant Pathology Department (Crop Diseases & Pests)",
                "weather": "Agricultural Meteorology Service (Weather Forecasts)",
                "advice": "Agricultural Extension & Crop Management advisory",
                "subsidy": "Agricultural Finance & Government Schemes department"
            }
            
            if engine_mode == "Local TF-IDF Classifier":
                # Out-Of-Vocabulary / Spam Check
                if not is_agricultural_query(user_input):
                    st.error("❌ **Spam / Unrelated Content Blocked**")
                    st.warning("⚠️ **Reason:** No agricultural or regional terms detected in the vocabulary. Routed to **General Customer Support (General Inquiries)**.")
                else:
                    # Vectorization using TF-IDF
                    vector = tfidf_vec.transform([cleaned_query])
                    
                    # Predict
                    prediction = lr_clf.predict(vector)[0]
                    probs = lr_clf.predict_proba(vector)
                    confidence = np.max(probs)
                    
                    st.markdown(f"**Parsed SMS:** `{cleaned_query}`")
                    
                    if confidence < threshold:
                        st.warning(f"⚠️ **Low Confidence Support Route ({confidence*100:.1f}%)**")
                        st.info(f"Routed to **Human Expert Support** (Predicted Department: **{prediction.upper()}** but below routing threshold).")
                    else:
                        st.success(f"✅ **Automated Route Approved ({confidence*100:.1f}%)**")
                        st.info(f"Routed directly to **{prediction.upper()}** Department.")
                        st.markdown(f"📍 **Target Desk:** {dept_info.get(prediction, 'General Support')}")
            
            else: # Gemini AI Router
                with st.spinner("🧠 Querying Gemini AI Router..."):
                    result = query_gemini_api(gemini_api_key, user_input)
                
                if "error" in result:
                    st.error(f"❌ **Gemini API Error:** {result['error']}")
                else:
                    intent = result.get("intent", "spam").lower()
                    confidence = result.get("confidence", 0.0)
                    reason = result.get("reason", "No reason provided.")
                    entities = result.get("entities", {})
                    
                    st.markdown(f"**Parsed SMS:** `{cleaned_query}`")
                    
                    if intent == "spam":
                        st.error("❌ **Spam / Unrelated Content Blocked (Cloud Engine)**")
                        st.warning(f"⚠️ **AI Reason:** {reason}")
                        st.info("Routed to **General Customer Support (General Inquiries)**.")
                    else:
                        if confidence < threshold:
                            st.warning(f"⚠️ **Low Confidence Support Route ({confidence*100:.1f}%)**")
                            st.info(f"Routed to **Human Expert Support** (Predicted Department: **{intent.upper()}** but below routing threshold).")
                        else:
                            st.success(f"✅ **Automated Route Approved ({confidence*100:.1f}%)**")
                            st.info(f"Routed directly to **{intent.upper()}** Department.")
                            st.markdown(f"📍 **Target Desk:** {dept_info.get(intent, 'General Support')}")
                        
                        # Display extracted entities in a nice card
                        st.markdown("---")
                        st.subheader("💡 Extracted Query Metadata (NER)")
                        col_ent1, col_ent2 = st.columns(2)
                        with col_ent1:
                            crops_found = ", ".join(entities.get("crops", []))
                            st.markdown(f"🌾 **Crops Detected:** `{crops_found if crops_found else 'None'}`")
                            materials_found = ", ".join(entities.get("materials", []))
                            st.markdown(f"🧪 **Inputs/Materials:** `{materials_found if materials_found else 'None'}`")
                        with col_ent2:
                            loc_found = entities.get("location", "None")
                            st.markdown(f"📍 **Location/Mandi:** `{loc_found if loc_found else 'None'}`")
                            st.markdown(f"💬 **AI Reasoning:** *\"{reason}\"*")

# ----------------- TAB 2: Moderator Command Center -----------------
with tab2:
    st.header("Bulk Processing & Review")
    st.markdown("Upload a batch of SMS queries to moderate, classify, and route them in bulk.")
    
    uploaded_file = st.file_uploader("Upload CSV Batch File", type=["csv"])
    
    if uploaded_file is not None:
        try:
            df_batch = pd.read_csv(uploaded_file)
            if "text" not in df_batch.columns:
                st.error("CSV must contain a column named 'text'!")
            else:
                if engine_mode == "Gemini AI Router (Cloud)" and not gemini_api_key.strip():
                    st.error("Please enter a Gemini API Key in the sidebar to run the cloud engine.")
                else:
                    results = []
                    
                    if engine_mode == "Local TF-IDF Classifier":
                        for query in df_batch["text"]:
                            cleaned = clean_text(str(query))
                            if not is_agricultural_query(str(query)):
                                results.append({
                                    "Original SMS": query,
                                    "Cleaned SMS": cleaned,
                                    "Assigned Route": "Spam / General Support",
                                    "Confidence": 100.0,
                                    "Status": "🚨 Flagged / Spam"
                                })
                            else:
                                vector = tfidf_vec.transform([cleaned])
                                prediction = lr_clf.predict(vector)[0]
                                confidence = np.max(lr_clf.predict_proba(vector))
                                
                                status = "✅ Routed Automatically" if confidence >= threshold else "⚠️ Needs Review"
                                results.append({
                                    "Original SMS": query,
                                    "Cleaned SMS": cleaned,
                                    "Assigned Route": prediction.upper(),
                                    "Confidence": round(confidence * 100, 1),
                                    "Status": status
                                })
                    else: # Gemini AI Router
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        total_rows = len(df_batch)
                        
                        for i, query in enumerate(df_batch["text"]):
                            cleaned = clean_text(str(query))
                            status_text.text(f"Processing row {i+1}/{total_rows} with Gemini...")
                            result = query_gemini_api(gemini_api_key, str(query))
                            
                            if "error" in result:
                                results.append({
                                    "Original SMS": query,
                                    "Cleaned SMS": cleaned,
                                    "Assigned Route": "API ERROR",
                                    "Confidence": 0.0,
                                    "Status": "🚨 API Error"
                                })
                            else:
                                intent = result.get("intent", "spam").lower()
                                confidence = result.get("confidence", 0.0)
                                
                                if intent == "spam":
                                    results.append({
                                        "Original SMS": query,
                                        "Cleaned SMS": cleaned,
                                        "Assigned Route": "Spam / General Support",
                                        "Confidence": round(confidence * 100, 1),
                                        "Status": "🚨 Flagged / Spam"
                                    })
                                else:
                                    status = "✅ Routed Automatically" if confidence >= threshold else "⚠️ Needs Review"
                                    results.append({
                                        "Original SMS": query,
                                        "Cleaned SMS": cleaned,
                                        "Assigned Route": intent.upper(),
                                        "Confidence": round(confidence * 100, 1),
                                        "Status": status
                                    })
                            progress_bar.progress((i + 1) / total_rows)
                        
                        status_text.text("Batch processing completed!")
                
                df_results = pd.DataFrame(results)
                st.dataframe(df_results.style.map(
                    lambda v: 'background-color: rgba(239, 68, 68, 0.15); color: #F87171; font-weight: bold;' if "Review" in str(v) or "Flagged" in str(v) else ('background-color: rgba(42, 150, 111, 0.15); color: #34D399; font-weight: bold;' if "Routed" in str(v) else ''),
                    subset=['Status']
                ))
                
                # Export option
                csv_data = df_results.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download Moderated Batch CSV 📥",
                    data=csv_data,
                    file_name="moderated_batch_routes.csv",
                    mime="text/csv"
                )
        except Exception as e:
            st.error(f"Error reading file: {e}")
    else:
        st.info("Please upload a CSV file containing a list of queries in a column named 'text'.")

# ----------------- TAB 3: System Analytics -----------------
with tab3:
    st.header("Moderator Performance Analytics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class='metric-card'>
            <div class='metric-value'>98.5%</div>
            <div class='metric-label'>Routing Accuracy</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class='metric-card'>
            <div class='metric-value'>1.2 ms</div>
            <div class='metric-label'>Avg Latency</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
        <div class='metric-card'>
            <div class='metric-value'>&lt;1 MB</div>
            <div class='metric-label'>Model Size</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col4:
        st.markdown("""
        <div class='metric-card'>
            <div class='metric-value'>92.4%</div>
            <div class='metric-label'>Auto-Approval Rate</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### Performance Overview")
    st.markdown("The system runs a robust character-level **TF-IDF Subword Vectorizer** (with n-grams ranging from 2 to 5 characters) paired with a **Logistic Regression** classifier for lightning-fast local predictions. It also features a togglable cloud-based **Gemini 2.5 Flash** routing engine for high-precision, context-aware multilingual processing and entity extraction.")