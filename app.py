from flask import Flask, render_template, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

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

# create a model for database
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    # create a string
    def __repr__(self):
        return '<Name %r>' % self.name
    
# fixed the 'working outside of app' error
with app.app_context():     
    db.create_all()

# creating user form class
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    submit = SubmitField("Submit")

# update db
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        try:
            db.session.commit()
            flash("User Updated Successfuly!!")
            return render_template("update.html", form=form, name_to_update=name_to_update)
        except:
            flash("User NOT Updated Successfully :(")
            return render_template("update.html", form=form, name_to_update=name_to_update)
    else:
        return render_template("update.html", form=form, name_to_update=name_to_update)

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
            user = Users(name=form.name.data, email=form.email.data)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.email.data = ''
        flash("User Added Successfully")
    our_users = Users.query.order_by(Users.date_added)
    return render_template("add_user.html", form=form, name=name, our_users=our_users)

# creating a route (decorator)
@app.route('/')
def index():
    first_name = "Chris"
    stuff = "This is <strong>Bold</strong> Text"
    
    favorite_pizza = ["Pepperoni", "Cheese", "Olives", 41]
    return render_template("index.html", first_name=first_name, stuff=stuff, favorite_pizza=favorite_pizza)

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