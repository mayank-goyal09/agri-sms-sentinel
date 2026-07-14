import streamlit as st
import pandas as pd
import numpy as np
import pickle
from gensim.models import FastText

# --- PAGE CONFIG ---
st.set_page_config(page_title="Agri-SMS Router", page_icon="🌾")

# --- LOAD MODELS ---
@st.cache_resource # This keeps the app fast by loading models only once
def load_models():
    ft_model = FastText.load("agri_fasttext.model")
    with open('intent_classifier.pkl', 'rb') as f:
        lr_clf = pickle.load(f)
    return ft_model, lr_clf

ft_model, lr_clf = load_models()

# --- HELPER FUNCTION ---
def get_vector(text, model):
    words = text.lower().split()
    vectors = [model.wv[w] for w in words if w in model.wv]
    return np.mean(vectors, axis=0) if vectors else np.zeros(model.vector_size)

# --- UI ---
st.title("🌾 Agri-SMS Intent Router")
st.markdown("Enter a farmer's query below to route it to the correct department.")

user_input = st.text_input("SMS Content:", placeholder="e.g., wheat price today or crop yellowing")

if st.button("Route SMS 🚀"):
    if user_input:
        # 1. Vectorize
        vector = get_vector(user_input, ft_model).reshape(1, -1)
        
        # 2. Predict
        prediction = lr_clf.predict(vector)[0]
        probs = lr_clf.predict_proba(vector)
        confidence = np.max(probs)
        
        # 3. Display Results
        st.divider()
        if confidence < 0.70:
            st.warning(f"⚠️ Low Confidence ({confidence:.2f}). Routing to Human Expert.")
        else:
            st.success(f"✅ Intent Detected: **{prediction.upper()}**")
            st.info(f"🧠 Model Confidence: {confidence*100:.1f}%")
            
        # Visualizing the "thought process"
        st.bar_chart(pd.DataFrame(probs, columns=lr_clf.classes_).T)
    else:
        st.error("Please enter some text!")