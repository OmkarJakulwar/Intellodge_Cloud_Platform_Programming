import json
from datetime import datetime, timezone
from intellodge_core.base_service import BaseDynamoDBService
from intellodge_core.logger import get_logger

log = get_logger(__name__)

class BookingService(BaseDynamoDBService):
    def __init__(self):
        super().__init__("Bookings")

class RoomService(BaseDynamoDBService):
    def __init__(self):
        super().__init__("Rooms")

def lambda_handler(event, context):
    today = datetime.now(timezone.utc).date()
    
    booking_service = BookingService()
    room_service = RoomService()
    log.info("Starting automated room status update...")

    try:
        bookings = booking_service.find_all().get("items", [])
        
        for booking in bookings:
            booking_id = booking["booking_id"]
            room_number = booking.get("room_number")
            status = booking.get("status")
            check_out_str = booking.get("check_out_date")

            if not check_out_str or status in ["Cancelled", "Completed"]:
                continue

            check_out_dt = datetime.fromisoformat(check_out_str)
            
            if check_out_dt.tzinfo is None:
                check_out_dt = check_out_dt.replace(tzinfo=timezone.utc)

            check_out_date = check_out_dt.date()
            
            if check_out_date <= today:
                room_service.update({"room_number": room_number}, {"status": "Vacant"})
                booking_service.update({"booking_id": booking_id}, {"status": "Completed"})
                log.info(f"Booking {booking_id} completed. Room {room_number} set to Vacant.")

        log.info("Automated room status update completed successfully.")
        return {"status": "success"}

    except Exception as e:
        log.error(f"Error in auto room status Lambda: {e}")
        return {"status": "failure", "error": str(e)}
