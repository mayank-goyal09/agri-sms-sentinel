import streamlit as st
import pandas as pd
import numpy as np
import pickle
from gensim.models import Word2Vec
from utils import clean_text, get_sentence_vector

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Agri-SMS Router",
    page_icon="🌾",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS FOR PREMIUM AESTHETICS ---
st.markdown("""
<style>
    .main-title {
        color: #2E7D32;
        font-family: 'Outfit', 'Inter', sans-serif;
        font-weight: 700;
        text-align: center;
        margin-bottom: 5px;
    }
    .sub-title {
        color: #558B2F;
        text-align: center;
        margin-bottom: 25px;
        font-size: 1.1rem;
    }
    .stButton>button {
        background-color: #2E7D32;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 24px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #1B5E20;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    .card {
        background-color: #F1F8E9;
        border-left: 6px solid #558B2F;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# --- LOAD MODELS ---
@st.cache_resource # This keeps the app fast by loading models only once
def load_models():
    w2v_model = Word2Vec.load("agri_word2vec.model")
    with open('intent_classifier.pkl', 'rb') as f:
        lr_clf = pickle.load(f)
    return w2v_model, lr_clf

try:
    w2v_model, lr_clf = load_models()
except Exception as e:
    st.error(f"⚠️ Error loading models: {e}. Please ensure the training pipeline has run and generated the model files.")
    w2v_model, lr_clf = None, None

# --- SIDEBAR CONFIGURATION ---
st.sidebar.image("https://img.icons8.com/color/96/wheat.png", width=80)
st.sidebar.title("⚙️ Route Settings")
st.sidebar.markdown("Configure the intent routing sensitivity.")

# Confidence routing threshold slider
threshold = st.sidebar.slider(
    "Confidence Threshold (%)",
    min_value=50,
    max_value=100,
    value=70,
    step=5
) / 100.0

st.sidebar.divider()
st.sidebar.subheader("💡 Sample Farmer SMS")

# Quick test buttons
sample_queries = {
    "Wheat Price Query": "wheat price today mandi rate",
    "Pest Infection Alert": "yellowing spots on potato leaves",
    "Weather Forecast": "will it rain tomorrow in punjab?",
    "Government Subsidy": "how to apply loan for tractor pm kisan",
    "Fertilizer Advice": "best urea fertilizer for sugarcane boi"
}

# Initial text value
query_value = ""
for label, query in sample_queries.items():
    if st.sidebar.button(label):
        query_value = query

# --- MAIN UI ---
st.markdown("<h1 class='main-title'>🌾 Agri-SMS Intent Router</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Routing agricultural query SMS to corresponding department experts automatically.</p>", unsafe_allow_html=True)

# Main input box
user_input = st.text_input("Enter SMS Content:", value=query_value, placeholder="e.g., ganna rates aaj or wheat crop leaf yellowing spots")

if st.button("Route SMS 🚀"):
    if user_input.strip() == "":
        st.error("Please enter a query or choose a sample SMS from the sidebar!")
    elif w2v_model is None or lr_clf is None:
        st.error("Model files not loaded. Please run the training pipeline first.")
    else:
        # Preprocessing & Vectorization (Fully Aligned)
        cleaned_query = clean_text(user_input)
        vector = get_sentence_vector(cleaned_query, w2v_model.wv).reshape(1, -1)
        
        # Predict Intent
        prediction = lr_clf.predict(vector)[0]
        probs = lr_clf.predict_proba(vector)
        confidence = np.max(probs)
        
        st.subheader("Routing Decision")
        
        # Display clean view of parsed SMS
        st.markdown(f"**Cleaned SMS:** `{cleaned_query}`")
        
        # Routing checks
        if confidence < threshold:
            st.warning(f"⚠️ **Low Confidence ({confidence*100:.1f}%)**. Routing to **Human Expert Support**.")
        else:
            intent_formatted = prediction.upper()
            st.success(f"✅ Route to Department: **{intent_formatted}** (Confidence: **{confidence*100:.1f}%**)")
            
            # Additional context on target departments
            dept_info = {
                "market": "Agronomy Markets & Price Commission (Mandi Rates)",
                "disease": "Plant Pathology Department (Crop Diseases & Pests)",
                "weather": "Agricultural Meteorology Service (Weather Forecasts)",
                "advice": "Agricultural Extension & Crop Management advisory (Fertilizer, seed choice)",
                "subsidy": "Agricultural Finance & PM-Kisan Schemes department"
            }
            st.info(f"📍 **Target Dept:** {dept_info.get(prediction, 'General Support')}")
            
        # Probability Breakdown
        st.subheader("Model Probability Breakdown")
        prob_df = pd.DataFrame(probs * 100, columns=lr_clf.classes_).T
        prob_df.columns = ["Confidence (%)"]
        st.bar_chart(prob_df)