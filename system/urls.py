from django.urls import path

from system.views import ImagesView, ImageView

urlpatterns = [
    path('container/', ImagesView.as_view()),
    path('container/<challenge_name>/', ImageView.as_view()),
    #path('container/<manager_id>/action/<action>', ImageActions.as_view()),
]
