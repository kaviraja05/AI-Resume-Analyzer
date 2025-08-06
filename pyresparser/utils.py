# Author: Resume Analyzer Utils

import io
import os
import re
import nltk
import pandas as pd
import docx2txt
from datetime import datetime
from dateutil import relativedelta
from . import constants as cs
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFSyntaxError
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')


def extract_text_from_pdf(pdf_path):
    '''
    Helper function to extract the plain text from .pdf files
    '''
    if isinstance(pdf_path, str):
        # for local pdf file
        try:
            with open(pdf_path, 'rb') as fh:
                for page in PDFPage.get_pages(
                        fh,
                        caching=True,
                        check_extractable=True
                ):
                    resource_manager = PDFResourceManager()
                    fake_file_handle = io.StringIO()
                    converter = TextConverter(
                        resource_manager,
                        fake_file_handle,
                        codec='utf-8',
                        laparams=LAParams()
                    )
                    page_interpreter = PDFPageInterpreter(
                        resource_manager,
                        converter
                    )
                    page_interpreter.process_page(page)

                    text = fake_file_handle.getvalue()
                    yield text

                    # close open handles
                    converter.close()
                    fake_file_handle.close()
        except PDFSyntaxError:
            return
    else:
        # extract text from remote pdf file
        try:
            for page in PDFPage.get_pages(
                    pdf_path,
                    caching=True,
                    check_extractable=True
            ):
                resource_manager = PDFResourceManager()
                fake_file_handle = io.StringIO()
                converter = TextConverter(
                    resource_manager,
                    fake_file_handle,
                    codec='utf-8',
                    laparams=LAParams()
                )
                page_interpreter = PDFPageInterpreter(
                    resource_manager,
                    converter
                )
                page_interpreter.process_page(page)

                text = fake_file_handle.getvalue()
                yield text

                # close open handles
                converter.close()
                fake_file_handle.close()
        except PDFSyntaxError:
            return


def extract_text_from_docx(docx_path):
    '''
    Helper function to extract plain text from .docx files
    '''
    try:
        text = docx2txt.process(docx_path)
        return text
    except Exception:
        return ''


def extract_text_from_doc(doc_path):
    '''
    Helper function to extract plain text from .doc files
    '''
    try:
        import subprocess
        cmd = ['antiword', doc_path]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        return stdout.decode('utf-8')
    except Exception:
        return ''


def extract_text(file_path, extension):
    '''
    Wrapper function to detect the file extension and call text
    extraction function accordingly
    '''
    text = ''
    if extension == '.pdf':
        for page in extract_text_from_pdf(file_path):
            text += ' ' + page
    elif extension == '.docx':
        text = extract_text_from_docx(file_path)
    elif extension == '.doc':
        text = extract_text_from_doc(file_path)
    return text


def get_number_of_pages(file_name):
    try:
        if isinstance(file_name, io.BytesIO):
            # for remote pdf file
            count = 0
            for page in PDFPage.get_pages(
                        file_name,
                        caching=True,
                        check_extractable=True
            ):
                count += 1
            return count
        else:
            # for local pdf file
            if file_name.endswith('.pdf'):
                count = 0
                with open(file_name, 'rb') as fh:
                    for page in PDFPage.get_pages(
                            fh,
                            caching=True,
                            check_extractable=True
                    ):
                        count += 1
                return count
            else:
                return None
    except PDFSyntaxError:
        return None


def extract_name(nlp_text, matcher=None):
    '''
    Helper function to extract name from spacy nlp text
    Uses simple entity recognition instead of complex patterns
    '''
    # Primary method: Use spaCy's built-in named entity recognition
    for ent in nlp_text.ents:
        if ent.label_ == "PERSON":
            return ent.text

    # Fallback method: Look for capitalized words at the beginning
    text_lines = nlp_text.text.split('\n')
    for line in text_lines[:10]:  # Check first 10 lines
        line = line.strip()
        if line and not any(keyword in line.lower() for keyword in ['email', 'phone', 'address', 'objective', 'summary']):
            words = line.split()
            if len(words) >= 2:
                # Check if first two words are capitalized (likely a name)
                if all(word[0].isupper() and word.isalpha() for word in words[:2]):
                    return ' '.join(words[:2])

    return None


def extract_email(text):
    '''
    Helper function to extract email id from text
    '''
    email = re.findall(r"([^@|\s]+@[^@]+\.[^@|\s]+)", text)
    if email:
        try:
            return email[0].split()[0].strip(';')
        except IndexError:
            return None


def extract_mobile_number(text, custom_regex=None):
    '''
    Helper function to extract mobile number from text
    '''
    if custom_regex:
        mob_num = re.findall(custom_regex, text)
    else:
        mob_num = re.findall(r'[\+]?[1-9]?[0-9]{7,14}', text)
    
    if mob_num:
        return mob_num[0]
    return None


def extract_skills(nlp_text, noun_chunks, skills_file=None):
    '''
    Helper function to extract skills from spacy nlp text
    '''
    tokens = [token.text for token in nlp_text if not token.is_stop]
    
    # Default skills list
    default_skills = [
        'python', 'java', 'javascript', 'html', 'css', 'sql', 'mysql', 'postgresql',
        'mongodb', 'react', 'angular', 'vue', 'node', 'express', 'django', 'flask',
        'spring', 'hibernate', 'git', 'docker', 'kubernetes', 'aws', 'azure', 'gcp',
        'machine learning', 'deep learning', 'data science', 'artificial intelligence',
        'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy', 'matplotlib',
        'tableau', 'power bi', 'excel', 'r', 'scala', 'spark', 'hadoop', 'kafka',
        'redis', 'elasticsearch', 'jenkins', 'ci/cd', 'agile', 'scrum', 'jira',
        'photoshop', 'illustrator', 'figma', 'sketch', 'ui/ux', 'wireframing',
        'prototyping', 'user research', 'usability testing'
    ]
    
    skills = []
    text_lower = nlp_text.text.lower()
    
    for skill in default_skills:
        if skill.lower() in text_lower:
            skills.append(skill)
    
    return list(set(skills))


def extract_entities_wih_custom_model(nlp_text):
    '''
    Helper function to extract entities with custom model
    '''
    entities = {}
    
    # Extract degree information
    degree_patterns = [
        r'bachelor', r'master', r'phd', r'doctorate', r'diploma', r'certificate',
        r'b\.?tech', r'b\.?e', r'm\.?tech', r'm\.?e', r'b\.?sc', r'm\.?sc',
        r'b\.?com', r'm\.?com', r'b\.?a', r'm\.?a', r'mba', r'bba'
    ]
    
    degrees = []
    text_lower = nlp_text.text.lower()
    for pattern in degree_patterns:
        matches = re.findall(pattern, text_lower)
        degrees.extend(matches)
    
    entities['Degree'] = list(set(degrees)) if degrees else None
    
    # Extract name (fallback)
    names = []
    for ent in nlp_text.ents:
        if ent.label_ == "PERSON":
            names.append(ent.text)
    
    entities['Name'] = names if names else None
    
    return entities


def extract_entity_sections_grad(text):
    '''
    Helper function to extract entity sections
    '''
    entities = {}
    
    # Extract education section
    education_section = re.search(
        r'education.*?(?=experience|skills|projects|$)',
        text.lower(),
        re.DOTALL
    )
    
    if education_section:
        entities['education'] = education_section.group()
    
    return entities
