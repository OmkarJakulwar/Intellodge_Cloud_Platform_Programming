from django.urls import path, include
from intelrev import views

urlpatterns = [
    path('', views.home_redirect, name='home_redirect'),
    
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.home_dashboard, name='home_dashboard'),
    path('register/', views.register, name='register'),
    
]