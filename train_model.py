import pandas as pd
import numpy as np
import pickle
import os
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score
from utils import clean_text

def main():
    print("[INFO] Starting model training pipeline...")
    
    # 1. Load dataset
    dataset_path = "farmers_dataset.csv"
    if not os.path.exists(dataset_path):
        print(f"[WARN] {dataset_path} not found. Running generate_dataset.py...")
        import generate_dataset
        # This will create farmers_dataset.csv
    
    df = pd.read_csv(dataset_path)
    print(f"[INFO] Loaded dataset with {len(df)} records.")
    
    # 2. Preprocess text
    print("[INFO] Cleaning SMS query texts...")
    df['cleaned_text'] = df['text'].apply(clean_text)
    
    X = df['cleaned_text']
    y = df['intent']
    
    # 3. Split into Train & Test sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    
    # 4. Feature Extraction: Character-level TF-IDF (Sub-word tokenization)
    # analyzer='char_wb' handles typos/slang naturally within word boundaries
    print("[INFO] Fitting TF-IDF Vectorizer (Character n-grams 2-5)...")
    vectorizer = TfidfVectorizer(
        analyzer='char_wb',
        ngram_range=(2, 5),
        min_df=2,
        max_df=0.95,
        sublinear_tf=True
    )
    
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)
    
    print(f"[INFO] Vocabulary size (n-grams count): {X_train_vec.shape[1]}")
    
    # 5. Model Training: Logistic Regression
    print("[INFO] Training Logistic Regression Classifier...")
    clf = LogisticRegression(
        C=2.0,
        class_weight='balanced',
        max_iter=1000,
        random_state=42
    )
    clf.fit(X_train_vec, y_train)
    
    # 6. Evaluation
    y_pred = clf.predict(X_test_vec)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"[INFO] Training completed. Test Accuracy: {accuracy * 100:.2f}%")
    print("\n[INFO] Classification Report:")
    print(classification_report(y_test, y_pred))
    
    # 7. Serialize and Save models
    print("[INFO] Saving models to disk...")
    with open("tfidf_vectorizer.pkl", "wb") as f:
        pickle.dump(vectorizer, f)
    with open("intent_classifier.pkl", "wb") as f:
        pickle.dump(clf, f)
        
    print("[SUCCESS] Saved tfidf_vectorizer.pkl and intent_classifier.pkl.")

if __name__ == "__main__":
    main()
