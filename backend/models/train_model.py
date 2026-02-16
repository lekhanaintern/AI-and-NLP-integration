import pandas as pd
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
from models.preprocessor import ResumePreprocessor

class ResumeClassifierTrainer:
    """
    Trains ML model to classify resumes into job categories
    """
    
    def __init__(self):
        self.preprocessor = ResumePreprocessor()
        self.vectorizer = TfidfVectorizer(
            max_features=1500,
            min_df=2,
            max_df=0.8,
            ngram_range=(1, 2)
        )
        self.model = None
        self.label_encoder = {}
        
    def load_data(self):
        """Load the cleaned dataset"""
        print("📂 Loading dataset...")
        current_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(os.path.dirname(current_dir), 'data')
        csv_path = os.path.join(data_dir, 'resumes_clean.csv')
        
        df = pd.read_csv(csv_path)
        print(f"✅ Loaded {len(df)} resumes with {df['Category'].nunique()} categories")
        
        return df
    
    def preprocess_data(self, df):
        """Clean all resume texts"""
        print("\n🧹 Preprocessing resume texts...")
        print("This may take 2-3 minutes...")
        
        df['Cleaned_Resume'] = df['Resume'].apply(self.preprocessor.preprocess)
        df = df[df['Cleaned_Resume'].str.len() > 50]
        
        print(f"✅ Preprocessed {len(df)} resumes")
        return df
    
    def prepare_features(self, df):
        """Convert text to TF-IDF features"""
        print("\n🔢 Converting text to numerical features (TF-IDF)...")
        
        X = df['Cleaned_Resume']
        y = df['Category']
        
        # Encode labels
        unique_categories = sorted(y.unique())
        self.label_encoder = {cat: idx for idx, cat in enumerate(unique_categories)}
        self.inverse_label_encoder = {idx: cat for cat, idx in self.label_encoder.items()}
        
        y_encoded = y.map(self.label_encoder)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, 
            test_size=0.2, 
            random_state=42,
            stratify=y_encoded
        )
        
        # Fit TF-IDF
        X_train_tfidf = self.vectorizer.fit_transform(X_train)
        X_test_tfidf = self.vectorizer.transform(X_test)
        
        print(f"✅ Training set: {X_train_tfidf.shape[0]} resumes")
        print(f"✅ Test set: {X_test_tfidf.shape[0]} resumes")
        print(f"✅ Features: {X_train_tfidf.shape[1]} TF-IDF features")
        
        return X_train_tfidf, X_test_tfidf, y_train, y_test
    
    def train_model(self, X_train, y_train):
        """Train Random Forest model"""
        print("\n🤖 Training Random Forest model...")
        print("This may take 3-5 minutes...")
        
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=20,
            random_state=42,
            n_jobs=-1,
            verbose=1
        )
        
        self.model.fit(X_train, y_train)
        print("✅ Model training completed!")
        
    def evaluate_model(self, X_test, y_test):
        """Evaluate model performance"""
        print("\n📊 Evaluating model...")
        
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"\n🎯 Overall Accuracy: {accuracy * 100:.2f}%")
        
        # Show top 10 categories performance
        print("\n📋 Performance by Category (Top 10):")
        category_names = [self.inverse_label_encoder[i] for i in sorted(self.inverse_label_encoder.keys())]
        report = classification_report(y_test, y_pred, target_names=category_names, output_dict=True, zero_division=0)
        
        # Sort by support (number of samples)
        category_scores = []
        for cat in category_names:
            if cat in report:
                category_scores.append({
                    'Category': cat,
                    'Precision': report[cat]['precision'],
                    'Recall': report[cat]['recall'],
                    'F1-Score': report[cat]['f1-score'],
                    'Support': report[cat]['support']
                })
        
        category_scores.sort(key=lambda x: x['Support'], reverse=True)
        
        print(f"{'Category':<30} {'Precision':<12} {'Recall':<12} {'F1-Score':<12} {'Samples':<10}")
        print("-" * 80)
        for cat in category_scores[:10]:
            print(f"{cat['Category']:<30} {cat['Precision']:<12.2f} {cat['Recall']:<12.2f} {cat['F1-Score']:<12.2f} {int(cat['Support']):<10}")
        
        return accuracy
    
    def save_model(self):
        """Save trained model and vectorizer"""
        print("\n💾 Saving model...")
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        models_dir = os.path.join(os.path.dirname(current_dir), 'saved_models')
        
        os.makedirs(models_dir, exist_ok=True)
        
        model_path = os.path.join(models_dir, 'model.pkl')
        joblib.dump(self.model, model_path)
        
        vectorizer_path = os.path.join(models_dir, 'vectorizer.pkl')
        joblib.dump(self.vectorizer, vectorizer_path)
        
        encoder_path = os.path.join(models_dir, 'label_encoder.pkl')
        joblib.dump(self.label_encoder, encoder_path)
        
        print("✅ Model saved to:", model_path)
        print("✅ Vectorizer saved to:", vectorizer_path)
        print("✅ Label encoder saved to:", encoder_path)

def main():
    print("="*60)
    print("   RESUME CLASSIFIER TRAINING PIPELINE")
    print("="*60)
    
    trainer = ResumeClassifierTrainer()
    
    # Step 1: Load data
    df = trainer.load_data()
    
    # Step 2: Preprocess
    df = trainer.preprocess_data(df)
    
    # Step 3: Prepare features
    X_train, X_test, y_train, y_test = trainer.prepare_features(df)
    
    # Step 4: Train model
    trainer.train_model(X_train, y_train)
    
    # Step 5: Evaluate
    accuracy = trainer.evaluate_model(X_test, y_test)
    
    # Step 6: Save model
    trainer.save_model()
    
    print("\n" + "="*60)
    print(f"✅ TRAINING COMPLETED! Final Accuracy: {accuracy * 100:.2f}%")
    print("="*60)

if __name__ == "__main__":
    main()