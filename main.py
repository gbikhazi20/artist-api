from fastapi import FastAPI, HTTPException, Header
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import declarative_base, sessionmaker
from pydantic import BaseModel
from typing import List
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional
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
    popularity = Column(Integer)
    demo_url = Column(String)

# Pydantic model for API
class Artist(BaseModel):
    name: str
    genre: str
    description: str
    popularity: int
    demo_url: str

    class Config:
        orm_mode = True

# Create tables
Base.metadata.create_all(bind=engine)

def init_db():
    db = SessionLocal()
    sample_artists = [
        ArtistDB(
            name="Twig Lake",
            genre="Indie Rock",
            description="Up and coming singer-songwriter project focused on introspective lyrics and catchy melodies",
            popularity=80,
            demo_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        ),
        ArtistDB(
            name="Fling",
            genre="Jazz",
            description="New age jazz punk band with a focus on improvisation and experimentation",
            popularity=65,
            demo_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        ),
        ArtistDB(
            name="The Daisies",
            genre="Pop",
            description="Pop band with a focus on catchy hooks and danceable beats",
            popularity=90,
            demo_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        ),
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


app = FastAPI()

def get_db_connection():
    DATABASE_URL = os.getenv("DATABASE_URL")
    return psycopg2.connect(DATABASE_URL)

# Keep the original endpoint for reference
@app.get("/artists")
async def get_artists():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cur.execute('SELECT * FROM artists')
        artists = cur.fetchall()
        return list(artists)
    finally:
        cur.close()
        conn.close()

# Updated endpoint that accepts genre in header
@app.get("/artists/top")
async def get_top_artist_by_genre(genre: Optional[str] = Header(None, alias="X-Genre")):
    if not genre:
        raise HTTPException(status_code=400, detail="Genre header (X-Genre) is required")
    
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cur.execute('''
            SELECT * FROM artists 
            WHERE LOWER(genre) = LOWER(%s)
            ORDER BY popularity DESC 
            LIMIT 1
        ''', (genre,))
        
        artist = cur.fetchone()
        if not artist:
            raise HTTPException(status_code=404, detail=f"No artists found for genre: {genre}")
        
        return artist
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 3000))
    uvicorn.run(app, host="0.0.0.0", port=port)