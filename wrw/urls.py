from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('user/<int:user_id>/', views.user_page, name='user-page'),
    path('symptom/<int:symptom_id>/', views.symptom_page, name='symptom-page'),
    path('symptom/<int:symptom_id>/method/<int:method_id>',
         views.method_page, name='method-page'),
    path('user/<int:user_id>/add/symptom',
         views.add_symptom_page, name='add-symptom-page'),
#     path('user/<int:user_id>/add/symptom_update',
     #     views.add_symptom_update_page, name='add-symptom-update-page')
]
