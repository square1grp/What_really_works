from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('user/<int:user_id>/', views.user, name='user-detail'),
    path('symptom/<int:symptom_id>/', views.symptom, name='symptom-detail'),
]
