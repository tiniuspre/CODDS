from __future__ import annotations

from django.urls import path

from system.views import ImageView, ImagesView

urlpatterns = [
    path('container/', ImagesView.as_view()),
    path('container/<challenge_name>/', ImageView.as_view()),
    # path('container/<manager_id>/action/<action>', ImageActions.as_view()),
]
