from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# PostgreSQL configuration
POSTGRES_USER = 'postgres'
POSTGRES_PASSWORD = '8700420275'
POSTGRES_DB = 'travel_db'
POSTGRES_HOST = 'localhost'
POSTGRES_PORT = '5432'

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# SQLAlchemy model
class Destination(Base):
    __tablename__ = 'destinations'
    id = Column(Integer, primary_key=True, index=True)
    destination = Column(String(100), nullable=False)
    country = Column(String(100), nullable=False)
    rating = Column(Float, nullable=False)

# Pydantic model
class DestinationSchema(BaseModel):
    destination: str
    country: str
    rating: float

class DestinationResponse(DestinationSchema):
    id: int
    model_config = {
    "from_attributes": True
}


# Create tables
Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI(title="Travel API with FastAPI")

# Home route
@app.get("/")
def read_root():
    return {"message": "Welcome to the Travel API!"}

# Get all destinations
@app.get("/destinations", response_model=List[DestinationResponse])
def get_destinations():
    db = SessionLocal()
    destinations = db.query(Destination).all()
    db.close()
    return destinations

# Get destination by ID
@app.get("/destinations/{destination_id}", response_model=DestinationResponse)
def get_destination(destination_id: int):
    db = SessionLocal()
    destination = db.query(Destination).filter(Destination.id == destination_id).first()
    db.close()
    if not destination:
        raise HTTPException(status_code=404, detail="no destination found")
    return destination

# Add a new destination
@app.post("/destinations", response_model=DestinationResponse, status_code=201)
def create_destination(dest: DestinationSchema):
    db = SessionLocal()
    new_dest = Destination(**dest.dict())
    db.add(new_dest)
    db.commit()
    db.refresh(new_dest)
    db.close()
    return new_dest

# Update a destination
@app.put("/destinations/{destination_id}", response_model=DestinationResponse)
def update_destination(destination_id: int, updated: DestinationSchema):
    db = SessionLocal()
    destination = db.query(Destination).filter(Destination.id == destination_id).first()
    if not destination:
        db.close()
        raise HTTPException(status_code=404, detail="Destination not found")
    
    destination.destination = updated.destination
    destination.country = updated.country
    destination.rating = updated.rating
    db.commit()
    db.refresh(destination)
    db.close()
    return destination

# Delete a destination
@app.delete("/destinations/{destination_id}")
def delete_destination(destination_id: int):
    db = SessionLocal()
    destination = db.query(Destination).filter(Destination.id == destination_id).first()
    if not destination:
        db.close()
        raise HTTPException(status_code=404, detail="Destination not found")
    
    db.delete(destination)
    db.commit()
    db.close()
    return {"message": "Destination deleted"}
