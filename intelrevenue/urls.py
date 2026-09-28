from django.urls import path
from intelrevenue import views

urlpatterns = [
    path('', views.revenue_dashboard, name='revenue_dashboard'),  # main revenue page
    
]
