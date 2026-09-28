# intelroom/models/dynamo_rooms.py
from decimal import Decimal
from intellodge_core.base_service import BaseDynamoDBService
from intellodge_core.logger import get_logger

log = get_logger(__name__)

class Room:
    # Room service using BaseDynamoDBService python library+

    ROOM_TYPES = ["Single", "Double", "Deluxe", "Suite"]
    STATUS_OPTIONS = ["Vacant", "Occupied", "Under Maintenance"]

    def __init__(self):
        self.roomService = BaseDynamoDBService("Rooms")

    def create(self, room_number, room_type, price, status):
        item = {
            "room_number": room_number,
            "room_type": room_type,
            "price": Decimal(str(price)),
            "status": status
        }
        response = self.roomService.create(item)
        if response.get("success"):
            log.info(f"Room created: {room_number}")
        else:
            log.error(f"Failed to create room {room_number}: {response}")
        return response

    def get(self, room_number):
        key = {"room_number": room_number}
        response = self.roomService.read(key)
        if response.get("success"):
            return response["item"]
        log.warning(f"Room {room_number} not found")
        return None

    def update(self, room_number, **updates):
        if "price" in updates:
            updates["price"] = Decimal(str(updates["price"]))
        response = self.roomService.update({"room_number": room_number}, updates)
        if response.get("success"):
            log.info(f"Room updated: {room_number} -> {updates}")
        else:
            log.error(f"Failed to update room {room_number}: {response}")
        return response

    def delete(self, room_number):
        response = self.roomService.delete({"room_number": room_number})
        if response.get("success"):
            log.info(f"Room deleted: {room_number}")
        else:
            log.error(f"Failed to delete room {room_number}: {response}")
        return response

    def list_all(self):
        response = self.roomService.find_all()
        if response.get("success"):
            return response.get("items", [])
        log.warning("No rooms found or failed to fetch rooms")
        return []
