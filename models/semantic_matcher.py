from sentence_transformers import SentenceTransformer, util
from typing import Dict, List, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from utils.preprocessing import normalize_skill_set, flatten_experience_description
import config

class SemanticMatcher:
    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize the Sentence-BERT model for semantic matching and prepare TF-IDF.
        """
        self.model = SentenceTransformer(model_name or config.SENTENCE_BERT_MODEL)
        self._job_embedding = None
        self._bert_weight = config.SEMANTIC_BERT_WEIGHT
        self._tfidf_weight = config.SEMANTIC_TFIDF_WEIGHT
        self._tfidf_vectorizer: Optional[TfidfVectorizer] = None
        self._tfidf_job_vec = None

    def _build_job_text(self, job_data: Dict) -> str:
        return f"{job_data.get('title','')} {job_data.get('description','')} " \
               f"{' '.join(job_data.get('required_skills', []))} {' '.join(job_data.get('preferred_skills', []))}"

    def compute_similarity(self, job_data: Dict, resume_data: Dict) -> float:
        """
        Compute semantic similarity between job description and resume.
        Uses job title + description + required skills vs resume skills + experience text.
        """
        # Build job text
        job_text = self._build_job_text(job_data)

        # Build resume text safely - extract from various skill structures
        skills_data = resume_data.get('skills', {})
        technical_skills_data = resume_data.get('technical_skills', {})

        # Flatten and normalize skills
        resume_raw_skills: List[str] = []
        for skill_source in (skills_data, technical_skills_data):
            if isinstance(skill_source, dict):
                for _, skill_list in skill_source.items():
                    if isinstance(skill_list, list):
                        resume_raw_skills.extend([s for s in skill_list if isinstance(s, str)])
            elif isinstance(skill_source, list):
                resume_raw_skills.extend([s for s in skill_source if isinstance(s, str)])
        normalized_skills = normalize_skill_set(resume_raw_skills)
        resume_skills = ' '.join(sorted(normalized_skills))

        # Experience text (handle list or string descriptions)
        exp_text = " ".join([
            flatten_experience_description(exp)
            for exp in resume_data.get('experience', [])
        ])
        resume_text = f"{resume_skills} {exp_text}".strip()

        # BERT similarity with cached job embedding
        if self._job_embedding is None:
            self._job_embedding = self.model.encode([job_text], convert_to_tensor=True)[0]
        resume_embedding = self.model.encode([resume_text], convert_to_tensor=True)[0]
        bert_sim = float(util.cos_sim(self._job_embedding, resume_embedding).item())

        # TF-IDF similarity (initialize vectorizer once per run)
        if self._tfidf_vectorizer is None:
            self._tfidf_vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2), max_features=20000)
            self._tfidf_job_vec = self._tfidf_vectorizer.fit_transform([job_text])
        resume_vec = self._tfidf_vectorizer.transform([resume_text])
        tfidf_sim = float(cosine_similarity(self._tfidf_job_vec, resume_vec).ravel()[0])

        # Blend similarities
        blended = self._bert_weight * bert_sim + self._tfidf_weight * tfidf_sim
        return max(0.0, min(1.0, blended))

    def compute_skill_coverage(self, job_data: Dict, resume_data: Dict) -> float:
        """
        Compute coverage of required skills in the resume.
        """
        required = set([s.lower() for s in job_data.get('required_skills', [])])

        # Extract and normalize skills from various structures
        skills_data = resume_data.get('skills', {})
        technical_skills_data = resume_data.get('technical_skills', {})
        resume_raw_skills: List[str] = []
        for skill_source in (skills_data, technical_skills_data):
            if isinstance(skill_source, dict):
                for _, skill_list in skill_source.items():
                    if isinstance(skill_list, list):
                        resume_raw_skills.extend([s for s in skill_list if isinstance(s, str)])
            elif isinstance(skill_source, list):
                resume_raw_skills.extend([s for s in skill_source if isinstance(s, str)])
        resume_skills = normalize_skill_set(resume_raw_skills)

        if not required:
            return 0.0
        return len(required & resume_skills) / float(len(required))

    def compute_composite_score(self, job_data: Dict, resume_data: Dict) -> float:
        """
        Combine semantic similarity and skill coverage into a composite score (0-100).
        """
        semantic = self.compute_similarity(job_data, resume_data)
        skill_coverage = self.compute_skill_coverage(job_data, resume_data)
        score = (0.6 * semantic + 0.4 * skill_coverage) * 100.0
        return float(max(0.0, min(100.0, score)))
