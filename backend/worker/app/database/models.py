from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class DistressCall(Base):
    __tablename__ = 'distress_calls'
    
    id = Column(Integer, primary_key=True)
    bovine_id = Column(Integer, ForeignKey('bovines.id'), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    probability = Column(Float, nullable=False)

class LamenessInference(Base):
    __tablename__ = 'lameness_inferences'
    
    id = Column(Integer, primary_key=True)
    bovine_id = Column(Integer, ForeignKey('bovines.id'), nullable=False)
    metric = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False)

class OestrousCall(Base):
    __tablename__ = 'oestrous_calls'
    
    id = Column(Integer, primary_key=True)
    bovine_id = Column(Integer, ForeignKey('bovines.id'), nullable=False)
    probability = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False)