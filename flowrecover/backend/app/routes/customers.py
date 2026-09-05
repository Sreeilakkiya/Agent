from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Customer, Company, RiskPrediction, RecoveryAction
from app.schemas import CustomerResponse, DashboardKPI, LeakCategory, DashboardResponse
from app.routes.auth import get_current_user
from datetime import datetime

router = APIRouter()

@router.get("/", response_model=List[CustomerResponse])
def get_customers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all customers for the current user's company."""
    customers = db.query(Customer).filter(
        Customer.company_id == current_user.company_id
    ).offset(skip).limit(limit).all()
    
    return customers

@router.get("/{customer_id}")
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a specific customer by ID."""
    customer = db.query(Customer).filter(
        Customer.id == customer_id,
        Customer.company_id == current_user.company_id
    ).first()
    
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Get risk predictions for this customer
    predictions = db.query(RiskPrediction).filter(
        RiskPrediction.customer_id == customer.id
    ).all()
    
    # Get recovery actions
    actions = db.query(RecoveryAction).join(RiskPrediction).filter(
        RiskPrediction.customer_id == customer.id
    ).all()
    
    return {
        "customer": customer,
        "predictions": predictions,
        "actions": actions
    }
