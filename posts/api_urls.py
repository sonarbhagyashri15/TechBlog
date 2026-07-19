from django.urls import path
from .api_views import (
    BlogListCreateAPIView,
    BlogRetrieveUpdateDestroyAPIView,
)

urlpatterns = [
    path(
        "posts/",
        BlogListCreateAPIView.as_view(),
        name="api_posts"
    ),

    path(
        "posts/<int:pk>/",
        BlogRetrieveUpdateDestroyAPIView.as_view(),
        name="api_post"
    ),
]