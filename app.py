from flask import Flask, render_template

# creating a flask instance (website)
app = Flask(__name__)

# creating a route (decorator)
@app.route('/')
def index():
    return "<h1>Hello World!</h1>"

if (__name__) == '__main__':
    app.run(debug=True)