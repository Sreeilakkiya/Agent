from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Company(Base):
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    users = relationship("User", back_populates="company")
    customers = relationship("Customer", back_populates="company")

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    company = relationship("Company", back_populates="users")

class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    customer_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    email = Column(String(255))
    tenure_days = Column(Integer, default=0)
    plan_value = Column(Float, default=0.0)
    activity_score = Column(Float, default=0.0)
    days_since_last_login = Column(Integer, default=0)
    monthly_usage = Column(Float, default=0.0)
    complaint_count = Column(Integer, default=0)
    previous_renewals = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    company = relationship("Company", back_populates="customers")
    transactions = relationship("Transaction", back_populates="customer")
    subscriptions = relationship("Subscription", back_populates="customer")
    risk_predictions = relationship("RiskPrediction", back_populates="customer")

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    amount = Column(Float, nullable=False)
    payment_method = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False)  # success, failed, pending
    failure_count = Column(Integer, default=0)
    transaction_frequency = Column(Float, default=0.0)
    subscription_age = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    customer = relationship("Customer", back_populates="transactions")
    refunds = relationship("Refund", back_populates="transaction")

class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime)
    status = Column(String(20), nullable=False)  # active, expired, cancelled
    renewal_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    customer = relationship("Customer", back_populates="subscriptions")

class Refund(Base):
    __tablename__ = "refunds"
    
    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=False)
    reason = Column(String(255))
    amount = Column(Float, nullable=False)
    status = Column(String(20), nullable=False)  # pending, approved, rejected
    delivery_delay = Column(Integer, default=0)
    product_category = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    transaction = relationship("Transaction", back_populates="refunds")

class RiskPrediction(Base):
    __tablename__ = "risk_predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    prediction_type = Column(String(50), nullable=False)  # payment_failure, churn, refund
    probability = Column(Float, nullable=False)
    revenue_at_risk = Column(Float, nullable=False)
    severity = Column(String(20), nullable=False)  # low, medium, high
    risk_factors = Column(Text)
    recommended_action = Column(Text)
    ai_explanation = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    customer = relationship("Customer", back_populates="risk_predictions")
    recovery_actions = relationship("RecoveryAction", back_populates="prediction")

class RecoveryAction(Base):
    __tablename__ = "recovery_actions"
    
    id = Column(Integer, primary_key=True, index=True)
    prediction_id = Column(Integer, ForeignKey("risk_predictions.id"), nullable=False)
    action_type = Column(String(100), nullable=False)
    status = Column(String(20), nullable=False)  # pending, in_progress, completed, ignored
    outcome = Column(String(255))
    revenue_protected = Column(Float, default=0.0)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    prediction = relationship("RiskPrediction", back_populates="recovery_actions")
