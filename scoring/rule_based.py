from typing import Dict, Tuple, List, Set
from utils.preprocessing import normalize_skill_set, flatten_experience_description
import config

class RuleBasedScorer:
    def __init__(self):
        self.weights = config.RULE_WEIGHTS

    def score(self, resume: Dict, job: Dict) -> Tuple[float, Dict, List[str], List[str]]:
        """
        Compute a rule-based score for a resume against a job description.
        Returns: (score, breakdown, matched_skills, missing_skills)
        """
        score = 0
        breakdown = {"skills_score": 0, "education_score": 0, "experience_score": 0, "projects_score": 0, "company_score": 0}
        
        # Skills - extract and normalize from various skill structures
        skills_data = resume.get("skills", {})
        technical_skills_data = resume.get("technical_skills", {})
        resume_raw_skills: List[str] = []
        for skill_source in (skills_data, technical_skills_data):
            if isinstance(skill_source, dict):
                for _, skill_list in skill_source.items():
                    if isinstance(skill_list, list):
                        resume_raw_skills.extend([s for s in skill_list if isinstance(s, str)])
            elif isinstance(skill_source, list):
                resume_raw_skills.extend([s for s in skill_source if isinstance(s, str)])
        resume_skills: Set[str] = normalize_skill_set(resume_raw_skills)
        
        required_skills = normalize_skill_set(job.get("required_skills", []))
        preferred_skills = normalize_skill_set(job.get("preferred_skills", []))
        
        # Direct matching
        matched_required = resume_skills.intersection(required_skills)
        matched_preferred = resume_skills.intersection(preferred_skills)
        
        # Add partial matching for compound skills like "REST API Development"
        for req_skill in required_skills:
            if req_skill not in matched_required:
                # Check if any resume skill contains key parts of the required skill
                skill_parts = req_skill.split()
                for resume_skill in resume_skills:
                    if any(part in resume_skill for part in skill_parts if len(part) > 2):
                        matched_required.add(req_skill)
                        break
        
        for pref_skill in preferred_skills:
            if pref_skill not in matched_preferred:
                # Check if any resume skill contains key parts of the preferred skill
                skill_parts = pref_skill.split()
                for resume_skill in resume_skills:
                    if any(part in resume_skill for part in skill_parts if len(part) > 2):
                        matched_preferred.add(pref_skill)
                        break
        breakdown["skills_score"] = (
            len(matched_required) * self.weights["required_skill_point"]
            + len(matched_preferred) * self.weights["preferred_skill_point"]
        )
        score += breakdown["skills_score"]
        
        # Education
        edu_score = 0
        for edu in resume.get("education", []):
            # Handle both dictionary format (from base parser) and string format (from GPT parser)
            if isinstance(edu, dict):
                degree = (edu.get("degree") or "").lower()
                field = (edu.get("field") or "").lower()
            elif isinstance(edu, str):
                degree = edu.lower()
                field = edu.lower()
            else:
                continue
                
            req = job.get("education_required", "").lower()
            base = req.split()[0] if req else ""
            if base and base in degree:
                # If field specified, check a simple contains match for partial credit
                if "computer" in req and "science" in req and ("computer" in field or "comput" in field):
                    edu_score = self.weights["education_full"]
                else:
                    edu_score = max(edu_score, self.weights["education_partial"])
                break
        breakdown["education_score"] = edu_score
        score += edu_score
        
        # Experience
        exp_score = 0
        desc_bonus = 0
        for exp in resume.get("experience", []):
            # Handle both dictionary format (from base parser) and string format (from GPT parser)
            if isinstance(exp, dict):
                title = (exp.get("title") or "").lower()
                desc_text = flatten_experience_description(exp).lower()
            elif isinstance(exp, str):
                title = exp.lower()
                desc_text = exp.lower()
            else:
                continue
                
            if any(skill in title for skill in required_skills):
                exp_score += self.weights["experience_title_point"]
            # Count occurrences of required skills in description for a small bonus
            for req_skill in required_skills:
                if req_skill in desc_text:
                    desc_bonus += self.weights["experience_desc_bonus"]
        desc_bonus = min(desc_bonus, self.weights["experience_desc_bonus_cap"])
        breakdown["experience_score"] = min(exp_score + desc_bonus, 15)
        score += breakdown["experience_score"]
        
        # Projects
        proj_score = 0
        for proj in resume.get("projects", []):
            # Handle both dictionary format (from base parser) and string format (from GPT parser)
            if isinstance(proj, dict):
                techs = set([t.lower() for t in proj.get("technologies", [])])
            elif isinstance(proj, str):
                # If project is a string, check if any required skills are mentioned in it
                techs = set([skill for skill in required_skills if skill in proj.lower()])
            else:
                techs = set()
                
            proj_score += len(techs.intersection(required_skills)) * 2
        breakdown["projects_score"] = min(proj_score, self.weights["projects_cap"])
        score += breakdown["projects_score"]
        
        # Company Experience
        company_score = 0
        preferred_companies = set([c.lower() for c in job.get("preferred_companies", [])])
        
        # Check experience for preferred companies
        for exp in resume.get("experience", []):
            if isinstance(exp, dict):
                company = (exp.get("company") or "").lower()
                for pref_company in preferred_companies:
                    if pref_company in company:
                        company_score += self.weights["company_point"]  # per preferred company
                        break
        
        # Also check work_experience field (different resumes use different field names)
        for exp in resume.get("work_experience", []):
            if isinstance(exp, dict):
                company = (exp.get("company") or "").lower()
                for pref_company in preferred_companies:
                    if pref_company in company:
                        company_score += self.weights["company_point"]
                        break
        
        breakdown["company_score"] = min(company_score, self.weights["company_cap"])  # Cap
        score += breakdown["company_score"]

        # Must-have gating/penalty (if provided)
        must_have = normalize_skill_set(job.get("must_have_skills", []))
        missing_must = [s for s in must_have if s not in resume_skills]
        if missing_must:
            score = max(0, score - config.MUST_HAVE_PENALTY)
        
        return min(score, 100), breakdown, list(matched_required), list(required_skills - matched_required)
