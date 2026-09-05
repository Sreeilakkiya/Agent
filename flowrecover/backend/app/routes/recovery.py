from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.database import get_db
from app.models import RecoveryAction, RiskPrediction, Customer
from app.routes.auth import get_current_user

router = APIRouter()

@router.get("/")
def get_recovery_stats(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get recovery center statistics and actions."""
    company_id = current_user.company_id
    
    # Get all actions for the company
    actions = db.query(RecoveryAction).join(RiskPrediction).filter(
        RiskPrediction.customer_id.in_(
            db.query(Customer.id).filter(Customer.company_id == company_id)
        )
    ).all()
    
    # Calculate stats
    total_actions = len(actions)
    completed_actions = sum(1 for a in actions if a.status == "completed")
    pending_actions = sum(1 for a in actions if a.status == "pending")
    total_revenue_protected = sum(a.revenue_protected or 0 for a in actions)
    
    return {
        "stats": {
            "total_actions": total_actions,
            "completed_actions": completed_actions,
            "pending_actions": pending_actions,
            "revenue_protected": round(total_revenue_protected, 2)
        },
        "actions": actions
    }
