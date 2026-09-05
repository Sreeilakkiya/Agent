import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict

def generate_demo_data(num_customers: int = 1000) -> Dict[str, pd.DataFrame]:
    """Generate realistic synthetic demo data for FlowRecover."""
    np.random.seed(42)
    random.seed(42)
    
    # Generate customers with realistic correlations
    customers_data = []
    for i in range(num_customers):
        customer_id = f"C{1000 + i}"
        tenure_days = random.randint(30, 1000)
        plan_value = random.choice([499, 999, 1999, 4999, 9999])
        
        # Correlation: longer tenure → higher activity
        base_activity = min(100, tenure_days / 10)
        activity_score = max(0, min(100, base_activity + random.gauss(0, 15)))
        
        # Correlation: lower activity → more days since login
        days_since_login = max(0, int(100 - activity_score + random.gauss(0, 10)))
        
        # Correlation: lower activity → lower usage
        monthly_usage = max(0, activity_score * random.gauss(10, 2))
        
        # Correlation: lower activity → more complaints
        complaint_count = max(0, int((100 - activity_score) / 20 + random.gauss(0, 1)))
        
        previous_renewals = max(0, int(tenure_days / 90) + random.randint(-1, 1))
        
        customers_data.append({
            "customer_id": customer_id,
            "name": f"Customer {customer_id}",
            "email": f"{customer_id.lower()}@example.com",
            "tenure_days": tenure_days,
            "plan_value": plan_value,
            "activity_score": round(activity_score, 2),
            "days_since_last_login": days_since_login,
            "monthly_usage": round(monthly_usage, 2),
            "complaint_count": complaint_count,
            "previous_renewals": previous_renewals
        })
    
    customers_df = pd.DataFrame(customers_data)
    
    # Generate transactions with payment failure correlations
    transactions_data = []
    for _, customer in customers_df.iterrows():
        num_transactions = random.randint(1, 10)
        for _ in range(num_transactions):
            amount = customer["plan_value"]
            payment_method = random.choice(["credit_card", "debit_card", "upi", "net_banking", "wallet"])
            
            # Correlation: more previous failures → higher failure probability
            base_failure_prob = 0.1
            if customer["complaint_count"] > 3:
                base_failure_prob += 0.2
            if customer["activity_score"] < 30:
                base_failure_prob += 0.15
            
            is_failed = random.random() < base_failure_prob
            failure_count = random.randint(1, 5) if is_failed else 0
            status = "failed" if is_failed else "success"
            
            transaction_frequency = random.uniform(0.1, 5.0)
            subscription_age = random.randint(1, 365)
            
            transactions_data.append({
                "customer_id": customer["customer_id"],
                "amount": amount,
                "payment_method": payment_method,
                "status": status,
                "failure_count": failure_count,
                "transaction_frequency": round(transaction_frequency, 2),
                "subscription_age": subscription_age
            })
    
    transactions_df = pd.DataFrame(transactions_data)
    
    # Generate subscriptions
    subscriptions_data = []
    for _, customer in customers_df.iterrows():
        start_date = datetime.utcnow() - timedelta(days=customer["tenure_days"])
        end_date = start_date + timedelta(days=365) if customer["previous_renewals"] > 0 else None
        status = "active" if customer["activity_score"] > 40 else random.choice(["active", "expired", "cancelled"])
        
        subscriptions_data.append({
            "customer_id": customer["customer_id"],
            "start_date": start_date,
            "end_date": end_date,
            "status": status,
            "renewal_count": customer["previous_renewals"]
        })
    
    subscriptions_df = pd.DataFrame(subscriptions_data)
    
    # Generate refunds with delivery delay correlation
    refunds_data = []
    failed_transactions = transactions_df[transactions_df["status"] == "failed"]
    for idx, txn in failed_transactions.sample(frac=0.3).iterrows():
        delivery_delay = random.randint(0, 30)
        product_category = random.choice(["electronics", "clothing", "home", "books", "other"])
        
        # Correlation: longer delay → higher refund probability
        refund_prob = min(0.9, 0.3 + delivery_delay * 0.02)
        if random.random() < refund_prob:
            refunds_data.append({
                "transaction_id": txn.name,
                "reason": random.choice(["late_delivery", "damaged", "wrong_item", "not_as_described"]),
                "amount": txn["amount"],
                "status": random.choice(["pending", "approved", "rejected"]),
                "delivery_delay": delivery_delay,
                "product_category": product_category
            })
    
    refunds_df = pd.DataFrame(refunds_data) if refunds_data else pd.DataFrame(columns=[
        "transaction_id", "reason", "amount", "status", "delivery_delay", "product_category"
    ])
    
    return {
        "customers": customers_df,
        "transactions": transactions_df,
        "subscriptions": subscriptions_df,
        "refunds": refunds_df
    }
