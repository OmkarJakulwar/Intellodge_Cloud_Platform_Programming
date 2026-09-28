from django.shortcuts import render, redirect
from django.contrib import messages
from intelrev.decorators import login_required_custom, role_required
from intelroom.models.dynamo_rooms import Room
from intelrev.services.s3_setup import upload_fileobj, get_s3_client, delete_s3_image
from django.conf import settings
from intellodge_core.logger import get_logger
from botocore.exceptions import ClientError

log = get_logger(__name__)

room_service = Room()
room_types = room_service.ROOM_TYPES
status_options = room_service.STATUS_OPTIONS


def generate_presigned_url(bucket_name, key, expiry=3600):
    # Generate a temporary pre-signed S3 URL for private image access.
    s3 = get_s3_client()
    try:
        url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': key},
            ExpiresIn=expiry  # URL valid for 1 hour
        )
        return url
    except ClientError as e:
        log.warning(f"Error generating presigned URL for {key}: {e}")
        return None

@login_required_custom
@role_required(["admin", "staff"])
def room_list(request):
    # Display all rooms with pre-signed S3 image URLs.
    rooms = room_service.list_all()
    bucket_name = getattr(settings, "AWS_S3_BUCKET")

    for room in rooms:
        try:
            key = f"{room['room_type'].lower()}/{room['room_number']}.jpg"
            presigned_url = generate_presigned_url(bucket_name, key)
            room["image_url"] = presigned_url
        except KeyError as e:
            log.warning(f"Missing key while generating image URL: {e}")
            room["image_url"] = None

    log.info(f"Generated {len([r for r in rooms if r.get('image_url')])} presigned image URLs")
    context = {"rooms": rooms}
    return render(request, "intelroom/room_list.html", context)


@login_required_custom
@role_required(["admin"])
def add_room(request):
    # Add a new room and upload its image to S3.
    if request.method == "POST":
        room_number = request.POST.get("room_number")
        room_type = request.POST.get("room_type")
        price = request.POST.get("price")
        status = request.POST.get("status")

        # Upload image if provided
        image_file = request.FILES.get("room_image")
        if image_file:
            key = f"{room_type.lower()}/{room_number}.jpg"
            upload_fileobj(image_file, key)
            log.info(f"Uploaded room image to S3: {key}")

        room_service.create(
            room_number=room_number,
            room_type=room_type,
            price=float(price),
            status=status
        )

        messages.success(request, f"Room {room_number} added successfully!")
        return redirect("room_list")

    return render(request, "intelroom/room_form.html", {
        "edit_mode": False,
        "room_types": room_types,
        "status_options": status_options,
    })


@login_required_custom
@role_required(["admin", "staff"])
def edit_room(request, room_number):
    # Edit existing room details and update S3 image if re-uploaded.
    room = room_service.get(room_number)
    if not room:
        messages.error(request, "Room not found.")
        return redirect("room_list")

    if request.method == "POST":
        room_type = request.POST.get("room_type")
        price = request.POST.get("price")
        status = request.POST.get("status")

        # Upload image if provided
        image_file = request.FILES.get("room_image")
        if image_file:
            key = f"{room_type.lower()}/{room_number}.jpg"
            log(f"your key is:", key)
            upload_fileobj(image_file, key)
            log.info(f"Re-uploaded image for room {room_number}: {key}")

        # Update room data in DynamoDB
        update_data = {"room_type": room_type, "price": float(price), "status": status}
        room_service.update(room_number, **update_data)

        messages.success(request, f"Room {room_number} updated successfully!")
        return redirect("room_list")

    # Generate presigned URL for image
    bucket_name = getattr(settings, "AWS_S3_BUCKET")
    key = f"{room['room_type'].lower()}/{room['room_number']}.jpg"
    room["image_url"] = generate_presigned_url(bucket_name, key)

    return render(request, "intelroom/room_form.html", {
        "edit_mode": True,
        "room": room,
        "room_types": room_types,
        "status_options": status_options,
    })


@login_required_custom
@role_required(["admin"])
def delete_room(request, room_number):
    # Delete a room record and deleting the image from s3
    room = room_service.get(room_number)
    if room:
        # Build S3 key
        room_type = room.get("room_type")
        key = f"{room_type.lower()}/{room_number}.jpg"
        
        # Delete S3 image
        deleted = delete_s3_image(key)
        if deleted:
            log.info(f"S3 image deleted for room {room_number}")
        else:
            log.warning(f"S3 image NOT deleted for room {room_number}")
        
        # Delete room from DynamoDB    
        room_service.delete(room_number)
        messages.success(request, f"Room {room_number} deleted successfully!")
    else:
        messages.error(request, "Room not found.")
    return redirect("room_list")
