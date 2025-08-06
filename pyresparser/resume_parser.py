import os
import io
import spacy
import json
import multiprocessing as mp
from spacy.matcher import Matcher
from . import utils  # Make sure your `utils.py` is in the same directory


class ResumeParser:
    def __init__(self, resume, skills_file=None, custom_regex=None):
        # Load the standard SpaCy model
        try:
            self.nlp_model = spacy.load('en_core_web_sm')
        except Exception as e:
            raise RuntimeError(f"Failed to load SpaCy model: {e}")

        self.__skills_file = skills_file
        self.__custom_regex = custom_regex
        self.__matcher = Matcher(self.nlp_model.vocab)
        self.__details = {
            'name': None,
            'email': None,
            'mobile_number': None,
            'skills': None,
            'degree': None,
            'no_of_pages': None,
        }

        self.__resume = resume

        # Determine file extension
        try:
            if isinstance(self.__resume, io.BytesIO):
                ext = self.__resume.name.split('.')[-1]
            else:
                ext = os.path.splitext(self.__resume)[1].split('.')[-1]
        except Exception:
            ext = 'pdf'  # fallback to PDF

        # Extract text
        self.__text_raw = utils.extract_text(self.__resume, '.' + ext)
        if not self.__text_raw:
            raise ValueError("Could not extract text from resume.")

        self.__text = ' '.join(self.__text_raw.split())
        self.__nlp = self.nlp_model(self.__text)
        self.__noun_chunks = list(self.__nlp.noun_chunks)

        self.__get_basic_details()

    def get_extracted_data(self):
        return self.__details

    def __get_basic_details(self):
        try:
            name = utils.extract_name(self.__nlp, matcher=self.__matcher)
            email = utils.extract_email(self.__text)
            mobile = utils.extract_mobile_number(self.__text, self.__custom_regex)
            skills = utils.extract_skills(self.__nlp, self.__noun_chunks, self.__skills_file)
            cust_ent = utils.extract_entities_wih_custom_model(self.__nlp)
            entities = utils.extract_entity_sections_grad(self.__text_raw)

            # Populate details dictionary
            self.__details['name'] = cust_ent.get('Name', [name])[0]
            self.__details['email'] = email
            self.__details['mobile_number'] = mobile
            self.__details['skills'] = skills
            self.__details['degree'] = cust_ent.get('Degree', None)
            self.__details['no_of_pages'] = utils.get_number_of_pages(self.__resume)

        except Exception as e:
            raise RuntimeError(f"Failed to extract basic details: {e}")


def resume_result_wrapper(resume):
    try:
        parser = ResumeParser(resume)
        return parser.get_extracted_data()
    except Exception as e:
        return {'error': str(e), 'file': resume}


if __name__ == '__main__':
    resumes_dir = 'resumes'
    if not os.path.exists(resumes_dir):
        raise FileNotFoundError("The 'resumes' folder was not found.")

    resumes = []
    for root, dirs, files in os.walk(resumes_dir):
        for filename in files:
            if filename.endswith(('.pdf', '.docx')):
                resumes.append(os.path.join(root, filename))

    pool = mp.Pool(mp.cpu_count())
    results = [pool.apply_async(resume_result_wrapper, args=(r,)) for r in resumes]
    pool.close()
    pool.join()

    output = [res.get() for res in results]

    # Save or print results
    with open("output.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=4, ensure_ascii=False)

    print("Extraction complete. Results saved to 'output.json'")
