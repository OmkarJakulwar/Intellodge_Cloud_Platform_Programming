from decimal import Decimal
from collections import defaultdict
from datetime import datetime
from intellodge_core.base_service import BaseDynamoDBService
from intellodge_core.logger import get_logger
from intellodge_core.datetime_utils import now_utc

logger = get_logger(__name__)

class RevenueService:
    def __init__(self, bookings_table="Bookings", rooms_table="Rooms"):
        self.bookings = BaseDynamoDBService(bookings_table)
        self.rooms = BaseDynamoDBService(rooms_table)

    @staticmethod
    def _to_float(value):
        if isinstance(value, Decimal):
            return float(value)
        try:
            return float(value)
        except Exception:
            return 0.0

    def all_bookings(self):
        # below will give booking list items
        resp = self.bookings.find_all()
        if isinstance(resp, dict) and resp.get("success") is not None:
            return resp.get("items", [])
        return resp or []

    def total_revenue(self, year=None):
        # Sum amounts for non-cancelled bookings
        total = 0.0
        for b in self.all_bookings():
            if b.get("status", "").lower() == "cancelled":
                continue
            amt = self._to_float(b.get("amount", 0))
            if year:
                # booking may have check_in_date
                d = b.get("check_in_date") or b.get("created_at")
                if not d:
                    continue
                y = datetime.fromisoformat(d).year
                if y != int(year):
                    continue
            total += amt
        return total

    def revenue_by_month(self, year=None):
        # It Returns dict {month_idx (1..12): amount}, If year is None, it uses current year.
        
        if year is None:
            year = datetime.utcnow().year
        monthly = defaultdict(float)
        for b in self.all_bookings():
            if b.get("status", "").lower() == "cancelled":
                continue
            d = b.get("check_in_date") or b.get("created_at")
            if not d:
                continue
            try:
                dt = datetime.fromisoformat(d)
            except Exception:
                continue
            if dt.year != int(year):
                continue
            month = dt.month
            monthly[month] += self._to_float(b.get("amount", 0))
            
        # ensure months 1..12 present
        return [round(monthly.get(m, 0.0), 2) for m in range(1, 13)]

    def revenue_by_years(self, years_back=5):
        # Return list of (year, total) starting from current year backwards.
        
        now = datetime.utcnow()
        data = []
        for i in range(years_back):
            y = now.year - i
            data.append((y, round(self.total_revenue(year=y), 2)))
        return list(reversed(data))  # oldest -> newest

    def bookings_count(self):
        items = self.all_bookings()
        return len(items)

    def active_bookings_count(self):
        items = [b for b in self.all_bookings() if b.get("status", "").lower() != "cancelled"]
        return len(items)

    def occupancy_rate(self):
        # Calculate occupancy = occupied rooms / total rooms * 100
        rooms_resp = self.rooms.find_all()
        rooms = rooms_resp.get("items", []) if isinstance(rooms_resp, dict) else rooms_resp or []
        total_rooms = len(rooms)
        if total_rooms == 0:
            return 0.0
        occupied = len([r for r in rooms if r.get("status") == "Occupied"])
        return round((occupied / total_rooms) * 100.0, 2)

    def revenue_summary(self):
        # Return a small summary dict for dashboard cards
        return {
            "total_revenue": round(self.total_revenue(), 2),
            "monthly_revenue": self.revenue_by_month(),
            "yearly": self.revenue_by_years(5),
            "bookings_count": self.bookings_count(),
            "active_bookings": self.active_bookings_count(),
            "occupancy_rate": self.occupancy_rate(),
            "generated_at": now_utc(),
        }
