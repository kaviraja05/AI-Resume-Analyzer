# --- Built-in & External Imports ---
import streamlit as st
import os
import socket
import platform
import secrets
try:
    import geocoder
    from geopy.geocoders import Nominatim
    from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
    GEOCODER_AVAILABLE = True
except ImportError:
    GEOCODER_AVAILABLE = False
import sys
import datetime
import sqlite3
import pandas as pd
try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
import re
import random
from datetime import datetime as dt
import base64

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Try to import the resume parser, fallback to simple text extraction if not available
try:
    from pyresparser.resume_parser import ResumeParser
    RESUME_PARSER_AVAILABLE = True
except ImportError:
    RESUME_PARSER_AVAILABLE = False
    st.warning("Advanced resume parsing not available. Using basic text extraction.")

try:
    import nltk
    nltk.download('stopwords', quiet=True)
    nltk.download('punkt', quiet=True)
    nltk.download('wordnet', quiet=True)
except ImportError:
    pass

# --- Database Setup ---
def init_database():
    """Initialize SQLite database for storing user data and feedback"""
    conn = sqlite3.connect('resume_analyzer.db')
    cursor = conn.cursor()

    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            mobile TEXT,
            resume_score INTEGER,
            predicted_field TEXT,
            experience_level TEXT,
            skills TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            ip_address TEXT,
            city TEXT,
            state TEXT,
            country TEXT
        )
    ''')

    # Create feedback table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            rating INTEGER,
            comments TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()

# --- Simple Resume Parser (Fallback) ---
def simple_resume_parser(text):
    """Simple text-based resume parsing when advanced parser is not available"""
    data = {}

    # Extract email
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    data['email'] = emails[0] if emails else None

    # Extract phone numbers
    phone_pattern = r'[\+]?[1-9]?[0-9]{7,14}'
    phones = re.findall(phone_pattern, text)
    data['mobile_number'] = phones[0] if phones else None

    # Extract skills (basic keyword matching)
    skills_keywords = [
        'python', 'java', 'javascript', 'html', 'css', 'sql', 'react', 'angular',
        'node', 'django', 'flask', 'machine learning', 'data science', 'aws',
        'docker', 'kubernetes', 'git', 'mongodb', 'postgresql', 'mysql'
    ]

    found_skills = []
    text_lower = text.lower()
    for skill in skills_keywords:
        if skill in text_lower:
            found_skills.append(skill)

    data['skills'] = found_skills
    data['name'] = None  # Will be filled from user input
    data['no_of_pages'] = 1  # Default

    return data

# --- Skill Recommendations ---
def get_skill_recommendations(current_skills, predicted_field):
    """Get skill recommendations based on current skills and predicted field"""

    field_skills = {
        'Data Science': ['python', 'r', 'machine learning', 'pandas', 'numpy', 'matplotlib', 'seaborn', 'scikit-learn', 'tensorflow', 'pytorch'],
        'Web Development': ['html', 'css', 'javascript', 'react', 'angular', 'vue', 'node.js', 'express', 'mongodb', 'postgresql'],
        'Mobile Development': ['android', 'ios', 'react native', 'flutter', 'swift', 'kotlin'],
        'DevOps': ['docker', 'kubernetes', 'aws', 'azure', 'jenkins', 'terraform', 'ansible'],
        'Backend Development': ['python', 'java', 'node.js', 'django', 'spring', 'sql', 'mongodb', 'redis'],
        'Frontend Development': ['html', 'css', 'javascript', 'react', 'angular', 'vue', 'typescript', 'sass']
    }

    if predicted_field in field_skills:
        recommended = []
        for skill in field_skills[predicted_field]:
            if skill.lower() not in [s.lower() for s in current_skills]:
                recommended.append(skill)
        return recommended[:5]  # Return top 5 recommendations

    return []

# --- Experience Level Prediction ---
def predict_experience_level(skills, text):
    """Predict experience level based on skills and resume content"""
    skill_count = len(skills)
    text_length = len(text.split())

    # Simple heuristic based on skills count and resume length
    if skill_count >= 15 and text_length > 500:
        return "Senior"
    elif skill_count >= 10 and text_length > 300:
        return "Mid-Level"
    elif skill_count >= 5 and text_length > 200:
        return "Junior"
    else:
        return "Fresher"

# --- Job Field Prediction ---
def predict_job_field(skills):
    """Predict job field based on skills"""

    field_keywords = {
        'Data Science': ['python', 'r', 'machine learning', 'data science', 'pandas', 'numpy', 'matplotlib', 'tensorflow', 'pytorch'],
        'Web Development': ['html', 'css', 'javascript', 'react', 'angular', 'vue', 'node', 'express', 'django', 'flask'],
        'Mobile Development': ['android', 'ios', 'react native', 'flutter', 'swift', 'kotlin'],
        'DevOps': ['docker', 'kubernetes', 'aws', 'azure', 'jenkins', 'terraform', 'ansible', 'ci/cd'],
        'Backend Development': ['python', 'java', 'node', 'django', 'spring', 'sql', 'mongodb', 'api'],
        'Frontend Development': ['html', 'css', 'javascript', 'react', 'angular', 'vue', 'typescript']
    }

    field_scores = {}
    skills_lower = [skill.lower() for skill in skills]

    for field, keywords in field_keywords.items():
        score = sum(1 for keyword in keywords if keyword in skills_lower)
        field_scores[field] = score

    if field_scores:
        return max(field_scores, key=field_scores.get)
    return "General Software Development"

# --- Resume Scoring ---
def calculate_resume_score(data, text):
    """Calculate resume score based on various factors"""
    score = 0

    # Basic information (20 points)
    if data.get('name'): score += 5
    if data.get('email'): score += 5
    if data.get('mobile_number'): score += 5
    if len(text.split()) > 100: score += 5

    # Skills (30 points)
    skills_count = len(data.get('skills', []))
    if skills_count >= 10: score += 30
    elif skills_count >= 7: score += 25
    elif skills_count >= 5: score += 20
    elif skills_count >= 3: score += 15
    elif skills_count >= 1: score += 10

    # Content quality (30 points)
    text_length = len(text.split())
    if text_length > 500: score += 30
    elif text_length > 300: score += 25
    elif text_length > 200: score += 20
    elif text_length > 100: score += 15

    # Professional keywords (20 points)
    professional_keywords = ['experience', 'project', 'achievement', 'responsibility', 'developed', 'managed', 'led', 'created']
    keyword_count = sum(1 for keyword in professional_keywords if keyword.lower() in text.lower())
    score += min(keyword_count * 3, 20)

    return min(score, 100)  # Cap at 100

# --- Utility: Safe Geolocation ---
def safe_reverse_geocode(latlong):
    if not GEOCODER_AVAILABLE:
        return "Unavailable", "Unavailable", "Unavailable"

    try:
        geolocator = Nominatim(user_agent="resume-analyzer")
        location = geolocator.reverse(latlong, language='en', timeout=10)
        address = location.raw.get('address', {})
        city = address.get('city', '')
        state = address.get('state', '')
        country = address.get('country', '')
        return city, state, country
    except (GeocoderTimedOut, GeocoderUnavailable):
        return "Unknown", "Unknown", "Unknown"
    except Exception as e:
        print(f"[Geocoding Error] {e}")
        return "Error", "Error", "Error"

# --- Initialize Database ---
init_database()

# --- Custom CSS for Professional Look ---
def load_css():
    st.markdown("""
    <style>
    /* Hide Streamlit branding and menu */
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    header {visibility: hidden !important;}
    .stDeployButton {display: none !important;}
    .stDecoration {display: none !important;}

    /* Hide deploy button and menu with multiple selectors */
    button[title="Deploy"] {display: none !important;}
    .css-1rs6os {display: none !important;}
    .css-17eq0hr {display: none !important;}
    [data-testid="stToolbar"] {display: none !important;}
    .css-1544g2n {display: none !important;}
    .css-1v0mbdj {display: none !important;}

    /* Hide "Made with Streamlit" */
    .css-1dp5vir {display: none !important;}
    .css-hi6a2p {display: none !important;}

    .main {
        padding-top: 2rem;
    }
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    }
    .css-1d391kg {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    }

    /* Ensure text is readable on gradient background */
    .stMarkdown, .stText, p, h1, h2, h3, h4, h5, h6 {
        color: white !important;
    }

    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    }

    /* Input fields with better contrast */
    .stTextInput > div > div > input {
        background-color: rgba(255, 255, 255, 0.9) !important;
        color: #333 !important;
        border: 2px solid #667eea !important;
    }
    .stSelectbox > div > div {
        background-color: rgba(255, 255, 255, 0.9) !important;
        color: #333 !important;
        border: 2px solid #667eea !important;
        border-radius: 8px !important;
    }
    .stTextInput > div > div > input {
        background-color: rgba(255, 255, 255, 0.9) !important;
        color: #333 !important;
        border: 2px solid #667eea !important;
        border-radius: 8px !important;
    }
    .stFileUploader > div {
        background-color: rgba(255, 255, 255, 0.9) !important;
        border: 2px dashed #667eea !important;
        border-radius: 10px !important;
        color: #333 !important;
    }
    .metric-card {
        background: linear-gradient(135deg, #88C999 0%, #5D737E 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .skill-tag {
        background: linear-gradient(135deg, #FF6B6B 0%, #4ECDC4 100%);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        margin: 0.2rem;
        display: inline-block;
        font-size: 0.8rem;
    }
    .recommendation-card {
        background: linear-gradient(135deg, #FFA726 0%, #FB8C00 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        color: white;
    }
    .score-card {
        background: linear-gradient(135deg, #66BB6A 0%, #43A047 100%);
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        color: white;
        font-size: 1.2rem;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Streamlit UI ---
st.set_page_config(
    page_title='AI Resume Analyzer',
    layout='wide',
    page_icon="📄",
    initial_sidebar_state="expanded"
)



load_css()

# Header with gradient background
st.markdown("""
<div style='background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 10px; margin-bottom: 2rem;'>
    <h1 style='color: white; text-align: center; margin: 0; font-size: 3rem;'>🤖 AI Resume Analyzer</h1>
    <p style='color: white; text-align: center; margin: 0; font-size: 1.2rem;'>Analyze, Score, and Improve Your Resume with AI</p>
</div>
""", unsafe_allow_html=True)

# Sidebar with professional styling
st.sidebar.markdown("""
<div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1rem; border-radius: 10px; margin-bottom: 1rem;'>
    <h2 style='color: white; text-align: center; margin: 0;'>Navigation</h2>
</div>
""", unsafe_allow_html=True)

menu = ["🏠 User Dashboard", "👨‍💼 Admin Panel", "💬 Feedback", "ℹ️ About"]
choice = st.sidebar.selectbox("Choose Your Role", menu)

# --- USER DASHBOARD SECTION ---
if choice == "🏠 User Dashboard":
    st.markdown("### 📋 Resume Analysis Dashboard")

    # Create two columns for better layout
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("#### 📝 Personal Information")
        act_name = st.text_input('Full Name*', placeholder="Enter your full name")
        act_mail = st.text_input('Email Address*', placeholder="your.email@example.com")
        act_mob = st.text_input('Mobile Number*', placeholder="+1234567890")

        st.markdown("#### 📄 Upload Your Resume")
        uploaded_file = st.file_uploader(
            "Choose your resume file",
            type=["pdf", "docx", "txt"],
            help="Upload your resume in PDF, DOCX, or TXT format"
        )

    with col2:
        st.markdown("#### 🎯 Quick Stats")
        st.info("📊 Upload your resume to see detailed analytics")
        st.info("🎯 Get personalized recommendations")
        st.info("📈 Track your resume score")

    # System info collection
    sec_token = secrets.token_urlsafe(12)
    host_name = socket.gethostname()
    ip_add = socket.gethostbyname(host_name)
    dev_user = os.getlogin()
    os_name_ver = platform.system() + " " + platform.release()

    # Geolocation
    if GEOCODER_AVAILABLE:
        try:
            g = geocoder.ip('me')
            latlong = g.latlng if g.latlng else [0, 0]
            city, state, country = safe_reverse_geocode(latlong)
        except Exception as e:
            print(f"[Geolocation Error] {e}")
            city, state, country = "Unavailable", "Unavailable", "Unavailable"
    else:
        city, state, country = "Unavailable", "Unavailable", "Unavailable"

    if uploaded_file is not None and act_name.strip() and act_mail.strip():
        # Read file content
        if uploaded_file.type == "application/pdf":
            # For PDF files, save and process
            with open("uploaded_resume.pdf", "wb") as f:
                f.write(uploaded_file.read())

            with st.spinner('🔍 Analyzing your resume...'):
                if RESUME_PARSER_AVAILABLE:
                    try:
                        data = ResumeParser("uploaded_resume.pdf").get_extracted_data()
                        # Read text for additional analysis
                        with open("uploaded_resume.pdf", "rb") as f:
                            # Simple text extraction fallback
                            resume_text = str(uploaded_file.getvalue())
                        st.success("✅ Advanced AI parsing completed!")
                    except Exception as e:
                        st.warning(f"⚠️ Advanced parsing failed: {str(e)[:100]}... Using fallback method.")
                        resume_text = str(uploaded_file.getvalue())
                        data = simple_resume_parser(resume_text)
                        st.info("✅ Fallback parsing completed!")
                else:
                    resume_text = str(uploaded_file.getvalue())
                    data = simple_resume_parser(resume_text)
                    st.info("✅ Basic parsing completed!")
        else:
            # For text files
            resume_text = str(uploaded_file.read(), "utf-8")
            with st.spinner('🔍 Analyzing your resume...'):
                data = simple_resume_parser(resume_text)

        # Update data with user input
        data['name'] = act_name
        if not data.get('email'):
            data['email'] = act_mail
        if not data.get('mobile_number'):
            data['mobile_number'] = act_mob

        # Perform analysis
        predicted_field = predict_job_field(data.get('skills', []))
        experience_level = predict_experience_level(data.get('skills', []), resume_text)
        resume_score = calculate_resume_score(data, resume_text)
        skill_recommendations = get_skill_recommendations(data.get('skills', []), predicted_field)

        st.success("✅ Resume analysis complete!")

        # Display results in organized sections
        st.markdown("---")

        # Score Card
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="score-card">
                <h3>Resume Score</h3>
                <h1>{resume_score}/100</h1>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h4>🎯 Predicted Field</h4>
                <h3>{predicted_field}</h3>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h4>📊 Experience Level</h4>
                <h3>{experience_level}</h3>
            </div>
            """, unsafe_allow_html=True)

        # Extracted Information
        st.markdown("### 📋 Extracted Information")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 👤 Personal Details")
            st.write(f"**Name:** {data.get('name', 'Not found')}")
            st.write(f"**Email:** {data.get('email', 'Not found')}")
            st.write(f"**Mobile:** {data.get('mobile_number', 'Not found')}")
            st.write(f"**Resume Pages:** {data.get('no_of_pages', 'N/A')}")

        with col2:
            st.markdown("#### 🛠️ Skills Found")
            skills = data.get('skills', [])
            if skills:
                skills_html = ""
                for skill in skills:
                    skills_html += f'<span class="skill-tag">{skill}</span>'
                st.markdown(skills_html, unsafe_allow_html=True)
            else:
                st.write("No specific skills detected. Consider adding more technical skills to your resume.")

        # Recommendations Section
        if skill_recommendations:
            st.markdown("### 💡 Skill Recommendations")
            st.markdown(f"""
            <div class="recommendation-card">
                <h4>🎯 Recommended Skills for {predicted_field}</h4>
                <p>Based on your current skills and target field, consider learning:</p>
            </div>
            """, unsafe_allow_html=True)

            rec_cols = st.columns(len(skill_recommendations))
            for i, skill in enumerate(skill_recommendations):
                with rec_cols[i]:
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #FF9800 0%, #F57C00 100%);
                                padding: 0.8rem; border-radius: 8px; text-align: center; color: white; margin: 0.2rem;">
                        <strong>{skill}</strong>
                    </div>
                    """, unsafe_allow_html=True)

        # Course Recommendations
        st.markdown("### 📚 Course Recommendations")
        course_recommendations = {
            'Data Science': [
                "Machine Learning Specialization - Andrew Ng (Coursera)",
                "Python for Data Science - IBM (Coursera)",
                "Data Science Professional Certificate - IBM"
            ],
            'Web Development': [
                "Full Stack Web Development - FreeCodeCamp",
                "The Complete Web Developer Course - Udemy",
                "React - The Complete Guide - Udemy"
            ],
            'Mobile Development': [
                "Android Development for Beginners - Google",
                "iOS App Development with Swift - Apple",
                "React Native - The Practical Guide - Udemy"
            ]
        }

        if predicted_field in course_recommendations:
            for course in course_recommendations[predicted_field]:
                st.markdown(f"📖 {course}")

        # Resume Tips
        st.markdown("### 💡 Resume Improvement Tips")
        tips = [
            "🎯 Add more quantifiable achievements (e.g., 'Increased efficiency by 25%')",
            "🔧 Include more technical skills relevant to your target role",
            "📊 Add project descriptions with technologies used",
            "🏆 Include certifications and professional development",
            "📝 Use action verbs to describe your accomplishments",
            "🔗 Add links to your portfolio, GitHub, or LinkedIn profile"
        ]

        for tip in tips:
            st.markdown(f"- {tip}")

        # Save to database
        try:
            conn = sqlite3.connect('resume_analyzer.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (name, email, mobile, resume_score, predicted_field,
                                 experience_level, skills, ip_address, city, state, country)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (act_name, act_mail, act_mob, resume_score, predicted_field,
                  experience_level, ', '.join(skills), ip_add, city, state, country))
            conn.commit()
            conn.close()
            st.success("✅ Your data has been saved for analytics!")
        except Exception as e:
            st.error(f"Error saving data: {e}")

    elif uploaded_file is not None:
        # Debug information
        missing_fields = []
        if not act_name.strip():
            missing_fields.append("Name")
        if not act_mail.strip():
            missing_fields.append("Email")

        if missing_fields:
            st.warning(f"⚠️ Please fill in the following required fields: {', '.join(missing_fields)}")
        else:
            st.error("⚠️ Unexpected validation error. Please try again.")

    else:
        st.info("👆 Please upload your resume and fill in your details to get started!")

# --- ADMIN PANEL SECTION ---
elif choice == "👨‍💼 Admin Panel":
    st.markdown("### 🔐 Admin Dashboard")

    # Simple authentication
    if 'admin_logged_in' not in st.session_state:
        st.session_state.admin_logged_in = False

    if not st.session_state.admin_logged_in:
        st.markdown("#### 🔑 Admin Login")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            admin_user = st.text_input("Username", placeholder="admin")
            admin_pass = st.text_input("Password", type="password", placeholder="admin@resume-analyzer")

            if st.button("🔓 Login", use_container_width=True):
                if admin_user == "admin" and admin_pass == "admin@resume-analyzer":
                    st.session_state.admin_logged_in = True
                    st.success("✅ Login successful!")
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials!")

    else:
        # Admin Dashboard Content
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("#### 👋 Welcome, Admin!")
        with col2:
            if st.button("🚪 Logout"):
                st.session_state.admin_logged_in = False
                st.rerun()

        # Admin Guide
        with st.expander("📖 Admin Panel Guide - Click to expand"):
            st.markdown("""
            ### 🎯 What You Can Do in Admin Panel

            #### 📊 **Analytics Tab**
            - **View Charts**: Experience level and job field distribution pie charts
            - **Monitor Trends**: See what types of users are using the system
            - **Track Patterns**: Identify popular career fields and experience levels

            #### 👥 **User Data Tab**
            - **View All Users**: Complete list of all users who uploaded resumes
            - **User Details**: Name, email, mobile, resume score, predicted field, experience level
            - **Download Data**: Export all user data as CSV file for external analysis
            - **Track Activity**: See timestamps of when users used the system

            #### 💬 **Feedback Tab**
            - **Read Reviews**: See all user feedback and ratings (1-5 stars)
            - **Monitor Satisfaction**: Track user satisfaction levels
            - **Improvement Ideas**: Read user suggestions for system improvements
            - **Response Management**: View detailed comments from users

            #### 📈 **Charts Tab**
            - **Resume Score Distribution**: See how users are scoring overall
            - **Geographic Data**: View top countries using the system
            - **Performance Metrics**: Analyze system usage patterns

            #### 🔧 **Key Admin Actions**
            1. **Monitor System Health**: Check if users are getting good scores
            2. **Export Data**: Download CSV files for reporting
            3. **Analyze Feedback**: Improve system based on user suggestions
            4. **Track Usage**: Monitor how many people are using the system
            5. **Quality Control**: Ensure the AI is working correctly

            #### 📋 **Best Practices**
            - **Regular Monitoring**: Check the dashboard weekly
            - **Data Export**: Download data monthly for backup
            - **Feedback Review**: Read feedback to improve the system
            - **Performance Tracking**: Monitor average resume scores
            """)

        st.markdown("---")

        # Fetch data from database
        try:
            conn = sqlite3.connect('resume_analyzer.db')

            # User data
            users_df = pd.read_sql_query("SELECT * FROM users ORDER BY timestamp DESC", conn)
            feedback_df = pd.read_sql_query("SELECT * FROM feedback ORDER BY timestamp DESC", conn)

            conn.close()

            # Dashboard metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("👥 Total Users", len(users_df))
            with col2:
                avg_score = users_df['resume_score'].mean() if not users_df.empty else 0
                st.metric("📊 Avg Resume Score", f"{avg_score:.1f}")
            with col3:
                st.metric("💬 Total Feedback", len(feedback_df))
            with col4:
                avg_rating = feedback_df['rating'].mean() if not feedback_df.empty else 0
                st.metric("⭐ Avg Rating", f"{avg_rating:.1f}")

            # Tabs for different views
            tab1, tab2, tab3, tab4 = st.tabs(["📊 Analytics", "👥 User Data", "💬 Feedback", "📈 Charts"])

            with tab1:
                st.markdown("#### 📊 Analytics Overview")
                if not users_df.empty:
                    col1, col2 = st.columns(2)

                    with col1:
                        # Experience level distribution
                        exp_counts = users_df['experience_level'].value_counts()
                        if PLOTLY_AVAILABLE:
                            fig_exp = px.pie(values=exp_counts.values, names=exp_counts.index,
                                            title="Experience Level Distribution")
                            st.plotly_chart(fig_exp, use_container_width=True)
                        else:
                            st.subheader("Experience Level Distribution")
                            st.bar_chart(exp_counts)

                    with col2:
                        # Predicted field distribution
                        field_counts = users_df['predicted_field'].value_counts()
                        if PLOTLY_AVAILABLE:
                            fig_field = px.pie(values=field_counts.values, names=field_counts.index,
                                              title="Predicted Field Distribution")
                            st.plotly_chart(fig_field, use_container_width=True)
                        else:
                            st.subheader("Predicted Field Distribution")
                            st.bar_chart(field_counts)
                else:
                    st.info("No user data available yet.")

            with tab2:
                st.markdown("#### 👥 User Data Management")
                if not users_df.empty:
                    st.dataframe(users_df, use_container_width=True)

                    # Download CSV
                    csv = users_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download User Data as CSV",
                        data=csv,
                        file_name=f"user_data_{dt.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                else:
                    st.info("No user data available.")

            with tab3:
                st.markdown("#### 💬 User Feedback")
                if not feedback_df.empty:
                    for _, feedback in feedback_df.iterrows():
                        with st.expander(f"Feedback from {feedback['name']} - {'⭐' * feedback['rating']}"):
                            st.write(f"**Email:** {feedback['email']}")
                            st.write(f"**Rating:** {'⭐' * feedback['rating']} ({feedback['rating']}/5)")
                            st.write(f"**Comments:** {feedback['comments']}")
                            st.write(f"**Date:** {feedback['timestamp']}")
                else:
                    st.info("No feedback available yet.")

            with tab4:
                st.markdown("#### 📈 Detailed Charts")
                if not users_df.empty:
                    # Resume score distribution
                    if PLOTLY_AVAILABLE:
                        fig_scores = px.histogram(users_df, x='resume_score', nbins=20,
                                                title="Resume Score Distribution")
                        st.plotly_chart(fig_scores, use_container_width=True)
                    else:
                        st.subheader("Resume Score Distribution")
                        score_counts = users_df['resume_score'].value_counts().sort_index()
                        st.bar_chart(score_counts)

                    # Location distribution
                    if 'country' in users_df.columns:
                        country_counts = users_df['country'].value_counts().head(10)
                        if PLOTLY_AVAILABLE:
                            fig_country = px.bar(x=country_counts.index, y=country_counts.values,
                                               title="Top 10 Countries")
                            st.plotly_chart(fig_country, use_container_width=True)
                        else:
                            st.subheader("Top 10 Countries")
                            st.bar_chart(country_counts)
                else:
                    st.info("No data available for charts.")

        except Exception as e:
            st.error(f"Error loading admin data: {e}")

# --- FEEDBACK SECTION ---
elif choice == "💬 Feedback":
    st.markdown("### 💬 Share Your Feedback")

    st.markdown("""
    <div class="recommendation-card">
        <h4>🌟 Help Us Improve!</h4>
        <p>Your feedback is valuable to us. Please share your experience and suggestions.</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("feedback_form"):
        col1, col2 = st.columns(2)
        with col1:
            feedback_name = st.text_input("Your Name*")
            feedback_email = st.text_input("Your Email*")
        with col2:
            feedback_rating = st.selectbox("Rating*", [5, 4, 3, 2, 1],
                                         format_func=lambda x: "⭐" * x + f" ({x}/5)")

        feedback_comments = st.text_area("Comments and Suggestions*",
                                       placeholder="Tell us about your experience...")

        submitted = st.form_submit_button("📤 Submit Feedback", use_container_width=True)

        if submitted:
            if feedback_name and feedback_email and feedback_comments:
                try:
                    conn = sqlite3.connect('resume_analyzer.db')
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO feedback (name, email, rating, comments)
                        VALUES (?, ?, ?, ?)
                    ''', (feedback_name, feedback_email, feedback_rating, feedback_comments))
                    conn.commit()
                    conn.close()
                    st.success("✅ Thank you for your feedback!")
                except Exception as e:
                    st.error(f"Error saving feedback: {e}")
            else:
                st.error("❌ Please fill in all required fields.")

# --- ABOUT SECTION ---
elif choice == 'ℹ️ About':
    st.markdown("### ℹ️ About AI Resume Analyzer")

    # Hero section
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 2rem; border-radius: 15px; color: white; text-align: center; margin-bottom: 2rem;'>
        <h2>🤖 AI-Powered Resume Analysis</h2>
        <p style='font-size: 1.1rem; margin: 0;'>
            Transform your resume with intelligent analysis, personalized recommendations, and professional insights.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Features section
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="metric-card">
            <h4>🔍 Smart Analysis</h4>
            <p>Advanced NLP algorithms extract key information from your resume including skills, experience, and qualifications.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="metric-card">
            <h4>📊 Intelligent Scoring</h4>
            <p>Get a comprehensive resume score based on industry standards and best practices.</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="metric-card">
            <h4>💡 Personalized Tips</h4>
            <p>Receive tailored recommendations to improve your resume and increase your chances of success.</p>
        </div>
        """, unsafe_allow_html=True)

    # How it works
    st.markdown("### 🚀 How It Works")

    steps = [
        ("1️⃣", "Upload Resume", "Upload your resume in PDF, DOCX, or TXT format"),
        ("2️⃣", "AI Analysis", "Our AI analyzes your resume for skills, experience, and content quality"),
        ("3️⃣", "Get Insights", "Receive detailed analysis, score, and personalized recommendations"),
        ("4️⃣", "Improve", "Apply suggestions to enhance your resume and career prospects")
    ]

    for icon, title, description in steps:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #88C999 0%, #5D737E 100%);
                    padding: 1rem; border-radius: 10px; margin: 0.5rem 0; color: white;'>
            <h4>{icon} {title}</h4>
            <p style='margin: 0;'>{description}</p>
        </div>
        """, unsafe_allow_html=True)

    # Features list
    st.markdown("### ✨ Key Features")

    features = [
        "🎯 **Job Field Prediction** - Identifies your target career field based on skills",
        "📈 **Experience Level Assessment** - Determines your professional experience level",
        "🛠️ **Skills Extraction** - Automatically identifies technical and soft skills",
        "💯 **Resume Scoring** - Comprehensive scoring based on multiple criteria",
        "📚 **Course Recommendations** - Suggests relevant courses for skill development",
        "👨‍💼 **Admin Dashboard** - Analytics and user management for administrators",
        "💬 **Feedback System** - Collect and analyze user feedback",
        "📊 **Data Analytics** - Detailed insights and visualizations"
    ]

    for feature in features:
        st.markdown(f"- {feature}")

    # Technology stack
    st.markdown("### 🛠️ Technology Stack")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **Frontend & UI:**
        - 🎨 Streamlit for interactive web interface
        - 📊 Plotly for data visualizations
        - 🎯 Custom CSS for professional styling
        """)

    with col2:
        st.markdown("""
        **Backend & AI:**
        - 🐍 Python for core functionality
        - 🧠 spaCy for natural language processing
        - 🗄️ SQLite for data storage
        - 📄 PDF/DOCX parsing libraries
        """)

    # Contact and support
    st.markdown("### 📞 Support & Contact")

    st.markdown("""
    <div class="recommendation-card">
        <h4>🤝 Need Help?</h4>
        <p>If you encounter any issues or have suggestions for improvement, please use our feedback system
        or contact our support team. We're here to help you succeed!</p>
    </div>
    """, unsafe_allow_html=True)

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 2rem; border-radius: 15px; text-align: center;
                color: white; margin-top: 2rem; box-shadow: 0 4px 15px rgba(0,0,0,0.2);'>
        <h3 style='margin: 0; font-size: 1.5rem;'>🤖 AI Resume Analyzer</h3>
        <p style='margin: 0.5rem 0; font-size: 1.1rem; opacity: 0.9;'>Empowering careers through intelligent analysis</p>
        <p style='margin: 0; font-size: 1rem; font-weight: bold;'>Built with ❤️ using Python, Streamlit, and AI</p>
    </div>
    """, unsafe_allow_html=True)
