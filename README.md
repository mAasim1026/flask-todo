
# Flask Todo App with Task Reminders

This is a simple yet powerful Todo application built using Flask and SQLAlchemy, designed to help users manage their tasks efficiently. The app includes essential features such as task categorization, priority setting, tagging, and a search functionality to filter tasks based on keywords. Additionally, task reminders are implemented using Celery, allowing users to receive timely notifications via email or in-app alerts.

## Features

### 1. User Authentication
- **Signup and Login**: Secure user registration and login.
- **Password Hashing**: Passwords are stored securely with hashing.

### 2. Task Management
- **Create, Update, and Delete Tasks**: Users can manage their tasks, providing titles, descriptions, due dates, priorities, and tags.
- **Task Categorization**:
  - **Priority Levels**: Assign tasks as High, Medium, or Low priority.
  - **Tags**: Organize tasks with tags for easier filtering.
  - **Due Date**: Set due dates for timely reminders and organization.

### 3. Task Sharing
- **Share Tasks**: Share tasks with other users, allowing collaboration.

### 4. Filtering and Search
- **Search Tasks**: Search by keywords in task titles or descriptions.
- **Filter by Priority and Tags**: Quickly filter tasks based on priority or tags.

### 5. Task Reminders and Notifications
- **Automated Reminders**: Background jobs using Celery send notifications for tasks due within 24 hours.
- **Email and In-App Alerts**: Receive reminders via email to stay updated on upcoming tasks.

## Project Setup

### Prerequisites
- Python 3.x
- Flask
- Redis (for Celery message brokering)
- SQLite (or another database if preferred)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/mAasim1026/flask-todo-app.git
   cd flask-todo-app
   ```

2. **Create a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Redis** (as the message broker for Celery):
   - For Ubuntu:
     ```bash
     sudo apt-get install redis-server
     ```
   - Start Redis:
     ```bash
     redis-server
     ```

5. **Database Initialization**:
   - Create the initial database tables:
     ```bash
     flask db init
     flask db migrate
     flask db upgrade
     ```

6. **Configure Environment Variables**:
   - Set up environment variables in a `.env` file:
     ```plaintext
     FLASK_APP=app.py
     FLASK_ENV=development
     CELERY_BROKER_URL=redis://localhost:6379/0
     CELERY_RESULT_BACKEND=redis://localhost:6379/0
     MAIL_SERVER=smtp.example.com
     MAIL_PORT=587
     MAIL_USE_TLS=True
     MAIL_USERNAME=your_email@example.com
     MAIL_PASSWORD=your_password
     ```

### Running the App

1. **Run the Flask app**:
   ```bash
   flask run
   ```

2. **Start the Celery worker**:
   ```bash
   celery -A app.celery worker --loglevel=info
   ```

3. **Start the Celery Beat Scheduler** (for periodic tasks like reminders):
   ```bash
   celery -A app.celery beat --loglevel=info
   ```

### Usage

1. **Access the application**: Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your web browser.
2. **Register/Login**: Sign up or log in to your account.
3. **Add Tasks**: Use the "Add Task" form to create a new task with details like title, description, priority, tags, and due date.
4. **Filter & Search**: Filter tasks by priority, tag, or search for keywords.
5. **Set Reminders**: Tasks with due dates automatically trigger reminders 24 hours in advance.

### File Structure

- **`app.py`**: Main application file containing Flask app configuration, routes, and views.
- **`templates/`**: HTML templates for pages.
- **`static/`**: Static files such as CSS and JavaScript.
- **`models.py`**: Database models for tasks and user management.
- **`tasks.py`**: Celery tasks for background job processing.
- **`requirements.txt`**: List of dependencies.

### Technologies Used

- **Flask**: Web framework for Python.
- **SQLAlchemy**: ORM for handling database interactions.
- **Celery**: Asynchronous task queue for handling background jobs.
- **Redis**: Message broker for Celery.
- **Flask-Mail**: Extension for sending email notifications.

### Future Improvements

- **Recurring Tasks**: Add support for tasks that repeat on a schedule.
- **Mobile Notifications**: Send mobile push notifications for due reminders.
- **Task Assignment**: Allow users to assign tasks to collaborators.

### License

This project is open-source and licensed under the MIT License.
