from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session
from db.database import SessionLocal
from db.models import DistressCall, FeedingAnalytics, LamenessInference, SMSAlerts, User, Bovine, BreedType
from core.security import verify_password, create_access_token, get_password_hash
from typing import Optional, List
from datetime import datetime, timedelta

router = APIRouter()

class LoginForm(BaseModel):
    username: str
    password: str
    phone_number: Optional[str] = None
    

class SignupForm(BaseModel):
    username: str
    password: str
    phone_number: Optional[str] = None
    
class BovineCreate(BaseModel):
    name: str
    weight: int
    breed: BreedType
    owner_id:int
    age: Optional[int] = None
    location: Optional[str] = None
    father_id: Optional[int] = None
    mother_id: Optional[int] = None
    image_base64: Optional[str] = None 


class BovineBase(BaseModel):
    name: str
    age: Optional[int] = None
    weight: int
    breed: BreedType
    location: Optional[str] = None
    father_id: Optional[int] = None
    mother_id: Optional[int] = None
    image_base64: Optional[str] = None  

class BovineResponse(BovineBase):
    id: int
    
    class Config:
        from_attributes = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/login")
def login(form: LoginForm, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form.username).first()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer", "user_id": user.id,"username": user.username} 

@router.post("/signup")
def signup(form: SignupForm, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == form.username or User.phone_number == form.phone_number).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username/phonenumber already registered")
    
    hashed_password = get_password_hash(form.password)
    new_user = User(
        username=form.username,
        phone_number=form.phone_number,
        hashed_password=hashed_password
    )
    
    db.add(new_user)
    db.commit()
    
    token = create_access_token({"sub": new_user.username})
    return {"access_token": token, "token_type": "bearer"}

import base64

@router.post("/bovines/", response_model=BovineResponse)
async def create_bovine(
    bovine: BovineCreate,
    db: Session = Depends(get_db)
):
    image_data = None
    if bovine.image_base64:
        try:
            image_data = base64.b64decode(bovine.image_base64)
        except Exception as e:
            raise HTTPException(status_code=400, detail="Invalid image encoding")

    new_bovine = Bovine(
        name=bovine.name,
        age=bovine.age,
        weight=bovine.weight,
        breed=bovine.breed,
        location=bovine.location,
        father_id=bovine.father_id,
        mother_id=bovine.mother_id,
        image_data=image_data,
        owner_id=bovine.owner_id
    )
    db.add(new_bovine)
    db.commit()
    db.refresh(new_bovine)
    return new_bovine

@router.get("/bovines/", response_model=List[BovineResponse])
def get_bovines(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    bovines = db.query(Bovine).offset(skip).limit(limit).all()
    return bovines

@router.get("/bovines/{bovine_id}", response_model=BovineResponse)
def get_bovine(bovine_id: int, db: Session = Depends(get_db)):
    bovine = db.query(Bovine).filter(Bovine.id == bovine_id).first()
    if bovine is None:
        raise HTTPException(status_code=404, detail="Bovine not found")
    return bovine

@router.get("/bovines/{bovine_id}/image")
def get_bovine_image(bovine_id: int, db: Session = Depends(get_db)):
    bovine = db.query(Bovine).filter(Bovine.id == bovine_id).first()
    if bovine is None:
        raise HTTPException(status_code=404, detail="Bovine not found")
    if bovine.image_data is None:
        raise HTTPException(status_code=404, detail="No image found for this bovine")
    
    return Response(content=bovine.image_data, media_type="image/jpeg")

@router.put("/bovines/{bovine_id}", response_model=BovineResponse)
async def update_bovine(
    bovine_id: int,
    name: Optional[str] = None,
    age: Optional[int] = None,
    weight: Optional[int] = None,
    breed: Optional[BreedType] = None,
    location: Optional[str] = None,
    father_id: Optional[int] = None,
    mother_id: Optional[int] = None,
    image_base64: Optional[str] = None,
    db: Session = Depends(get_db)
):
    bovine = db.query(Bovine).filter(Bovine.id == bovine_id).first()
    if bovine is None:
        raise HTTPException(status_code=404, detail="Bovine not found")
    
    if image_base64:
        try:
            image_data = base64.b64decode(image_base64)
        except Exception as e:
            raise HTTPException(status_code=400, detail="Invalid image encoding")
        
    update_data = {
        "name": name,
        "age": age,
        "weight": weight,
        "breed": breed,
        "location": location,
        "father_id": father_id,
        "mother_id": mother_id,
        "image_data": image_data
    }
    
    
    for key, value in update_data.items():
        if value is not None:
            setattr(bovine, key, value)
    
    db.commit()
    db.refresh(bovine)
    return bovine

@router.delete("/bovines/{bovine_id}")
def delete_bovine(bovine_id: int, db: Session = Depends(get_db)):
    bovine = db.query(Bovine).filter(Bovine.id == bovine_id).first()
    if bovine is None:
        raise HTTPException(status_code=404, detail="Bovine not found")
    
    db.delete(bovine)
    db.commit()
    return {"message": "Bovine deleted"}

@router.get("/bovines/user/{user_id}", response_model=List[BovineResponse])
def get_bovines_by_user(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    bovines = db.query(Bovine).filter(Bovine.owner_id == user_id).offset(skip).limit(limit).all()
    if not bovines:
        raise HTTPException(status_code=404, detail="No bovines found for this user")
    return bovines


class HomeResponse(BaseModel):
    anamalies: int
    avg_steps: int
    grazing_volume: int
    bovines: List[BovineResponse]
    status: List[dict] 
    
class HomeForm(BaseModel):
    user_id: int


@router.get("/home/{user_id}",response_model=HomeResponse)
def get_home_data(user_id: int, db: Session = Depends(get_db)):
    bovines = db.query(Bovine).filter(Bovine.owner_id == user_id).all()
    if not bovines:
        raise HTTPException(status_code=404, detail="No bovines found for this user")
    
    status_list  = []
        # When to show red - distress + red
        # Any one -- orange
        # None -- green
    
    for bovine in bovines:
        print(bovine.id)
        current_time = datetime.utcnow()
        ten_days_ago = current_time - timedelta(days=10)
        distress_calls = db.query(DistressCall).filter(
            (DistressCall.bovine_id == bovine.id) &
            (DistressCall.timestamp >= ten_days_ago) &
            (DistressCall.probability > 0.7)
        ).count()
        
        
       
        lameness_inferences = db.query(LamenessInference).filter(
            (LamenessInference.bovine_id == bovine.id) &
            (LamenessInference.timestamp >= ten_days_ago) &
            (LamenessInference.metric > 3)).count()
        
        
        
        status = "normal"
        
        if(distress_calls > 0 and lameness_inferences > 0):
            status = "danger"
        elif(distress_calls > 0 or lameness_inferences > 0):
            status = "needsAttention"
        else:
            status = "normal"
        
        status_list.append({
            "bovine_id": bovine.id,
            "status": status
        })
    
    print("distress_calls",distress_calls)
    print("lameness_inferences",lameness_inferences)
    
    # Calculate grazing volume dynamically using FeedingAnalytics
    grazing_volume = 0
    try:
        # Get all bovine IDs for this user
        bovine_ids = [bovine.id for bovine in bovines]
        
        # Query FeedingAnalytics for all bovines belonging to this user
        # Calculate sum of (feeding_rate * average_feeding_time) for all records
        feeding_analytics = db.query(FeedingAnalytics).filter(
            FeedingAnalytics.bovine_id.in_(bovine_ids)
        ).all()
        
        # Calculate total grazing volume
        for feeding in feeding_analytics:
            grazing_volume += feeding.feeding_rate * feeding.average_feeding_time
        
        # Convert to integer for response
        grazing_volume = int(grazing_volume)
        
    except Exception as e:
        print("Error calculating grazing volume:", e)
        grazing_volume = 0  # Default to 0 if calculation fails
    
    # Calculate anomalies as count of bovines with "danger" status
    anamalies = 0
    avg_steps = 0
    try:
        # Count bovines with "danger" status
        anamalies = sum(1 for status in status_list if status["status"] == "danger")
        avg_steps = (sum(bovine.avg_steps for bovine in bovines) / len(bovines)) if len(bovines)>0 else 0
    except Exception as e:
        print("Error fetching data:", e)
        raise HTTPException(status_code=500, detail="Error fetching data")
    
    
    return HomeResponse(
        anamalies=anamalies,
        avg_steps=int(avg_steps),
        grazing_volume=int(grazing_volume),
        bovines=bovines,
        status=status_list
    )
    
    
@router.get("/sms-alerts/{user_id}")
def get_sms_alerts(user_id: int, db: Session = Depends(get_db)):
    alerts = db.query(SMSAlerts).filter(SMSAlerts.user_id == user_id).all()
    if not alerts:
        raise HTTPException(status_code=404, detail="No SMS alerts found for this user")
    return alerts

@router.get("/bovines/problems/{bovine_id}", response_model=List[dict])
def get_bovine_problems(bovine_id: int, db: Session = Depends(get_db)):
        current_time = datetime.utcnow()
        ten_days_ago = current_time - timedelta(days=10)
        
        distress_calls = db.query(DistressCall).filter(
            (DistressCall.bovine_id == bovine_id) &
            (DistressCall.timestamp >= ten_days_ago) &
            (DistressCall.probability > 0.7)
        ).all()
        
        lameness_inferences = db.query(LamenessInference).filter(
            (LamenessInference.bovine_id == bovine_id) &
            (LamenessInference.timestamp >= ten_days_ago) &
            (LamenessInference.metric > 3)).all()
        
        problems = []
        
        if distress_calls:
            problems.append({
                "type": "Distress",
                "timestamp": distress_calls[0].timestamp,
                "probability": distress_calls[0].probability
            })
        
        if lameness_inferences:
            problems.append({
                "type": "Lameness",
                "timestamp": lameness_inferences[0].timestamp,
                "metric": lameness_inferences[0].metric
            })
        
        return problems

@router.get("/bovines/feeding-times/{bovine_id}")
def get_bovine_feeding_times(bovine_id: int, db: Session = Depends(get_db)):
    feeding_times = db.query(FeedingAnalytics).filter(FeedingAnalytics.bovine_id == bovine_id).where(
        FeedingAnalytics.timestamp >= datetime.utcnow() - timedelta(days=5)
    ).all()
    if not feeding_times:
        raise HTTPException(status_code=404, detail="No feeding times found for this bovine")
    
    return [{"date": feeding.date, "feeding_time": feeding.feeding_time} for feeding in feeding_times]


@router.get("/health")
def health_check():
    return {"status": "ok"}

@router.get("/bovines/{bovine_id}/details")
def get_bovine_details(bovine_id: int, db: Session = Depends(get_db)):
    bovine = db.query(Bovine).filter(Bovine.id == bovine_id).first()
    if not bovine:
        raise HTTPException(status_code=404, detail="Bovine not found")
    
    # Example health entries (these could be fetched from a database or external service)
    current_time = datetime.utcnow()
    ten_days_ago = current_time - timedelta(days=10)
        
    health_entries = []
    distress_calls = db.query(DistressCall).filter(
        (DistressCall.bovine_id == bovine_id) &
        (DistressCall.timestamp >= ten_days_ago) &
        (DistressCall.probability > 0.7)
    ).count()
    
    # Query lameness inferences for the bovine
    lameness_inferences = db.query(LamenessInference).filter(
        (LamenessInference.bovine_id == bovine_id) &
        (LamenessInference.timestamp >= ten_days_ago) &
        (LamenessInference.metric > 3)
    ).count()


    if distress_calls:
        health_entries.append({
            "problem": "High distress detected",
            "solution": "Check for environmental stressors or health issues",
            "status": "Pending",
        })
        health_entries.append({
            "problem": "Abnormal vocalizations indicating distress",
            "solution": "Ensure adequate food and water are available",
            "status": "Pending",
        })
        health_entries.append({
            "problem": "Increased heart rate",
            "solution": "Monitor for signs of illness",
            "status": "In Progress",
        })
    
    if lameness_inferences:
        health_entries.append({
            "problem": "Lameness detected",
            "solution": "Inspect hooves and provide necessary treatment",
            "status": "In Progress",
        })
        health_entries.append({
            "problem": "Reduced mobility due to lameness",
            "solution": "Provide rest and monitor for signs of improvement",
            "status": "In Progress",
        })
        
    if not health_entries:
        health_entries.append({
            "problem": "No issues detected",
            "solution": "Continue regular monitoring",
            "status": "Normal",
        }) 
    feeding_data = db.query(FeedingAnalytics).filter(FeedingAnalytics.bovine_id == bovine_id).order_by(FeedingAnalytics.date.asc()).all()
    feeding_analysis = [
        {"date": feeding.date.strftime("%Y-%m-%d"), "avg": feeding.average_feeding_time}
        for feeding in feeding_data
    ]       
    # Example image URL (this could be dynamically generated or fetched from a storage service)
    image_url = "url"
    
    # Example status (this could be calculated based on health metrics or other data)
  
    
    # Query distress calls for the bovine
    distress_calls = db.query(DistressCall).filter(
        (DistressCall.bovine_id == bovine_id) &
        (DistressCall.timestamp >= ten_days_ago) &
        (DistressCall.probability > 0.7)
    ).count()
    
    # Query lameness inferences for the bovine
    lameness_inferences = db.query(LamenessInference).filter(
        (LamenessInference.bovine_id == bovine_id) &
        (LamenessInference.timestamp >= ten_days_ago) &
        (LamenessInference.metric > 3)
    ).count()
    
    # Determine the status
    status = "allGood"
    if distress_calls > 0 and lameness_inferences > 0:
        status = "needsImmediateAttention"
    elif distress_calls > 0 or lameness_inferences > 0:
        status = "needsAttention"
    if len(feeding_analysis) <= 0:
        feeding_analysis = None
    return {
        "id": bovine.id,
        "name": bovine.name,
        "imageUrl": image_url,
        "status": status,
        "healthEntries": health_entries,
        "feeding_analysis": feeding_analysis,  # Add feeding analysis here
        "weight": bovine.weight,
        "age": bovine.age,
    }

@router.get("/users/{user_id}/smsalerts")
def get_user_sms_alerts(user_id: int, db: Session = Depends(get_db)):
    alerts = db.query(SMSAlerts).filter(SMSAlerts.user_id == user_id).all()
    if not alerts:
        raise HTTPException(status_code=404, detail="No SMS alerts found for this user")
    
    messages = [
        {
            "id": alert.id,
            "content": alert.message,
            "timestamp": alert.timestamp.isoformat(),
        }
        for alert in alerts
    ]
    
    return {"messages": messages}    