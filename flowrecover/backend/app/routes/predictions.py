from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict
from app.database import get_db
from app.models import Customer, RiskPrediction, Transaction
from app.routes.auth import get_current_user
from app.ml.payment_model import PaymentFailureModel
from app.ml.churn_model import ChurnModel
from app.ml.refund_model import RefundModel
import pandas as pd
import os

router = APIRouter()

# Initialize models
payment_model = PaymentFailureModel()
churn_model = ChurnModel()
refund_model = RefundModel()

# Model paths
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "ml", "models")
os.makedirs(MODEL_DIR, exist_ok=True)

PAYMENT_MODEL_PATH = os.path.join(MODEL_DIR, "payment_model.joblib")
CHURN_MODEL_PATH = os.path.join(MODEL_DIR, "churn_model.joblib")
REFUND_MODEL_PATH = os.path.join(MODEL_DIR, "refund_model.joblib")

def load_or_train_models(db: Session):
    """Load trained models or train new ones if data exists."""
    # Try to load existing models
    payment_model.load(PAYMENT_MODEL_PATH)
    churn_model.load(CHURN_MODEL_PATH)
    refund_model.load(REFUND_MODEL_PATH)
    
    # If any model is not trained, try to train with existing data
    if not all([payment_model.is_trained, churn_model.is_trained, refund_model.is_trained]):
        # Get data from database
        customers = db.query(Customer).all()
        if len(customers) > 10:
            # Convert to DataFrames
            customers_data = []
            for c in customers:
                customers_data.append({
                    "customer_id": c.customer_id,
                    "name": c.name,
                    "email": c.email,
                    "tenure_days": c.tenure_days,
                    "plan_value": c.plan_value,
                    "activity_score": c.activity_score,
                    "days_since_last_login": c.days_since_last_login,
                    "monthly_usage": c.monthly_usage,
                    "complaint_count": c.complaint_count,
                    "previous_renewals": c.previous_renewals
                })
            
            customers_df = pd.DataFrame(customers_data)
            
            # Get transactions
            transactions = db.query(Transaction).all()
            if len(transactions) > 10:
                transactions_data = []
                for t in transactions:
                    transactions_data.append({
                        "id": t.id,
                        "customer_id": t.customer_id,
                        "amount": t.amount,
                        "payment_method": t.payment_method,
                        "status": t.status,
                        "failure_count": t.failure_count,
                        "transaction_frequency": t.transaction_frequency,
                        "subscription_age": t.subscription_age
                    })
                
                transactions_df = pd.DataFrame(transactions_data)
                
                # Train payment model
                if not payment_model.is_trained:
                    try:
                        payment_model.train(customers_df, transactions_df)
                        payment_model.save(PAYMENT_MODEL_PATH)
                    except Exception as e:
                        print(f"Error training payment model: {e}")
                
                # Train churn model (need subscriptions - simplified for now)
                if not churn_model.is_trained:
                    try:
                        # Create simple subscriptions df from customers
                        subscriptions_df = pd.DataFrame({
                            "customer_id": customers_df["customer_id"],
                            "status": ["active" if c.activity_score > 40 else "expired" for c in customers],
                            "renewal_count": [c.previous_renewals for c in customers]
                        })
                        churn_model.train(customers_df, subscriptions_df)
                        churn_model.save(CHURN_MODEL_PATH)
                    except Exception as e:
                        print(f"Error training churn model: {e}")

@router.post("/payment")
def predict_payment_risk(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Predict payment failure risk for a customer."""
    load_or_train_models(db)
    
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Get latest transaction
    latest_txn = db.query(Transaction).filter(
        Transaction.customer_id == customer_id
    ).order_by(Transaction.created_at.desc()).first()
    
    if not latest_txn:
        raise HTTPException(status_code=404, detail="No transactions found for customer")
    
    # Prepare customer data for prediction
    customer_data = {
        "amount": latest_txn.amount,
        "payment_method": latest_txn.payment_method,
        "failure_count": latest_txn.failure_count,
        "activity_score": customer.activity_score,
        "subscription_age": latest_txn.subscription_age,
        "transaction_frequency": latest_txn.transaction_frequency,
        "tenure_days": customer.tenure_days
    }
    
    prediction = payment_model.predict(customer_data)
    
    return {
        "customer_id": customer.customer_id,
        "prediction_type": "payment_failure",
        **prediction
    }

@router.post("/churn")
def predict_churn_risk(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Predict churn risk for a customer."""
    load_or_train_models(db)
    
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    customer_data = {
        "days_since_last_login": customer.days_since_last_login,
        "monthly_usage": customer.monthly_usage,
        "complaint_count": customer.complaint_count,
        "tenure_days": customer.tenure_days,
        "previous_renewals": customer.previous_renewals,
        "plan_value": customer.plan_value,
        "activity_score": customer.activity_score
    }
    
    prediction = churn_model.predict(customer_data)
    
    return {
        "customer_id": customer.customer_id,
        "prediction_type": "churn",
        **prediction
    }

@router.post("/refund")
def predict_refund_risk(
    customer_id: int,
    transaction_id: int = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Predict refund risk for a customer/transaction."""
    load_or_train_models(db)
    
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    transaction_data = {}
    if transaction_id:
        txn = db.query(Transaction).filter(Transaction.id == transaction_id).first()
        if txn:
            transaction_data = {
                "amount": txn.amount,
                "delivery_delay": 0,  # Would need to get from refunds table
                "previous_refunds": 0
            }
    
    prediction = refund_model.predict(
        {
            "complaint_count": customer.complaint_count,
            "tenure_days": customer.tenure_days,
            "activity_score": customer.activity_score,
            "plan_value": customer.plan_value
        },
        transaction_data
    )
    
    return {
        "customer_id": customer.customer_id,
        "prediction_type": "refund",
        **prediction
    }

@router.get("/")
def get_all_predictions(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all predictions for the company."""
    predictions = db.query(RiskPrediction).filter(
        RiskPrediction.customer_id.in_(
            db.query(Customer.id).filter(Customer.company_id == current_user.company_id)
        )
    ).all()
    
    return predictions
