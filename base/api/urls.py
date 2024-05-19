from django.urls import path, include
from . import views
from .views import MyTokenObtainPairView
from .views import SignUpView
from .views import UpdateProfilePic, EvaluateMoodView, UpdateUserDetails, OCRView
from .views import ResetPassword, ResetPasswordSet, resetPasswordPage
from .views import GetHobbies



from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns = [
    path('', views.getRoutes),

    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('signup/', SignUpView.as_view(), name='sign_up'),

    path('profile/', views.getProfile, name="get_profile"),
    path('updateprofile/', views.updateProfile, name='update_profile'),
    path('updateprofilepic/', UpdateProfilePic.as_view(), name='update_profile_pic'),
    path('removeprofilepic/', views.removeProfilePic, name='remove_profilepic'),
    path('changepassword/', views.changePassword, name='change_password'),

    path('resetpassword/', ResetPassword.as_view(), name='reset_password'),
    path('resetpassword/<str:encoded_pk>/<str:token>/', views.resetPasswordPage, name='reset_password'),
    path('resetpasswordcomplete/', views.passwordResetComplete, name='password_reset_complete'),
    

    path('evaluatemood/', EvaluateMoodView.as_view(), name='evaluate_mood'),
    path('ocr/', OCRView.as_view(), name='ocr_view'),

    path('getmoods/', views.getMoodRecords, name='get_mood_records'),

    path('gethobbies/', GetHobbies.as_view(), name='get_hobbies'),
    path('getrecommendations/', views.getRecommendations, name='get_recommendations'),

    path('updateuserdetails/', UpdateUserDetails.as_view(), name='update_user_details'),

    path('gethabits/', views.GetHabits.as_view(), name='get_habits'),

    path('getuseractivity/', views.GetUserActivity.as_view(), name='get_user_activity'),
    path('updateuseractivity/', views.UpdateUserActivity.as_view(), name='update_user_activity'),

    path('addmedication/', views.AddMedicine.as_view(), name='add_medicine'),
    path('getmedications/', views.GetMedications.as_view(), name='get_medications'),

    path('addhabitrecord/', views.AddHabitRecord.as_view(), name='add_habit_record'),
    path('gethabitrecords/', views.GetHabitRecords.as_view(), name='get_habit_records'),
    #path('login/', views.userLogin),
]


