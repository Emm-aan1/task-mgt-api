from django.urls import path
from .views import (
    TaskListCreateView,
    TaskDetailView,
    RegisterUserView,
    LogoutView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
)

urlpatterns = [
    path("tasks/", TaskListCreateView.as_view(), name="task-list-create"),
    path("tasks/<int:pk>/", TaskDetailView.as_view(), name="task-detail"),
    path("register/", RegisterUserView.as_view(), name="user-register"),
    path("logout/", LogoutView.as_view(), name="user-logout"),
    path("password-reset/", PasswordResetRequestView.as_view(), name="password-reset"),
    path(
        "password-reset-confirm/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(),
        name="password-reset-confirm",
    ),
]
