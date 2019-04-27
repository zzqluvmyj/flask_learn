'''
flask表单相关操作
'''

import os
import uuid # 生成不重复的随机数

from flask import Flask,render_template,flash,redirect,url_for,request,send_from_directory,session
from flask_ckeditor import CKEditor,upload_success,upload_fail
from flask_dropzone import Dropzone#  拖拽上传文件
from flask_wtf.csrf import validate_csrf,CSRFProtect,CSRFError,generate_csrf
from wtforms import ValidationError

from forms import LoginForm,FortyTwoForm,NewPostForm,UploadForm,MultiUploadForm,SigninForm,RegisterForm,SigninForm2,RegisterForm2,RichTextForm

app=Flask(__name__)
app.secret_key=os.getenv('SECRET_KEY','secret string')
app.jinja_env.trim_blocks=True
app.jinja_env.lstrip_blocks=True

app.config['UPLOAD_PATH']=os.path.join(app.root_path,'uploads')
app.config['ALLOWED_EXTENSIONS']=['png','jpg','jpeg','gif']
app.config['MAX_CONTENT_LENGTH'] = 3 * 1024 * 1024  # 3Mb

# flask-ckeditor config
app.config['CKEDITOR_SERVE_LOCAL']=True
app.config['CKEDITOR_FILE_UPLOADER']='upload_for_ckeditor'

# flask-Dropzone config
app.config['DROPZONE_ALLOWED_FILE_TYPE']='image'
app.config['DROPZONE_MAX_FILE_SIZE']=3
app.config['DROPZONE_MAX_FILES']=30
# app.config['DROPZONE_ENABLE_CSRF']=True

ckeditor=CKEditor(app)
dropzone=Dropzone(app)
csrf=CSRFProtect(app)# 在图片上传时使用csrf

# 处理csrf错误,此处主要是dropzone使用
@app.errorhandler(CSRFError)
def csrf_error(e):
    return e.description, 400

@app.route('/',methods=['GET','POST'])
def index():
    return render_template('index.html')

# @app.after_request
# def after_request(response):
#     # 通过generate_csrf()生成csrf_token的值
#     csrf_token = generate_csrf()
#     # 设置到cookie中
#     response.set_cookie("csrf_token", csrf_token)
#     return response


#  注意,此处没有将form传入模板中,网页中的模板完全由网页代码渲染
#  此时没有数据验证,也没有csrf验证
@app.route('/html',methods=['GET','POST'])
def html():
    #  form=LoginForm()
    #  此处其实不用生命form,因为form是在html中编写的,不是由flask的form自动生成的,但是在作者的代码中加了这个,个人觉得不合理
    #  但是之后我配置了csrf保护,所以原代码中没有csrf造成了错误,既然如此,我就手动传个csrf,具体见pure_html.html
    #  但是手动传的报错,好吧,我只能百度了,搜到了generate_csrf()
    #  好吧,这对我来说有些过于复杂了
    #  但是我还是要啃下来
    #  如果每个函数都生成csrf并且传递,会很复杂,所以用钩子函数.....具体见https://zhyannan.gitee.io/zyannan.blog/2017/08/09/2017-8-9-Flask-csrf-token/
    #  好吧,应该他是在研究源码,要想完成我的功能,我只需要在其中加入csrf_token()即可,如果传入了form,则需要form.csrf_token
    if request.method=='POST':
        username=request.form.get('username')
        flash('Welcome home,%s' % username)
        return redirect(url_for('index'))
    return render_template('pure_html.html')

@app.route('/basic',methods=['GET','POST'])
def basic():
    form=LoginForm()
    if form.validate_on_submit():#  如果是post请求,并且通过了form的验证
        username=form.username.data
        flash('Welcome home,%s' % username)
        return redirect(url_for('index'))
    return render_template('basic.html',form=form)

@app.route('/bootstrap',methods=['GET','POST'])
def bootstrap():
    form = LoginForm()
    if form.validate_on_submit():
        username=form.username.data
        flash('Welcome home,%s' % username)
        return redirect(url_for('index'))
    return render_template('bootstrap.html',form=form)

@app.route('/custom-validator',methods=['GET','POST'])
def custom_validator():
    form=FortyTwoForm()
    if form.validate_on_submit():
        flash('bingo!')
        return redirect(url_for('index'))
    return render_template('custom_validator.html',form=form)



@app.route('/uploaded-images')
def show_images():
    return render_template('uploaded.html')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def random_filename(filename):
    ext=os.path.splitext(filename)[1]#  后缀名
    new_filename=uuid.uuid4().hex+ext#  hex是32表示,uuid4()是随机数
    return new_filename

@app.route('/upload',methods=['GET','POST'])
def upload():
    form=UploadForm()
    if form.validate_on_submit():
        f=form.photo.data
        filename=random_filename(f.filename)
        f.save(os.path.join(app.config['UPLOAD_PATH'],filename))
        flash('upload success.')
        session['filenames']=[filename]
        return redirect(url_for('show_images'))
    return render_template('upload.html',form=form)

@app.route('/multi-upload',methods=['GET','POST'])
def multi_upload():
    form = MultiUploadForm()

    if request.method=='POST':
        filenames=[]
    # 手动验证csrf
        try:
            validate_csrf(form.csrf_token.data)
        except ValidationError:
            flash('CSRF token error.')
            return redirect(url_for('multi_upload'))
    
    # 相当于FileRequired()验证器
        if 'photo' not in request.files:
            flash('This field is required.')
            return redirect(url_for('multi_upload'))

        for f in request.files.getlist('photo'):
            if f and allowed_file(f.filename):# 相当于FileAllowed()验证器
                filename=random_filename(f.filename)
                f.save(os.path.join(app.config['UPLOAD_PATH'],filename))
                filenames.append(filename)
            else:
                flash('invalid file type')
                return redirect(url_for('multi_upload'))
        flash('upload success')
        session['filenames']=filenames
        return redirect(url_for('show_images'))
    return render_template('upload.html',form=form)


@app.route('/dropzone-upload',methods=['GET','POST'])
def dropzone_upload():
    #  使用此时,无法进行自动化的验证,所有此处手动验证了post,是否上传了文件,是否是允许的文件名
    #  配置了dropzone的csrf后,此处应该不再需要手动验证csrf
    if request.method=='POST':
        if 'file' not in request.files:
            return 'This field is required',400
        f=request.files.get('file')

        if f and allowed_file(f.filename):
            filename=random_filename(f.filename)
            f.save(os.path.join(app.config['UPLOAD_PATH'],filename))
        else:
            return 'Invalid file type',400
    return render_template('dropzone.html')

@app.route('/two-submits',methods=['GET','POST'])
def two_submits():
    form=NewPostForm()
    if form.validate_on_submit():
        if form.save.data:
            flash('you click the save button')
        elif form.publish.data:
            flash('you click the publish button')
        return redirect(url_for('index'))
    return render_template('2submit.html',form=form)

@app.route('/multi-form',methods=['GET','POST'])
def multi_form():
    signin_form=SigninForm()
    register_form=RegisterForm()

    if signin_form.submit1.data and signin_form.validate():
        username=signin_form.username.data
        flash('%s,you just submit the signin form.' % username)
        return redirect(url_for('index'))
    
    if register_form.submit2.data and register_form.validate():
        username=register_form.username.data
        flash('%s,you just submit the register form.' % username)
        return redirect(url_for('index'))

    return render_template('2form.html',signin_form=signin_form,register_form=register_form)

# form请求由其他视图函数,而不是该函数
@app.route('/multi-form-multi-view')
def multi_form_multi_view():
    signin_form=SigninForm2()
    register_form=RegisterForm2()
    return render_template('2form2view.html',signin_form=signin_form,register_form=register_form)

@app.route('/handle-signin',methods=['POST'])
def handle_signin():
    signin_form=SigninForm2()
    register_form=RegisterForm2()

    if signin_form.validate_on_submit():
        username=signin_form.username.data
        flash('%s,you just submit the signin form.' % username)
        return redirect(url_for('index'))

    return render_template('2form2view.html',signin_form=signin_form,register_form=register_form)

@app.route('/handle-register',methods=['POST'])
def handle_register():
    signin_form=SigninForm2()
    register_form=RegisterForm2()
    
    if register_form.validate_on_submit():
        username=register_form.username.data
        flash('%s,you just submit the register form' % username)
        return redirect(url_for('index'))
    return render_template('2form2view.html',signin_form=signin_form,register_form=register_form)


@app.route('/uploads/<path:filename>')
def get_file(filename):
    return send_from_directory(app.config['UPLOAD_PATH'], filename)

@app.route('/ckeditor', methods=['GET', 'POST'])
def integrate_ckeditor():
    form = RichTextForm()
    if form.validate_on_submit():
        title = form.title.data
        body = form.body.data
        flash('Your post is published!')
        return render_template('post.html', title=title, body=body)
    return render_template('ckeditor.html', form=form)


# handle image upload for ckeditor
@app.route('/upload-ck', methods=['POST','GET'])
def upload_for_ckeditor():
    f = request.files.get('upload')
    if not allowed_file(f.filename):
        return upload_fail('Image only!')
    f.save(os.path.join(app.config['UPLOAD_PATH'], f.filename))
    url = url_for('get_file', filename=f.filename)
    return upload_success(url)