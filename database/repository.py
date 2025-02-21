from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import Venue, Artist, Event, Ticket, Booking

class Repository:
    def __init__(self, database_url):
        self.engine = create_engine(database_url)
        self.Session = sessionmaker(bind=self.engine)

    def _execute_transaction(self, operation):
        """Helper method to handle session management and error handling"""
        session = self.Session()
        try:
            result = operation(session)
            session.commit()
            return result
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

class VenueRepository(Repository):
    def create_venue(self, name, location, seat_map):
        def operation(session):
            venue = Venue(name=name, location=location, seat_map=seat_map)
            session.add(venue)
            return venue
        return self._execute_transaction(operation)

    def get_venue(self, venue_id):
        def operation(session):
            return session.query(Venue).filter(Venue.id == venue_id).first()
        return self._execute_transaction(operation)

    def get_venues(self):
        def operation(session):
            return session.query(Venue).all()
        return self._execute_transaction(operation)

class ArtistRepository(Repository):
    def create_artist(self, name):
        def operation(session):
            artist = Artist(name=name)
            session.add(artist)
            return artist
        return self._execute_transaction(operation)

    def get_artist(self, artist_id):
        def operation(session):
            return session.query(Artist).filter(Artist.id == artist_id).first()
        return self._execute_transaction(operation)

    def get_artists(self):
        def operation(session):
            return session.query(Artist).all()
        return self._execute_transaction(operation)

class EventRepository(Repository):
    def create_event(self, name, desc, datetime, artist_id, venue_id):
        def operation(session):
            event = Event(
                name=name,
                desc=desc,
                datetime=datetime,
                artist_id=artist_id,
                venue_id=venue_id
            )
            session.add(event)
            return event
        return self._execute_transaction(operation)
    
    def get_event(self, event_id):
        def operation(session):
            return session.query(Event).filter(Event.id == event_id).first()
        return self._execute_transaction(operation)

    def get_events(self):
        def operation(session):
            return session.query(Event).all()
        return self._execute_transaction(operation)

class TicketRepository(Repository):
    def create_ticket(self, seat_number, status, price, event_id, venue_id):
        def operation(session):
            ticket = Ticket(
                seat_number=seat_number,
                status=status,
                price=price,
                event_id=event_id,
                venue_id=venue_id
            )
            session.add(ticket)
            return ticket
        return self._execute_transaction(operation)

    def get_ticket(self, ticket_id):
        def operation(session):
            return session.query(Ticket).filter(Ticket.id == ticket_id).first()
        return self._execute_transaction(operation)

    def get_tickets(self):
        def operation(session):
            return session.query(Ticket).all()
        return self._execute_transaction(operation)

class BookingRepository(Repository):
    def create_booking(self, user_sub, event_id, seats):
        def operation(session):
            booking = Booking(
                user_sub=user_sub,
                event_id=event_id,
                seats=seats
            )
            session.add(booking)
            return booking
        return self._execute_transaction(operation)
    
    def get_bookings(self):
        def operation(session):
            return session.query(Booking).all()
        return self._execute_transaction(operation)
    
    def get_booking(self, booking_id):
        def operation(session):
            return session.query(Booking).filter(Booking.id == booking_id).first()
        return self._execute_transaction(operation)
# Example usage

# Example usage
if __name__ == "__main__":
    DATABASE_URL = "postgresql://postgres:mysecretpassword@localhost:5432/bms_db"
    repo = Repository(DATABASE_URL)

    # Example creation of entities
    try:
        # Create a venue
        venue = repo.create_venue(
            name="Concert Hall",
            location="123 Music Street",
            seat_map=[1, 2, 3, 4, 5]
        )

        # Create an artist
        artist = repo.create_artist(name="Famous Band")

        # Create an event
        event = repo.create_event(
            name="Summer Concert",
            desc="Amazing summer concert",
            datetime="2024-07-01 20:00:00",
            artist_id=artist.id,
            venue_id=venue.id
        )

        # Create a ticket
        ticket = repo.create_ticket(
            seat_number=1,
            status="available",
            price=100,
            event_id=event.id,
            venue_id=venue.id
        )

        # Create a booking
        booking = repo.create_booking(
            user_sub="user123",
            event_id=event.id,
            seats=[1]
        )

        print("All entities created successfully!")

    except Exception as e:
        print(f"Error creating entities: {e}") 