from django.urls import path
from profiles import views

urlpatterns = [
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('confirm/', views.confirm_needed, name='confirmation-needed'),
    path('confirm/<str:token>/', views.confirm_email, name='confirm'),
    path('top/', views.TopProfilesList.as_view(), name='profile-top'),
    path('<int:pk>/', views.ProfileDetail.as_view(), name='profile-detail'),
]
