from sqlalchemy import Column, Integer, String, Boolean,LargeBinary,ForeignKey
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship
from db.database import Base
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
    email = Column(String, unique=True, index=True)
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
    
    # Self-referencing relationships for father and mother
    father_id = Column(Integer, ForeignKey('bovines.id'), nullable=True)  # Father is a reference to Bovine's id
    mother_id = Column(Integer, ForeignKey('bovines.id'), nullable=True)  # Mother is a reference to Bovine's id
    
    # Relationships
    father = relationship("Bovine", remote_side=[id], backref="children_father", foreign_keys=[father_id])
    mother = relationship("Bovine", remote_side=[id], backref="children_mother", foreign_keys=[mother_id])
