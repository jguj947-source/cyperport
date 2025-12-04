from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from functools import wraps
from datetime import datetime
import os
import sqlite3
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from config import Config
from models import init_db, get_db_connection, get_user_by_email, check_password, create_user
from forms import LoginForm, RegistrationForm, ReportForm, ArticleForm, QuizForm, TipAlertForm

app = Flask(__name__)
app.config.from_object(Config)

@app.before_request
def set_language_on_first_visit():
    if 'language' not in session:
        session['language'] = app.config['DEFAULT_LANGUAGE']

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize database
if not os.path.exists(app.config['DATABASE']):
    init_db()

# --- Helper Functions ---

def get_current_language():
    """Get the current language from session."""
    return session.get('language')

def translate_report_types():
    """Get report types for the current language."""
    lang = get_current_language()
    return app.config['REPORT_TYPES'].get(lang, app.config['REPORT_TYPES']['ar'])

def login_required(f):
    """Decorator to require login."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('يجب تسجيل الدخول أولاً.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin role."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('يجب تسجيل الدخول أولاً.', 'warning')
            return redirect(url_for('login'))
        
        conn = get_db_connection()
        user = conn.execute("SELECT role FROM users WHERE id = ?", (session['user_id'],)).fetchone()
        conn.close()
        
        if not user or user['role'] != 'admin':
            flash('لا توجد صلاحيات كافية.', 'danger')
            return redirect(url_for('index'))
        
        return f(*args, **kwargs)
    return decorated_function

# --- Routes: Authentication ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = get_user_by_email(email)
        if user and check_password(user, password):
            session['user_id'] = user['id']
            session['user_email'] = user['email']
            session['user_role'] = user['role']
            flash('تم تسجيل الدخول بنجاح.', 'success')
            return redirect(url_for('index'))
        else:
            flash('البريد الإلكتروني أو كلمة المرور غير صحيحة.', 'danger')
    
    lang = get_current_language()
    return render_template('login.html', lang=lang)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        password = request.form.get('password')
        password2 = request.form.get('password2')
        department = request.form.get('department')
        job_role = request.form.get('job_role')
        lang = get_current_language()
        
        if password != password2:
            flash('كلمتا المرور غير متطابقتان.', 'danger')
        elif len(password) < 8:
            flash('كلمة المرور يجب أن تكون 8 أحرف على الأقل.', 'danger')
        elif create_user(full_name, email, password, department, job_role):
            flash('تم إنشاء الحساب بنجاح. يمكنك الآن تسجيل الدخول.', 'success')
            return redirect(url_for('login'))
        else:
            flash('البريد الإلكتروني موجود بالفعل.', 'danger')
    
    lang = get_current_language()
    return render_template('register.html', lang=lang)

@app.route('/logout')
def logout():
    session.clear()
    flash('تم تسجيل الخروج بنجاح.', 'success')
    return redirect(url_for('index'))

# --- Routes: Language Selection ---

@app.route('/set-language/<language>')
def set_language(language):
    if language in app.config['LANGUAGES']:
        session['language'] = language
    return redirect(request.referrer or url_for('index'))

# --- Routes: Public Pages ---

@app.route('/')
def index():
    lang = get_current_language()
    return render_template('index.html', lang=lang)

@app.route('/articles')
def articles():
    conn = get_db_connection()
    lang = get_current_language()
    
    # Get articles for the current language
    articles_list = conn.execute("SELECT * FROM articles WHERE is_published = 1").fetchall()
    conn.close()
    
    return render_template('articles.html', articles=articles_list, lang=lang)

@app.route('/article/<int:article_id>')
def article_detail(article_id):
    conn = get_db_connection()
    lang = get_current_language()
    
    article = conn.execute("SELECT * FROM articles WHERE id = ?", (article_id,)).fetchone()
    
    if not article:
        flash('المقالة غير موجودة.', 'danger')
        return redirect(url_for('articles'))
    
    # Increment views
    conn.execute("UPDATE articles SET views = views + 1 WHERE id = ?", (article_id,))
    conn.commit()
    conn.close()
    
    return render_template('article_detail.html', article=article, lang=lang)

@app.route('/quizzes')
def quizzes():
    conn = get_db_connection()
    lang = get_current_language()
    
    quizzes_list = conn.execute("SELECT * FROM quizzes").fetchall()
    
    # For each quiz, get user's best score if logged in
    user_scores = {}
    if 'user_id' in session:
        for quiz in quizzes_list:
            result = conn.execute(
                "SELECT MAX(score) as best_score FROM user_quiz_results WHERE user_id = ? AND quiz_id = ?",
                (session['user_id'], quiz['id'])
            ).fetchone()
            if result and result['best_score']:
                user_scores[quiz['id']] = result['best_score']
    
    conn.close()
    
    return render_template('quizzes.html', quizzes=quizzes_list, user_scores=user_scores, lang=lang)

@app.route('/quiz/<int:quiz_id>')
def take_quiz(quiz_id):
    if 'user_id' not in session:
        flash('يجب تسجيل الدخول لخوض الاختبار.', 'warning')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    lang = get_current_language()
    
    quiz = conn.execute("SELECT * FROM quizzes WHERE id = ?", (quiz_id,)).fetchone()
    if not quiz:
        flash('الاختبار غير موجود.', 'danger')
        return redirect(url_for('quizzes'))
    
    questions = conn.execute(
        "SELECT * FROM quiz_questions WHERE quiz_id = ?",
        (quiz_id,)
    ).fetchall()
    
    # Get options for each question
    quiz_data = []
    for q in questions:
        options = conn.execute(
            "SELECT * FROM quiz_options WHERE question_id = ?",
            (q['id'],)
        ).fetchall()
        quiz_data.append({
            'question': q,
            'options': options
        })
    
    conn.close()
    
    return render_template('take_quiz.html', quiz=quiz, quiz_data=quiz_data, lang=lang)

@app.route('/submit-quiz/<int:quiz_id>', methods=['POST'])
@login_required
def submit_quiz(quiz_id):
    conn = get_db_connection()
    
    quiz = conn.execute("SELECT * FROM quizzes WHERE id = ?", (quiz_id,)).fetchone()
    if not quiz:
        return jsonify({'error': 'Quiz not found'}), 404
    
    questions = conn.execute(
        "SELECT * FROM quiz_questions WHERE quiz_id = ?",
        (quiz_id,)
    ).fetchall()
    
    score = 0
    total = len(questions)
    
    for q in questions:
        user_answer = request.form.get(f'question_{q["id"]}')
        if user_answer and int(user_answer) == q['correct_option']:
            score += 1
    
    percentage = int((score / total) * 100) if total > 0 else 0
    
    # Save result
    conn.execute(
        "INSERT INTO user_quiz_results (user_id, quiz_id, score) VALUES (?, ?, ?)",
        (session['user_id'], quiz_id, percentage)
    )
    conn.commit()
    conn.close()
    
    return redirect(url_for('quiz_result', quiz_id=quiz_id, score=percentage))

@app.route('/quiz/<int:quiz_id>/result')
def quiz_result(quiz_id):
    score = request.args.get('score', 0, type=int)
    conn = get_db_connection()
    quiz = conn.execute("SELECT * FROM quizzes WHERE id = ?", (quiz_id,)).fetchone()
    conn.close()
    
    if not quiz:
        return redirect(url_for('quizzes'))
    
    lang = get_current_language()
    passed = score >= quiz['pass_score']
    
    return render_template('quiz_result.html', quiz=quiz, score=score, passed=passed, lang=lang)

@app.route('/tips')
def tips():
    conn = get_db_connection()
    lang = get_current_language()
    
    tips_list = conn.execute("SELECT * FROM tips_alerts WHERE type = 'tip' ORDER BY publish_date DESC").fetchall()
    conn.close()
    
    return render_template('tips.html', tips=tips_list, lang=lang)

@app.route('/alerts')
def alerts():
    conn = get_db_connection()
    lang = get_current_language()
    
    alerts_list = conn.execute("SELECT * FROM tips_alerts WHERE type = 'alert' ORDER BY publish_date DESC").fetchall()
    conn.close()
    
    return render_template('alerts.html', alerts=alerts_list, lang=lang)

# --- Routes: Vulnerability Reporting ---

@app.route('/report', methods=['GET', 'POST'])
@login_required
def submit_report():
    if request.method == 'POST':
        report_type = request.form.get('report_type')
        title = request.form.get('title')
        description = request.form.get('description')
        
        file_path = None
        if 'file_upload' in request.files:
            file = request.files['file_upload']
            if file and file.filename:
                # Validate file
                allowed_extensions = {'jpg', 'jpeg', 'png', 'pdf'}
                if '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions:
                    filename = secure_filename(file.filename)
                    # Add timestamp to ensure uniqueness
                    filename = f"{datetime.now().timestamp()}_{filename}"
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    file_path = f"uploads/{filename}"
        
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO reports (user_id, report_type, title, description, file_path, status) VALUES (?, ?, ?, ?, ?, ?)",
            (session['user_id'], report_type, title, description, file_path, 'new')
        )
        conn.commit()
        conn.close()
        
        flash('تم إرسال التقرير بنجاح. شكراً لك على المساهمة في تحسين الأمان.', 'success')
        return redirect(url_for('index'))
    
    lang = get_current_language()
    report_types = translate_report_types()
    
    return render_template('report.html', report_types=report_types, lang=lang)

@app.route('/my-reports')
@login_required
def my_reports():
    conn = get_db_connection()
    lang = get_current_language()
    
    reports = conn.execute(
        "SELECT * FROM reports WHERE user_id = ? ORDER BY created_at DESC",
        (session['user_id'],)
    ).fetchall()
    
    conn.close()
    
    return render_template('my_reports.html', reports=reports, lang=lang)

@app.route('/report/<int:report_id>')
@login_required
def report_detail(report_id):
    conn = get_db_connection()
    lang = get_current_language()
    
    report = conn.execute("SELECT * FROM reports WHERE id = ?", (report_id,)).fetchone()
    
    if not report:
        flash('التقرير غير موجود.', 'danger')
        return redirect(url_for('my_reports'))
    
    # Check if user is the owner or admin
    if session['user_id'] != report['user_id'] and session.get('user_role') != 'admin':
        flash('لا توجد صلاحيات كافية.', 'danger')
        return redirect(url_for('my_reports'))
    
    conn.close()
    
    return render_template('report_detail.html', report=report, lang=lang)

# --- Routes: Admin Dashboard ---

@app.route('/admin')
@admin_required
def admin_dashboard():
    conn = get_db_connection()
    lang = get_current_language()
    
    # Get statistics
    total_reports = conn.execute("SELECT COUNT(*) as count FROM reports").fetchone()['count']
    new_reports = conn.execute("SELECT COUNT(*) as count FROM reports WHERE status = 'new'").fetchone()['count']
    total_users = conn.execute("SELECT COUNT(*) as count FROM users WHERE role = 'user'").fetchone()['count']
    total_articles = conn.execute("SELECT COUNT(*) as count FROM articles").fetchone()['count']
    total_quizzes = conn.execute("SELECT COUNT(*) as count FROM quizzes").fetchone()['count']
    
    conn.close()
    
    return render_template('admin_dashboard.html', 
                         total_reports=total_reports,
                         new_reports=new_reports,
                         total_users=total_users,
                         total_articles=total_articles,
                         total_quizzes=total_quizzes,
                         lang=lang)

@app.route('/admin/reports')
@admin_required
def admin_reports():
    conn = get_db_connection()
    lang = get_current_language()
    
    # Get filter parameters
    status_filter = request.args.get('status', '')
    type_filter = request.args.get('type', '')
    
    query = "SELECT r.*, u.email FROM reports r JOIN users u ON r.user_id = u.id WHERE 1=1"
    params = []
    
    if status_filter:
        query += " AND r.status = ?"
        params.append(status_filter)
    
    if type_filter:
        query += " AND r.report_type = ?"
        params.append(type_filter)
    
    query += " ORDER BY r.created_at DESC"
    
    reports = conn.execute(query, params).fetchall()
    conn.close()
    
    return render_template('admin_reports.html', reports=reports, lang=lang)

@app.route('/admin/report/<int:report_id>')
@admin_required
def admin_report_detail(report_id):
    conn = get_db_connection()
    lang = get_current_language()
    
    report = conn.execute(
        "SELECT r.*, u.email, u.full_name FROM reports r JOIN users u ON r.user_id = u.id WHERE r.id = ?",
        (report_id,)
    ).fetchone()
    
    if not report:
        flash('التقرير غير موجود.', 'danger')
        return redirect(url_for('admin_reports'))
    
    conn.close()
    
    return render_template('admin_report_detail.html', report=report, lang=lang)

@app.route('/admin/report/<int:report_id>/update-status', methods=['POST'])
@admin_required
def update_report_status(report_id):
    new_status = request.form.get('status')
    
    if new_status not in ['new', 'in_review', 'closed']:
        flash('حالة غير صحيحة.', 'danger')
        return redirect(url_for('admin_report_detail', report_id=report_id))
    
    conn = get_db_connection()
    conn.execute("UPDATE reports SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (new_status, report_id))
    conn.commit()
    conn.close()
    
    flash('تم تحديث حالة التقرير.', 'success')
    return redirect(url_for('admin_report_detail', report_id=report_id))

# --- Routes: Admin Content Management ---

@app.route('/admin/articles')
@admin_required
def admin_articles():
    conn = get_db_connection()
    lang = get_current_language()
    
    articles_list = conn.execute("SELECT * FROM articles ORDER BY created_at DESC").fetchall()
    conn.close()
    
    return render_template('admin_articles.html', articles=articles_list, lang=lang)

@app.route('/admin/article/new', methods=['GET', 'POST'])
@admin_required
def admin_new_article():
    if request.method == 'POST':
        title_ar = request.form.get('title_ar')
        title_en = request.form.get('title_en')
        content_ar = request.form.get('content_ar')
        content_en = request.form.get('content_en')
        
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO articles (title_ar, title_en, content_ar, content_en) VALUES (?, ?, ?, ?)",
            (title_ar, title_en, content_ar, content_en)
        )
        conn.commit()
        conn.close()
        
        flash('تم إنشاء المقالة بنجاح.', 'success')
        return redirect(url_for('admin_articles'))
    
    lang = get_current_language()
    return render_template('admin_article_form.html', lang=lang)

@app.route('/admin/article/<int:article_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_edit_article(article_id):
    conn = get_db_connection()
    article = conn.execute("SELECT * FROM articles WHERE id = ?", (article_id,)).fetchone()
    
    if not article:
        flash('المقالة غير موجودة.', 'danger')
        return redirect(url_for('admin_articles'))
    
    if request.method == 'POST':
        title_ar = request.form.get('title_ar')
        title_en = request.form.get('title_en')
        content_ar = request.form.get('content_ar')
        content_en = request.form.get('content_en')
        
        conn.execute(
            "UPDATE articles SET title_ar = ?, title_en = ?, content_ar = ?, content_en = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (title_ar, title_en, content_ar, content_en, article_id)
        )
        conn.commit()
        conn.close()
        
        flash('تم تحديث المقالة بنجاح.', 'success')
        return redirect(url_for('admin_articles'))
    
    lang = get_current_language()
    return render_template('admin_article_form.html', article=article, lang=lang)

@app.route('/admin/articles/delete/<int:article_id>', methods=['POST'])
@admin_required
def admin_delete_article(article_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM articles WHERE id = ?", (article_id,))
    conn.commit()
    conn.close()
    flash('تم حذف المقالة بنجاح.', 'success')
    return redirect(url_for('admin_articles'))

# --- Routes: Admin Quiz Management ---

@app.route('/admin/quizzes')
@admin_required
def admin_quizzes():
    conn = get_db_connection()
    quizzes_list = conn.execute("SELECT * FROM quizzes").fetchall()
    conn.close()
    lang = get_current_language()
    return render_template('admin_quizzes.html', quizzes=quizzes_list, lang=lang)

@app.route('/admin/quiz/new', methods=['GET', 'POST'])
@admin_required
def admin_new_quiz():
    form = QuizForm()
    if form.validate_on_submit():
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO quizzes (title_ar, title_en, pass_score) VALUES (?, ?, ?)",
            (form.title_ar.data, form.title_en.data, form.pass_score.data)
        )
        conn.commit()
        conn.close()
        flash('تم إنشاء الاختبار بنجاح.', 'success')
        return redirect(url_for('admin_quizzes'))
    
    lang = get_current_language()
    return render_template('admin_quiz_form.html', form=form, lang=lang, quiz=None)

@app.route('/admin/quiz/edit/<int:quiz_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_quiz(quiz_id):
    conn = get_db_connection()
    quiz = conn.execute("SELECT * FROM quizzes WHERE id = ?", (quiz_id,)).fetchone()
    
    if not quiz:
        flash('الاختبار غير موجود.', 'danger')
        conn.close()
        return redirect(url_for('admin_quizzes'))
    
    form = QuizForm(data=quiz)
    
    if form.validate_on_submit():
        conn.execute(
            "UPDATE quizzes SET title_ar = ?, title_en = ?, pass_score = ? WHERE id = ?",
            (form.title_ar.data, form.title_en.data, form.pass_score.data, quiz_id)
        )
        conn.commit()
        conn.close()
        flash('تم تحديث الاختبار بنجاح.', 'success')
        return redirect(url_for('admin_quizzes'))
    
    conn.close()
    lang = get_current_language()
    return render_template('admin_quiz_form.html', form=form, lang=lang, quiz=quiz)

@app.route('/admin/quiz/delete/<int:quiz_id>', methods=['POST'])
@admin_required
def admin_delete_quiz(quiz_id):
    conn = get_db_connection()
    # Delete questions and options first
    conn.execute("DELETE FROM quiz_options WHERE question_id IN (SELECT id FROM quiz_questions WHERE quiz_id = ?)", (quiz_id,))
    conn.execute("DELETE FROM quiz_questions WHERE quiz_id = ?", (quiz_id,))
    conn.execute("DELETE FROM quizzes WHERE id = ?", (quiz_id,))
    conn.commit()
    conn.close()
    flash('تم حذف الاختبار بنجاح.', 'success')
    return redirect(url_for('admin_quizzes'))

@app.route('/admin/quiz/<int:quiz_id>/questions')
@admin_required
def admin_quiz_questions(quiz_id):
    conn = get_db_connection()
    quiz = conn.execute("SELECT * FROM quizzes WHERE id = ?", (quiz_id,)).fetchone()
    questions = conn.execute("SELECT * FROM quiz_questions WHERE quiz_id = ?", (quiz_id,)).fetchall()
    
    questions_data = []
    for q in questions:
        options = conn.execute("SELECT * FROM quiz_options WHERE question_id = ?", (q['id'],)).fetchall()
        questions_data.append({'question': q, 'options': options})
        
    conn.close()
    lang = get_current_language()
    return render_template('admin_quiz_questions.html', quiz=quiz, questions_data=questions_data, lang=lang)

@app.route('/admin/quiz/<int:quiz_id>/question/new', methods=['GET', 'POST'])
@admin_required
def admin_new_question(quiz_id):
    form = QuestionForm()
    conn = get_db_connection()
    quiz = conn.execute("SELECT * FROM quizzes WHERE id = ?", (quiz_id,)).fetchone()
    
    if not quiz:
        flash('الاختبار غير موجود.', 'danger')
        conn.close()
        return redirect(url_for('admin_quizzes'))
    
    if form.validate_on_submit():
        # Insert question
        cursor = conn.execute(
            "INSERT INTO quiz_questions (quiz_id, question_ar, question_en, correct_option) VALUES (?, ?, ?, ?)",
            (quiz_id, form.question_ar.data, form.question_en.data, form.correct_option.data)
        )
        question_id = cursor.lastrowid
        
        # Insert options
        options_ar = [form.option1_ar.data, form.option2_ar.data, form.option3_ar.data, form.option4_ar.data, form.option5_ar.data]
        options_en = [form.option1_en.data, form.option2_en.data, form.option3_en.data, form.option4_en.data, form.option5_en.data]
        
        for ar, en in zip(options_ar, options_en):
            if ar and en:
                conn.execute(
                    "INSERT INTO quiz_options (question_id, option_ar, option_en) VALUES (?, ?, ?)",
                    (question_id, ar, en)
                )
        
        conn.commit()
        conn.close()
        flash('تم إنشاء السؤال بنجاح.', 'success')
        return redirect(url_for('admin_quiz_questions', quiz_id=quiz_id))
    
    conn.close()
    lang = get_current_language()
    return render_template('admin_question_form.html', form=form, lang=lang, quiz=quiz, question=None)

@app.route('/admin/quiz/<int:quiz_id>/question/edit/<int:question_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_question(quiz_id, question_id):
    conn = get_db_connection()
    quiz = conn.execute("SELECT * FROM quizzes WHERE id = ?", (quiz_id,)).fetchone()
    question = conn.execute("SELECT * FROM quiz_questions WHERE id = ?", (question_id,)).fetchone()
    options = conn.execute("SELECT * FROM quiz_options WHERE question_id = ?", (question_id,)).fetchall()
    
    if not quiz or not question:
        flash('الاختبار أو السؤال غير موجود.', 'danger')
        conn.close()
        return redirect(url_for('admin_quizzes'))
    
    # Prepare data for form
    form_data = {
        'question_ar': question['question_ar'],
        'question_en': question['question_en'],
        'correct_option': question['correct_option']
    }
    for i, opt in enumerate(options):
        form_data[f'option{i+1}_ar'] = opt['option_ar']
        form_data[f'option{i+1}_en'] = opt['option_en']
        
    form = QuestionForm(data=form_data)
    
    if form.validate_on_submit():
        # Update question
        conn.execute(
            "UPDATE quiz_questions SET question_ar = ?, question_en = ?, correct_option = ? WHERE id = ?",
            (form.question_ar.data, form.question_en.data, form.correct_option.data, question_id)
        )
        
        # Update options (simple approach: delete and re-insert)
        conn.execute("DELETE FROM quiz_options WHERE question_id = ?", (question_id,))
        
        options_ar = [form.option1_ar.data, form.option2_ar.data, form.option3_ar.data, form.option4_ar.data, form.option5_ar.data]
        options_en = [form.option1_en.data, form.option2_en.data, form.option3_en.data, form.option4_en.data, form.option5_en.data]
        
        for ar, en in zip(options_ar, options_en):
            if ar and en:
                conn.execute(
                    "INSERT INTO quiz_options (question_id, option_ar, option_en) VALUES (?, ?, ?)",
                    (question_id, ar, en)
                )
        
        conn.commit()
        conn.close()
        flash('تم تحديث السؤال بنجاح.', 'success')
        return redirect(url_for('admin_quiz_questions', quiz_id=quiz_id))
    
    conn.close()
    lang = get_current_language()
    return render_template('admin_question_form.html', form=form, lang=lang, quiz=quiz, question=question)

@app.route('/admin/quiz/<int:quiz_id>/question/delete/<int:question_id>', methods=['POST'])
@admin_required
def admin_delete_question(quiz_id, question_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM quiz_options WHERE question_id = ?", (question_id,))
    conn.execute("DELETE FROM quiz_questions WHERE id = ?", (question_id,))
    conn.commit()
    conn.close()
    flash('تم حذف السؤال بنجاح.', 'success')
    return redirect(url_for('admin_quiz_questions', quiz_id=quiz_id))

# --- Routes: Admin Tips/Alerts Management ---



# --- Routes: Admin Tips/Alerts Management ---

@app.route('/admin/tips-alerts')
@admin_required
def admin_tips_alerts():
    conn = get_db_connection()
    tips_alerts_list = conn.execute("SELECT * FROM tips_alerts ORDER BY publish_date DESC").fetchall()
    conn.close()
    lang = get_current_language()
    return render_template('admin_tips_alerts.html', tips_alerts=tips_alerts_list, lang=lang)

@app.route('/admin/tips-alerts/new', methods=['GET', 'POST'])
@admin_required
def admin_new_tip_alert():
    form = TipAlertForm()
    if form.validate_on_submit():
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO tips_alerts (type, content_ar, content_en) VALUES (?, ?, ?)",
            (form.type.data, form.content_ar.data, form.content_en.data)
        )
        conn.commit()
        conn.close()
        flash('تم إنشاء النصيحة/التنبيه بنجاح.', 'success')
        return redirect(url_for('admin_tips_alerts'))
    
    lang = get_current_language()
    return render_template('admin_tip_alert_form.html', form=form, lang=lang, item=None)

@app.route('/admin/tips-alerts/edit/<int:item_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_tip_alert(item_id):
    conn = get_db_connection()
    item = conn.execute("SELECT * FROM tips_alerts WHERE id = ?", (item_id,)).fetchone()
    
    if not item:
        flash('العنصر غير موجود.', 'danger')
        conn.close()
        return redirect(url_for('admin_tips_alerts'))
    
    form = TipAlertForm(data=item)
    
    if form.validate_on_submit():
        conn.execute(
            "UPDATE tips_alerts SET type = ?, content_ar = ?, content_en = ? WHERE id = ?",
            (form.type.data, form.content_ar.data, form.content_en.data, item_id)
        )
        conn.commit()
        conn.close()
        flash('تم تحديث النصيحة/التنبيه بنجاح.', 'success')
        return redirect(url_for('admin_tips_alerts'))
    
    conn.close()
    lang = get_current_language()
    return render_template('admin_tip_alert_form.html', form=form, lang=lang, item=item)

@app.route('/admin/tips-alerts/delete/<int:item_id>', methods=['POST'])
@admin_required
def admin_delete_tip_alert(item_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM tips_alerts WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    flash('تم حذف النصيحة/التنبيه بنجاح.', 'success')
    return redirect(url_for('admin_tips_alerts'))

if __name__ == '__main__':
    # For local development
    app.run(debug=True)
# For production (Render/Gunicorn)
# The Procfile will use 'gunicorn app:app' which calls the 'app' object


