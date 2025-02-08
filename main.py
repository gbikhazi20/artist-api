from fastapi import FastAPI
from sqlalchemy import create_engine, Column, String
from sqlalchemy.orm import declarative_base, sessionmaker
from pydantic import BaseModel
from typing import List
import os

# Initialize FastAPI app
app = FastAPI(title="Music Artists API")

# Get DATABASE_URL from environment variable (Railway sets this automatically)
DATABASE_URL = os.getenv("DATABASE_URL", "test")

print("--------DATABASE-URL-----------")
print(DATABASE_URL)

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# SQLAlchemy model
class ArtistDB(Base):
    __tablename__ = "artists"
    name = Column(String, primary_key=True)
    genre = Column(String)
    description = Column(String)

# Pydantic model for API
class Artist(BaseModel):
    name: str
    genre: str
    description: str

    class Config:
        orm_mode = True

# Create tables
Base.metadata.create_all(bind=engine)

# Initialize database with sample data
def init_db():
    db = SessionLocal()
    sample_artists = [
        ArtistDB(
            name="The Beatles",
            genre="Rock",
            description="Legendary British rock band from Liverpool"
        ),
        ArtistDB(
            name="Miles Davis",
            genre="Jazz",
            description="Influential jazz trumpeter and composer"
        )
    ]
    
    for artist in sample_artists:
        try:
            db.add(artist)
            db.commit()
        except:
            db.rollback()
    
    db.close()

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()

# GET endpoint to retrieve all artists
@app.get("/artists", response_model=List[Artist])
async def get_artists():
    db = SessionLocal()
    artists = db.query(ArtistDB).all()
    db.close()
    return artists

# Optional: Add an artist (for testing)
@app.post("/artists")
async def add_artist(artist: Artist):
    db = SessionLocal()
    db_artist = ArtistDB(**artist.dict())
    db.add(db_artist)
    db.commit()
    db.close()
    return {"message": "Artist added successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))