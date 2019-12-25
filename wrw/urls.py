from django.urls import path
from .views.index import IndexPage
from .views.register import RegisterPage
from .views.verify import VerifyTokenPage
from .views.user import UserPage
from .views.symptom import SymptomPage
from .views.method import MethodPage
from .views.user_symptom import UserSymptomPage
from .views.user_method_trial import UserMethodTrialPage
from .views.user_symptom_update import UserSymptomUpdatePage
from .views.user_side_effect_update import UserSideEffectUpdatePage

urlpatterns = [
    path('', IndexPage.as_view()),
    path('register/', RegisterPage.as_view()),
    path('register/verity-token/<str:token>/', VerifyTokenPage.as_view()),
    path('user/<int:user_id>/', UserPage.as_view()),
    path('symptom/<int:symptom_id>/', SymptomPage.as_view()),
    path('symptom/<int:symptom_id>/method/<int:method_id>/', MethodPage.as_view()),
    path('user/<int:user_id>/add/symptom/', UserSymptomPage.as_view()),
    path('user/<int:user_id>/add/treatment/', UserMethodTrialPage.as_view()),
    path('user/<int:user_id>/add/symptom_update/',
         UserSymptomUpdatePage.as_view()),
    path('user/<int:user_id>/add/side_effect_update/',
         UserSideEffectUpdatePage.as_view())
]
