from django.urls import path
from intelbookings import views

urlpatterns = [
    path("", views.booking_list, name="booking_list"),
    path("create/", views.booking_create, name="booking_create"),
    path("cancel/<str:booking_id>/", views.booking_cancel, name="booking_cancel"),
    path("<str:booking_id>/", views.booking_detail, name="booking_detail"),
]
