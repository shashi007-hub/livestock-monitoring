from sqlalchemy import Column, Integer, String, Boolean,LargeBinary,ForeignKey,MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship
# from db.database import Base
import enum
from sqlalchemy import Boolean,  Float, DateTime

metadata = MetaData()
Base = declarative_base(metadata=metadata)

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
    avg_steps = Column(Integer, nullable=True)  # Average steps per day
    
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
    

class FeedingPatterns(Base):
    __tablename__ = 'feeding_patterns'
    
    id = Column(Integer, primary_key=True)
    bovine_id = Column(Integer, ForeignKey(Bovine.id), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    bite_chew = Column(Integer, nullable=False)  
    
    
class FeedingAnalytics(Base):
    __tablename__ = 'feeding_analytics'
    
    id = Column(Integer, primary_key=True)
    bovine_id = Column(Integer, ForeignKey(Bovine.id), nullable=False)
    date = Column(DateTime, nullable=False)
    feeding_time = Column(DateTime, nullable=False)  # Time when the bovine was fed
    feeding_frequency = Column(Integer, nullable=False)  # Frequency of feeding in hours
    average_feeding_time = Column(Float, nullable=False)  # Average time spent feeding in minutes
    meal_interval = Column(Integer, nullable=False)  # Interval between meals in hours
    feeding_rate = Column(Float, nullable=False)  # Rate of feeding in kg/hour


class SMSAlerts(Base):
    __tablename__ = 'sms_alerts'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    bovine_id = Column(Integer, ForeignKey(Bovine.id), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    message = Column(String, nullable=False)  # The content of the SMS alert

class SkinDiseases(Base):
    __tablename__ = 'skin_diseases'
    
    id = Column(Integer, primary_key=True)

    bovine_id = Column(Integer, ForeignKey(Bovine.id), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    disease   = Column(String, nullable=False)   