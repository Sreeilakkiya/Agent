from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import pandas as pd
import io
from app.database import get_db
from app.models import Customer, Transaction, Company
from app.routes.auth import get_current_user
from app.schemas import UploadResponse
from app.utils.data_generator import generate_demo_data

router = APIRouter()

@router.post("/csv", response_model=UploadResponse)
async def upload_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Upload CSV file with customer/transaction data."""
    errors = []
    records_imported = 0
    
    try:
        # Read CSV
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
        
        # Validate required columns for customers
        required_customer_cols = ["customer_id", "name"]
        missing_cols = [col for col in required_customer_cols if col not in df.columns]
        
        if missing_cols:
            return UploadResponse(
                success=False,
                records_imported=0,
                errors=[f"Missing required columns: {', '.join(missing_cols)}"]
            )
        
        # Import customers
        for _, row in df.iterrows():
            try:
                customer = Customer(
                    company_id=current_user.company_id,
                    customer_id=str(row["customer_id"]),
                    name=row["name"],
                    email=row.get("email"),
                    tenure_days=int(row.get("tenure_days", 0)),
                    plan_value=float(row.get("plan_value", 0)),
                    activity_score=float(row.get("activity_score", 50)),
                    days_since_last_login=int(row.get("days_since_last_login", 0)),
                    monthly_usage=float(row.get("monthly_usage", 0)),
                    complaint_count=int(row.get("complaint_count", 0)),
                    previous_renewals=int(row.get("previous_renewals", 0))
                )
                db.add(customer)
                records_imported += 1
            except Exception as e:
                errors.append(f"Error importing row: {str(e)}")
        
        db.commit()
        
        return UploadResponse(
            success=True,
            records_imported=records_imported,
            errors=errors
        )
        
    except Exception as e:
        return UploadResponse(
            success=False,
            records_imported=0,
            errors=[f"Failed to process file: {str(e)}"]
        )

@router.post("/demo", response_model=UploadResponse)
def load_demo_data(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Load demo dataset for testing."""
    try:
        # Generate demo data
        demo_data = generate_demo_data(num_customers=1000)
        
        records_imported = 0
        errors = []
        
        # Import customers
        for _, row in demo_data["customers"].iterrows():
            customer = Customer(
                company_id=current_user.company_id,
                customer_id=row["customer_id"],
                name=row["name"],
                email=row["email"],
                tenure_days=int(row["tenure_days"]),
                plan_value=float(row["plan_value"]),
                activity_score=float(row["activity_score"]),
                days_since_last_login=int(row["days_since_last_login"]),
                monthly_usage=float(row["monthly_usage"]),
                complaint_count=int(row["complaint_count"]),
                previous_renewals=int(row["previous_renewals"])
            )
            db.add(customer)
            records_imported += 1
        
        db.commit()
        
        # Import transactions (get customer IDs first)
        customers = db.query(Customer).filter(
            Customer.company_id == current_user.company_id
        ).all()
        customer_map = {c.customer_id: c.id for c in customers}
        
        txn_count = 0
        for _, row in demo_data["transactions"].iterrows():
            if row["customer_id"] in customer_map:
                txn = Transaction(
                    customer_id=customer_map[row["customer_id"]],
                    amount=float(row["amount"]),
                    payment_method=row["payment_method"],
                    status=row["status"],
                    failure_count=int(row["failure_count"]),
                    transaction_frequency=float(row["transaction_frequency"]),
                    subscription_age=int(row["subscription_age"])
                )
                db.add(txn)
                txn_count += 1
        
        db.commit()
        
        return UploadResponse(
            success=True,
            records_imported=records_imported,
            errors=errors
        )
        
    except Exception as e:
        return UploadResponse(
            success=False,
            records_imported=0,
            errors=[f"Failed to load demo data: {str(e)}"]
        )
