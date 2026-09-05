import requests
from typing import Optional, Dict, List
from app.config import LLM_API_KEY, LLM_API_URL

class AIService:
    """Service for generating AI explanations using LLM."""
    
    def __init__(self):
        self.api_key = LLM_API_KEY
        self.api_url = LLM_API_URL
    
    def generate_explanation(
        self,
        customer_id: str,
        prediction_type: str,
        probability: float,
        risk_factors: List[str],
        amount: float,
        recommended_action: str
    ) -> Dict:
        """Generate AI explanation for a risk prediction."""
        
        # If no API key configured, return mock explanation
        if not self.api_key or not self.api_url:
            return self._generate_mock_explanation(
                customer_id, prediction_type, probability, risk_factors, amount, recommended_action
            )
        
        try:
            prompt = self._build_prompt(
                customer_id, prediction_type, probability, risk_factors, amount, recommended_action
            )
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": "You are a revenue protection analyst. Provide clear, actionable insights."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 300,
                "temperature": 0.7
            }
            
            response = requests.post(self.api_url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            explanation_text = result["choices"][0]["message"]["content"]
            
            return self._parse_explanation(explanation_text, risk_factors, recommended_action)
            
        except Exception as e:
            print(f"AI API error: {e}")
            return self._generate_mock_explanation(
                customer_id, prediction_type, probability, risk_factors, amount, recommended_action
            )
    
    def _build_prompt(
        self,
        customer_id: str,
        prediction_type: str,
        probability: float,
        risk_factors: List[str],
        amount: float,
        recommended_action: str
    ) -> str:
        """Build the prompt for the LLM."""
        type_names = {
            "payment_failure": "payment failure",
            "churn": "customer churn",
            "refund": "refund request"
        }
        
        risk_type = type_names.get(prediction_type, prediction_type)
        factors_str = ", ".join(risk_factors)
        
        prompt = f"""
Analyze this revenue risk case:

Customer ID: {customer_id}
Risk Type: {risk_type}
Risk Probability: {probability * 100:.1f}%
Revenue At Risk: ₹{amount:,.2f}
Key Risk Factors: {factors_str}
Recommended Action: {recommended_action}

Please provide:
1. A brief explanation of why this risk is occurring
2. The most important contributing factors
3. Confirmation of the recommended action
4. Expected business impact if action is taken

Keep the response concise and professional (under 150 words).
"""
        return prompt
    
    def _parse_explanation(
        self, 
        explanation_text: str, 
        risk_factors: List[str], 
        recommended_action: str
    ) -> Dict:
        """Parse the LLM response into structured format."""
        # Simple parsing - in production, use more robust parsing
        return {
            "explanation": explanation_text.strip(),
            "contributing_factors": risk_factors[:3],  # Top 3 factors
            "recommended_action": recommended_action,
            "expected_impact": f"Potential to protect ₹{abs(float(explanation_text.split('₹')[1].split()[0])) if '₹' in explanation_text else 0:,.2f} in revenue"
        }
    
    def _generate_mock_explanation(
        self,
        customer_id: str,
        prediction_type: str,
        probability: float,
        risk_factors: List[str],
        amount: float,
        recommended_action: str
    ) -> Dict:
        """Generate a mock explanation when LLM API is unavailable."""
        type_names = {
            "payment_failure": "payment failure",
            "churn": "customer churn", 
            "refund": "refund request"
        }
        
        risk_type = type_names.get(prediction_type, prediction_type)
        
        explanation = (
            f"Customer {customer_id} shows elevated {risk_type} risk ({probability*100:.0f}% probability) "
            f"primarily due to: {', '.join(risk_factors[:2])}. "
            f"The recommended action is: {recommended_action} "
            f"Taking this action could protect approximately ₹{amount:,.2f} in revenue."
        )
        
        return {
            "explanation": explanation,
            "contributing_factors": risk_factors[:3],
            "recommended_action": recommended_action,
            "expected_impact": f"Potential to protect ₹{amount:,.2f} in revenue"
        }
