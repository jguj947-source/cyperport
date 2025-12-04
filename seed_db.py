#!/usr/bin/env python3
"""
Script to seed the database with sample data.
Run this after initializing the database.
"""

import sqlite3
from werkzeug.security import generate_password_hash
from config import Config
from models import init_db

DATABASE = Config.DATABASE

def seed_database():
    init_db()
    conn = sqlite3.connect(DATABASE)
    
    # 1. Create admin user
    admin_password_hash = generate_password_hash(Config.ADMIN_PASSWORD)
    conn.execute(
        "INSERT OR IGNORE INTO users (full_name, email, password_hash, department, job_role, role) VALUES (?, ?, ?, ?, ?, ?)",
        ('المسؤول', Config.ADMIN_EMAIL, admin_password_hash, 'IT', 'مسؤول النظام', 'admin')
    )
    
    # 2. Create sample users
    user1_password = generate_password_hash('User123456!')
    user2_password = generate_password_hash('User123456!')
    
    conn.execute(
        "INSERT OR IGNORE INTO users (full_name, email, password_hash, department, job_role, role) VALUES (?, ?, ?, ?, ?, ?)",
        ('أحمد محمد', 'ahmed@example.com', user1_password, 'IT', 'مهندس أمان', 'user')
    )
    
    conn.execute(
        "INSERT OR IGNORE INTO users (full_name, email, password_hash, department, job_role, role) VALUES (?, ?, ?, ?, ?, ?)",
        ('فاطمة علي', 'fatima@example.com', user2_password, 'HR', 'موظفة موارد بشرية', 'user')
    )
    
    # 3. Create sample articles
    articles = [
        {
            'title_ar': 'مقدمة في الأمن السيبراني',
            'title_en': 'Introduction to Cybersecurity',
            'content_ar': 'الأمن السيبراني هو ممارسة حماية الأنظمة والشبكات والبرامج من الهجمات الرقمية. تهدف هذه الهجمات عادةً إلى الوصول إلى المعلومات الحساسة أو تغييرها أو تدميرها أو ابتزاز المستخدمين. يتطلب تنفيذ فعال للأمن السيبراني مزيجاً من التقنيات والعمليات والتدريب.',
            'content_en': 'Cybersecurity is the practice of protecting systems, networks, and programs from digital attacks. These attacks are usually aimed at accessing, changing, or destroying sensitive information, extorting money from users, or interrupting normal business processes. Implementing effective cybersecurity measures is particularly challenging today because there are more devices than people, and attackers are becoming more innovative.'
        },
        {
            'title_ar': 'كيفية إنشاء كلمة مرور قوية',
            'title_en': 'How to Create a Strong Password',
            'content_ar': 'كلمة المرور القوية هي خط الدفاع الأول ضد الوصول غير المصرح به إلى حساباتك. يجب أن تتكون من 12 حرفاً على الأقل وتجمع بين الأحرف الكبيرة والصغيرة والأرقام والرموز. تجنب استخدام معلومات شخصية أو كلمات شائعة.',
            'content_en': 'A strong password is your first line of defense against unauthorized access to your accounts. It should consist of at least 12 characters and combine uppercase and lowercase letters, numbers, and symbols. Avoid using personal information or common words.'
        },
        {
            'title_ar': 'التعرف على هجمات التصيد الاحتيالي',
            'title_en': 'Recognizing Phishing Attacks',
            'content_ar': 'التصيد الاحتيالي هو محاولة خبيثة للحصول على معلومات حساسة مثل أسماء المستخدمين وكلمات المرور وتفاصيل بطاقات الائتمان. تحذر من رسائل البريد الإلكتروني المريبة والروابط المشبوهة.',
            'content_en': 'Phishing is a malicious attempt to obtain sensitive information such as usernames, passwords, and credit card details. Be wary of suspicious emails and suspicious links.'
        },
        {
            'title_ar': 'حماية بياناتك الشخصية على الإنترنت',
            'title_en': 'Protecting Your Personal Data Online',
            'content_ar': 'أصبحت حماية البيانات الشخصية أكثر أهمية من أي وقت مضى. استخدم كلمات مرور قوية، فعّل المصادقة الثنائية، وراجع إعدادات الخصوصية بانتظام.',
            'content_en': 'Personal data protection has become more important than ever. Use strong passwords, enable two-factor authentication, and regularly review privacy settings.'
        },
        {
            'title_ar': 'أمن الأجهزة المحمولة',
            'title_en': 'Mobile Device Security',
            'content_ar': 'أصبحت الأجهزة المحمولة جزءاً لا يتجزأ من حياتنا اليومية. حافظ على تحديث نظام التشغيل والتطبيقات، استخدم قفل الشاشة، وكن حذراً من التطبيقات المريبة.',
            'content_en': 'Mobile devices have become an integral part of our daily lives. Keep your operating system and apps updated, use screen locks, and be careful with suspicious apps.'
        }
    ]
    
    for article in articles:
        conn.execute(
            "INSERT OR IGNORE INTO articles (title_ar, title_en, content_ar, content_en) VALUES (?, ?, ?, ?)",
            (article['title_ar'], article['title_en'], article['content_ar'], article['content_en'])
        )
    
    # 4. Create sample quizzes
    # Delete existing quizzes to avoid duplicates during re-seeding
    conn.execute("DELETE FROM user_quiz_results")
    conn.execute("DELETE FROM quiz_options")
    conn.execute("DELETE FROM quiz_questions")
    conn.execute("DELETE FROM quizzes")
    quizzes = [
        {
            'title_ar': 'اختبار الأمن السيبراني الأساسي',
            'title_en': 'Basic Cybersecurity Quiz',
            'pass_score': 70,
            'questions': [
                {
                    'question_ar': 'ما هو الهدف الأساسي من الأمن السيبراني؟',
                    'question_en': 'What is the primary goal of cybersecurity?',
                    'options_ar': ['زيادة سرعة الإنترنت', 'حماية الأنظمة والبيانات من التهديدات', 'تطوير تطبيقات الهاتف', 'تحسين جودة الكاميرات'],
                    'options_en': ['Increase internet speed', 'Protect systems and data from threats', 'Develop mobile applications', 'Improve camera quality'],
                    'correct': 1
                },
                {
                    'question_ar': 'ما هو المصادقة الثنائية (2FA)؟',
                    'question_en': 'What is Two-Factor Authentication (2FA)?',
                    'options_ar': ['استخدام كلمة مرور واحدة', 'استخدام بصمة الإصبع فقط', 'طبقة أمان إضافية تتطلب طريقتين للتحقق', 'تسجيل الدخول تلقائياً'],
                    'options_en': ['Using a single password', 'Using only a fingerprint', 'An extra layer of security requiring two verification methods', 'Automatic login'],
                    'correct': 2
                },
                {
                    'question_ar': 'ماذا يعني "البرامج الضارة" (Malware)؟',
                    'question_en': 'What does "Malware" mean?',
                    'options_ar': ['برنامج مفيد لتحسين الأداء', 'برنامج مصمم لإلحاق الضرر بالأنظمة', 'نظام تشغيل جديد', 'أداة لتصميم الجرافيك'],
                    'options_en': ['Useful software for performance improvement', 'Software designed to harm systems', 'A new operating system', 'A graphic design tool'],
                    'correct': 1
                },
                {
                    'question_ar': 'ما هي أفضل طريقة لحماية كلمة المرور؟',
                    'question_en': 'What is the best way to protect a password?',
                    'options_ar': ['كتابتها على ورقة', 'مشاركتها مع الزملاء', 'استخدام مدير كلمات مرور قوي', 'استخدام كلمة مرور سهلة التذكر'],
                    'options_en': ['Writing it on paper', 'Sharing it with colleagues', 'Using a strong password manager', 'Using an easy-to-remember password'],
                    'correct': 2
                },
                {
                    'question_ar': 'ما هو هجوم حجب الخدمة (DDoS)؟',
                    'question_en': 'What is a Denial of Service (DDoS) attack?',
                    'options_ar': ['هجوم يهدف إلى سرقة البيانات', 'هجوم يهدف إلى إغراق الخادم بالطلبات لتعطيله', 'هجوم يهدف إلى تغيير إعدادات النظام', 'هجوم يهدف إلى نشر الإعلانات'],
                    'options_en': ['An attack aimed at stealing data', 'An attack aimed at flooding a server with requests to shut it down', 'An attack aimed at changing system settings', 'An attack aimed at spreading advertisements'],
                    'correct': 1
                }
            ]
        },
        {
            'title_ar': 'اختبار أمن كلمات المرور',
            'title_en': 'Password Security Quiz',
            'pass_score': 75,
            'questions': [
                {
                    'question_ar': 'ما هي الممارسة الأفضل لإنشاء كلمة مرور؟',
                    'question_en': 'What is the best practice for creating a password?',
                    'options_ar': ['استخدام اسم الحيوان الأليف', 'استخدام جملة طويلة ومعقدة', 'استخدام تاريخ الميلاد', 'استخدام كلمة واحدة شائعة'],
                    'options_en': ['Using a pet\'s name', 'Using a long and complex passphrase', 'Using a birth date', 'Using a single common word'],
                    'correct': 1
                },
                {
                    'question_ar': 'ما هو الغرض من مدير كلمات المرور؟',
                    'question_en': 'What is the purpose of a password manager?',
                    'options_ar': ['تخزين كلمات المرور بشكل غير آمن', 'توليد وتخزين كلمات مرور قوية ومشفرة', 'مشاركة كلمات المرور مع الآخرين', 'تذكيرك بكلمات المرور الضعيفة فقط'],
                    'options_en': ['Storing passwords insecurely', 'Generating and storing strong, encrypted passwords', 'Sharing passwords with others', 'Only reminding you of weak passwords'],
                    'correct': 1
                },
                {
                    'question_ar': 'ماذا يجب أن تفعل إذا نسيت كلمة المرور الخاصة بك؟',
                    'question_en': 'What should you do if you forget your password?',
                    'options_ar': ['محاولة تخمينها عدة مرات', 'الاتصال بالدعم الفني وطلب إعادة تعيينها', 'إنشاء حساب جديد', 'استخدام نفس كلمة المرور لحساب آخر'],
                    'options_en': ['Try guessing it multiple times', 'Contact technical support and ask for a reset', 'Create a new account', 'Use the same password for another account'],
                    'correct': 1
                },
                {
                    'question_ar': 'ما هو التشفير (Encryption)؟',
                    'question_en': 'What is Encryption?',
                    'options_ar': ['تحويل البيانات إلى شكل غير قابل للقراءة إلا للمصرح لهم', 'إخفاء البيانات عن الجميع', 'ضغط حجم الملفات', 'زيادة سرعة نقل البيانات'],
                    'options_en': ['Converting data into an unreadable form except for authorized parties', 'Hiding data from everyone', 'Compressing file size', 'Increasing data transfer speed'],
                    'correct': 0
                }
            ]
        },
        {
            'title_ar': 'اختبار التصيد الاحتيالي',
            'title_en': 'Phishing Quiz',
            'pass_score': 80,
            'questions': [
                {
                    'question_ar': 'ما هي علامات التصيد الاحتيالي؟',
                    'question_en': 'What are signs of phishing?',
                    'options_ar': ['أخطاء إملائية وطلبات عاجلة', 'روابط غريبة', 'طلب معلومات شخصية', 'جميع ما سبق'],
                    'options_en': ['Spelling errors and urgent requests', 'Strange links', 'Requests for personal information', 'All of the above'],
                    'correct': 3
                },
                {
                    'question_ar': 'ماذا تفعل إذا تلقيت بريداً مريباً؟',
                    'question_en': 'What should you do if you receive a suspicious email?',
                    'options_ar': ['انقر على الروابط', 'احذفه فوراً', 'أرسله لآخرين', 'أبلغ عن البريد كرسالة مزعجة'],
                    'options_en': ['Click on the links', 'Delete it immediately', 'Send it to others', 'Report the email as spam'],
                    'correct': 3
                },
                {
                    'question_ar': 'كيف تتحقق من صحة موقع ويب؟',
                    'question_en': 'How do you verify a website is legitimate?',
                    'options_ar': ['تحقق من HTTPS والقفل', 'تحقق من عنوان URL', 'ابحث عن علامات الأمان', 'جميع ما سبق'],
                    'options_en': ['Check for HTTPS and lock', 'Check the URL address', 'Look for security badges', 'All of the above'],
                    'correct': 3
                },
                {
                    'question_ar': 'ما هو التصيد الاحتيالي الموجه (Spear Phishing)؟',
                    'question_en': 'What is Spear Phishing?',
                    'options_ar': ['هجوم تصيد عشوائي', 'هجوم تصيد يستهدف شخصاً أو مؤسسة محددة', 'هجوم تصيد عبر الهاتف', 'هجوم تصيد عبر الرسائل النصية'],
                    'options_en': ['A random phishing attack', 'A phishing attack targeting a specific person or organization', 'A phishing attack via phone', 'A phishing attack via text message'],
                    'correct': 1
                },
                {
                    'question_ar': 'ماذا يعني "HTTPS" في عنوان الموقع؟',
                    'question_en': 'What does "HTTPS" in a website address mean?',
                    'options_ar': ['الموقع غير آمن', 'الموقع يستخدم اتصالاً مشفراً وآمناً', 'الموقع بطيء', 'الموقع مخصص للهواة'],
                    'options_en': ['The site is insecure', 'The site uses an encrypted and secure connection', 'The site is slow', 'The site is for amateurs'],
                    'correct': 1
                }
            ]
        }
    ]
    
    for quiz in quizzes:
        cursor = conn.execute(
            "INSERT OR IGNORE INTO quizzes (title_ar, title_en, pass_score) VALUES (?, ?, ?)",
            (quiz['title_ar'], quiz['title_en'], quiz['pass_score'])
        )
        quiz_id = cursor.lastrowid
        
        # Add questions
        for q in quiz['questions']:
            cursor = conn.execute(
                "INSERT INTO quiz_questions (quiz_id, question_ar, question_en, correct_option) VALUES (?, ?, ?, ?)",
                (quiz_id, q['question_ar'], q['question_en'], q['correct'])
            )
            question_id = cursor.lastrowid
            
            # Add options
            for i, (opt_ar, opt_en) in enumerate(zip(q['options_ar'], q['options_en'])):
                conn.execute(
                    "INSERT INTO quiz_options (question_id, option_ar, option_en) VALUES (?, ?, ?)",
                    (question_id, opt_ar, opt_en)
                )
    
    # 5. Create sample tips and alerts
    tips_alerts = [
        {
            'type': 'tip',
            'content_ar': 'استخدم كلمات مرور قوية تتكون من 12 حرفاً على الأقل',
            'content_en': 'Use strong passwords consisting of at least 12 characters'
        },
        {
            'type': 'tip',
            'content_ar': 'فعّل المصادقة الثنائية على جميع حساباتك المهمة',
            'content_en': 'Enable two-factor authentication on all your important accounts'
        },
        {
            'type': 'tip',
            'content_ar': 'حدّث برامجك بانتظام للحصول على أحدث إصلاحات الأمان',
            'content_en': 'Update your software regularly to get the latest security patches'
        },
        {
            'type': 'tip',
            'content_ar': 'كن حذراً من رسائل البريد الإلكتروني المريبة',
            'content_en': 'Be careful with suspicious emails'
        },
        {
            'type': 'tip',
            'content_ar': 'استخدم VPN عند الاتصال بشبكات Wi-Fi العامة',
            'content_en': 'Use VPN when connecting to public Wi-Fi networks'
        },
        {
            'type': 'tip',
            'content_ar': 'راجع إعدادات الخصوصية على وسائل التواصل الاجتماعي',
            'content_en': 'Review privacy settings on social media'
        },
        {
            'type': 'tip',
            'content_ar': 'قم بعمل نسخ احتياطية منتظمة لبياناتك المهمة',
            'content_en': 'Make regular backups of your important data'
        },
        {
            'type': 'tip',
            'content_ar': 'استخدم قفل الشاشة على جميع أجهزتك',
            'content_en': 'Use screen lock on all your devices'
        },
        {
            'type': 'alert',
            'content_ar': 'تحذير: اكتُشف هجوم تصيد احتيالي يستهدف بيانات العملاء',
            'content_en': 'Alert: A phishing attack targeting customer data has been discovered'
        },
        {
            'type': 'alert',
            'content_ar': 'تنبيه أمني: ثغرة جديدة في متصفح Chrome تتطلب تحديثاً فوراً',
            'content_en': 'Security Alert: New vulnerability in Chrome browser requires immediate update'
        },
        {
            'type': 'alert',
            'content_ar': 'تحذير: محاولات اختراق متزايدة على حسابات البريد الإلكتروني',
            'content_en': 'Warning: Increasing attempts to breach email accounts'
        }
    ]
    
    for item in tips_alerts:
        conn.execute(
            "INSERT OR IGNORE INTO tips_alerts (type, content_ar, content_en) VALUES (?, ?, ?)",
            (item['type'], item['content_ar'], item['content_en'])
        )
    
    # 6. Create sample reports
    reports = [
        {
            'user_id': 1,
            'report_type': 'XSS',
            'title': 'ثغرة XSS في صفحة البحث',
            'description': 'تم اكتشاف ثغرة حقن سكريبت في صفحة البحث تسمح بتنفيذ كود JavaScript غير موثوق به',
            'status': 'new'
        },
        {
            'user_id': 2,
            'report_type': 'SQLi',
            'title': 'ثغرة SQL Injection في نموذج تسجيل الدخول',
            'description': 'تم العثور على ثغرة حقن SQL في حقل البريد الإلكتروني في نموذج تسجيل الدخول',
            'status': 'in_review'
        },
        {
            'user_id': 1,
            'report_type': 'Auth',
            'title': 'مشكلة في التحقق من الصلاحيات',
            'description': 'يمكن للمستخدمين الوصول إلى بيانات المستخدمين الآخرين من خلال تعديل معرف المستخدم في URL',
            'status': 'closed'
        },
        {
            'user_id': 2,
            'report_type': 'CSRF',
            'title': 'ثغرة CSRF في نموذج تغيير كلمة المرور',
            'description': 'تم اكتشاف ثغرة تزوير طلب عبر المواقع في نموذج تغيير كلمة المرور',
            'status': 'new'
        }
    ]
    
    for report in reports:
        conn.execute(
            "INSERT OR IGNORE INTO reports (user_id, report_type, title, description, status) VALUES (?, ?, ?, ?, ?)",
            (report['user_id'], report['report_type'], report['title'], report['description'], report['status'])
        )
    
    conn.commit()
    conn.close()
    print("✓ Database seeded successfully!")

if __name__ == '__main__':
    seed_database()
