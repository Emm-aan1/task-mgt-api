from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from .models import Task
from .serializers import (
    TaskSerializer,
    RegisterUserSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
)
from django_filters import rest_framework as filters
from django.core.mail import send_mail
from django.utils import timezone
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.hashers import make_password


# Create your views here.
class RegisterUserView(APIView):
    def post(self, request):
        serializer = RegisterUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            send_mail(
                subject="Welcome to Task Management!",
                message=f"Hello {user.username},\n\nThank you for registering with us.",
                from_email=None,
                recipient_list=[user.email],
                fail_silently=False,
            )
            return Response(
                {"message": "User created successfully"}, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskFilter(filters.FilterSet):
    status = filters.CharFilter(field_name="status", lookup_expr="iexact")
    due_date = filters.DateFilter(field_name="due_date", lookup_expr="exact")

    class Meta:
        model = Task
        fields = ["status", "due_date"]


class TaskListCreateView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Task.objects.filter(user=self.request.user)
        status = self.request.query_params.get("status", None)
        priority = self.request.query_params.get("priority", None)
        due_date = self.request.query_params.get("due_date", None)
        category = self.request.query_params.get("category", None)
        sort_by = self.request.query_params.get("sort_by", None)

        if status:
            queryset = queryset.filter(status__iexact=status)

        if priority:
            queryset = queryset.filter(priority__iexact=priority)

        if due_date:
            queryset = queryset.filter(due_date__exact=due_date)

        if category:
            queryset = queryset.filter(category__iexact=category)

        if sort_by in ["due_date", "created_at"]:
            queryset = queryset.order_by(sort_by)

        return queryset

    def perform_create(self, serializer):
        category = self.request.data.get("category")
        task = serializer.save(user=self.request.user, category=category)
        self.send_task_created_email(task)

        if task.status == "Completed":
            task.completed_at = timezone.now()
            task.save()

    def send_task_created_email(self, task):
        send_mail(
            subject=f'New Task Created: "{task.title}"',
            message=f'Hello {task.user.username},\n\nA new task "{task.title}" has been created for you with a due date of {task.due_date}.\n\nTask Management Team',
            from_email=None,
            recipient_list=[task.user.email],
            fail_silently=False,
        )


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        instance = serializer.save()

        if instance.status == "Completed" and not instance.completed_at:
            instance.completed_at = timezone.now()
            self.send_task_completed_email(instance)

    def send_task_completed_email(self, task):
        send_mail(
            subject=f"Task '{task.title}' has been completed",
            message=f"Hello {task.user.username}, \n\nYour task '{task.title}' has been marked as completed. \n\nTask Management App",
            from_email=None,
            recipient_list=[task.user.email],
            fail_silently=False,
        )

    def get_object(self):
        try:
            return super().get_object()
        except Task.DoesNotExist:
            raise NotFound({"error": "Task not found"})

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"message": "Task deleted successfully"}, status=status.HTTP_200_OK
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user
            token = RefreshToken.for_user(user)
            token.blacklist()

            return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(APIView):
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = User.objects.get(email=serializer.validated_data["email"])
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))

                reset_url = (
                    f"http://localhost:8000/api/password-reset-confirm/{uid}/{token}/"
                )
                message = f"Hi {user.username},\n\nUse the link below to reset your password:\n{reset_url}"

                send_mail(
                    subject="Password Reset Request",
                    message=f"Hi {user.username},\n\nUse the link below to reset your password:\n{reset_url}",
                    from_email=None,
                    recipient_list=[user.email],
                    fail_silently=False,
                )

                return Response(
                    {"message": "Password reset email sent."}, status=status.HTTP_200_OK
                )
            except User.DoesNotExist:
                return Response(
                    {"error": "User with this email does not exist."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    def post(self, request, uidb64, token):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            try:
                uid = force_str(urlsafe_base64_decode(uidb64))
                user = User.objects.get(pk=uid)

                if default_token_generator.check_token(user, token):
                    user.password = make_password(
                        serializer.validated_data["new_password"]
                    )
                    user.save()

                    message = f"""
                    Hi {user.username},

                    Your password has been reset successfully. If you did not request this change, please contact our support team immediately.

                    Thank you,
                    Task Management Support Team
                    """

                    send_mail(
                        subject="Password Reset Confirmation",
                        message=message,
                        from_email=None,
                        recipient_list=[user.email],
                        fail_silently=False,
                    )
                    return Response(
                        {"message": "Password has been reset successfully."},
                        status=status.HTTP_200_OK,
                    )
                else:
                    return Response(
                        {"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST
                    )
            except User.DoesNotExist:
                return Response(
                    {"error": "User does not exist."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
