import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
import joblib
import os

class RefundModel:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
        self.feature_columns = [
            "amount", "delivery_delay", "complaint_count", 
            "product_category_encoded", "previous_refunds", "tenure_days", "activity_score"
        ]
        self.is_trained = False
    
    def prepare_data(self, customers_df: pd.DataFrame, transactions_df: pd.DataFrame, refunds_df: pd.DataFrame) -> pd.DataFrame:
        """Merge customer, transaction and refund data for training."""
        # Start with transactions
        df = transactions_df.merge(customers_df, on="customer_id", how="left")
        
        # Add refund information
        refund_counts = refunds_df.groupby("transaction_id").size().reset_index(name="refund_count")
        df = df.merge(refund_counts, left_on="id", right_on="transaction_id", how="left")
        df["refund_count"] = df["refund_count"].fillna(0)
        
        # If we have refunds data with delivery_delay, merge it
        if "delivery_delay" in refunds_df.columns and len(refunds_df) > 0:
            refund_delays = refunds_df[["transaction_id", "delivery_delay"]]
            df = df.merge(refund_delays, left_on="id", right_on="transaction_id", how="left")
            df["delivery_delay"] = df["delivery_delay"].fillna(0)
        elif "delivery_delay" not in df.columns:
            df["delivery_delay"] = 0
        
        # Encode product category
        category_encoding = {"electronics": 0, "clothing": 1, "home": 2, "books": 3, "other": 4}
        if "product_category" in refunds_df.columns:
            # Get category from refunds if available
            refund_categories = refunds_df[["transaction_id", "product_category"]]
            df = df.merge(refund_categories, left_on="id", right_on="transaction_id", how="left")
            df["product_category"] = df["product_category"].fillna("other")
        else:
            df["product_category"] = "other"
        
        df["product_category_encoded"] = df["product_category"].map(category_encoding).fillna(4)
        
        # Fill missing values
        df["complaint_count"] = df["complaint_count"].fillna(0)
        df["tenure_days"] = df["tenure_days"].fillna(df["tenure_days"].median())
        df["activity_score"] = df["activity_score"].fillna(df["activity_score"].median())
        df["previous_refunds"] = df["refund_count"]
        
        # Create target: 1 = no refund, 0 = refund requested
        df["no_refund"] = (df["refund_count"] == 0).astype(int)
        
        return df
    
    def train(self, customers_df: pd.DataFrame, transactions_df: pd.DataFrame, refunds_df: pd.DataFrame):
        """Train the refund model."""
        df = self.prepare_data(customers_df, transactions_df, refunds_df)
        
        X = df[self.feature_columns]
        y = df["no_refund"]
        
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
        print(f"Refund Model trained with metrics: {metrics}")
        return metrics
    
    def predict(self, customer_data: dict, transaction_data: dict = None) -> dict:
        """Predict refund probability for a transaction/customer."""
        if not self.is_trained:
            raise ValueError("Model not trained yet")
        
        if transaction_data is None:
            transaction_data = {}
        
        category_encoding = {"electronics": 0, "clothing": 1, "home": 2, "books": 3, "other": 4}
        
        features = {
            "amount": transaction_data.get("amount", customer_data.get("plan_value", 0)),
            "delivery_delay": transaction_data.get("delivery_delay", random.randint(0, 10)),
            "complaint_count": customer_data.get("complaint_count", 0),
            "product_category_encoded": category_encoding.get(transaction_data.get("product_category", "other"), 4),
            "previous_refunds": transaction_data.get("previous_refunds", 0),
            "tenure_days": customer_data.get("tenure_days", 0),
            "activity_score": customer_data.get("activity_score", 50)
        }
        
        X = pd.DataFrame([features])[self.feature_columns]
        proba = self.model.predict_proba(X)[0][1]  # Probability of no refund
        
        refund_probability = 1 - proba
        
        # Calculate risk level
        if refund_probability > 0.7:
            severity = "high"
        elif refund_probability > 0.4:
            severity = "medium"
        else:
            severity = "low"
        
        # Calculate revenue at risk
        revenue_at_risk = features["amount"] * refund_probability
        
        # Identify risk factors
        risk_factors = []
        if transaction_data.get("delivery_delay", 0) > 7:
            risk_factors.append("Significant delivery delay")
        if customer_data.get("complaint_count", 0) > 2:
            risk_factors.append("Customer has multiple complaints")
        if transaction_data.get("previous_refunds", 0) > 1:
            risk_factors.append("History of previous refunds")
        if features["amount"] > 5000:
            risk_factors.append("High-value order")
        
        if not risk_factors:
            risk_factors.append("Normal risk profile")
        
        # Generate recommendation
        if refund_probability > 0.7:
            recommendation = "Prioritize order resolution and proactively contact customer to address concerns."
        elif refund_probability > 0.4:
            recommendation = "Monitor order status and send proactive updates to customer."
        else:
            recommendation = "Standard processing, no special action required."
        
        return {
            "probability": round(refund_probability, 4),
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

# Import random for default delivery delay
import random
