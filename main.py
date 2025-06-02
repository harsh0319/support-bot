from fastapi import FastAPI, HTTPException
from uuid import uuid4
from datetime import datetime
from models import ComplaintCreate, ComplaintCreateResponse, ComplaintResponse
from database import complaints_collection

app = FastAPI()


@app.post("/complaints", response_model=ComplaintCreateResponse)
async def create_complaint(complaint: ComplaintCreate):
    complaint_id = str(uuid4())
    complaint_doc = {
        "complaint_id": complaint_id,
        "name": complaint.name,
        "phone_number": complaint.phone_number,
        "email": complaint.email,
        "complaint_details": complaint.complaint_details,
        "created_at": datetime.utcnow()
    }

    await complaints_collection.insert_one(complaint_doc)

    return {"complaint_id": complaint_id, "message": "Complaint created successfully"}


@app.get("/complaints/{complaint_id}", response_model=ComplaintResponse)
async def get_complaint(complaint_id: str): 
    complaint = await complaints_collection.find_one({"complaint_id": complaint_id})
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    # Convert MongoDB document to Pydantic model
    return ComplaintResponse(**complaint)
