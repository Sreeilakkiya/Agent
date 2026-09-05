from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.ai_service import AIService
from app.schemas import AIExplainRequest, AIExplainResponse
from app.routes.auth import get_current_user

router = APIRouter()
ai_service = AIService()

@router.post("/explain", response_model=AIExplainResponse)
def explain_risk(
    request: AIExplainRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Generate AI explanation for a risk prediction."""
    result = ai_service.generate_explanation(
        customer_id=request.customer_id,
        prediction_type=request.prediction_type,
        probability=request.probability,
        risk_factors=request.risk_factors,
        amount=request.amount,
        recommended_action=""  # Would need to pass this separately
    )
    
    return AIExplainResponse(**result)
