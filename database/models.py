from sqlalchemy import Column, Integer, String, ARRAY, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Venue(Base):
    __tablename__ = 'venue'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    seat_map = Column(ARRAY(Integer), nullable=False)

    def __repr__(self):
        return f"<Venue(name='{self.name}', location='{self.location}')>"

class Artist(Base):
    __tablename__ = 'artist'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    def __repr__(self):
        return f"<Artist(name='{self.name}')>"

class Event(Base):
    __tablename__ = 'event'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    desc = Column(String, nullable=True)
    datetime = Column(DateTime, nullable=False)
    artist_id = Column(Integer, ForeignKey('artist.id'), nullable=False)
    venue_id = Column(Integer, ForeignKey('venue.id'), nullable=False)

    artist = relationship("Artist")
    venue = relationship("Venue")

    def __repr__(self):
        return f"<Event(name='{self.name}', datetime='{self.datetime}')>"

class Ticket(Base):
    __tablename__ = 'ticket'

    id = Column(Integer, primary_key=True)
    seat_number = Column(Integer, nullable=False)
    status = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    event_id = Column(Integer, ForeignKey('event.id'), nullable=False)
    venue_id = Column(Integer, ForeignKey('venue.id'), nullable=False)

    event = relationship("Event")
    venue = relationship("Venue")

    def __repr__(self):
        return f"<Ticket(seat_number={self.seat_number}, status='{self.status}', price={self.price})>"

class Booking(Base):
    __tablename__ = 'booking'

    id = Column(Integer, primary_key=True)
    user_sub = Column(String, nullable=False)
    event_id = Column(Integer, ForeignKey('event.id'), nullable=False)
    seats = Column(ARRAY(Integer), nullable=False)
    status = Column(String, nullable=False)

    event = relationship("Event")

    def __repr__(self):
        return f"<Booking(user_sub='{self.user_sub}', seats={self.seats})>"

from sqlalchemy import create_engine
from models import Base

# Database connection parameters
DB_NAME = "bms_db"
DB_USER = "postgres"  # Default PostgreSQL user
DB_PASSWORD = "mysecretpassword"  # Use the password you set in Docker
DB_HOST = "localhost"  # Or use "bmsdb" if running from another container
DB_PORT = "5432"  # Default PostgreSQL port

# Create the database URL
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def create_tables():
    try:
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        # Create all tables
        Base.metadata.create_all(engine)
        
        print("Tables created successfully!")
        
    except Exception as e:
        print(f"Error creating tables: {e}")

if __name__ == "__main__":
    create_tables() 