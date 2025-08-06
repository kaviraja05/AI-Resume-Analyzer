# 🚀 Quick Start Guide - AI Resume Analyzer

## 🔧 Installation

### Option 1: Automatic Installation (Recommended)
```bash
python install_requirements.py
```

### Option 2: Manual Installation
```bash
pip install streamlit pandas plotly spacy nltk pdfminer.six docx2txt python-dateutil geocoder geopy
python -m spacy download en_core_web_sm
```

## 🏃‍♂️ Running the Application

### Option 1: Using Batch File (Windows)
Double-click `run_app.bat`

### Option 2: Command Line
```bash
cd App
streamlit run App.py
```

### Option 3: Custom Port
```bash
cd App
streamlit run App.py --server.port 8502
```

## 🌐 Accessing the Application

Open your browser and go to:
- **Default**: http://localhost:8501
- **Custom port**: http://localhost:8502

## 🎯 Features Overview

### 🏠 User Dashboard
1. **Enter Personal Info**: Name, email, mobile number
2. **Upload Resume**: PDF, DOCX, or TXT format
3. **Get Analysis**: Instant AI-powered analysis
4. **View Results**: Score, predictions, and recommendations

### 👨‍💼 Admin Panel
1. **Login**: Username: `admin`, Password: `admin@resume-analyzer`
2. **View Analytics**: User data and statistics
3. **Export Data**: Download CSV files
4. **Manage Feedback**: Review user feedback

### 💬 Feedback System
1. **Rate Experience**: 5-star rating system
2. **Leave Comments**: Detailed feedback
3. **Help Improve**: Contribute to development

## 📄 Sample Resume

Use the provided `sample_resume.txt` file to test the application features.

## 🎨 UI Features

- **Professional Design**: Purple/violet gradient theme
- **Responsive Layout**: Works on all screen sizes
- **Interactive Elements**: Modern cards and buttons
- **Real-time Updates**: Instant analysis results

## 🔍 Analysis Features

- **Resume Score**: 100-point comprehensive scoring
- **Job Field Prediction**: AI-powered career field identification
- **Experience Level**: Automatic classification
- **Skill Detection**: Technical and soft skills extraction
- **Recommendations**: Personalized improvement suggestions

## 🛠️ Troubleshooting

### Common Issues

1. **Module Not Found Error**
   ```bash
   pip install [missing-module]
   ```

2. **spaCy Model Missing**
   ```bash
   python -m spacy download en_core_web_sm
   ```

3. **Port Already in Use**
   ```bash
   streamlit run App.py --server.port 8502
   ```

4. **Database Issues**
   - Delete `resume_analyzer.db` file and restart the app

### Getting Help

1. Check the console output for error messages
2. Ensure all dependencies are installed
3. Try running with a different port
4. Use the feedback system within the app

## 📚 Documentation

For detailed information, see:
- `ENHANCED_README.md` - Complete documentation
- `README.md` - Original project documentation

## 🎉 Enjoy!

Your AI Resume Analyzer is now ready to help improve resumes and careers!
