import streamlit as st
import sqlite3
import json
import hashlib
import uuid
import os
from datetime import datetime, timedelta
from decimal import Decimal
import pandas as pd

# =====================================================
# Database Setup
# =====================================================

DB_PATH = "survey_rewards.db"

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    """Initialize database tables"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            phone TEXT,
            balance REAL DEFAULT 0.00,
            total_earned REAL DEFAULT 0.00,
            total_withdrawn REAL DEFAULT 0.00,
            is_verified INTEGER DEFAULT 0,
            referral_code TEXT UNIQUE,
            referred_by INTEGER,
            date_joined TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (referred_by) REFERENCES users(id)
        )
    ''')
    
    # User profiles table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            country TEXT DEFAULT 'Pakistan',
            city TEXT,
            address TEXT,
            date_of_birth TEXT,
            completed_surveys INTEGER DEFAULT 0,
            referral_earnings REAL DEFAULT 0.00,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # Surveys table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS surveys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT DEFAULT 'general',
            difficulty TEXT DEFAULT 'easy',
            reward REAL NOT NULL,
            estimated_time INTEGER NOT NULL,
            questions_count INTEGER DEFAULT 10,
            is_active INTEGER DEFAULT 1,
            max_participants INTEGER,
            current_participants INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TEXT
        )
    ''')
    
    # Survey questions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS survey_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            survey_id INTEGER NOT NULL,
            question_text TEXT NOT NULL,
            question_type TEXT DEFAULT 'multiple_choice',
            options TEXT,
            question_order INTEGER DEFAULT 0,
            FOREIGN KEY (survey_id) REFERENCES surveys(id) ON DELETE CASCADE
        )
    ''')
    
    # Survey answers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS survey_answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            survey_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            answer_data TEXT NOT NULL,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            reward_earned REAL NOT NULL,
            UNIQUE(survey_id, user_id),
            FOREIGN KEY (survey_id) REFERENCES surveys(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # Withdrawal methods table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS withdrawal_methods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            icon TEXT NOT NULL,
            min_amount REAL DEFAULT 5.00,
            max_amount REAL DEFAULT 1000.00,
            processing_time TEXT NOT NULL,
            fee_percentage REAL DEFAULT 0.00,
            is_active INTEGER DEFAULT 1,
            instructions TEXT
        )
    ''')
    
    # Withdrawals table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS withdrawals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            method_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            fee REAL DEFAULT 0.00,
            net_amount REAL NOT NULL,
            status TEXT DEFAULT 'pending',
            account_number TEXT NOT NULL,
            account_name TEXT NOT NULL,
            payment_details TEXT,
            transaction_id TEXT,
            notes TEXT,
            admin_notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            processed_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (method_id) REFERENCES withdrawal_methods(id)
        )
    ''')
    
    # Transactions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type TEXT NOT NULL,
            amount REAL NOT NULL,
            balance_after REAL NOT NULL,
            description TEXT NOT NULL,
            reference_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    conn.close()

# =====================================================
# Helper Functions
# =====================================================

def hash_password(password):
    """Hash password"""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_referral_code():
    """Generate unique referral code"""
    return str(uuid.uuid4())[:8].upper()

def create_sample_data():
    """Create sample surveys and data"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if surveys already exist
    cursor.execute("SELECT COUNT(*) FROM surveys")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return
    
    # Create sample surveys
    surveys = [
        {
            'title': 'Consumer Shopping Habits Survey',
            'description': 'Help us understand your shopping preferences and habits. This survey covers online and offline shopping behaviors.',
            'category': 'shopping',
            'difficulty': 'easy',
            'reward': 1.50,
            'estimated_time': 5,
            'questions_count': 8,
            'max_participants': 100,
        },
        {
            'title': 'Technology Usage & Preferences',
            'description': 'Share your thoughts on technology products and services. Your feedback helps shape future innovations.',
            'category': 'tech',
            'difficulty': 'medium',
            'reward': 2.50,
            'estimated_time': 10,
            'questions_count': 12,
            'max_participants': 50,
        },
        {
            'title': 'Health & Wellness Check',
            'description': 'Tell us about your health and wellness routines. This survey focuses on lifestyle and health habits.',
            'category': 'health',
            'difficulty': 'easy',
            'reward': 2.00,
            'estimated_time': 7,
            'questions_count': 10,
            'max_participants': 75,
        },
        {
            'title': 'Food & Dining Preferences',
            'description': 'Share your food preferences and dining habits. Help restaurants improve their services.',
            'category': 'food',
            'difficulty': 'easy',
            'reward': 1.00,
            'estimated_time': 4,
            'questions_count': 6,
            'max_participants': 150,
        },
        {
            'title': 'Travel & Tourism Survey',
            'description': 'Tell us about your travel experiences and preferences. This survey covers domestic and international travel.',
            'category': 'travel',
            'difficulty': 'medium',
            'reward': 3.00,
            'estimated_time': 12,
            'questions_count': 15,
            'max_participants': 40,
        },
        {
            'title': 'Financial Planning & Savings',
            'description': 'Share insights about your financial habits and planning strategies.',
            'category': 'finance',
            'difficulty': 'hard',
            'reward': 5.00,
            'estimated_time': 15,
            'questions_count': 20,
            'max_participants': 30,
        },
    ]
    
    for survey in surveys:
        cursor.execute('''
            INSERT INTO surveys (title, description, category, difficulty, reward, estimated_time, questions_count, max_participants)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            survey['title'], survey['description'], survey['category'],
            survey['difficulty'], survey['reward'], survey['estimated_time'],
            survey['questions_count'], survey['max_participants']
        ))
        survey_id = cursor.lastrowid
        
        # Add questions based on survey type
        questions = get_sample_questions(survey['category'])
        for i, q in enumerate(questions):
            cursor.execute('''
                INSERT INTO survey_questions (survey_id, question_text, question_type, options, question_order)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                survey_id, q['text'], q['type'],
                json.dumps(q.get('options')) if q.get('options') else None,
                i + 1
            ))
    
    # Create withdrawal methods
    methods = [
        ('EasyPaisa', '📱', 5.00, 500.00, '24-48 hours', 0, 'Provide your EasyPaisa account number'),
        ('JazzCash', '📱', 5.00, 500.00, '24-48 hours', 0, 'Provide your JazzCash account number'),
        ('PayPal', '💳', 10.00, 1000.00, '2-3 business days', 2.5, 'Provide your PayPal email'),
        ('Bank Transfer', '🏦', 20.00, 2000.00, '3-5 business days', 1.5, 'Provide bank account details'),
    ]
    
    for method in methods:
        cursor.execute('''
            INSERT INTO withdrawal_methods (name, icon, min_amount, max_amount, processing_time, fee_percentage, instructions)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', method)
    
    conn.commit()
    conn.close()

def get_sample_questions(category):
    """Get sample questions based on category"""
    questions = {
        'shopping': [
            {'text': 'How often do you shop online?', 'type': 'multiple_choice', 'options': ['Daily', 'Weekly', 'Monthly', 'Rarely', 'Never']},
            {'text': 'What is your preferred shopping method?', 'type': 'multiple_choice', 'options': ['Online only', 'In-store only', 'Both equally']},
            {'text': 'Rate your overall shopping satisfaction (1-5)', 'type': 'rating'},
            {'text': 'Do you use coupons or discount codes?', 'type': 'yes_no'},
            {'text': 'What factors influence your purchase decisions?', 'type': 'multiple_choice', 'options': ['Price', 'Quality', 'Brand', 'Reviews', 'Recommendations']},
            {'text': 'How much do you typically spend per month?', 'type': 'multiple_choice', 'options': ['Under $100', '$100-$300', '$300-$500', '$500-$1000', 'Over $1000']},
            {'text': 'What is your favorite online shopping platform?', 'type': 'text'},
            {'text': 'Would you recommend online shopping to others?', 'type': 'yes_no'},
        ],
        'tech': [
            {'text': 'How many devices do you own?', 'type': 'multiple_choice', 'options': ['1-2', '3-4', '5-6', '7+']},
            {'text': 'What is your primary device?', 'type': 'multiple_choice', 'options': ['Smartphone', 'Laptop', 'Desktop', 'Tablet']},
            {'text': 'Rate your tech-savviness (1-5)', 'type': 'rating'},
            {'text': 'Do you upgrade devices regularly?', 'type': 'yes_no'},
            {'text': 'Which operating system do you prefer?', 'type': 'multiple_choice', 'options': ['Windows', 'macOS', 'Linux', 'iOS', 'Android']},
            {'text': 'How important is technology in your daily life?', 'type': 'multiple_choice', 'options': ['Very important', 'Important', 'Neutral', 'Not important']},
            {'text': 'What tech product changed your life most?', 'type': 'text'},
            {'text': 'Do you use cloud services?', 'type': 'yes_no'},
            {'text': 'How much do you spend on tech annually?', 'type': 'multiple_choice', 'options': ['Under $500', '$500-$1000', '$1000-$2000', 'Over $2000']},
            {'text': 'Are you interested in AI technology?', 'type': 'yes_no'},
            {'text': 'What is your favorite tech brand?', 'type': 'text'},
            {'text': 'Would you recommend tech products to others?', 'type': 'yes_no'},
        ],
        'health': [
            {'text': 'How often do you exercise?', 'type': 'multiple_choice', 'options': ['Daily', '3-5 times/week', '1-2 times/week', 'Rarely', 'Never']},
            {'text': 'What type of exercise do you prefer?', 'type': 'multiple_choice', 'options': ['Cardio', 'Strength training', 'Yoga', 'Sports', 'Walking']},
            {'text': 'Rate your overall health (1-5)', 'type': 'rating'},
            {'text': 'Do you follow a specific diet?', 'type': 'yes_no'},
            {'text': 'How many hours of sleep do you get?', 'type': 'multiple_choice', 'options': ['Less than 5', '5-6', '7-8', '9+']},
            {'text': 'Do you take vitamins or supplements?', 'type': 'yes_no'},
            {'text': 'What is your biggest health concern?', 'type': 'text'},
            {'text': 'How often do you visit a doctor?', 'type': 'multiple_choice', 'options': ['Monthly', 'Quarterly', 'Annually', 'Rarely']},
            {'text': 'Do you practice meditation?', 'type': 'yes_no'},
            {'text': 'Rate your stress level (1-5)', 'type': 'rating'},
        ],
        'food': [
            {'text': 'How often do you eat out?', 'type': 'multiple_choice', 'options': ['Daily', 'Weekly', 'Monthly', 'Rarely', 'Never']},
            {'text': 'What is your favorite cuisine?', 'type': 'text'},
            {'text': 'Rate your cooking skills (1-5)', 'type': 'rating'},
            {'text': 'Do you have dietary restrictions?', 'type': 'yes_no'},
            {'text': 'What is your preferred meal delivery app?', 'type': 'multiple_choice', 'options': ['UberEats', 'DoorDash', 'Grubhub', 'Other', 'None']},
            {'text': 'How much do you spend on food monthly?', 'type': 'multiple_choice', 'options': ['Under $200', '$200-$400', '$400-$600', 'Over $600']},
        ],
        'travel': [
            {'text': 'How often do you travel?', 'type': 'multiple_choice', 'options': ['Monthly', 'Quarterly', 'Annually', 'Rarely']},
            {'text': 'What is your preferred travel type?', 'type': 'multiple_choice', 'options': ['Business', 'Leisure', 'Adventure', 'Cultural', 'Beach']},
            {'text': 'Rate your travel experience (1-5)', 'type': 'rating'},
            {'text': 'Do you travel domestically or internationally?', 'type': 'multiple_choice', 'options': ['Domestic only', 'Mostly domestic', 'Mostly international', 'International only']},
            {'text': 'What is your travel budget range?', 'type': 'multiple_choice', 'options': ['Under $500', '$500-$1000', '$1000-$3000', 'Over $3000']},
            {'text': 'Do you use travel booking websites?', 'type': 'yes_no'},
            {'text': 'What is your dream destination?', 'type': 'text'},
            {'text': 'Do you prefer solo or group travel?', 'type': 'multiple_choice', 'options': ['Solo', 'Couple', 'Family', 'Friends', 'Tour group']},
            {'text': 'How important is travel insurance?', 'type': 'multiple_choice', 'options': ['Very important', 'Important', 'Neutral', 'Not important']},
            {'text': 'Have you used Airbnb?', 'type': 'yes_no'},
            {'text': 'What is your preferred accommodation?', 'type': 'multiple_choice', 'options': ['Hotel', 'Hostel', 'Airbnb', 'Resort', 'Camping']},
            {'text': 'Do you travel for work?', 'type': 'yes_no'},
            {'text': 'Rate your last travel experience (1-5)', 'type': 'rating'},
            {'text': 'Would you recommend your favorite destination?', 'type': 'yes_no'},
            {'text': 'What is your travel planning method?', 'type': 'text'},
        ],
        'finance': [
            {'text': 'Do you have a monthly budget?', 'type': 'yes_no'},
            {'text': 'What is your savings rate?', 'type': 'multiple_choice', 'options': ['0-10%', '10-20%', '20-30%', '30%+']},
            {'text': 'Rate your financial knowledge (1-5)', 'type': 'rating'},
            {'text': 'Do you invest in stocks?', 'type': 'yes_no'},
            {'text': 'What is your primary income source?', 'type': 'multiple_choice', 'options': ['Salary', 'Business', 'Investments', 'Freelance', 'Other']},
            {'text': 'Do you have an emergency fund?', 'type': 'yes_no'},
            {'text': 'What is your biggest financial goal?', 'type': 'text'},
            {'text': 'How often do you review your finances?', 'type': 'multiple_choice', 'options': ['Weekly', 'Monthly', 'Quarterly', 'Annually', 'Never']},
            {'text': 'Do you use budgeting apps?', 'type': 'yes_no'},
            {'text': 'What is your debt level?', 'type': 'multiple_choice', 'options': ['None', 'Low', 'Moderate', 'High']},
            {'text': 'Do you have retirement savings?', 'type': 'yes_no'},
            {'text': 'Rate your financial stress (1-5)', 'type': 'rating'},
            {'text': 'What financial advice do you need?', 'type': 'text'},
            {'text': 'Do you have insurance?', 'type': 'yes_no'},
            {'text': 'What is your credit score range?', 'type': 'multiple_choice', 'options': ['Excellent', 'Good', 'Fair', 'Poor', 'Unknown']},
            {'text': 'Do you track your expenses?', 'type': 'yes_no'},
            {'text': 'What is your investment preference?', 'type': 'multiple_choice', 'options': ['Stocks', 'Bonds', 'Real Estate', 'Crypto', 'Mutual Funds']},
            {'text': 'Have you used financial advisors?', 'type': 'yes_no'},
            {'text': 'How confident are you in your financial future?', 'type': 'multiple_choice', 'options': ['Very confident', 'Confident', 'Neutral', 'Not confident']},
            {'text': 'What financial product interests you?', 'type': 'text'},
        ],
        'general': [
            {'text': 'How did you hear about us?', 'type': 'multiple_choice', 'options': ['Social Media', 'Friends', 'Search Engine', 'Advertisement', 'Other']},
            {'text': 'Rate your experience so far (1-5)', 'type': 'rating'},
            {'text': 'Would you recommend our platform?', 'type': 'yes_no'},
            {'text': 'What improvements would you suggest?', 'type': 'text'},
            {'text': 'How often do you participate in surveys?', 'type': 'multiple_choice', 'options': ['Daily', 'Weekly', 'Monthly', 'Rarely']},
            {'text': 'What topics interest you most?', 'type': 'multiple_choice', 'options': ['Technology', 'Health', 'Finance', 'Shopping', 'Entertainment']},
            {'text': 'Are you satisfied with the rewards?', 'type': 'yes_no'},
            {'text': 'What is your age group?', 'type': 'multiple_choice', 'options': ['18-24', '25-34', '35-44', '45-54', '55+']},
            {'text': 'What is your occupation?', 'type': 'text'},
            {'text': 'Would you participate again?', 'type': 'yes_no'},
        ],
    }
    return questions.get(category, questions['general'])

# =====================================================
# Session State Management
# =====================================================

def init_session_state():
    """Initialize session state variables"""
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'user_email' not in st.session_state:
        st.session_state.user_email = None
    if 'user_username' not in st.session_state:
        st.session_state.user_username = None
    if 'page' not in st.session_state:
        st.session_state.page = 'home'

# =====================================================
# Authentication Functions
# =====================================================

def register_user(username, email, password, country='Pakistan', referral_code=None):
    """Register a new user"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Check if email already exists
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            conn.close()
            return False, "Email already registered"
        
        # Check if username already exists
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            conn.close()
            return False, "Username already taken"
        
        # Create user
        password_hash = hash_password(password)
        user_referral_code = generate_referral_code()
        referred_by_id = None
        
        # Check referral code
        if referral_code:
            cursor.execute("SELECT id FROM users WHERE referral_code = ?", (referral_code,))
            referrer = cursor.fetchone()
            if referrer:
                referred_by_id = referrer[0]
        
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, balance, total_earned, is_verified, referral_code, referred_by)
            VALUES (?, ?, ?, 0, 0, 1, ?, ?)
        ''', (username, email, password_hash, user_referral_code, referred_by_id))
        
        user_id = cursor.lastrowid
        
        # Create user profile
        cursor.execute('''
            INSERT INTO user_profiles (user_id, country)
            VALUES (?, ?)
        ''', (user_id, country))
        
        # Give referral bonus if applicable
        if referred_by_id:
            cursor.execute("SELECT balance, total_earned FROM users WHERE id = ?", (referred_by_id,))
            referrer_data = cursor.fetchone()
            new_balance = referrer_data[0] + 1.00
            new_total = referrer_data[1] + 1.00
            
            cursor.execute('''
                UPDATE users SET balance = ?, total_earned = ? WHERE id = ?
            ''', (new_balance, new_total, referred_by_id))
            
            cursor.execute('''
                INSERT INTO transactions (user_id, type, amount, balance_after, description)
                VALUES (?, 'referral_bonus', 1.00, ?, ?)
            ''', (referred_by_id, new_balance, f'Referral bonus for {email}'))
            
            cursor.execute('''
                UPDATE user_profiles SET referral_earnings = referral_earnings + 1.00 WHERE user_id = ?
            ''', (referred_by_id,))
        
        conn.commit()
        conn.close()
        return True, "Registration successful!"
        
    except Exception as e:
        conn.rollback()
        conn.close()
        return False, f"Error: {str(e)}"

def login_user(email, password):
    """Login user"""
    conn = get_db()
    cursor = conn.cursor()
    
    password_hash = hash_password(password)
    cursor.execute('''
        SELECT id, username, email, balance, total_earned, total_withdrawn 
        FROM users 
        WHERE email = ? AND password_hash = ?
    ''', (email, password_hash))
    
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return True, {
            'id': user[0],
            'username': user[1],
            'email': user[2],
            'balance': user[3],
            'total_earned': user[4],
            'total_withdrawn': user[5]
        }
    else:
        return False, "Invalid email or password"

def get_user_data(user_id):
    """Get user data"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT u.id, u.username, u.email, u.balance, u.total_earned, u.total_withdrawn,
               u.referral_code, up.country, up.city, up.completed_surveys, up.referral_earnings
        FROM users u
        LEFT JOIN user_profiles up ON u.id = up.user_id
        WHERE u.id = ?
    ''', (user_id,))
    
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return {
            'id': user[0],
            'username': user[1],
            'email': user[2],
            'balance': user[3],
            'total_earned': user[4],
            'total_withdrawn': user[5],
            'referral_code': user[6],
            'country': user[7],
            'city': user[8],
            'completed_surveys': user[9],
            'referral_earnings': user[10]
        }
    return None

# =====================================================
# Survey Functions
# =====================================================

def get_all_surveys():
    """Get all active surveys"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, title, description, category, difficulty, reward, 
               estimated_time, questions_count, current_participants, max_participants
        FROM surveys
        WHERE is_active = 1
        ORDER BY created_at DESC
    ''')
    
    surveys = cursor.fetchall()
    conn.close()
    
    return [dict(s) for s in surveys]

def get_available_surveys(user_id):
    """Get surveys available for user"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, title, description, category, difficulty, reward, 
               estimated_time, questions_count, current_participants, max_participants
        FROM surveys
        WHERE is_active = 1
        AND id NOT IN (SELECT survey_id FROM survey_answers WHERE user_id = ?)
        ORDER BY created_at DESC
    ''', (user_id,))
    
    surveys = cursor.fetchall()
    conn.close()
    
    return [dict(s) for s in surveys]

def get_survey_by_id(survey_id):
    """Get survey details"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM surveys WHERE id = ?', (survey_id,))
    survey = cursor.fetchone()
    
    cursor.execute('''
        SELECT id, question_text, question_type, options, question_order
        FROM survey_questions
        WHERE survey_id = ?
        ORDER BY question_order
    ''', (survey_id,))
    
    questions = cursor.fetchall()
    conn.close()
    
    if survey:
        return {
            'id': survey[0],
            'title': survey[1],
            'description': survey[2],
            'category': survey[3],
            'difficulty': survey[4],
            'reward': survey[5],
            'estimated_time': survey[6],
            'questions_count': survey[7],
            'is_active': survey[8],
            'max_participants': survey[9],
            'current_participants': survey[10],
            'questions': [dict(q) for q in questions]
        }
    return None

def has_completed_survey(user_id, survey_id):
    """Check if user has completed survey"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT COUNT(*) FROM survey_answers 
        WHERE user_id = ? AND survey_id = ?
    ''', (user_id, survey_id))
    
    count = cursor.fetchone()[0]
    conn.close()
    
    return count > 0

def submit_survey(user_id, survey_id, answers):
    """Submit survey answers"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Get survey reward
        cursor.execute("SELECT reward, title FROM surveys WHERE id = ?", (survey_id,))
        survey = cursor.fetchone()
        reward = survey[0]
        title = survey[1]
        
        # Save survey answer
        cursor.execute('''
            INSERT INTO survey_answers (survey_id, user_id, answer_data, reward_earned)
            VALUES (?, ?, ?, ?)
        ''', (survey_id, user_id, json.dumps(answers), reward))
        
        # Update user balance
        cursor.execute('''
            UPDATE users 
            SET balance = balance + ?, total_earned = total_earned + ?
            WHERE id = ?
        ''', (reward, reward, user_id))
        
        # Get new balance
        cursor.execute("SELECT balance FROM users WHERE id = ?", (user_id,))
        new_balance = cursor.fetchone()[0]
        
        # Create transaction
        cursor.execute('''
            INSERT INTO transactions (user_id, type, amount, balance_after, description)
            VALUES (?, 'survey_reward', ?, ?, ?)
        ''', (user_id, reward, new_balance, f'Completed: {title}'))
        
        # Update survey participants
        cursor.execute('''
            UPDATE surveys 
            SET current_participants = current_participants + 1
            WHERE id = ?
        ''', (survey_id,))
        
        # Update user profile completed surveys
        cursor.execute('''
            UPDATE user_profiles 
            SET completed_surveys = completed_surveys + 1
            WHERE user_id = ?
        ''', (user_id,))
        
        # Check for referral bonus
        cursor.execute("SELECT referred_by FROM users WHERE id = ?", (user_id,))
        user_data = cursor.fetchone()
        
        if user_data[0]:
            referral_bonus = 0.10  # 10% of reward
            cursor.execute('''
                UPDATE users 
                SET balance = balance + ?, total_earned = total_earned + ?
                WHERE id = ?
            ''', (referral_bonus, referral_bonus, user_data[0]))
            
            cursor.execute("SELECT balance FROM users WHERE id = ?", (user_data[0],))
            referrer_balance = cursor.fetchone()[0]
            
            cursor.execute('''
                INSERT INTO transactions (user_id, type, amount, balance_after, description)
                VALUES (?, 'referral_bonus', ?, ?, ?)
            ''', (user_data[0], referral_bonus, referrer_balance, f'Referral earnings from user {user_id}'))
            
            cursor.execute('''
                UPDATE user_profiles 
                SET referral_earnings = referral_earnings + ?
                WHERE user_id = ?
            ''', (referral_bonus, user_data[0]))
        
        conn.commit()
        conn.close()
        return True, f"Survey completed! You earned ${reward:.2f}"
        
    except Exception as e:
        conn.rollback()
        conn.close()
        return False, f"Error: {str(e)}"

# =====================================================
# Payment Functions
# =====================================================

def get_withdrawal_methods():
    """Get all active withdrawal methods"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, name, icon, min_amount, max_amount, processing_time, fee_percentage, instructions
        FROM withdrawal_methods
        WHERE is_active = 1
        ORDER BY name
    ''')
    
    methods = cursor.fetchall()
    conn.close()
    
    return [dict(m) for m in methods]

def create_withdrawal(user_id, method_id, amount, account_number, account_name, payment_details):
    """Create withdrawal request"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Get user balance
        cursor.execute("SELECT balance FROM users WHERE id = ?", (user_id,))
        user_balance = cursor.fetchone()[0]
        
        if user_balance < amount:
            conn.close()
            return False, "Insufficient balance"
        
        # Get method details
        cursor.execute('''
            SELECT min_amount, max_amount, fee_percentage 
            FROM withdrawal_methods WHERE id = ?
        ''', (method_id,))
        method = cursor.fetchone()
        
        if amount < method[0]:
            conn.close()
            return False, f"Minimum withdrawal is ${method[0]:.2f}"
        
        if amount > method[1]:
            conn.close()
            return False, f"Maximum withdrawal is ${method[1]:.2f}"
        
        # Calculate fee
        fee = (amount * method[2]) / 100
        net_amount = amount - fee
        
        # Create withdrawal
        cursor.execute('''
            INSERT INTO withdrawals (user_id, method_id, amount, fee, net_amount, account_number, account_name, payment_details)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, method_id, amount, fee, net_amount, account_number, account_name, json.dumps(payment_details)))
        
        # Update user balance
        new_balance = user_balance - amount
        new_total_withdrawn = user_balance - amount  # This will be updated correctly
        
        cursor.execute('''
            UPDATE users 
            SET balance = ?, total_withdrawn = total_withdrawn + ?
            WHERE id = ?
        ''', (new_balance, amount, user_id))
        
        # Create transaction
        cursor.execute('''
            INSERT INTO transactions (user_id, type, amount, balance_after, description)
            VALUES (?, 'withdrawal', ?, ?, ?)
        ''', (user_id, amount, new_balance, f'Withdrawal via {method_id}'))
        
        conn.commit()
        conn.close()
        return True, "Withdrawal request submitted successfully!"
        
    except Exception as e:
        conn.rollback()
        conn.close()
        return False, f"Error: {str(e)}"

def get_user_transactions(user_id, limit=20):
    """Get user transactions"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, type, amount, balance_after, description, created_at
        FROM transactions
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT ?
    ''', (user_id, limit))
    
    transactions = cursor.fetchall()
    conn.close()
    
    return [dict(t) for t in transactions]

def get_user_withdrawals(user_id, limit=10):
    """Get user withdrawals"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT w.id, w.amount, w.fee, w.net_amount, w.status, w.account_number,
               wm.name as method_name, w.created_at
        FROM withdrawals w
        JOIN withdrawal_methods wm ON w.method_id = wm.id
        WHERE w.user_id = ?
        ORDER BY w.created_at DESC
        LIMIT ?
    ''', (user_id, limit))
    
    withdrawals = cursor.fetchall()
    conn.close()
    
    return [dict(w) for w in withdrawals]

# =====================================================
# Page Navigation
# =====================================================

def navigate_to(page):
    """Navigate to different page"""
    st.session_state.page = page

# =====================================================
# UI Components
# =====================================================

def render_sidebar():
    """Render sidebar navigation"""
    with st.sidebar:
        st.title("💰 SurveyRewards")
        
        if st.session_state.user_id:
            user_data = get_user_data(st.session_state.user_id)
            st.success(f"💵 Balance: ${user_data['balance']:.2f}")
            
            st.markdown("---")
            
            if st.button("🏠 Home", use_container_width=True):
                navigate_to('home')
            if st.button("📊 Dashboard", use_container_width=True):
                navigate_to('dashboard')
            if st.button("📝 Surveys", use_container_width=True):
                navigate_to('surveys')
            if st.button("💳 Withdraw", use_container_width=True):
                navigate_to('withdraw')
            if st.button("📜 Transactions", use_container_width=True):
                navigate_to('transactions')
            if st.button("❓ FAQ", use_container_width=True):
                navigate_to('faq')
            if st.button("ℹ️ About", use_container_width=True):
                navigate_to('about')
            
            st.markdown("---")
            
            if st.button("🚪 Logout", use_container_width=True, type="secondary"):
                st.session_state.user_id = None
                st.session_state.user_email = None
                st.session_state.user_username = None
                st.session_state.page = 'home'
                st.rerun()
        else:
            if st.button("🏠 Home", use_container_width=True):
                navigate_to('home')
            if st.button("📝 Available Surveys", use_container_width=True):
                navigate_to('surveys')
            if st.button("❓ FAQ", use_container_width=True):
                navigate_to('faq')
            if st.button("ℹ️ About", use_container_width=True):
                navigate_to('about')
            
            st.markdown("---")
            
            if st.button("🔑 Login", use_container_width=True):
                navigate_to('login')
            if st.button("📝 Register", use_container_width=True):
                navigate_to('register')

def render_home():
    """Render home/landing page"""
    st.title("🎯 Earn Money by Completing Surveys")
    st.markdown("Join thousands of users who are earning money daily by sharing their opinions!")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("💰 Total Paid Out", "$50,000+")
    with col2:
        st.metric("👥 Active Users", "10,000+")
    with col3:
        st.metric("📝 Surveys Available", "100+")
    
    st.markdown("---")
    
    st.subheader("🚀 How It Works")
    
    step1, step2, step3, step4 = st.columns(4)
    with step1:
        st.markdown("### 1️⃣ Register")
        st.write("Create your free account in seconds")
    with step2:
        st.markdown("### 2️⃣ Complete Surveys")
        st.write("Answer questions and earn rewards")
    with step3:
        st.markdown("### 3️⃣ Accumulate Balance")
        st.write("Watch your earnings grow")
    with step4:
        st.markdown("### 4️⃣ Withdraw")
        st.write("Cash out via EasyPaisa, JazzCash, PayPal & more")
    
    st.markdown("---")
    
    st.subheader("📋 Available Surveys")
    
    surveys = get_all_surveys()
    
    if surveys:
        cols = st.columns(2)
        for i, survey in enumerate(surveys[:6]):
            with cols[i % 2]:
                with st.container(border=True):
                    st.markdown(f"### {survey['title']}")
                    st.markdown(f"**Category:** {survey['category'].title()}")
                    st.markdown(f"**Difficulty:** {survey['difficulty'].title()}")
                    st.markdown(f"**Time:** {survey['estimated_time']} mins")
                    st.markdown(f"**Reward:** ${survey['reward']:.2f}")
                    
                    if st.button("View Details", key=f"survey_{survey['id']}"):
                        st.session_state.selected_survey = survey['id']
                        navigate_to('survey_detail')
                        st.rerun()
                    st.markdown("")
    else:
        st.info("No surveys available at the moment. Check back soon!")
    
    if not st.session_state.user_id:
        st.markdown("---")
        st.markdown("### Ready to start earning?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📝 Register Now", use_container_width=True, type="primary"):
                navigate_to('register')
                st.rerun()
        with col2:
            if st.button("🔑 Login", use_container_width=True):
                navigate_to('login')
                st.rerun()

def render_login():
    """Render login page"""
    st.title("🔑 Login")
    
    with st.form("login_form"):
        email = st.text_input("📧 Email")
        password = st.text_input("🔒 Password", type="password")
        
        submitted = st.form_submit_button("Login", use_container_width=True, type="primary")
        
        if submitted:
            if not email or not password:
                st.error("Please fill in all fields")
            else:
                success, result = login_user(email, password)
                if success:
                    st.session_state.user_id = result['id']
                    st.session_state.user_email = result['email']
                    st.session_state.user_username = result['username']
                    st.success(f"Welcome back, {result['email']}!")
                    navigate_to('dashboard')
                    st.rerun()
                else:
                    st.error(result)
    
    st.markdown("---")
    st.markdown("Don't have an account?")
    if st.button("📝 Register here"):
        navigate_to('register')
        st.rerun()

def render_register():
    """Render registration page"""
    st.title("📝 Create Account")
    
    with st.form("register_form"):
        col1, col2 = st.columns(2)
        with col1:
            username = st.text_input("👤 Username")
            email = st.text_input("📧 Email")
        with col2:
            password = st.text_input("🔒 Password", type="password")
            confirm_password = st.text_input("🔒 Confirm Password", type="password")
        
        country = st.selectbox("🌍 Country", ["Pakistan", "India", "Bangladesh", "USA", "UK", "Other"], index=0)
        referral_code = st.text_input("🎁 Referral Code (optional)")
        
        submitted = st.form_submit_button("Create Account", use_container_width=True, type="primary")
        
        if submitted:
            if not username or not email or not password:
                st.error("Please fill in all required fields")
            elif password != confirm_password:
                st.error("Passwords do not match")
            elif len(password) < 6:
                st.error("Password must be at least 6 characters")
            else:
                success, message = register_user(username, email, password, country, referral_code)
                if success:
                    st.success(message)
                    st.info("Please login with your credentials")
                    navigate_to('login')
                    st.rerun()
                else:
                    st.error(message)
    
    st.markdown("---")
    st.markdown("Already have an account?")
    if st.button("🔑 Login here"):
        navigate_to('login')
        st.rerun()

def render_dashboard():
    """Render user dashboard"""
    if not st.session_state.user_id:
        st.warning("Please login to view dashboard")
        navigate_to('login')
        st.rerun()
    
    user_data = get_user_data(st.session_state.user_id)
    
    st.title(f"📊 Welcome, {user_data['username']}!")
    
    # Balance cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("💰 Current Balance", f"${user_data['balance']:.2f}")
    with col2:
        st.metric("📈 Total Earned", f"${user_data['total_earned']:.2f}")
    with col3:
        st.metric("💸 Total Withdrawn", f"${user_data['total_withdrawn']:.2f}")
    with col4:
        st.metric("✅ Surveys Completed", user_data['completed_surveys'])
    
    st.markdown("---")
    
    # Referral code
    st.subheader("🎁 Your Referral Code")
    st.code(user_data['referral_code'])
    st.info(f"Share this code and earn $1.00 for each friend who joins! Referral earnings: ${user_data['referral_earnings']:.2f}")
    
    st.markdown("---")
    
    # Available surveys
    st.subheader("📝 Available Surveys")
    available_surveys = get_available_surveys(st.session_state.user_id)
    
    if available_surveys:
        for survey in available_surveys[:5]:
            with st.container(border=True):
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.markdown(f"**{survey['title']}**")
                    st.caption(f"{survey['estimated_time']} mins • ${survey['reward']:.2f}")
                with col2:
                    st.markdown(f"**${survey['reward']:.2f}**")
                with col3:
                    if st.button("Start", key=f"dash_survey_{survey['id']}"):
                        st.session_state.selected_survey = survey['id']
                        navigate_to('survey_detail')
                        st.rerun()
    else:
        st.info("No new surveys available. Check back soon!")
    
    st.markdown("---")
    
    # Recent transactions
    st.subheader("📜 Recent Transactions")
    transactions = get_user_transactions(st.session_state.user_id, limit=5)
    
    if transactions:
        for txn in transactions:
            icon = "💰" if txn['type'] == 'survey_reward' else "🎁" if txn['type'] == 'referral_bonus' else "💸"
            st.markdown(f"{icon} **{txn['description']}** - ${txn['amount']:.2f} - {txn['created_at']}")
    else:
        st.info("No transactions yet")

def render_surveys():
    """Render surveys listing page"""
    st.title("📝 Available Surveys")
    
    if st.session_state.user_id:
        surveys = get_available_surveys(st.session_state.user_id)
    else:
        surveys = get_all_surveys()
    
    if surveys:
        for survey in surveys:
            with st.container(border=True):
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                with col1:
                    st.markdown(f"### {survey['title']}")
                    st.markdown(f"**Category:** {survey['category'].title()}")
                    st.caption(f"Difficulty: {survey['difficulty'].title()}")
                with col2:
                    st.metric("Reward", f"${survey['reward']:.2f}")
                with col3:
                    st.metric("Time", f"{survey['estimated_time']} min")
                with col4:
                    if st.button("View", key=f"list_survey_{survey['id']}"):
                        st.session_state.selected_survey = survey['id']
                        navigate_to('survey_detail')
                        st.rerun()
                st.markdown("")
    else:
        st.info("No surveys available at the moment. Check back soon!")
        
        if not st.session_state.user_id:
            st.markdown("---")
            st.markdown("### Login to access exclusive surveys!")
            if st.button("🔑 Login"):
                navigate_to('login')
                st.rerun()

def render_survey_detail():
    """Render survey detail page"""
    if 'selected_survey' not in st.session_state:
        navigate_to('surveys')
        st.rerun()
    
    survey = get_survey_by_id(st.session_state.selected_survey)
    
    if not survey:
        st.error("Survey not found")
        navigate_to('surveys')
        st.rerun()
    
    # Check if user has completed this survey
    already_completed = False
    if st.session_state.user_id:
        already_completed = has_completed_survey(st.session_state.user_id, survey['id'])
    
    st.title(f"📋 {survey['title']}")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("💰 Reward", f"${survey['reward']:.2f}")
    with col2:
        st.metric("⏱️ Estimated Time", f"{survey['estimated_time']} mins")
    with col3:
        st.metric("📊 Difficulty", survey['difficulty'].title())
    
    st.markdown("---")
    
    st.subheader("📝 Description")
    st.write(survey['description'])
    
    st.markdown("---")
    
    st.subheader("❓ Questions")
    
    for i, question in enumerate(survey['questions'], 1):
        st.markdown(f"**Q{i}: {question['question_text']}**")
        
        if question['question_type'] == 'multiple_choice':
            options = json.loads(question['options']) if question['options'] else []
            st.radio("Select one:", options, key=f"q_{question['id']}", label_visibility="collapsed")
        elif question['question_type'] == 'rating':
            st.slider("Rate (1-5):", 1, 5, 3, key=f"q_{question['id']}", label_visibility="collapsed")
        elif question['question_type'] == 'yes_no':
            st.radio("Select:", ["Yes", "No"], key=f"q_{question['id']}", label_visibility="collapsed")
        elif question['question_type'] == 'text':
            st.text_input("Your answer:", key=f"q_{question['id']}", label_visibility="collapsed")
        
        st.markdown("")
    
    st.markdown("---")
    
    if already_completed:
        st.warning("You have already completed this survey!")
        if st.button("← Back to Surveys"):
            navigate_to('surveys')
            st.rerun()
    elif not st.session_state.user_id:
        st.info("Please login to complete this survey")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔑 Login", use_container_width=True):
                navigate_to('login')
                st.rerun()
        with col2:
            if st.button("📝 Register", use_container_width=True):
                navigate_to('register')
                st.rerun()
    else:
        if st.button("✅ Submit Survey", use_container_width=True, type="primary"):
            # Collect answers
            answers = {}
            for question in survey['questions']:
                answer_key = f"q_{question['id']}"
                if answer_key in st.session_state:
                    answers[str(question['id'])] = st.session_state[answer_key]
            
            success, message = submit_survey(
                st.session_state.user_id,
                survey['id'],
                answers
            )
            
            if success:
                st.success(message)
                navigate_to('dashboard')
                st.rerun()
            else:
                st.error(message)

def render_withdraw():
    """Render withdrawal page"""
    if not st.session_state.user_id:
        st.warning("Please login to withdraw")
        navigate_to('login')
        st.rerun()
    
    user_data = get_user_data(st.session_state.user_id)
    
    st.title("💳 Withdraw Funds")
    
    st.metric("💰 Available Balance", f"${user_data['balance']:.2f}")
    
    if user_data['balance'] < 5:
        st.warning("Minimum withdrawal is $5.00. Keep completing surveys!")
    
    st.markdown("---")
    
    methods = get_withdrawal_methods()
    
    if methods:
        with st.form("withdraw_form"):
            st.subheader("Select Withdrawal Method")
            
            method_options = {m['id']: f"{m['icon']} {m['name']} (Min: ${m['min_amount']:.2f}, Max: ${m['max_amount']:.2f})" for m in methods}
            selected_method = st.selectbox("Method", options=list(method_options.keys()), format_func=lambda x: method_options[x])
            
            amount = st.number_input("Amount ($)", min_value=0.01, max_value=user_data['balance'], value=5.00, step=0.01)
            
            col1, col2 = st.columns(2)
            with col1:
                account_number = st.text_input("Account Number")
            with col2:
                account_name = st.text_input("Account Name")
            
            additional_details = st.text_area("Additional Details (if required)")
            
            submitted = st.form_submit_button("Submit Withdrawal Request", use_container_width=True, type="primary")
            
            if submitted:
                if not account_number or not account_name:
                    st.error("Please fill in account details")
                elif amount < 5:
                    st.error("Minimum withdrawal is $5.00")
                elif amount > user_data['balance']:
                    st.error("Insufficient balance")
                else:
                    payment_details = {"additional": additional_details}
                    success, message = create_withdrawal(
                        st.session_state.user_id,
                        selected_method,
                        amount,
                        account_number,
                        account_name,
                        payment_details
                    )
                    
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
        
        st.markdown("---")
        
        # Show withdrawal history
        st.subheader("📜 Withdrawal History")
        withdrawals = get_user_withdrawals(st.session_state.user_id)
        
        if withdrawals:
            for w in withdrawals:
                status_emoji = "⏳" if w['status'] == 'pending' else "🔄" if w['status'] == 'processing' else "✅" if w['status'] == 'completed' else "❌"
                st.markdown(f"{status_emoji} **${w['amount']:.2f}** via {w['method_name']} - {w['status'].title()} - {w['created_at']}")
        else:
            st.info("No withdrawals yet")
    else:
        st.error("No withdrawal methods available")

def render_transactions():
    """Render transactions page"""
    if not st.session_state.user_id:
        st.warning("Please login to view transactions")
        navigate_to('login')
        st.rerun()
    
    st.title("📜 Transaction History")
    
    transactions = get_user_transactions(st.session_state.user_id, limit=50)
    
    if transactions:
        # Create DataFrame for better display
        df_data = []
        for txn in transactions:
            icon = "💰" if txn['type'] == 'survey_reward' else "🎁" if txn['type'] == 'referral_bonus' else "💸"
            df_data.append({
                'Date': txn['created_at'],
                'Type': txn['type'].replace('_', ' ').title(),
                'Description': txn['description'],
                'Amount': f"${txn['amount']:.2f}",
                'Balance After': f"${txn['balance_after']:.2f}"
            })
        
        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No transactions yet. Start completing surveys to earn rewards!")

def render_faq():
    """Render FAQ page"""
    st.title("❓ Frequently Asked Questions")
    
    faqs = [
        {
            'question': 'How do I earn money?',
            'answer': 'Simply register an account, complete surveys, and earn rewards. Each survey pays between $0.50 to $5.00 depending on length and complexity.'
        },
        {
            'question': 'How do I withdraw my earnings?',
            'answer': 'You can withdraw via JazzCash, EasyPaisa, PayPal, Bank Transfer, or Gift Cards. Minimum withdrawal is $5.00.'
        },
        {
            'question': 'How long does withdrawal take?',
            'answer': 'JazzCash and EasyPaisa: 24-48 hours. PayPal: 2-3 business days. Bank Transfer: 3-5 business days.'
        },
        {
            'question': 'Is this platform legitimate?',
            'answer': 'Yes! We are a registered company working with legitimate market research firms. Your data is protected with encryption.'
        },
        {
            'question': 'How do I get more surveys?',
            'answer': 'Complete your profile, verify your email, and check back daily. We send survey invitations based on your demographics.'
        },
        {
            'question': 'Can I refer friends?',
            'answer': 'Yes! Share your referral code and earn $1.00 bonus for each friend who joins and completes their first survey.'
        },
    ]
    
    for faq in faqs:
        with st.expander(faq['question']):
            st.write(faq['answer'])

def render_about():
    """Render about page"""
    st.title("ℹ️ About SurveyRewards")
    
    st.markdown("""
    ## 🎯 Our Mission
    
    SurveyRewards connects you with market research opportunities that pay you for your opinions. 
    We work with leading brands and research companies to bring you high-quality surveys.
    
    ## 💰 How It Works
    
    1. **Register** - Create your free account in seconds
    2. **Complete Surveys** - Answer questions honestly and earn rewards
    3. **Accumulate** - Watch your balance grow with each survey
    4. **Withdraw** - Cash out via your preferred payment method
    
    ## 🌟 Why Choose Us?
    
    - **High Rewards** - Earn up to $5.00 per survey
    - **Fast Payments** - Withdraw via EasyPaisa, JazzCash, PayPal & more
    - **Referral Program** - Earn $1.00 for each friend you refer
    - **Secure Platform** - Your data is protected with encryption
    - **24/7 Support** - We're here to help anytime
    
    ## 📊 Our Impact
    
    - **10,000+** Active Users
    - **$50,000+** Paid Out to Users
    - **100+** Available Surveys
    - **95%** User Satisfaction Rate
    
    ## 📞 Contact Us
    
    For support or inquiries, please reach out to us at:
    - 📧 Email: support@surveyrewards.com
    - 📱 Phone: +92-XXX-XXXXXXX
    
    ---
    
    *Thank you for being part of our community!*
    """)

# =====================================================
# Main App
# =====================================================

def main():
    """Main Streamlit app"""
    st.set_page_config(
        page_title="SurveyRewards - Earn Money Online",
        page_icon="💰",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize database
    init_db()
    create_sample_data()
    
    # Initialize session state
    init_session_state()
    
    # Render sidebar
    render_sidebar()
    
    # Main content area
    page = st.session_state.page
    
    if page == 'home':
        render_home()
    elif page == 'login':
        render_login()
    elif page == 'register':
        render_register()
    elif page == 'dashboard':
        render_dashboard()
    elif page == 'surveys':
        render_surveys()
    elif page == 'survey_detail':
        render_survey_detail()
    elif page == 'withdraw':
        render_withdraw()
    elif page == 'transactions':
        render_transactions()
    elif page == 'faq':
        render_faq()
    elif page == 'about':
        render_about()
    else:
        render_home()

if __name__ == "__main__":
    main()
