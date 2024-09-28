from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Task
from .serializers import TaskSerializer, RegisterUserSerializer 
from django_filters import rest_framework as filters
from rest_framework.views import APIView
from django.core.mail import send_mail
from django.utils import timezone

# Create your views here.
class RegisterUserView(APIView):
  def post(self, request):
    serializer = RegisterUserSerializer(data=request.data)
    if serializer.is_valid():
      serializer.save()
      return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskFilter(filters.FilterSet):
  status = filters.CharFilter(field_name='status', lookup_expr='iexact')
  due_date = filters.DateFilter(field_name='due_date', lookup_expr='exact')

  class Meta:
    model = Task
    fields = ['status', 'due_date'] 


class TaskListCreateView(generics.ListCreateAPIView):
  serializer_class = TaskSerializer
  permission_classes = [permissions.IsAuthenticated]

  def get_queryset(self):
    queryset = Task.objects.filter(user=self.request.user)
    status = self.request.query_params.get('status', None)
    priority = self.request.query_params.get('priority', None)
    due_date = self.request.query_params.get('due_date', None)
    category = self.request.query_params.get('category', None)
    sort_by = self.request.query_params.get('sort_by', None)

    if status:
      queryset = queryset.filter(status__iexact=status)

    if priority:
      queryset = queryset.filter(priority__iexact=priority)

    if due_date:
      queryset = queryset.filter(due_date__exact=due_date)

    if category:
      queryset = queryset.filter(category__iexact=category)

    if sort_by in ['due_date', 'created_at']:
      queryset = queryset.order_by(sort_by)
   
    return queryset


  def perform_create(self, serializer):
    category = self.request.data.get('category')
    task = serializer.save(user=self.request.user, category=category)
    self.send_task_created_email(task)

    if task.status == 'Completed':
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

    if instance.status == 'Completed' and not instance.completed_at:
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
      raise NotFound({'error':'Task not found'})

  def destroy(self, request, *args, **kwargs):
    instance = self.get_object()
    self.perform_destroy(instance)
    return Response(
      {
      'message': 'Task deleted successfully'
      },
      status=status.HTTP_200_OK
    )
