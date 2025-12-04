from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField, FileField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, NumberRange
from config import Config

# --- Custom Validators ---

def validate_file_upload(form, field):
    if field.data:
        # Simple check for allowed extensions
        allowed_extensions = ['jpg', 'jpeg', 'png', 'pdf']
        filename = field.data.filename
        if '.' not in filename or filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
            raise ValidationError('الملف غير صالح. الأنواع المسموح بها: jpg, png, pdf.')

# --- Forms ---

class LoginForm(FlaskForm):
    email = StringField('البريد الإلكتروني', validators=[DataRequired(), Email()])
    password = PasswordField('كلمة المرور', validators=[DataRequired()])
    submit = SubmitField('تسجيل الدخول')

class RegistrationForm(FlaskForm):
    full_name = StringField('الاسم الكامل', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('البريد الإلكتروني', validators=[DataRequired(), Email()])
    password = PasswordField('كلمة المرور', validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField(
        'تأكيد كلمة المرور', validators=[DataRequired(), EqualTo('password', message='كلمتا المرور غير متطابقتان')]
    )
    # Department and Job/Role fields are required by the user's instructions
    department = SelectField('القسم', choices=[
        ('IT', 'تقنية المعلومات'), 
        ('HR', 'الموارد البشرية'), 
        ('Finance', 'المالية'), 
        ('Other', 'أخرى')
    ], validators=[DataRequired()])
    job_role = StringField('الوظيفة/الدور', validators=[DataRequired(), Length(min=2, max=100)])
    submit = SubmitField('إنشاء حساب')

class ReportForm(FlaskForm):
    # The choices will be set dynamically in the route based on the current language
    report_type = SelectField('نوع التقرير', validators=[DataRequired()])
    title = StringField('العنوان', validators=[DataRequired(), Length(min=5, max=200)])
    description = TextAreaField('الوصف التفصيلي', validators=[DataRequired()])
    file_upload = FileField('ملف/صورة اختيارية', validators=[validate_file_upload])
    submit = SubmitField('إرسال التقرير')

class ArticleForm(FlaskForm):
    title_ar = StringField('العنوان (العربية)', validators=[DataRequired()])
    title_en = StringField('العنوان (الإنجليزية)', validators=[DataRequired()])
    content_ar = TextAreaField('المحتوى (العربية)', validators=[DataRequired()])
    content_en = TextAreaField('المحتوى (الإنجليزية)', validators=[DataRequired()])
    submit = SubmitField('حفظ المقال')

class QuizForm(FlaskForm):
    title_ar = StringField('عنوان الاختبار (العربية)', validators=[DataRequired()])
    title_en = StringField('عنوان الاختبار (الإنجليزية)', validators=[DataRequired()])
    pass_score = IntegerField('درجة النجاح (%)', validators=[DataRequired(), NumberRange(min=0, max=100)])
    submit = SubmitField('حفظ الاختبار')

class QuestionForm(FlaskForm):
    question_ar = TextAreaField('السؤال (العربية)', validators=[DataRequired()])
    question_en = TextAreaField('السؤال (الإنجليزية)', validators=[DataRequired()])
    
    # Options fields (up to 5 options)
    option1_ar = StringField('الخيار 1 (العربية)', validators=[DataRequired()])
    option1_en = StringField('الخيار 1 (الإنجليزية)', validators=[DataRequired()])
    option2_ar = StringField('الخيار 2 (العربية)', validators=[DataRequired()])
    option2_en = StringField('الخيار 2 (الإنجليزية)', validators=[DataRequired()])
    option3_ar = StringField('الخيار 3 (العربية)', validators=[DataRequired()])
    option3_en = StringField('الخيار 3 (الإنجليزية)', validators=[DataRequired()])
    option4_ar = StringField('الخيار 4 (العربية)')
    option4_en = StringField('الخيار 4 (الإنجليزية)')
    option5_ar = StringField('الخيار 5 (العربية)')
    option5_en = StringField('الخيار 5 (الإنجليزية)')
    
    correct_option = SelectField('الخيار الصحيح', choices=[
        (0, 'الخيار 1'),
        (1, 'الخيار 2'),
        (2, 'الخيار 3'),
        (3, 'الخيار 4 (اختياري)'),
        (4, 'الخيار 5 (اختياري)')
    ], coerce=int, validators=[DataRequired()])
    
    submit = SubmitField('حفظ السؤال')

class TipAlertForm(FlaskForm):
    type = SelectField('النوع', choices=[('tip', 'نصيحة'), ('alert', 'تنبيه')], validators=[DataRequired()])
    content_ar = TextAreaField('المحتوى (العربية)', validators=[DataRequired()])
    content_en = TextAreaField('المحتوى (الإنجليزية)', validators=[DataRequired()])
    submit = SubmitField('حفظ')
