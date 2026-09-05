from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import RiskPrediction, Customer, Company
from app.routes.auth import get_current_user
from sqlalchemy import func

router = APIRouter()

@router.get("/")
def get_leaks(
    leak_type: str = None,
    severity: str = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all revenue leaks with optional filtering."""
    company_id = current_user.company_id
    
    query = db.query(RiskPrediction).filter(
        RiskPrediction.customer_id.in_(
            db.query(Customer.id).filter(Customer.company_id == company_id)
        )
    )
    
    if leak_type:
        query = query.filter(RiskPrediction.prediction_type == leak_type)
    
    if severity:
        query = query.filter(RiskPrediction.severity == severity)
    
    predictions = query.all()
    
    # Group by category for summary
    categories = {}
    for pred in predictions:
        cat = pred.prediction_type
        if cat not in categories:
            categories[cat] = {
                "category": cat,
                "cases": 0,
                "revenue_at_risk": 0.0,
                "severity": pred.severity,
                "predictions": []
            }
        categories[cat]["cases"] += 1
        categories[cat]["revenue_at_risk"] += pred.revenue_at_risk
        categories[cat]["predictions"].append(pred)
    
    # Update severity based on case count
    for cat in categories.values():
        if cat["cases"] > 50:
            cat["severity"] = "high"
        elif cat["cases"] > 20:
            cat["severity"] = "medium"
        else:
            cat["severity"] = "low"
    
    return {
        "summary": list(categories.values()),
        "details": predictions
    }
