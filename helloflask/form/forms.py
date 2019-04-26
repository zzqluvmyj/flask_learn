'''
表单项
'''

from flask_ckeditor import CKEditorField
from flask_wtf import FlaskForm
from flask_wtf.file import FileField,FileRequired,FileAllowed
from wtforms import StringField,PasswordField,BooleanField,IntegerField,\
    TextAreaField,SubmitField,MultipleFileField
from wtforms.validators import DataRequired,Length,ValidationError,Email


class LoginForm(FlaskForm):
    #  EqualTo()验证器
    username=StringField('用户名',validators=[DataRequired()],render_kw={'placeholder':'请输入您的名字'})
    password=PasswordField('密码',validators=[DataRequired(),Length(8,128,"最少8位,最多128位")])
    remember=BooleanField('记住我')
    submit=SubmitField('登录')

    #  能够将错写消息渲染为中文,但需要配置WTF_I18N_ENABLED为False
    #  不生效,不知道为什么
    class Meta:
        locals=['zh']

# 全局验证器示例,此时传入validators列表中的函数不要()
# def is_42(form,field):
#     if field.data!=42:
#         raise ValidationError('必须是42!')

# 工厂函数形式的全局验证器示例,此时传入validators列表中的函数需要()
def is_42(message=None):
    if message is None:
        message='必须是42'
    def _is_42(form,field):
        if field.data!=42:
            raise ValidationError(message)
    return _is_42


class FortyTwoForm(FlaskForm):
    #  answer=IntegerField('数字')

    #  自定义全局验证器的使用
    answer=IntegerField('数字',validators=[is_42()])
    submit=SubmitField()

    #  自定义行内验证器,验证单个字段,注意函数的命名
    def validate_answer(form,field):
        if field.data!=42:
            raise ValidationError('数字必须是42!')

class UploadForm(FlaskForm):
    photo=FileField('上传图片',validators=[FileRequired(),FileAllowed(['jpg','jpeg','png','gif'])])
    submit=SubmitField()

class MultiUploadForm(FlaskForm):
    photo=MultipleFileField('上传文件',validators=[DataRequired()])
    submit=SubmitField()

class NewPostForm(FlaskForm):
    title=StringField('标题',validators=[DataRequired(),Length(1,50)])
    body=TextAreaField('内容',validators=[DataRequired()])
    save=SubmitField('保存')
    publish=SubmitField('发布')

class SigninForm(FlaskForm):
    username=StringField('用户名',validators=[DataRequired(),Length(1,20)])
    password=PasswordField('密码',validators=[DataRequired(),Length(8,128)])
    submit1=SubmitField('登录')

class RegisterForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(1, 20)])
    email = StringField('邮箱', validators=[DataRequired(), Email(), Length(1, 254)])
    password = PasswordField('密码', validators=[DataRequired(), Length(8, 128)])
    submit2 = SubmitField('注册')

class SigninForm2(FlaskForm):
    username=StringField('用户名',validators=[DataRequired(),Length(1,24)])
    password=PasswordField('密码',validators=[DataRequired(),Length(8,128)])
    submit=SubmitField()

class RegisterForm2(FlaskForm):
    username=StringField('用户名',validators=[DataRequired(),Length(1,24)])
    email=StringField('邮箱',validators=[DataRequired(message="该项不能为空"),Email(message="请输入邮箱"),Length(1,254)])
    password=PasswordField('密码',validators=[DataRequired(),Length(8,128)])
    submit=SubmitField()

class RichTextForm(FlaskForm):
    title=StringField('标题',validators=[DataRequired(),Length(1,50)])
    body=CKEditorField('内容',validators=[DataRequired()])
    submit=SubmitField('发布')
