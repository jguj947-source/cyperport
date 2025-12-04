import os

class Config:
    # يجب تغيير هذا المفتاح في بيئة الإنتاج
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a_very_secret_key_for_cyberport_project_2025'
    
    # إعدادات قاعدة البيانات والتحميل
    DATABASE = 'database.sqlite'
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB limit for uploads
    
    # إعدادات اللغة
    LANGUAGES = ['ar', 'en']
    DEFAULT_LANGUAGE = 'ar'
    
    # إعدادات المستخدمين
    ADMIN_EMAIL = 'admin@cyberport.local'
    ADMIN_PASSWORD = 'ChangeMe123!'
    
    # أنواع التقارير للثغرات
    REPORT_TYPES = {
        'ar': [
            ('XSS', 'حقن سكريبت عبر المواقع (XSS)'),
            ('SQLi', 'حقن SQL'),
            ('CSRF', 'تزوير طلب عبر المواقع (CSRF)'),
            ('Auth', 'مشكلة في المصادقة/التفويض'),
            ('Other', 'أخرى')
        ],
        'en': [
            ('XSS', 'Cross-Site Scripting (XSS)'),
            ('SQLi', 'SQL Injection'),
            ('CSRF', 'Cross-Site Request Forgery (CSRF)'),
            ('Auth', 'Authentication/Authorization Issue'),
            ('Other', 'Other')
        ]
    }
