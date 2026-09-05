from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# Auth schemas
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    company_name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Customer schemas
class CustomerBase(BaseModel):
    customer_id: str
    name: str
    email: Optional[str] = None
    tenure_days: int = 0
    plan_value: float = 0.0
    activity_score: float = 0.0
    days_since_last_login: int = 0
    monthly_usage: float = 0.0
    complaint_count: int = 0
    previous_renewals: int = 0

class CustomerCreate(CustomerBase):
    company_id: int

class CustomerResponse(CustomerBase):
    id: int
    company_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Transaction schemas
class TransactionBase(BaseModel):
    amount: float
    payment_method: str
    status: str
    failure_count: int = 0
    transaction_frequency: float = 0.0
    subscription_age: int = 0

class TransactionCreate(TransactionBase):
    customer_id: int

class TransactionResponse(TransactionBase):
    id: int
    customer_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Risk Prediction schemas
class RiskPredictionBase(BaseModel):
    prediction_type: str
    probability: float
    revenue_at_risk: float
    severity: str
    risk_factors: Optional[str] = None
    recommended_action: Optional[str] = None
    ai_explanation: Optional[str] = None

class RiskPredictionCreate(RiskPredictionBase):
    customer_id: int

class RiskPredictionResponse(RiskPredictionBase):
    id: int
    customer_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Recovery Action schemas
class RecoveryActionBase(BaseModel):
    action_type: str
    status: str = "pending"
    outcome: Optional[str] = None
    revenue_protected: float = 0.0
    notes: Optional[str] = None

class RecoveryActionCreate(RecoveryActionBase):
    prediction_id: int

class RecoveryActionResponse(RecoveryActionBase):
    id: int
    prediction_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Dashboard schemas
class DashboardKPI(BaseModel):
    total_revenue: float
    revenue_at_risk: float
    revenue_protected: float
    high_risk_cases: int
    recovery_rate: float

class LeakCategory(BaseModel):
    category: str
    cases: int
    revenue_at_risk: float
    severity: str

class DashboardResponse(BaseModel):
    kpis: DashboardKPI
    leaks: List[LeakCategory]

# AI Explain schema
class AIExplainRequest(BaseModel):
    customer_id: str
    prediction_type: str
    probability: float
    risk_factors: dict
    amount: float

class AIExplainResponse(BaseModel):
    explanation: str
    contributing_factors: List[str]
    recommended_action: str
    expected_impact: str

# Upload schema
class UploadResponse(BaseModel):
    success: bool
    records_imported: int
    errors: List[str]
