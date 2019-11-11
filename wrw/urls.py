from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('user/<int:user_id>/', views.user_page, name='user-page'),
    path('symptom/<int:symptom_id>/', views.symptom_page, name='symptom-page'),
    path('symptom/<int:symptom_id>/method/<int:method_id>',
         views.method_page, name='symptom-page'),
]
