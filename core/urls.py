from django.urls import path 
from . import views 

urlpatterns = [
    path("", views.mood_generator)
]
