import click
from flask import Flask

app=Flask(__name__)


@app.route('/')
def index():
    return 'hello world'

@app.route('/hi')
@app.route('/hello')
def say_hello():
    return 'hello, Flask'

@app.route('/greet',defaults={'name':'Programmer'})
@app.route('/greet/<name>')
def greet(name):
    return 'hello, %s' % name

@app.cli.command()
def hello():
    click.echo('hello ,human!')