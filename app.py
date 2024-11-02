#To run:  flask --app app run
# pip install Flask-Mail
# pip install celery
# database model - pip install flask-sqlalchemy
# pip install flask-login
# pip install Flask-Migrate

#install these pkges
#pip show werkzeug
# sudo apt-get install redis-server
# start: redis-server
# Run Celery Workers
# Start the worker:
#     celery -A app.celery worker --loglevel=info

# Start the beat scheduler:
#     celery -A app.celery beat --loglevel=info


from flask_mail import Mail, Message
from celery import Celery
from celery.schedules import crontab
from datetime import datetime, timedelta
from flask import flash, redirect, url_for
from flask import Flask, redirect, render_template, request , url_for , flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, UserMixin, current_user, logout_user, login_required # type: ignore
from werkzeug.security import generate_password_hash, check_password_hash


def make_celery(app):
    celery = Celery(app.import_name, backend=app.config['CELERY_RESULT_BACKEND'],  broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    return celery

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///todo.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '12345678mysecretkey' #for session cookie

#celery config
app.config['CELERY_BROKER_URL'] = 'redis://localhost:8000/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:8000/0'
celery = make_celery(app)
 
db = SQLAlchemy(app)

#config mail
app.config['MAIL_SERVER'] = 'smtp.example.com'  # Update with your mail server
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'test4dopamine@gmail.com'
app.config['MAIL_PASSWORD'] = 'qwerty@UIOP123456'
mail = Mail(app)

login_manager = LoginManager(app)
#redirect user who are not authenticated
login_manager.login_view = 'login_signup'


if current_user and current_user.is_authenticated:
    user_email = current_user.email
else:
    user_email = None
#creating user table
class User(db.Model, UserMixin):
    id =db.Column(db.Integer, primary_key=True)
    email= db.Column(db.String(100), nullable=False, unique=True)
    password= db.Column(db.String(150), nullable=False)
    user_name = db.Column(db.String(100), nullable=False)
    
class shareTodo(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    desc = db.Column(db.String(500), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    user_email = db.Column(db.String(100), nullable=False)
    due_date = db.Column(db.DateTime)
    priority = db.Column(db.String(10), nullable=False, default='Medium') #others are : High, Low
    tags = db.Column(db.String(200)) #for user help 
    shareWith = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(100),nullable=False, default='Active')   
    def __repr__(self) -> str:
        return f"Task('{self.title}', '{self.desc}', '{self.date_created}', '{self.user_email}', '{self.due_date}', '{self.priority}', '{self.tags}')"
    

#creating todo table
class Todo(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    desc = db.Column(db.String(500), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    user_email = db.Column(db.String(100), nullable=False)
    due_date = db.Column(db.DateTime)
    priority = db.Column(db.String(10), nullable=False, default='Medium') #others are : High, Low
    tags = db.Column(db.String(200)) #for user help    
    def __repr__(self) -> str:
        return f"Task('{self.title}', '{self.desc}', '{self.date_created}', '{self.user_email}', '{self.due_date}', '{self.priority}', '{self.tags}')"
    
# class RegisterForm(FlaskForm):
#     username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
#     password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})
#     submit = SubmitField("Register")
    
#     def validate_username(self, username):
#         user = User.query.filter_by(username=username.data).first()
#         if user:
#             raise ValidationError('Username is already taken')
        

# class LoginrForm(FlaskForm):
#     username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
#     password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})
#     submit = SubmitField("Login")


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Schedule the task to run every hour
    sender.add_periodic_task(crontab(minute=0, hour='1'), send_reminder.s())

@celery.task
def send_reminder():
    now = datetime.utcnow()
    soon_due = now + timedelta(days=1)
    
    todos = Todo.query.filter(
        Todo.due_date.between(now, soon_due),
        Todo.user_email == current_user.email
    ).all()
    
    for todo in todos:
        msg = Message(subject="Task Reminder",
                      sender='test4dopamine@gmail.com',
                      recipients=[current_user.email])
        msg.body = f"Reminder: Your task '{todo.title}' is due on {todo.due_date.strftime('%Y-%m-%d %H:%M')}."
        mail.send(msg)
        # Logic to send notification (e.g., send email or in-app alert)
        print(f"Reminder: Your task '{todo.title}' is due on {todo.due_date.strftime('%Y-%m-%d %H:%M')}.")

        # Here you could implement email sending logic using Flask-Mail or other methods

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#this celery part is taken completely from gpt
# Home route
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login-signup', methods=['GET', 'POST'])
def login_signup():
    if request.method == 'POST':
        if 'name' in request.form:
            name = request.form['name']
            email = request.form['email']
            password = request.form['password']
            password = generate_password_hash(request.form['password'], method='pbkdf2:sha256')
            print(f"Signup Name: {name}, Email: {email}")
            if User.query.filter_by(email=email).first():
                flash("Email already registered. Please use another email.", "danger")
            else:
                new_user = User(email=email, password=password, user_name=name)
                db.session.add(new_user)
                
                try:
                    db.session.commit() 
                    login_user(new_user)
                    flash("Account created successfully...", 'success')
                    return redirect(url_for('dashboard'))
                except Exception as e:
                    db.session.rollback() #for errros
                    flash(f"An error occurred: {str(e)}", 'danger')
                    print(f"Error occurred: {e}") 
        elif 'email' in request.form and 'password' in request.form:
            email = request.form['email']
            password = request.form['password']
            print(f"Email: {email}, Password: {password}")
            user = User.query.filter_by(email=email).first()
            if user and check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('dashboard'))  
            else:
                flash('Invalid credentials', 'danger')
        

    return render_template('login_signup.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been successfully logged out.", "info")
    return redirect(url_for('home'))



@app.route('/list', methods=['GET', 'POST'])
@login_required
def dashboard():
    
    #getting search args
    priority_filter = request.args.get('priority', default='All', type=str)
    tag_filter = request.args.get('tag', default='', type=str)
    search_query = request.args.get('search', default='', type=str)
    #debugging
    # print(f"Priority Filter: {priority_filter}")
    # print(f"Tag Filter: {tag_filter}")

    query = Todo.query.filter_by(user_email=current_user.email)

    if priority_filter != 'All':
        print(f"Applying priority filter: {priority_filter}")
        query = query.filter_by(priority=priority_filter)

    if tag_filter:
        print(f"Applying tag filter: {tag_filter}")
        query = query.filter(Todo.tags.like(f'%{tag_filter}%'))
    
    if search_query:
        print(f"Applying search query: {search_query}")
        #ilike is case insensitive
        query = query.filter(
            (Todo.title.ilike(f'%{search_query}%')) | 
            (Todo.desc.ilike(f'%{search_query}%'))
        )
    allTodo = query.all()

    if request.method == 'POST':
        title = request.form['title']
        desc = request.form['desc'] 
        due_date = request.form['due_date'] 
        priority = request.form['priority']
        tags = request.form['tags']   

        if due_date:  # Ensure due_date is not empty
            todo = Todo(
                title=title,
                desc=desc,
                due_date=datetime.strptime(due_date, "%Y-%m-%dT%H:%M"), 
                priority=priority, 
                tags=tags,
                user_email=current_user.email
            )
        else:
            todo = Todo(
                title=title,
                desc=desc,
                due_date=None,  # set a default date
                priority=priority, 
                tags=tags,
                user_email=current_user.email
            )


        db.session.add(todo)
        db.session.commit()
        
        flash("Todo added successfully", "success")
        return redirect(url_for('dashboard')) 

    return render_template('index.html', allTodo=allTodo, priority_filter=priority_filter, tag_filter=tag_filter)

@app.route('/shared/todo', methods=['GET', 'POST'])
@login_required
def shared_todo():
    #getting search args
    priority_filter = request.args.get('priority', default='All', type=str)
    tag_filter = request.args.get('tag', default='', type=str)
    search_query = request.args.get('search', default='', type=str)
    #debugging
    # print(f"Priority Filter: {priority_filter}")
    # print(f"Tag Filter: {tag_filter}")

    query = shareTodo.query.filter_by(shareWith=current_user.email)

    if priority_filter != 'All':
        print(f"Applying priority filter: {priority_filter}")
        query = query.filter_by(priority=priority_filter)

    if tag_filter:
        print(f"Applying tag filter: {tag_filter}")
        query = query.filter(Todo.tags.like(f'%{tag_filter}%'))
    
    if search_query:
        print(f"Applying search query: {search_query}")
        #ilike is case insensitive
        query = query.filter(
            (shareTodo.title.ilike(f'%{search_query}%')) | 
            (shareTodo.desc.ilike(f'%{search_query}%'))
        )
    allTodo = query.all()

    if request.method == 'POST':
        title = request.form['title']
        desc = request.form['desc'] 
        due_date = request.form['due_date'] 
        priority = request.form['priority']
        tags = request.form['tags'] 
        shareWith = request.form['shared_with']  

        if due_date:  # Ensure due_date is not empty
            sharetodo = shareTodo(
                title=title,
                desc=desc,
                due_date=datetime.strptime(due_date, "%Y-%m-%dT%H:%M"), 
                priority=priority, 
                tags=tags,
                shareWith = shareWith,
                user_email=current_user.email
            )
        else:
            sharetodo = shareTodo(
                title=title,
                desc=desc,
                due_date=None,  # set a default date
                priority=priority, 
                tags=tags,
                shareWith = shareWith,
                user_email=current_user.email
            )


        db.session.add(sharetodo)
        db.session.commit()
        
        flash("Todo Shared successfully", "success")
        return redirect(url_for('shared_todo')) 

    return render_template('shareTodo.html', allTodo=allTodo, priority_filter=priority_filter, tag_filter=tag_filter)

@app.route('/view/shared/todo')
@login_required
def view_shared_todo():
    #getting search args
    priority_filter = request.args.get('priority', default='All', type=str)
    tag_filter = request.args.get('tag', default='', type=str)
    search_query = request.args.get('search', default='', type=str)
    #debugging
    # print(f"Priority Filter: {priority_filter}")
    # print(f"Tag Filter: {tag_filter}")

    query = shareTodo.query.filter_by(user_email=current_user.email)

    if priority_filter != 'All':
        print(f"Applying priority filter: {priority_filter}")
        query = query.filter_by(priority=priority_filter)

    if tag_filter:
        print(f"Applying tag filter: {tag_filter}")
        query = query.filter(Todo.tags.like(f'%{tag_filter}%'))
    
    if search_query:
        print(f"Applying search query: {search_query}")
        #ilike is case insensitive
        query = query.filter(
            (shareTodo.title.ilike(f'%{search_query}%')) | 
            (shareTodo.desc.ilike(f'%{search_query}%'))
        )
    allTodo = query.all()

    return render_template('viewshareTodo.html', allTodo=allTodo)


# @app.route('/create-db')
# def create_db():
#     with app.app_context():
#         db.create_all()
#     return "Database created successfully!"

@app.route('/show')
def commits():
    allTodo = Todo.query.filter_by(user_email=current_user.email).all()
    print(allTodo)
    return render_template(allTodo=allTodo)

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = Todo.query.filter_by(sno=id).first()
    
    if request.method == 'POST':
        title = request.form['title']
        desc = request.form['desc']
        due_date_str = request.form['due_date']  # due date in string here
        priority = request.form['priority']
        tags = request.form['tags']
        task.title = title
        task.desc = desc
        
        # Converting the due_date to datetime object
        try:
            task.due_date = datetime.strptime(due_date_str, "%Y-%m-%dT%H:%M") if due_date_str else None
        except ValueError as e:
            flash("Invalid date format. Please use YYYY-MM-DDTHH:MM.", "danger")
            return render_template('update.html', task=task)

        task.priority = priority
        task.tags = tags
        
        
        db.session.commit()
        flash("Todo updated successfully", "success")
        return redirect("/list")
    
    return render_template('update.html', task=task)
    
    
@app.route('/updateShareTodo/<int:id>', methods=['GET', 'POST'])
def updateShareTodo(id):
    task = shareTodo.query.filter_by(sno=id).first()
    
    if request.method == 'POST':
        title = request.form['title']
        desc = request.form['desc']
        due_date_str = request.form['due_date']  # due date in string here
        priority = request.form['priority']
        tags = request.form['tags']
        shareWith = request.form['shared_with']
        task.title = title
        task.desc = desc
        task.shareWith = shareWith
        # Converting the due_date to datetime object
        try:
            task.due_date = datetime.strptime(due_date_str, "%Y-%m-%dT%H:%M") if due_date_str else None
        except ValueError as e:
            flash("Invalid date format. Please use YYYY-MM-DDTHH:MM.", "danger")
            return render_template('updateShareTodo.html', task=task)
        
        task.priority = priority
        task.tags = tags
        db.session.commit()
        flash("Todo updated successfully", "success")
        return redirect('/view/shared/todo')
    
    return render_template('updateShareTodo.html', task=task)

@app.route('/completeShareTodo/<int:id>')
def completeShareTodo(id):
    task = shareTodo.query.filter_by(sno=id).first()
    task.status = "Completed"
    db.session.commit()
    flash("Todo Completed successfully", "success")
    return redirect("/shared/todo")

@app.route('/stillgoingShareTodo/<int:id>')
def stillgoingShareTodo(id):
    task = shareTodo.query.filter_by(sno=id).first()
    task.status = "Active"
    db.session.commit()
    flash("Todo Activated again", "warning")
    return redirect("/shared/todo")


#todo delete
@app.route('/delete/<int:id>')
def delete(id):
    task = Todo.query.filter_by(sno=id).first()
    db.session.delete(task)
    db.session.commit()
    return redirect("/list")

@app.route('/share/delete/<int:id>')
def delete_shareTodo(id):
    task = shareTodo.query.filter_by(sno=id).first()
    db.session.delete(task)
    db.session.commit()
    flash("Shared Todo deleted successfully", "danger")
    return redirect("/view/shared/todo")

# @app.route('/login-signup')
# def login_signup():
#     return render_template('login_signup.html')

if __name__ == '__main__':
    app.run(debug=True)
