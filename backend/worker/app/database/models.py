from sqlalchemy import Boolean, Column, Integer, Float, DateTime, ForeignKey, LargeBinary, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Enum as SQLEnum


Base = declarative_base()

import enum

class BreedType(enum.Enum):
    GIR = "Gir"
    SAHIWAL = "Sahiwal"
    THARPARKAR = "Tharparkar"
    RATHI = "Rathi"
    KANKREJ = "Kankrej"
    RED_SINDHI = "Red Sindhi"
    ONGOLE = "Ongole"
    KANGAYAM = "Kangayam"
    HALLIKAR = "Hallikar"
    OTHER = "Other"


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String)


class Bovine(Base):
    __tablename__ = "bovines"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    age = Column(Integer, nullable=True)
    weight = Column(Integer, nullable=False)
    breed = Column(SQLEnum(BreedType), nullable=False)
    location = Column(String, nullable=True)
    image_data = Column(LargeBinary, nullable=True)  # Store the actual image bytes
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=True)  # Foreign key to the User table
    
    # Self-referencing relationships for father and mother
    father_id = Column(Integer, ForeignKey('bovines.id'), nullable=True)  # Father is a reference to Bovine's id
    mother_id = Column(Integer, ForeignKey('bovines.id'), nullable=True)  # Mother is a reference to Bovine's id
    
    # Relationships
    father = relationship("Bovine", remote_side=[id], backref="children_father", foreign_keys=[father_id])
    mother = relationship("Bovine", remote_side=[id], backref="children_mother", foreign_keys=[mother_id])

class DistressCall(Base):
    __tablename__ = 'distress_calls'
    
    id = Column(Integer, primary_key=True)
    bovine_id = Column(Integer, ForeignKey(Bovine.id), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    probability = Column(Float, nullable=False)

class LamenessInference(Base):
    __tablename__ = 'lameness_inferences'
    
    id = Column(Integer, primary_key=True)
    bovine_id = Column(Integer, ForeignKey(Bovine.id), nullable=False)
    metric = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False)

class OestrousCall(Base):
    __tablename__ = 'oestrous_calls'
    
    id = Column(Integer, primary_key=True)
    bovine_id = Column(Integer, ForeignKey(Bovine.id), nullable=False)
    probability = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False)