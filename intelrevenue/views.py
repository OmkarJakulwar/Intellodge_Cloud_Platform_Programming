from django.shortcuts import render
from intelbookings.models.dynamo_bookings import BookingService
from intelroom.models.dynamo_rooms import Room
from datetime import datetime
from intellodge_core.datetime_utils import now_utc
from intelrev.decorators import login_required_custom

@login_required_custom
def revenue_dashboard(request):
    room_service = Room()
    booking_service = BookingService()
    bookings = booking_service.list_bookings()
    rooms = room_service.list_all()

    # Total revenue (exclude cancelled bookings)
    total_revenue = sum(float(b["amount"]) for b in bookings if b.get("status") != "cancelled")

    # Total bookings
    total_bookings = len(bookings)

    # Active bookings (which is not cancelled)
    active_bookings = len([b for b in bookings if b.get("status") != "cancelled"])

    # Occupancy rate
    occupied_rooms = len([r for r in rooms if r.get("status") == "Occupied"])
    total_rooms = len(rooms)
    occupancy_rate = round((occupied_rooms / total_rooms) * 100, 2) if total_rooms else 0

    # Monthly revenue for chart (Jan-Dec)
    monthly = [0] * 12
    current_year = datetime.utcnow().year
    for b in bookings:
        if b.get("status") == "cancelled":
            continue
    
        check_in = datetime.fromisoformat(b["check_in_date"])
        if check_in.year == current_year:
            month_index = check_in.month - 1
            monthly[month_index] += float(b["amount"])

    # Yearly revenue for chart (last 5 years)
    yearly = {}
    for b in bookings:
        if b.get("status") == "cancelled":
            continue
        check_in = datetime.fromisoformat(b["check_in_date"])
        year = check_in.year
        yearly[year] = yearly.get(year, 0) + float(b["amount"])
    yearly = sorted(yearly.items())  # [(2023, 1200), (2024, 3000), ...]

    context = {
        "summary": {
            "total_revenue": total_revenue,
            "bookings_count": total_bookings,
            "active_bookings": active_bookings,
            "occupancy_rate": occupancy_rate
        },
        "monthly": monthly,
        "yearly": yearly,
        "selected_year": current_year
    }

    return render(request, "intelrevenue/revenue_dashboard.html", context)
