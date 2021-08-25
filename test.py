"""basic Flask app - demo of using a variable in a route"""
from flask import Flask, render_template,  request, url_for, flash, redirect


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('test.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True)