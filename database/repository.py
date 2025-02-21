from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, DateTime
from models import Venue, Artist, Event, Ticket, Booking
from typing import Union, List
from sqlalchemy import and_
from enum import Enum

class TicketStatus(Enum):
    AVAILABLE = "available"
    RESERVED = "reserved"
    BOOKED = "booked"

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
        # Input validation
        if not name or not isinstance(name, str):
            raise ValueError("Name must be a string")
        if not location or not isinstance(location, str):
            raise ValueError("Location must be a string")
        if not seat_map or not isinstance(seat_map, list):
            raise ValueError("Seat map must be a array")
        if not all(isinstance(seat, int) for seat in seat_map):
            raise ValueError("All seats in seat_map must be integers")

        def operation(session):
            venue = Venue(name=name, location=location, seat_map=seat_map)
            session.add(venue)
            return venue
        return self._execute_transaction(operation)

    def get_venue(self, search_term, search_by='name'):
        """
        Get venue by name or location using partial match
        Args:
            search_term (str): Term to search for
            search_by (str): Field to search by - either 'name' or 'location'
        """
        if not search_term or not isinstance(search_term, str):
            raise ValueError("Search term must be a non-empty string")
        if search_by not in ['name', 'location']:
            raise ValueError("search_by must be either 'name' or 'location'")

        def operation(session):
            if search_by == 'name':
                return session.query(Venue).filter(Venue.name.ilike(f'%{search_term}%')).all()
            else:
                return session.query(Venue).filter(Venue.location.ilike(f'%{search_term}%')).all()
        return self._execute_transaction(operation)

class ArtistRepository(Repository):
    def create_artist(self, name):
        # Input validation
        if not name or not isinstance(name, str):
            raise ValueError("Name must be a string")

        def operation(session):
            artist = Artist(name=name)
            session.add(artist)
            return artist
        return self._execute_transaction(operation)

    def get_artist(self, artist_name):
        """
        Get artist by name using partial match
        Args:
            artist_name (str): Term to search for
        """
        def operation(session):
            return session.query(Artist).filter(Artist.name.ilike(f'%{artist_name}%')).all()
        return self._execute_transaction(operation)

class EventRepository(Repository):
    def create_event(self, name, desc, datetime, artist_id, venue_id):
        # Input validation
        if not name or not isinstance(name, str):
            raise ValueError("Name must be a non-empty string")
        if not desc or not isinstance(desc, str):
            raise ValueError("Description must be a non-empty string")
        if not datetime or not isinstance(datetime, DateTime):
            raise ValueError("Input should be of Datetime type")
        if not isinstance(artist_id, int):
            raise ValueError("Artist ID must be an integer")
        if not isinstance(venue_id, int):
            raise ValueError("Venue ID must be an integer")

        def operation(session):
            # Check both artist and venue existence in a single query
            exists = session.query(
                session.query(Artist).filter(Artist.id == artist_id).exists(),
                session.query(Venue).filter(Venue.id == venue_id).exists()
            ).first()
            
            if not exists[0]:
                raise ValueError(f"Artist with id {artist_id} does not exist")
            if not exists[1]:
                raise ValueError(f"Venue with id {venue_id} does not exist")

            # First create the event
            event = Event(
                name=name,
                desc=desc,
                datetime=datetime,
                artist_id=artist_id,
                venue_id=venue_id
            )
            session.add(event)
            session.flush()  # Flush to get the event ID

            # Get venue's seat map
            venue = session.query(Venue).filter(Venue.id == venue_id).first()
            
            # Create tickets for each seat
            for seat_number in venue.seat_map:
                ticket = Ticket(
                    seat_number=seat_number,
                    status="available",
                    price=10,
                    event_id=event.id,
                    venue_id=venue_id
                )
                session.add(ticket)
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
    def get_ticket(self, ticket_id):
        def operation(session):
            return session.query(Ticket).filter(Ticket.id == ticket_id).first()
        return self._execute_transaction(operation)

    def get_tickets(self):
        def operation(session):
            return session.query(Ticket).all()
        return self._execute_transaction(operation)

    def update_ticket_status(self, ticket_ids: Union[int, List[int]], new_status: str):
        try:
            status = TicketStatus(new_status.lower())
        except ValueError:
            raise ValueError(f"Invalid status. Must be one of: {[s.value for s in TicketStatus]}")

        if isinstance(ticket_ids, int):
            ticket_ids = [ticket_ids]

        def operation(session):
            # First check if any ticket is already in the requested status
            invalid_tickets = session.query(Ticket).filter(
                and_(
                    Ticket.id.in_(ticket_ids),
                    Ticket.status == status.value
                )
            ).all()

            if invalid_tickets:
                ticket_details = [f"Ticket ID {t.id} is already {t.status}" for t in invalid_tickets]
                raise ValueError(f"Cannot update tickets. Following tickets are already in '{status.value}' state: {', '.join(ticket_details)}")

            # If we get here, all tickets are in a different state, safe to update
            result = session.query(Ticket).filter(
                Ticket.id.in_(ticket_ids)
            ).update(
                {Ticket.status: status.value}
            )

            return result

        return self._execute_transaction(operation)

class BookingRepository(Repository):
    def create_booking(self, user_sub: str, event_id: int, seats: List[int]):
        def operation(session):
            # Check event exists
            event = session.query(Event).filter(Event.id == event_id).first()
            if not event:
                raise ValueError(f"Event with ID {event_id} does not exist")

            # Check ticket availability for all requested seats
            available_tickets = session.query(Ticket).filter(
                Ticket.event_id == event_id,
                Ticket.status == "available",
                Ticket.seat_number.in_(seats)
            ).all()

            if len(available_tickets) != len(seats):
                raise ValueError(f"Not all requested seats are available for event with ID {event_id}")

            # Create booking
            booking = Booking(
                user_sub=user_sub,
                event_id=event_id,
                seats=seats,
                status="reserved"
            )
            session.add(booking)

            # Update ticket status to booked            
            return booking

        return self._execute_transaction(operation)
    
    def confirm_booking(self, booking_id: int):
        def operation(session):
            booking = session.query(Booking).filter(Booking.id == booking_id).first()
            if not booking:
                raise ValueError(f"Booking with ID {booking_id} does not exist")
            booking.status = "booked"
            session.add(booking)

            session.query(Ticket).filter(
                Ticket.event_id == booking.event_id,
                Ticket.seat_number.in_(booking.seats)
            ).update({Ticket.status: TicketStatus.BOOKED.value})

            return booking
        return self._execute_transaction(operation)

    def get_booking(self, booking_id):
        def operation(session):
            return session.query(Booking).filter(Booking.id == booking_id).first()
        return self._execute_transaction(operation)

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
            seats=1
        )

        print("All entities created successfully!")

    except Exception as e:
        print(f"Error creating entities: {e}") 