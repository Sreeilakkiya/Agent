import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
import joblib
import os

class ChurnModel:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
        self.feature_columns = [
            "days_since_last_login", "monthly_usage", "complaint_count",
            "tenure_days", "previous_renewals", "plan_value", "activity_score"
        ]
        self.is_trained = False
    
    def prepare_data(self, customers_df: pd.DataFrame, subscriptions_df: pd.DataFrame) -> pd.DataFrame:
        """Merge customer and subscription data for training."""
        df = customers_df.merge(subscriptions_df, on="customer_id", how="left")
        
        # Create target: 1 = active, 0 = churned (expired/cancelled)
        df["is_active"] = (df["status"] == "active").astype(int)
        
        # Fill missing values
        df["days_since_last_login"] = df["days_since_last_login"].fillna(df["days_since_last_login"].median())
        df["monthly_usage"] = df["monthly_usage"].fillna(df["monthly_usage"].median())
        df["complaint_count"] = df["complaint_count"].fillna(0)
        df["previous_renewals"] = df["previous_renewals"].fillna(0)
        df["plan_value"] = df["plan_value"].fillna(df["plan_value"].median())
        df["activity_score"] = df["activity_score"].fillna(df["activity_score"].median())
        df["tenure_days"] = df["tenure_days"].fillna(df["tenure_days"].median())
        
        return df
    
    def train(self, customers_df: pd.DataFrame, subscriptions_df: pd.DataFrame):
        """Train the churn model."""
        df = self.prepare_data(customers_df, subscriptions_df)
        
        X = df[self.feature_columns]
        y = df["is_active"]
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        
        # Train model
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        y_pred_proba = self.model.predict_proba(X_test)[:, 1]
        
        metrics = {
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred),
            "recall": recall_score(y_test, y_pred),
            "f1": f1_score(y_test, y_pred),
            "roc_auc": roc_auc_score(y_test, y_pred_proba)
        }
        
        self.is_trained = True
        print(f"Churn Model trained with metrics: {metrics}")
        return metrics
    
    def predict(self, customer_data: dict) -> dict:
        """Predict churn probability for a customer."""
        if not self.is_trained:
            raise ValueError("Model not trained yet")
        
        features = {
            "days_since_last_login": customer_data.get("days_since_last_login", 0),
            "monthly_usage": customer_data.get("monthly_usage", 0),
            "complaint_count": customer_data.get("complaint_count", 0),
            "tenure_days": customer_data.get("tenure_days", 0),
            "previous_renewals": customer_data.get("previous_renewals", 0),
            "plan_value": customer_data.get("plan_value", 0),
            "activity_score": customer_data.get("activity_score", 50)
        }
        
        X = pd.DataFrame([features])[self.feature_columns]
        proba = self.model.predict_proba(X)[0][1]  # Probability of being active
        
        churn_probability = 1 - proba
        
        # Calculate risk level
        if churn_probability > 0.7:
            severity = "high"
        elif churn_probability > 0.4:
            severity = "medium"
        else:
            severity = "low"
        
        # Calculate revenue at risk (plan value * churn probability)
        revenue_at_risk = customer_data.get("plan_value", 0) * churn_probability
        
        # Identify risk factors
        risk_factors = []
        if customer_data.get("days_since_last_login", 0) > 30:
            risk_factors.append("Inactive for extended period")
        if customer_data.get("monthly_usage", 0) < 20:
            risk_factors.append("Low product usage")
        if customer_data.get("complaint_count", 0) > 3:
            risk_factors.append("Multiple complaints filed")
        if customer_data.get("activity_score", 50) < 30:
            risk_factors.append("Declining engagement")
        if customer_data.get("previous_renewals", 0) == 0 and customer_data.get("tenure_days", 0) > 180:
            risk_factors.append("No renewals despite long tenure")
        
        if not risk_factors:
            risk_factors.append("Normal engagement pattern")
        
        # Generate recommendation
        if churn_probability > 0.7:
            recommendation = "Contact customer immediately with personalized retention offer and address any concerns."
        elif churn_probability > 0.4:
            recommendation = "Send engagement email with new features and check-in on satisfaction."
        else:
            recommendation = "Continue regular engagement, monitor for changes in behavior."
        
        return {
            "probability": round(churn_probability, 4),
            "severity": severity,
            "revenue_at_risk": round(revenue_at_risk, 2),
            "risk_factors": risk_factors,
            "recommended_action": recommendation
        }
    
    def save(self, filepath: str):
        """Save the trained model."""
        joblib.dump(self.model, filepath)
        print(f"Model saved to {filepath}")
    
    def load(self, filepath: str):
        """Load a trained model."""
        if os.path.exists(filepath):
            self.model = joblib.load(filepath)
            self.is_trained = True
            print(f"Model loaded from {filepath}")
        else:
            print(f"No model found at {filepath}")
