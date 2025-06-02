from pydantic import BaseModel, EmailStr, Field
from typing import Annotated
from datetime import datetime

PhoneNumber = Annotated[str, Field(pattern=r'^\+?[0-9]{10,15}$')]

class ComplaintCreate(BaseModel):
    name: str
    phone_number: PhoneNumber
    email: EmailStr
    complaint_details: str

class ComplaintResponse(BaseModel):
    complaint_id: str
    name: str
    phone_number: str
    email: str
    complaint_details: str
    created_at: datetime

class ComplaintCreateResponse(BaseModel):
    complaint_id: str
    message: str
