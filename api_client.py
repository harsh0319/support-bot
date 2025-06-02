import requests
import json
from settings import FASTAPI_BASE_URL

class APIClient:
    def __init__(self):
        self.base_url = FASTAPI_BASE_URL
    
    def create_complaint(self, complaint_data: dict):
        """Create a new complaint via API"""
        try:
            response = requests.post(
                f"{self.base_url}/complaints",
                json=complaint_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Failed to create complaint: {response.text}"}
        
        except requests.exceptions.RequestException as e:
            return {"error": f"Connection error: {str(e)}"}
    
    def get_complaint(self, complaint_id: str):
        """Retrieve complaint details by ID"""
        try:
            response = requests.get(f"{self.base_url}/complaints/{complaint_id}")
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return {"error": "Complaint not found"}
            else:
                return {"error": f"Failed to retrieve complaint: {response.text}"}
        
        except requests.exceptions.RequestException as e:
            return {"error": f"Connection error: {str(e)}"}

# Create global instance
api_client = APIClient()
