from django.urls import path

from admin_app.views import ChallengesView, ContainersView, UsersAdminView, UserAdminView, ContainersByUserView, ContainerByUserView

urlpatterns = [
    path('container/', ChallengesView.as_view()),
    path('container/<challenge_name>/', ContainersView.as_view()),
    path('container/<challenge_name>/<user_id>/', ContainerByUserView.as_view()),
    path('user/', UsersAdminView.as_view()),
    path('user/<user_id>/', UserAdminView.as_view()),
    path('user/<user_id>/containers/', ContainersByUserView.as_view()),

]
