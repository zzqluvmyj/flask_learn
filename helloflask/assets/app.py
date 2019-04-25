from flask import Flask, render_template
from flask_assets import Environment, Bundle
from flask_ckeditor import CKEditor

app = Flask(__name__)

app.secret_key = "secret key"

#  消除jinja模板中的空格
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

assert=Environment(app)
ckeditor=CKEditor(app)

css=Bundle()
