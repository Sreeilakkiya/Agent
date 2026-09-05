from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import RiskPrediction, RecoveryAction, Customer
from app.schemas import RecoveryActionCreate, RecoveryActionResponse
from app.routes.auth import get_current_user

router = APIRouter()

@router.get("/")
def get_prevention_queue(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get high-risk cases that require action."""
    company_id = current_user.company_id
    
    # Get high and medium severity predictions without completed actions
    predictions = db.query(RiskPrediction).filter(
        RiskPrediction.severity.in_(["high", "medium"]),
        RiskPrediction.customer_id.in_(
            db.query(Customer.id).filter(Customer.company_id == company_id)
        )
    ).all()
    
    # Filter out predictions that already have completed actions
    result = []
    for pred in predictions:
        existing_action = db.query(RecoveryAction).filter(
            RecoveryAction.prediction_id == pred.id,
            RecoveryAction.status == "completed"
        ).first()
        
        if not existing_action:
            result.append({
                "prediction": pred,
                "customer": db.query(Customer).filter(Customer.id == pred.customer_id).first()
            })
    
    return result

@router.post("/actions", response_model=RecoveryActionResponse)
def create_action(
    action_data: RecoveryActionCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new recovery action."""
    # Verify prediction belongs to user's company
    prediction = db.query(RiskPrediction).filter(
        RiskPrediction.id == action_data.prediction_id,
        RiskPrediction.customer_id.in_(
            db.query(Customer.id).filter(Customer.company_id == current_user.company_id)
        )
    ).first()
    
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
    
    action = RecoveryAction(**action_data.dict())
    db.add(action)
    db.commit()
    db.refresh(action)
    
    return action

@router.get("/actions")
def get_actions(
    status_filter: str = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all recovery actions."""
    query = db.query(RecoveryAction).join(RiskPrediction).filter(
        RiskPrediction.customer_id.in_(
            db.query(Customer.id).filter(Customer.company_id == current_user.company_id)
        )
    )
    
    if status_filter:
        query = query.filter(RecoveryAction.status == status_filter)
    
    return query.all()
