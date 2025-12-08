
import re
import math
from collections import Counter
from django.conf import settings


class ApplicationMatcher:
    def __init__(self, job, application, resume_text=""):
        self.job = job
        self.application = application
        self.resume_text = resume_text or ""
        
        # Weights for different matching criteria
        self.weights = {
            'skills': 0.60,
            'description': 0.30,
            'experience': 0.10
        }

    def _normalize_text(self, text):
        """Converts text to lowercase and removes punctuation."""
        if not text:
            return ""
        text = text.lower()
        return re.sub(r'[^\w\s]', '', text)

    def _get_tokens(self, text):
        """Simple tokenizer that removes common stopwords."""
        stopwords = {'and', 'the', 'is', 'in', 'at', 'of', 'or', 'a', 'an', 'to', 'for', 'with', 'on'}
        words = self._normalize_text(text).split()
        return [w for w in words if w not in stopwords]

    def calculate_skill_match(self):
        """Calculates Jaccard similarity between job skills and applicant resume."""
        job_skills = set()
        
        if hasattr(self.job, 'skills'):
            for skill in self.job.skills.all():
                job_skills.add(skill.name.lower())
        
        app_text = self._normalize_text(self.application.description or "")
        app_text += " " + self._normalize_text(self.resume_text)
        
        matched_skills = 0
        if not job_skills:
            return 100.0 # No skills required
            
        for skill in job_skills:
            if skill in app_text:
                matched_skills += 1
        return (matched_skills / len(job_skills)) * 100.0

    def calculate_description_similarity(self):
        """Calculates Cosine Similarity between Job Description and Resume Text."""
        text1 = self._get_tokens(self.job.description)
        
        # Use resume text as primary source, fallback to description if empty
        source_text = self.resume_text if self.resume_text else self.application.description
        text2 = self._get_tokens(source_text)
        
        if not text1 or not text2:
            return 0.0

        vec1 = Counter(text1)
        vec2 = Counter(text2)

        intersection = set(vec1.keys()) & set(vec2.keys())
        numerator = sum([vec1[x] * vec2[x] for x in intersection])

        sum1 = sum([vec1[x]**2 for x in vec1.keys()])
        sum2 = sum([vec2[x]**2 for x in vec2.keys()])
        denominator = math.sqrt(sum1) * math.sqrt(sum2)

        if not denominator:
            return 0.0
        
        return float(numerator) / denominator * 100.0

    def calculate_match_score(self):
        """Returns the final weighted matching score (0-100)."""
        try:
            skill_score = self.calculate_skill_match()
            desc_score = self.calculate_description_similarity()
            
            # Use resume text to guess experience if possible (very simple heuristic)
            # e.g. look for "5 years", "2015-2020"
            experience_score = 50.0 
            if "years" in self.resume_text.lower():
                 experience_score = 70.0
            
            final_score = (
                (skill_score * self.weights['skills']) +
                (desc_score * self.weights['description']) +
                (experience_score * self.weights['experience'])
            )
            
            return min(100.0, max(0.0, final_score))
            
        except Exception as e:
            print(f"Error calculating AI score: {e}")
            return 0.0

# Example Integration:
# score = ApplicationMatcher(job, app, resume_text=extracted_text).calculate_match_score()
