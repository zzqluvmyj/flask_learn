"""
    数据库练习
    :author:zzq
"""
import os, sys, click

from flask import Flask
from flask import redirect,url_for,abort,render_template,flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import SubmitField,TextAreaField
from wtforms.validators import DataRequired
from flask_migrate import Migrate

WIN=sys.platform.startswith('win')
if WIN:
    prefix="sqlite:///"
else:
    prefix="sqlite:////"

app = Flask(__name__)
app.jinja_env.trim_block=True
app.jinja_env.lstrip_blocks=True

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "secret string")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL", prefix + os.path.join(app.root_path, "data.db")
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db=SQLAlchemy(app)
migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
    return dict(
        db=db,
        Note=Note,
        Author=Author,
        Article=Article,
        Writer=Writer,
        Book=Book,
        Singer=Singer,
        Song=Song,
        Citizen=Citizen,
        City=City,
        Capital=Capital,
        Country=Country,
        Teacher=Teacher,
        Student=Student,
        Post=Post,
        Comment=Comment,
        Draft=Draft,
    )

@app.cli.command()
@click.option("--drop",is_flag=True,help="Create after drop.")
def initdb(drop):#  建立数据库表,不用这个,使用migrate也行
    if drop:
        db.drop_all()
    db.create_all()
    click.echo("Initialized database.")

class NewNoteForm(FlaskForm):
    body = TextAreaField("Body", validators=[DataRequired()])
    submit = SubmitField("Save")

class EditNoteForm(FlaskForm):
    body = TextAreaField("Body", validators=[DataRequired()])
    submit = SubmitField("Update")

class DeleteNoteForm(FlaskForm):
    submit = SubmitField("Delete")

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)

    # optional
    def __repr__(self):
        return "<Note %r>" % self.body

@app.route("/")
def index():
    form = DeleteNoteForm()
    notes = Note.query.all()
    return render_template("index.html", notes=notes, form=form)

@app.route("/new", methods=["GET", "POST"])
def new_note():
    form = NewNoteForm()
    if form.validate_on_submit():
        body = form.body.data
        note = Note(body=body)
        db.session.add(note)
        db.session.commit()
        flash("Your note is saved.")
        return redirect(url_for("index"))
    return render_template("new_note.html", form=form)


@app.route("/edit/<int:note_id>", methods=["GET", "POST"])
def edit_note(note_id):
    form = EditNoteForm()
    note = Note.query.get(note_id)
    if form.validate_on_submit():
        note.body = form.body.data
        db.session.commit()
        flash("Your note is updated.")
        return redirect(url_for("index"))
    form.body.data = note.body  # preset form input's value
    return render_template("edit_note.html", form=form)


@app.route("/delete/<int:note_id>", methods=["POST"])
def delete_note(note_id):
    form = DeleteNoteForm()
    if form.validate_on_submit():
        note = Note.query.get(note_id)
        db.session.delete(note)
        db.session.commit()
        flash("Your note is deleted.")
    else:
        abort(400)
    return redirect(url_for("index"))


#db.session.add(article)
#db.session.add(author)
#author.articles.append(article1)
#db.session.commit()
#多对一关系基本操作

# 常用的SQLAlchemy关系函数参数
# back_populates,建立双向关系
# backref,建立双向关系的简洁方法,可以隐式的建立双向的关系
# lazy
# userlist
# cascade
# order_by
# secondary
# primaryjoin
# secondaryjoin




class Author(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(20),unique=True)
    phone=db.Column(db.String(20))
    articles=db.relationship("Article")# 在数据库中并不存在,可以反向查找外键
    # collection集合属性

    def __repr__(self):
        return "<Author %r" % self.name
    # __repr__供机器可读,__str__供人读,在没有__str__的情况下,默认使用__repr__
    #  %r用于repr,%s用于str

class Article(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(50),index=True)
    body=db.Column(db.Text)
    author_id=db.Column(db.Integer,db.ForeignKey("author.id"))

    def __repr__(self):
        return "<Article %r>" % self.title

# 多对一
class Citizen(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(70), unique=True)
    city_id = db.Column(db.Integer, db.ForeignKey("city.id"))
    city = db.relationship("City")  # scalar,返回单个值的叫标量关系属性

    def __repr__(self):
        return "<Citizen %r>" % self.name

class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)

    def __repr__(self):
        return "<City %r>" % self.name

# one to one
class Country(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)
    capital = db.relationship("Capital", uselist=False)  # collection -> scalar,将原来的集合关系转化为标量关闭,返回单个值,在另一侧,本身就是标量关系,所以不用添加

    def __repr__(self):
        return "<Country %r>" % self.name


class Capital(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)
    country_id = db.Column(db.Integer, db.ForeignKey("country.id"))
    country = db.relationship("Country")  # scalar

    def __repr__(self):
        return "<Capital %r>" % self.name

#  多对多的关系表
association_table = db.Table(
    "association",
    db.Column("student_id", db.Integer, db.ForeignKey("student.id")),
    db.Column("teacher_id", db.Integer, db.ForeignKey("teacher.id")),
)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(70), unique=True)
    grade = db.Column(db.String(20))
    teachers = db.relationship(
        "Teacher", secondary=association_table, back_populates="students"
    )  # collection

    def __repr__(self):
        return "<Student %r>" % self.name
    
class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(70), unique=True)
    office = db.Column(db.String(20))
    students = db.relationship(
        "Student", secondary=association_table, back_populates="teachers"
    )  # collection

    def __repr__(self):
        return "<Teacher %r>" % self.name


class Writer(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(64),unique=True)
    books=db.relationship("Book",back_populates="writer")

    def __repr__(self):
        return "<Writer %r>" % self.name
    
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), index=True)
    writer_id = db.Column(db.Integer, db.ForeignKey("writer.id"))
    writer = db.relationship("Writer", back_populates="books")

    def __repr__(self):
        return "<Book %r>" % self.name

class Singer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(70), unique=True)
    songs = db.relationship("Song", backref="singer")# 这会在另一侧建立关系,隐式的

    def __repr__(self):
        return "<Singer %r>" % self.name


class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), index=True)
    singer_id = db.Column(db.Integer, db.ForeignKey("singer.id"))

    def __repr__(self):
        return "<Song %r>" % self.name

# 级联
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    body = db.Column(db.Text)
    comments = db.relationship(
        "Comment", back_populates="post", cascade="all, delete-orphan"
    )  # collection

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"))
    post = db.relationship("Post", back_populates="comments")  # scalar

#事件监听
class Draft(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    edit_time = db.Column(db.Integer, default=0)

@db.event.listens_for(Draft.body, "set")
def increment_edit_time(target, value, oldvalue, initiator):
    if target.edit_time is not None:
        target.edit_time += 1


# same with:
# @db.event.listens_for(Draft.body, 'set', named=True)
# def increment_edit_time(**kwargs):
#     if kwargs['target'].edit_time is not None:
#         kwargs['target'].edit_time += 1