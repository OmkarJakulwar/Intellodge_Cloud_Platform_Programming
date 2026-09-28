from django.urls import path
from intelroom import views

urlpatterns = [
    path('', views.room_list, name='room_list'),
    path('add/', views.add_room, name='add_room'),
    path('edit/<str:room_number>/', views.edit_room, name='edit_room'),
    path('delete/<str:room_number>/', views.delete_room, name='delete_room'),
]
