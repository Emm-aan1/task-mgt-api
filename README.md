# Task Management API

The Task Management API is a simple task management system built using Django and Django REST Framework. This API allows users to create, update, delete, and retrieve tasks, with JWT-based authentication and email notifications for various actions like registration and password reset.

## Features

- **User Registration & Authentication**: Secure user registration and JWT-based authentication (login/logout).
- **Task Management**: Create, update, delete, and view tasks.
- **Task Filtering**: Filter tasks by priority, status, due date, and category.
- **Password Reset**: Request and reset passwords via email.
- **Email Notifications**: Users receive email notifications on account creation, task creation, task completion, and password reset.
- **Token Blacklisting**: Secure logout functionality with token blacklisting to prevent reuse of invalid tokens.

## Technology Stack

- **Backend**: Django 5.1.1, Django REST Framework
- **Database**: SQLite (default)
- **Authentication**: JWT (JSON Web Tokens)
- **Email**: Gmail SMTP (or other email backends)

## Installation and Setup

### Prerequisites

- Python 3.8+
- SQLite (included with Django)
- Gmail account or another SMTP server for sending emails

### Steps to Run Locally

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/task_management_project.git
   cd task_management_project
   ```

2. **Create a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # For Linux/Mac
   venv\Scripts\activate  # For Windows
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**:
   Create a `.env` file in the project root and add your email configuration:
   ```bash
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-email-password
   ```

5. **Run Database Migrations**:
   ```bash
   python manage.py migrate
   ```

6. **Create a Superuser** (for admin access):
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the Development Server**:
   ```bash
   python manage.py runserver
   ```

   The API will be accessible at `http://127.0.0.1:8000/`.

## API Endpoints

### Authentication

- **User Registration**:  
  `POST /api/register/`  
  Allows users to register.

- **Login**:  
  `POST /api/login/`  
  JWT-based login to obtain access and refresh tokens.

- **Logout**:  
  `POST /api/logout/`  
  Logs the user out and blacklists the token.

### Task Management

- **List and Create Tasks**:  
  `GET /api/tasks/`  
  `POST /api/tasks/`  
  Fetch all tasks (for the authenticated user) or create a new task.

- **Retrieve, Update, or Delete a Task**:  
  `GET /api/tasks/<task_id>/`  
  `PUT /api/tasks/<task_id>/`  
  `DELETE /api/tasks/<task_id>/`  
  Fetch, update, or delete a specific task by ID.

- **Task Filtering**:  
  Tasks can be filtered by `status`, `priority`, `due_date`, and `category` using query parameters:
  ```
  /api/tasks/?status=Pending&priority=High
  ```

### Password Management

- **Request Password Reset**:  
  `POST /api/password-reset/`  
  Sends an email with the password reset link.

- **Confirm Password Reset**:  
  `POST /api/password-reset-confirm/<uidb64>/<token>/`  
  Resets the password using the token and user ID provided via email.

## Testing

To run the tests, execute the following command:

```bash
python manage.py test
```

## Environment Variables

- **EMAIL_HOST_USER**: Your email address for sending emails (e.g., Gmail).
- **EMAIL_HOST_PASSWORD**: The password for your email account.

## Static Files

Static files are handled using WhiteNoise for production.

```bash
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

## Project Structure

```bash
.
├── tasks/                   
│   ├── migrations/          
│   ├── models.py            
│   ├── serializers.py       
│   ├── urls.py              
│   ├── views.py             
├── task_management_project/  
│   ├── settings.py          
│   ├── urls.py              
│   ├── wsgi.py             
├── manage.py                
├── requirements.txt         
├── .env                    
```


## Contact

If you have any questions or feedback, feel free to reach out.

- **Author**: Ifeanyi Chidoka
- **Email**: ik.chidoka@gmail.com

