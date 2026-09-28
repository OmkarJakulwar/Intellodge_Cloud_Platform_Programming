from intellodge_core.base_service import BaseDynamoDBService
from intellodge_core.datetime_utils import now_utc
from intelroom.models.dynamo_rooms import Room
from intellodge_core.logger import get_logger
from intellodge_core.exceptions import NotFoundError, ValidationError

log = get_logger(__name__)
roomService = Room()

class BookingService(BaseDynamoDBService):
    # getting the bookings table from our intellodge library from basedynamodbservice
    def __init__(self):
        super().__init__("Bookings")
    

    def create_booking(self, booking_id, booking_code, room_number, amount, check_in_date, check_out_date, guest_name, guest_email, status="pending"):
        
        # Validating room exists
        room = roomService.get(room_number)
        if not room:
            raise ValueError(f"Room {room_number} does not exist.")

        if room["status"] != "Vacant":
            raise ValueError(f"Room {room_number} is currently {room['status']} and cannot be booked.")

        item = {
            "booking_id": booking_id,
            "booking_code": booking_code,
            "room_number": room_number,
            "amount": amount,
            "check_in_date": check_in_date,
            "check_out_date": check_out_date,
            "guest_name": guest_name,
            "guest_email": guest_email,
            "status": status,
            "created_at": now_utc(),
        }

        # Create booking in DynamoDB
        result = self.create(item)
        created_item = result.get("item")
        if not created_item:
            raise ValueError("Failed to create booking in DynamoDB.")

        # Marking room as Occupied
        try:
            roomService.update(room_number, status="Occupied")
        except Exception as e:
            log.error(f"Failed to mark room {room_number} as occupied: {e}")
            raise ValueError(f"Could not mark room {room_number} as occupied.")
        
        log.info(f"Booking created: {booking_code}, Room {room_number} now Occupied")
        return created_item

    # finding the bookings with booking id
    def get_booking(self, booking_id):
        result = self.read({"booking_id": booking_id})
        if not result.get("success") or not result.get("item"):
            raise NotFoundError(f"Booking {booking_id} not found")
        return result["item"]

    # updating booking with booking id
    def update_booking(self, booking_id, **updates):
        log.info(f"Updating booking {booking_id}: {updates}")
        return self.update({"booking_id": booking_id}, updates)

    # cancelling the booking with booking id
    def cancel_booking(self, booking_id):
        log.info(f"Attempting to cancel booking {booking_id}...")
        booking = self.get_booking(booking_id)
        room_number = booking["room_number"]

        # Mark room as Vacant
        roomService.update(room_number, status="Vacant")
        log.info(f"Room {room_number} marked as Vacant")

        # Update booking status
        self.update({"booking_id": booking_id}, {"status": "cancelled"})

        log.info(f"Booking {booking_id} Cancelled")
        return True

    # listing the bookings 
    def list_bookings(self):
        result = self.find_all()
        if result.get("success"):
            return result["items"]
        return []
