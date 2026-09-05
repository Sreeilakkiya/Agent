import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
import joblib
import os

class PaymentFailureModel:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
        self.feature_columns = [
            "amount", "payment_method_encoded", "failure_count", 
            "activity_score", "subscription_age", "transaction_frequency", "tenure_days"
        ]
        self.is_trained = False
    
    def prepare_data(self, customers_df: pd.DataFrame, transactions_df: pd.DataFrame) -> pd.DataFrame:
        """Merge customer and transaction data for training."""
        # Merge customer and transaction data
        df = transactions_df.merge(customers_df, on="customer_id", how="left")
        
        # Encode payment method
        payment_encoding = {"credit_card": 0, "debit_card": 1, "upi": 2, "net_banking": 3, "wallet": 4}
        df["payment_method_encoded"] = df["payment_method"].map(payment_encoding).fillna(0)
        
        # Fill missing values
        df["activity_score"] = df["activity_score"].fillna(df["activity_score"].median())
        df["tenure_days"] = df["tenure_days"].fillna(df["tenure_days"].median())
        
        # Create target: 1 = success, 0 = failure
        df["payment_success"] = (df["status"] == "success").astype(int)
        
        return df
    
    def train(self, customers_df: pd.DataFrame, transactions_df: pd.DataFrame):
        """Train the payment failure model."""
        df = self.prepare_data(customers_df, transactions_df)
        
        X = df[self.feature_columns]
        y = df["payment_success"]
        
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
        print(f"Payment Failure Model trained with metrics: {metrics}")
        return metrics
    
    def predict(self, customer_data: dict) -> dict:
        """Predict payment failure probability for a customer."""
        if not self.is_trained:
            raise ValueError("Model not trained yet")
        
        # Prepare features
        payment_encoding = {"credit_card": 0, "debit_card": 1, "upi": 2, "net_banking": 3, "wallet": 4}
        
        features = {
            "amount": customer_data.get("amount", 0),
            "payment_method_encoded": payment_encoding.get(customer_data.get("payment_method", "credit_card"), 0),
            "failure_count": customer_data.get("failure_count", 0),
            "activity_score": customer_data.get("activity_score", 50),
            "subscription_age": customer_data.get("subscription_age", 0),
            "transaction_frequency": customer_data.get("transaction_frequency", 1.0),
            "tenure_days": customer_data.get("tenure_days", 0)
        }
        
        X = pd.DataFrame([features])[self.feature_columns]
        proba = self.model.predict_proba(X)[0][1]  # Probability of success
        
        failure_probability = 1 - proba
        
        # Calculate risk level
        if failure_probability > 0.7:
            severity = "high"
        elif failure_probability > 0.4:
            severity = "medium"
        else:
            severity = "low"
        
        # Calculate revenue at risk
        revenue_at_risk = customer_data.get("amount", 0) * failure_probability
        
        # Identify risk factors
        risk_factors = []
        if customer_data.get("failure_count", 0) > 2:
            risk_factors.append("Multiple previous payment failures")
        if customer_data.get("activity_score", 50) < 30:
            risk_factors.append("Low customer activity")
        if customer_data.get("tenure_days", 0) < 90:
            risk_factors.append("New customer")
        if customer_data.get("payment_method", "") == "net_banking":
            risk_factors.append("High-risk payment method")
        
        if not risk_factors:
            risk_factors.append("Normal risk profile")
        
        # Generate recommendation
        if failure_probability > 0.7:
            recommendation = "Offer alternate payment method or initiate payment retry with customer support contact."
        elif failure_probability > 0.4:
            recommendation = "Send payment reminder and offer assistance with payment issues."
        else:
            recommendation = "Monitor transaction, no immediate action required."
        
        return {
            "probability": round(failure_probability, 4),
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
