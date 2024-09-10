from flask import Flask, render_template, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash

# creating a flask instance (website)

app = Flask(__name__)

# add database
# old sqlite database
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
# new mysql database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password123@localhost/our_users'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# every app needs this
app.config['SECRET_KEY'] = "my secret key"

# initialize database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# create a blog post model
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    author = db.Column(db.String(255))
    date_posted = db.Column(db.Datetime, default=datetime.utcnow)
    slug = db.Column(db.String(255))

# create a model for database
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)
    favorite_color = db.Column(db.String(120))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    # Password stuff
    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute!')

    @password.setter
    def password(self,password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # create a string
    def __repr__(self):
        return '<Name %r>' % self.name
    
# fixed the 'working outside of app' error
with app.app_context():     
    db.create_all()

@app.route('/delete/<int:id>')
def delete(id):
    user_to_delete = Users.query.get_or_404(id)
    name = None
    form = UserForm()

    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User Deleted Successfully!!")
        our_users = Users.query.order_by(Users.date_added)
        return render_template("add_user.html", form=form, name=name, our_users=our_users)
    except:
        flash("Whoops! There was an error deleting. Please try again!")
        return render_template("add_user.html", form=form, name=name, our_users=our_users)

# creating user form class
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    favorite_color = StringField("Favorite Color")
    password_hash = PasswordField('Password', validators=[DataRequired(), EqualTo('password_hash2', message='Passwords Must Match')])
    password_hash2 = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField("Submit")

# update db
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favorite_color = request.form['favorite_color']
        try:
            db.session.commit()
            flash("User Updated Successfuly!!")
            return render_template("update.html", form=form, name_to_update=name_to_update)
        except:
            flash("User NOT Updated Successfully :(")
            return render_template("update.html", form=form, name_to_update=name_to_update)
    else:
        return render_template("update.html", form=form, name_to_update=name_to_update, id=id)

class PasswordForm(FlaskForm):
    email = StringField("What's your email", validators=[DataRequired()])
    password_hash = PasswordField("What's your Password", validators=[DataRequired()])
    submit = SubmitField("Submit")

# creating form class
class NamerForm(FlaskForm):
    name = StringField("What's your name", validators=[DataRequired()])
    submit = SubmitField("Submit")

@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            # hashing password just next line
            hashed_pw = generate_password_hash(form.password_hash.data, "pbkdf2")
            user = Users(name=form.name.data, email=form.email.data, favorite_color=form.favorite_color.data, password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.email.data = ''
        form.favorite_color.data = ''
        form.password_hash = ''
        flash("User Added Successfully")
    our_users = Users.query.order_by(Users.date_added)
    return render_template("add_user.html", form=form, name=name, our_users=our_users)

# creating a route (decorator)
@app.route('/')
def index():
    first_name = "Chris"
    stuff = "This is <strong>Bold</strong> Text"
    
    return render_template("index.html", first_name=first_name, stuff=stuff)

@app.route('/user/<name>')
def user(name):
    return render_template("user.html", name=name)

# creating custom error pages
# invalid page
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

# internal server error
@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500

#creating password test page
@app.route('/test_pw', methods=['GET', 'POST'])
def test_pw():
    email = None
    password = None
    pw_to_check = None
    passed = None
    form = PasswordForm()

    #validate form
    if form.validate_on_submit():
        email = form.email.data
        password = form.password_hash.data

        form.email.data = ''
        form.password_hash.data = ''
        
        #looking up user by email in db
        pw_to_check = Users.query.filter_by(email=email).first()

        #check hash pass
        passed = check_password_hash(pw_to_check.password_hash, password)

    return render_template("test_pw.html", email=email, password=password, pw_to_check=pw_to_check, passed=passed, form=form)

#creating name page
@app.route('/name', methods=['GET', 'POST'])
def name():
    name = None
    form = NamerForm()
    #validate form
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash("Form Submitted Successfully")
    return render_template("name.html", name=name, form=form)



if (__name__) == '__main__':
    app.run(debug=True)