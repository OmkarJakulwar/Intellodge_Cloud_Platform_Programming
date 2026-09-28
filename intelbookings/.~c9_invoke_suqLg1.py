import uuid
from django.shortcuts import render, redirect
from django.contrib import messages
from intelrev.decorators import login_required_custom
from intelroom.models.dynamo_rooms import Room
from intelbookings.forms import BookingForm
from intelbookings.models.dynamo_bookings import BookingService
from intelbookings.utils import generate_booking_code
from intellodge_core.logger import get_logger
from intellodge_core.exceptions import NotFoundError, ValidationError
from decimal import Decimal
from django.core.paginator import Paginator


booking_service = BookingService()
log = get_logger(__name__)

@login_required_custom
def booking_list(request):
    # Fetch all bookings
    bookings = booking_service.list_bookings()

    # Ensure DynamoDB Decimal is converted to float
    for b in bookings:
        if "amount" in b:
            b["amount"] = float(b["amount"])

    # Use Django Pagination
    paginator = Paginator(bookings, 10)  # 10 per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "intelbookings/booking_list.html", {"page_obj": page_obj})


@login_required_custom
def booking_create(request):
    form = BookingForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            data = form.cleaned_data

            if not data.get("room_number"):
                messages.error(request, "⚠️ No vacant rooms available.")
                return redirect("booking_list")

            booking_id = str(uuid.uuid4())
            booking_code = generate_booking_code()

            try:
                # Status is automatically set to "confirmed"
                booking_service.create_booking(
                    booking_id=booking_id,
                    booking_code=booking_code,
                    room_number=data["room_number"],
                    amount=Decimal(data["amount"]),
                    check_in_date=data["check_in_date"].isoformat(),
                    check_out_date=data["check_out_date"].isoformat(),
                    guest_name=data["guest_name"],
                    guest_email=data["guest_email"],
                    status="confirmed",
                )
                messages.success(
                    request,
                    f"Booking for {data['guest_name']} created successfully! With Booking ID: {booking_code}"
                )
                return redirect("booking_list")

            except (ValidationError, NotFoundError) as e:
                messages.error(request, f"⚠️ {str(e)}")

            except Exception as e:
                log.error(f"Unexpected booking error: {e}")
                messages.error(request, f"⚠️ Something went wrong while creating booking: {e}")

        else:
            pass

    return render(request, "intelbookings/booking_form.html", {"form": form})


@login_required_custom
def booking_edit(request, booking_id):
    try:
        booking = booking_service.get_booking(booking_id)
    except NotFoundError:
        messages.error(request, "Booking not found.")
        return redirect("booking_list")

    if request.method == "POST":
        form = BookingForm(request.POST, editing=True)
        if form.is_valid():
            data = form.cleaned_data
            try:
                updates = {
                    "amount": float(data["amount"]),
                    "check_in_date": data["check_in_date"].isoformat(),
                    "check_out_date": data["check_out_date"].isoformat(),
                    "status": data.get("status", booking.get("status", "pending")),
                }
                booking_service.update_booking(booking_id, **updates)
                messages.success(request, f"Booking {booking['booking_code']} updated successfully!")
                return redirect("booking_list")
            except Exception as e:
                log.error(f"Booking update failed: {e}")
                messages.error(request, f"⚠️ {str(e)}")
        else:
            messages.error(request, "⚠️ Please correct the errors below.")
    else:
        form = BookingForm(
            initial={
                "room_number": booking["room_number"],
                "amount": booking["amount"],
                "check_in_date": booking["check_in_date"],
                "check_out_date": booking["check_out_date"],
                "status": booking.get("status", "pending")
            },
            editing=True
        )

    return render(
        request,
        "intelbookings/booking_form.html",
        {"form": form, "edit_mode": True, "booking": booking}
    )


@login_required_custom
def booking_cancel(request, booking_id):
    try:
        booking_service.cancel_booking(booking_id)
        messages.success(request, "Booking cancelled. Room is now Vacant.")
    except NotFoundError as e:
        messages.error(request, f"⚠️ {str(e)}")
    except Exception as e:
        log.error(f"Cancel booking failed: {e}")
        messages.error(request, f"⚠️ Unexpected error cancelling booking: {e}")

    return redirect("booking_list")
    
    
@login_required_custom
def booking_detail(request, booking_id):
    booking = booking_service.get_booking(booking_id)

    if not booking:
        messages.error(request, "Booking not found.")
        return redirect("booking_list")

    return render(request, "intelbookings/booking_detail.html", {"booking": booking})

