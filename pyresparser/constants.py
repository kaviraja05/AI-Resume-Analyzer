# Author: Resume Analyzer Constants

# Name patterns for spacy matcher (each pattern is a separate list)
NAME_PATTERNS = [
    [{'POS': 'PROPN'}, {'POS': 'PROPN'}],  # First name and Last name
    [{'POS': 'PROPN'}, {'POS': 'PROPN'}, {'POS': 'PROPN'}],  # First, Middle and Last name
    [{'POS': 'PROPN'}, {'POS': 'PROPN'}, {'POS': 'PROPN'}, {'POS': 'PROPN'}]  # First, Middle, Middle, Last name
]

# Skills database
SKILLS = [
    'python', 'java', 'javascript', 'html', 'css', 'sql', 'mysql', 'postgresql',
    'mongodb', 'react', 'angular', 'vue', 'node', 'express', 'django', 'flask',
    'spring', 'hibernate', 'git', 'docker', 'kubernetes', 'aws', 'azure', 'gcp',
    'machine learning', 'deep learning', 'data science', 'artificial intelligence',
    'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy', 'matplotlib',
    'tableau', 'power bi', 'excel', 'r', 'scala', 'spark', 'hadoop', 'kafka',
    'redis', 'elasticsearch', 'jenkins', 'ci/cd', 'agile', 'scrum', 'jira',
    'photoshop', 'illustrator', 'figma', 'sketch', 'ui/ux', 'wireframing',
    'prototyping', 'user research', 'usability testing', 'c++', 'c#', 'php',
    'ruby', 'swift', 'kotlin', 'go', 'rust', 'typescript', 'sass', 'less',
    'bootstrap', 'tailwind', 'material-ui', 'redux', 'vuex', 'graphql', 'rest',
    'api', 'microservices', 'serverless', 'lambda', 'firebase', 'heroku',
    'netlify', 'vercel', 'linux', 'ubuntu', 'centos', 'windows', 'macos',
    'bash', 'powershell', 'vim', 'emacs', 'vscode', 'intellij', 'eclipse',
    'android', 'ios', 'react native', 'flutter', 'xamarin', 'unity', 'unreal',
    'blender', 'maya', '3ds max', 'after effects', 'premiere pro', 'final cut',
    'wordpress', 'drupal', 'joomla', 'shopify', 'magento', 'woocommerce',
    'seo', 'sem', 'google analytics', 'google ads', 'facebook ads', 'social media',
    'content marketing', 'email marketing', 'copywriting', 'technical writing',
    'project management', 'product management', 'business analysis', 'data analysis',
    'financial modeling', 'accounting', 'bookkeeping', 'quickbooks', 'sap', 'erp',
    'crm', 'salesforce', 'hubspot', 'mailchimp', 'slack', 'teams', 'zoom',
    'communication', 'leadership', 'teamwork', 'problem solving', 'critical thinking',
    'time management', 'organization', 'attention to detail', 'creativity',
    'adaptability', 'customer service', 'sales', 'negotiation', 'presentation'
]

# Job roles and their associated skills
JOB_ROLES = {
    'Data Scientist': [
        'python', 'r', 'machine learning', 'deep learning', 'data science',
        'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy', 'matplotlib',
        'sql', 'statistics', 'data analysis', 'data visualization'
    ],
    'Web Developer': [
        'html', 'css', 'javascript', 'react', 'angular', 'vue', 'node',
        'express', 'django', 'flask', 'php', 'mysql', 'postgresql', 'mongodb'
    ],
    'Mobile Developer': [
        'android', 'ios', 'react native', 'flutter', 'swift', 'kotlin',
        'java', 'objective-c', 'xamarin', 'unity'
    ],
    'DevOps Engineer': [
        'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'jenkins', 'ci/cd',
        'linux', 'bash', 'terraform', 'ansible', 'monitoring'
    ],
    'UI/UX Designer': [
        'ui/ux', 'figma', 'sketch', 'photoshop', 'illustrator', 'wireframing',
        'prototyping', 'user research', 'usability testing', 'design thinking'
    ],
    'Backend Developer': [
        'python', 'java', 'node', 'express', 'django', 'flask', 'spring',
        'sql', 'mongodb', 'redis', 'api', 'microservices'
    ],
    'Frontend Developer': [
        'html', 'css', 'javascript', 'react', 'angular', 'vue', 'typescript',
        'sass', 'bootstrap', 'webpack', 'responsive design'
    ],
    'Full Stack Developer': [
        'html', 'css', 'javascript', 'react', 'node', 'express', 'python',
        'django', 'sql', 'mongodb', 'git', 'api'
    ],
    'Machine Learning Engineer': [
        'python', 'machine learning', 'deep learning', 'tensorflow', 'pytorch',
        'scikit-learn', 'pandas', 'numpy', 'docker', 'kubernetes', 'mlops'
    ],
    'Software Engineer': [
        'python', 'java', 'javascript', 'c++', 'data structures', 'algorithms',
        'git', 'testing', 'debugging', 'problem solving'
    ]
}

# Course recommendations based on skills
COURSE_RECOMMENDATIONS = {
    'python': [
        'Python for Everybody Specialization - University of Michigan',
        'Complete Python Bootcamp - Udemy',
        'Python Crash Course - No Starch Press'
    ],
    'machine learning': [
        'Machine Learning Course - Andrew Ng (Coursera)',
        'Machine Learning A-Z - Udemy',
        'Hands-On Machine Learning - O\'Reilly'
    ],
    'web development': [
        'The Complete Web Developer Course - Udemy',
        'Full Stack Web Development - FreeCodeCamp',
        'Web Development Bootcamp - The Odin Project'
    ],
    'data science': [
        'Data Science Specialization - Johns Hopkins University',
        'Applied Data Science with Python - University of Michigan',
        'Data Science Course - Kaggle Learn'
    ],
    'react': [
        'React - The Complete Guide - Udemy',
        'React Fundamentals - React Training',
        'Full Stack Open - University of Helsinki'
    ],
    'aws': [
        'AWS Certified Solutions Architect - A Cloud Guru',
        'AWS Fundamentals - Amazon Web Services',
        'AWS Cloud Practitioner Essentials'
    ]
}

# Experience levels
EXPERIENCE_LEVELS = {
    'Fresher': 0,
    'Junior': 1,
    'Mid-Level': 3,
    'Senior': 5,
    'Lead': 8,
    'Principal': 10
}

# Resume tips
RESUME_TIPS = [
    "Add more technical skills relevant to your target job role",
    "Include quantifiable achievements and metrics in your experience",
    "Add relevant certifications to boost your profile",
    "Include links to your portfolio, GitHub, or LinkedIn profile",
    "Use action verbs to describe your accomplishments",
    "Keep your resume concise and well-formatted",
    "Tailor your resume for each job application",
    "Include relevant keywords from the job description",
    "Add a professional summary at the top",
    "Proofread for grammar and spelling errors"
]

# Skill categories
SKILL_CATEGORIES = {
    'Programming Languages': [
        'python', 'java', 'javascript', 'c++', 'c#', 'php', 'ruby', 'swift',
        'kotlin', 'go', 'rust', 'typescript', 'scala', 'r'
    ],
    'Web Technologies': [
        'html', 'css', 'react', 'angular', 'vue', 'node', 'express', 'django',
        'flask', 'spring', 'bootstrap', 'sass', 'less'
    ],
    'Databases': [
        'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'sql',
        'nosql', 'sqlite', 'oracle', 'cassandra'
    ],
    'Cloud & DevOps': [
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'ci/cd',
        'terraform', 'ansible', 'linux', 'bash'
    ],
    'Data Science & ML': [
        'machine learning', 'deep learning', 'data science', 'tensorflow',
        'pytorch', 'scikit-learn', 'pandas', 'numpy', 'matplotlib', 'tableau'
    ],
    'Design': [
        'ui/ux', 'figma', 'sketch', 'photoshop', 'illustrator', 'wireframing',
        'prototyping', 'user research', 'usability testing'
    ],
    'Mobile Development': [
        'android', 'ios', 'react native', 'flutter', 'xamarin', 'unity'
    ],
    'Soft Skills': [
        'communication', 'leadership', 'teamwork', 'problem solving',
        'critical thinking', 'time management', 'creativity', 'adaptability'
    ]
}
