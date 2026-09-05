from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import Customer, Transaction, RiskPrediction, RecoveryAction, Company
from app.schemas import DashboardKPI, LeakCategory, DashboardResponse
from app.routes.auth import get_current_user

router = APIRouter()

@router.get("/", response_model=DashboardResponse)
def get_dashboard(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get dashboard KPIs and leak categories."""
    company_id = current_user.company_id
    
    # Calculate total revenue from successful transactions
    total_revenue = db.query(func.sum(Transaction.amount)).filter(
        Transaction.status == "success",
        Transaction.customer_id.in_(
            db.query(Customer.id).filter(Customer.company_id == company_id)
        )
    ).scalar() or 0.0
    
    # Calculate revenue at risk from predictions
    revenue_at_risk = db.query(func.sum(RiskPrediction.revenue_at_risk)).filter(
        RiskPrediction.customer_id.in_(
            db.query(Customer.id).filter(Customer.company_id == company_id)
        )
    ).scalar() or 0.0
    
    # Calculate revenue protected from completed actions
    revenue_protected = db.query(func.sum(RecoveryAction.revenue_protected)).filter(
        RecoveryAction.status == "completed",
        RecoveryAction.prediction_id.in_(
            db.query(RiskPrediction.id).filter(
                RiskPrediction.customer_id.in_(
                    db.query(Customer.id).filter(Customer.company_id == company_id)
                )
            )
        )
    ).scalar() or 0.0
    
    # Count high risk cases
    high_risk_cases = db.query(func.count(RiskPrediction.id)).filter(
        RiskPrediction.severity == "high",
        RiskPrediction.customer_id.in_(
            db.query(Customer.id).filter(Customer.company_id == company_id)
        )
    ).scalar() or 0
    
    # Calculate recovery rate
    if revenue_at_risk > 0:
        recovery_rate = (revenue_protected / revenue_at_risk) * 100
    else:
        recovery_rate = 0.0
    
    # Get leak categories
    leaks = []
    
    # Payment failure leaks
    payment_risk = db.query(
        func.count(RiskPrediction.id),
        func.sum(RiskPrediction.revenue_at_risk)
    ).filter(
        RiskPrediction.prediction_type == "payment_failure",
        RiskPrediction.customer_id.in_(
            db.query(Customer.id).filter(Customer.company_id == company_id)
        )
    ).first()
    
    if payment_risk[0] > 0:
        leaks.append(LeakCategory(
            category="Payment Failure",
            cases=payment_risk[0],
            revenue_at_risk=payment_risk[1] or 0.0,
            severity="high" if payment_risk[0] > 50 else "medium"
        ))
    
    # Churn leaks
    churn_risk = db.query(
        func.count(RiskPrediction.id),
        func.sum(RiskPrediction.revenue_at_risk)
    ).filter(
        RiskPrediction.prediction_type == "churn",
        RiskPrediction.customer_id.in_(
            db.query(Customer.id).filter(Customer.company_id == company_id)
        )
    ).first()
    
    if churn_risk[0] > 0:
        leaks.append(LeakCategory(
            category="Customer Churn",
            cases=churn_risk[0],
            revenue_at_risk=churn_risk[1] or 0.0,
            severity="high" if churn_risk[0] > 30 else "medium"
        ))
    
    # Refund leaks
    refund_risk = db.query(
        func.count(RiskPrediction.id),
        func.sum(RiskPrediction.revenue_at_risk)
    ).filter(
        RiskPrediction.prediction_type == "refund",
        RiskPrediction.customer_id.in_(
            db.query(Customer.id).filter(Customer.company_id == company_id)
        )
    ).first()
    
    if refund_risk[0] > 0:
        leaks.append(LeakCategory(
            category="Refund Risk",
            cases=refund_risk[0],
            revenue_at_risk=refund_risk[1] or 0.0,
            severity="medium"
        ))
    
    return DashboardResponse(
        kpis=DashboardKPI(
            total_revenue=round(total_revenue, 2),
            revenue_at_risk=round(revenue_at_risk, 2),
            revenue_protected=round(revenue_protected, 2),
            high_risk_cases=high_risk_cases,
            recovery_rate=round(recovery_rate, 2)
        ),
        leaks=leaks
    )
