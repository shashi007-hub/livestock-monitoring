from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session
from db.database import SessionLocal
from db.models import User, Bovine, BreedType
from core.security import verify_password, create_access_token, get_password_hash
from utils.tasks import publish_task
from typing import Optional, List

router = APIRouter()

class LoginForm(BaseModel):
    username: str
    password: str

class SignupForm(BaseModel):
    username: str
    password: str
    email: str

class BovineBase(BaseModel):
    name: str
    age: Optional[int] = None
    weight: int
    breed: BreedType
    location: Optional[str] = None
    father_id: Optional[int] = None
    mother_id: Optional[int] = None

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
    return {"access_token": token, "token_type": "bearer"}

@router.post("/signup")
def signup(form: SignupForm, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == form.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(form.password)
    new_user = User(
        username=form.username,
        email=form.email,
        hashed_password=hashed_password
    )
    
    db.add(new_user)
    db.commit()
    
    token = create_access_token({"sub": new_user.username})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/dispatch-task")
def dispatch_task(data: dict):
    # Sends task to MQTT broker
    publish_task(data)
    return {"message": "Task dispatched"}

@router.post("/bovines/", response_model=BovineResponse)
async def create_bovine(
    name: str,
    weight: int,
    breed: BreedType,
    age: Optional[int] = None,
    location: Optional[str] = None,
    father_id: Optional[int] = None,
    mother_id: Optional[int] = None,
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    image_data = None
    if image:
        image_data = await image.read()
    
    bovine = Bovine(
        name=name,
        age=age,
        weight=weight,
        breed=breed,
        location=location,
        father_id=father_id,
        mother_id=mother_id,
        image_data=image_data
    )
    db.add(bovine)
    db.commit()
    db.refresh(bovine)
    return bovine

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
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    bovine = db.query(Bovine).filter(Bovine.id == bovine_id).first()
    if bovine is None:
        raise HTTPException(status_code=404, detail="Bovine not found")
    
    if image:
        bovine.image_data = await image.read()
    
    update_data = {
        "name": name,
        "age": age,
        "weight": weight,
        "breed": breed,
        "location": location,
        "father_id": father_id,
        "mother_id": mother_id,
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
