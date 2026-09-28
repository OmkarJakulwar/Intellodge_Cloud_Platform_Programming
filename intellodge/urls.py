from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    # include the app urls
    path('', include('intelrev.urls')),
    path('rooms/', include('intelroom.urls')),  # new room management app
    path('bookings/', include('intelbookings.urls')), # new booking management app
    path("revenue/", include("intelrevenue.urls")),

]
