import os

from flask import (
    Flask,
    abort,
    jsonify,
    make_response,
    redirect,
    request,
    session,
    url_for,
)
from jinja2 import escape
from jinja2.utils import generate_lorem_ipsum

try:
    from urlparse import urlparse, urljoin
except ImportError:
    from urllib.parse import urlparse, urljoin


app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "secret string")


@app.route("/")
@app.route("/hello")
def hello():
    name = request.args.get("name")
    if name is None:
        name = request.cookies.get("name", "Human")
    response = "hello,%s" % escape(name)
    if "logged_in" in session:
        response += "[Authenticated]"
    else:
        response += "[not Authenticated]"
    return response


@app.route("/hi")
def hi():
    return redirect(url_for("hello"))


@app.route("/goback/<int:year>")
def go_back(year):
    return "Welcome to %d" % (2018 - year)


@app.route("/colors/<any(blue,white,red):color>")
def three_colors(color):
    return "love is %s" % color


@app.route("/brew/<drink>")
def teapot(drink):
    if drink == "coffee":
        abort(418)
    else:
        return "a drop of tea"


@app.route("/404")
def not_found():
    abort(404)


@app.route("/note", defaults={"content_type": "text"})
@app.route("/note/<content_type>")
def note(content_type):
    content_type = content_type.lower()
    if content_type == "text":
        body = "gsgsgsgsg"
        response = make_response(body)
        response.mimetype = "text/plain"
    elif content_type == "html":
        body = """
        <h1>gsgsgsg</h1>
        """
        response = make_response(body)
        response.mimetype = "text/html"
    elif content_type == "xml":
        body = """<?xml version="1.0" encoding="UTF-8"?>
<note>
  <to>Peter</to>
  <from>Jane</from>
  <heading>Reminder</heading>
  <body>Don't forget the party!</body>
</note>
"""
        response = make_response(body)
        response.mimetype = "application/xml"
    elif content_type == "json":
        body = {
            "note": {
                "to": "Peter",
                "from": "Jane",
                "heading": "Remider",
                "body": "Don't forget the party!",
            }
        }
        response = jsonify(body)
    else:
        abort(400)
    return response


@app.route("/set/<name>")
def set_cookie(name):
    response = make_response(redirect(url_for("hello")))
    response.set_cookie("name", name)
    return response


@app.route("/login")
def login():
    session["logged_in"] = True
    return redirect(url_for("hello"))


@app.route("/admin")
def admin():
    if "logged_in" not in session:
        abort(403)  #   没有权限
    return "welcome to admin page"


@app.route("/logout")
def logout():
    if "logged_in" in session:
        session.pop("logged_in")
    return redirect(url_for("hello"))


@app.route("/post")
def show_post():
    post_body = generate_lorem_ipsum(n=2)
    return (
        """
<h1>A very long post</h1>
<div class="body">%s</div>
<button id="load">Load More</button>
<script src="https://code.jquery.com/jquery-3.3.1.min.js"></script>
<script type="text/javascript">
$(function() {
    $('#load').click(function() {
        $.ajax({
            url: '/more',
            type: 'get',
            success: function(data){
                $('.body').append(data);
            }
        })
    })
})
</script>"""
        % post_body
    )


@app.route("/more")
def load_post():
    return generate_lorem_ipsum(n=1)  # 生成一行随机文本


# 重定向到上一个页面
@app.route("/foo")
def foo():
    return '<h1>Foo page</h1><a href="%s">Do something and redirect</a>' % url_for(
        "do_something", next=request.full_path
    )


@app.route("/bar")
def bar():
    return '<h1>Bar page</h1><a href="%s">Do something and redirect</a>' % url_for(
        "do_something", next=request.full_path
    )


@app.route("/do-something")
def do_something():
    return redirect_back()


def is_safe_url(target):
    #  urlparse将url分解为元组
    #  netloc是服务器网址
    #  urljoin拼接网址
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ("http", "https") and ref_url.netloc == test_url.netloc


def redirect_back(default="hello", **kwargs):
    #  一般来说浏览器会发送我是哪里来的链接,也就是referrer,但也有可能不发送
    for target in request.args.get("next"), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return redirect(target)
    return redirect(url_for(default, **kwargs))


