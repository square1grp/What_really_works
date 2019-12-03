from django.urls import path
from .views.index import IndexPage
from .views.user import UserPage
from .views.symptom import SymptomPage
from .views.method import MethodPage
from .views.user_symptom import UserSymptomPage
from .views.user_method_trial import UserMethodTrialPage

urlpatterns = [
    path('', IndexPage.as_view()),
    path('user/<int:user_id>/', UserPage.as_view()),
    path('symptom/<int:symptom_id>/', SymptomPage.as_view()),
    path('symptom/<int:symptom_id>/method/<int:method_id>', MethodPage.as_view()),
    path('user/<int:user_id>/add/symptom', UserSymptomPage.as_view()),
    path('user/<int:user_id>/add/treatment', UserMethodTrialPage.as_view())
]
