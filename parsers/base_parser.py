import re
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import logging
from dataclasses import dataclass, field
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SectionType(Enum):
    """Enum for different resume sections."""
    HEADER = "header"
    CONTACT = "contact"
    SUMMARY = "summary"
    SKILLS = "skills"
    EXPERIENCE = "experience"
    EDUCATION = "education"
    CERTIFICATIONS = "certifications"
    PROJECTS = "projects"
    ACCOMPLISHMENTS = "accomplishments"
    LANGUAGES = "languages"
    UNKNOWN = "unknown"

@dataclass
class ContactInfo:
    """Contact information structure."""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None

@dataclass
class Experience:
    """Work experience structure."""
    company: Optional[str] = None
    title: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[List[str]] = None
    raw_text: Optional[str] = None
    
    def __post_init__(self):
        if self.description is None:
            self.description = []

@dataclass
class Education:
    """Education structure."""
    degree: Optional[str] = None
    field: Optional[str] = None
    school: Optional[str] = None
    location: Optional[str] = None
    graduation_year: Optional[str] = None
    gpa: Optional[str] = None
    honors: Optional[List[str]] = None
    raw_text: Optional[str] = None
    
    def __post_init__(self):
        if self.honors is None:
            self.honors = []

class ResumeParser:
    """Enhanced resume parser with better section detection and extraction."""
    
    def __init__(self):
        # Section headers with priority scoring
        self.section_patterns = {
            SectionType.SUMMARY: [
                r'^(professional\s+)?summary$',
                r'^(career\s+)?objective$',
                r'^profile$',
                r'^about(\s+me)?$',
                r'^overview$',
                r'^statement$',
                r'^career\s+highlights?$'
            ],
            SectionType.EXPERIENCE: [
                r'^(professional\s+)?experience$',
                r'^work\s+(experience|history)$',
                r'^employment(\s+history)?$',
                r'^career\s+history$',
                r'^professional\s+background$',
                r'^relevant\s+experience$'
            ],
            SectionType.EDUCATION: [
                r'^education(\s+and\s+training)?$',
                r'^academic\s+(background|history)$',
                r'^academic\s+credentials$',
                r'^qualifications$',
                r'^training$',
                r'^education\s+&\s+certifications?$'
            ],
            SectionType.SKILLS: [
                r'^(technical\s+)?skills?$',
                r'^core\s+competenc(y|ies)$',
                r'^areas?\s+of\s+expertise$',
                r'^technical\s+expertise$',
                r'^skill\s+highlights?$',
                r'^qualifications$',
                r'^capabilities$'
            ],
            SectionType.CERTIFICATIONS: [
                r'^certifications?$',
                r'^licenses?(\s+and\s+certifications?)?$',
                r'^professional\s+certifications?$',
                r'^credentials?$'
            ],
            SectionType.PROJECTS: [
                r'^projects?$',
                r'^(personal\s+)?portfolio$',
                r'^key\s+projects?$',
                r'^notable\s+projects?$'
            ],
            SectionType.ACCOMPLISHMENTS: [
                r'^accomplishments?$',
                r'^achievements?$',
                r'^awards?(\s+and\s+honors?)?$',
                r'^honors?(\s+and\s+awards?)?$',
                r'^recognition$',
                r'^notable\s+achievements?$'
            ]
        }
        
        # Common job titles for better detection
        self.job_titles = [
            # Management
            r'\b(CEO|CFO|CTO|COO|CMO|CIO|VP|Vice\s+President)\b',
            r'\b(Director|Manager|Supervisor|Lead|Head\s+of|Chief)\b',
            r'\b(Coordinator|Administrator|Specialist|Analyst)\b',
            
            # Technical
            r'\b(Engineer|Developer|Programmer|Architect|Designer)\b',
            r'\b(Scientist|Researcher|Technician)\b',
            
            # Business
            r'\b(Consultant|Advisor|Strategist|Executive)\b',
            r'\b(Representative|Associate|Assistant|Officer)\b',
            
            # Specific roles
            r'\b(HR|Human\s+Resources?|Recruiter|Talent)\b',
            r'\b(Sales|Marketing|Business\s+Development)\b',
            r'\b(Finance|Accounting|Audit)\b',
            r'\b(Product|Project|Program)\s+(Manager|Owner)\b'
        ]
        
        # Company indicators
        self.company_indicators = [
            r'\b(Inc|LLC|Corp|Corporation|Company|Ltd|Limited|Group|Partners|LLP)\b',
            r'\b(Associates|Solutions|Services|Consulting|Technologies|Systems)\b',
            r'\b(University|College|Institute|School|Academy)\b',
            r'\b(Hospital|Medical|Health|Clinic)\b',
            r'\b(Bank|Financial|Capital|Investments)\b'
        ]
        
        # Date patterns
        self.date_patterns = {
            'month_year': r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}',
            'mm_yyyy': r'\d{1,2}/\d{4}',
            'yyyy': r'\b(19|20)\d{2}\b',
            'present': r'\b(Present|Current|Now|Ongoing|Today)\b',
            'date_range': r'(\d{1,2}/\d{4}|\w+\s+\d{4})\s*[-–—]\s*(\d{1,2}/\d{4}|\w+\s+\d{4}|Present|Current)',
        }

    def clean_text(self, text: str) -> str:
        """Clean text while preserving structure."""
        if not text:
            return ""
        
        # Normalize line endings
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        # Replace bullet points with standard marker
        text = re.sub(r'[•·▪▫◦‣⁃➤→]', '•', text)
        
        # Remove excessive spaces while preserving line breaks
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Clean up lines
        lines = text.split('\n')
        cleaned_lines = [line.strip() for line in lines]
        
        return '\n'.join(cleaned_lines)

    def detect_sections(self, text: str) -> Dict[SectionType, str]:
        """Detect and extract sections from resume text."""
        sections = {}
        lines = text.split('\n')
        
        current_section = SectionType.HEADER
        current_content = []
        section_start_idx = 0
        
        for i, line in enumerate(lines):
            if not line.strip():
                if current_content:
                    current_content.append('')
                continue
            
            # Check if this line is a section header
            section_type = self._identify_section_header(line)
            
            if section_type and section_type != SectionType.UNKNOWN:
                # Save previous section
                if current_content:
                    content = '\n'.join(current_content).strip()
                    if content:
                        sections[current_section] = content
                
                current_section = section_type
                current_content = []
                section_start_idx = i
            else:
                current_content.append(line)
        
        # Save last section
        if current_content:
            content = '\n'.join(current_content).strip()
            if content:
                sections[current_section] = content
        
        return sections

    def _identify_section_header(self, line: str) -> Optional[SectionType]:
        """Identify if a line is a section header."""
        # Clean the line
        clean_line = line.strip().lower()
        clean_line = re.sub(r'[:\-\s]+$', '', clean_line)  # Remove trailing colons, dashes
        clean_line = re.sub(r'^\W+', '', clean_line)  # Remove leading non-word chars
        
        # Skip if too long (likely not a header)
        if len(clean_line) > 50:
            return None
        
        # Check against patterns
        for section_type, patterns in self.section_patterns.items():
            for pattern in patterns:
                if re.match(pattern, clean_line):
                    return section_type
        
        return None

    def extract_contact_info(self, text: str) -> ContactInfo:
        """Extract contact information with improved logic."""
        contact = ContactInfo()
        
        # Take first 1000 chars for contact info search
        header_text = text[:1000]
        
        # Extract email (most reliable)
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, header_text)
        if email_match:
            contact.email = email_match.group()
        
        # Extract phone (improved pattern)
        phone_patterns = [
            r'(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            r'\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b',
            r'\(\d{3}\)\s*\d{3}-\d{4}',
        ]
        
        for pattern in phone_patterns:
            phone_match = re.search(pattern, header_text)
            if phone_match:
                phone = phone_match.group()
                # Validate it's not a year or other number
                if not re.match(r'^(19|20)\d{2}$', phone.strip()):
                    # Normalize US numbers to (XXX) XXX-XXXX when possible
                    digits = re.sub(r'\D', '', phone)
                    if len(digits) == 11 and digits.startswith('1'):
                        digits = digits[1:]
                    if len(digits) == 10:
                        contact.phone = f"({digits[0:3]}) {digits[3:6]}-{digits[6:10]}"
                    else:
                        contact.phone = phone
                    break
        
        # Extract LinkedIn
        linkedin_pattern = r'(?:https?://)?(?:www\.)?linkedin\.com/(?:in|pub)/([\w-]+)'
        linkedin_match = re.search(linkedin_pattern, header_text, re.IGNORECASE)
        if linkedin_match:
            contact.linkedin = f"linkedin.com/in/{linkedin_match.group(1)}"
        
        # Extract GitHub
        github_pattern = r'(?:https?://)?(?:www\.)?github\.com/([\w-]+)'
        github_match = re.search(github_pattern, header_text, re.IGNORECASE)
        if github_match:
            contact.github = f"github.com/{github_match.group(1)}"

        # Extract personal website (exclude linkedin/github)
        website_pattern = r'(https?://[\w.-]+(?:/\S*)?)'
        website_match = re.search(website_pattern, header_text)
        if website_match:
            site = website_match.group(1)
            if 'linkedin.com' not in site and 'github.com' not in site:
                contact.website = site.rstrip('/').strip()
        
        # Extract name (improved logic)
        contact.name = self._extract_name(header_text, contact.email)
        
        # Extract location
        location_pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),?\s*([A-Z]{2})\b'
        location_match = re.search(location_pattern, header_text)
        if location_match:
            contact.location = f"{location_match.group(1)}, {location_match.group(2)}"
        
        return contact

    def _extract_name(self, text: str, email: Optional[str] = None) -> Optional[str]:
        """Extract name with better heuristics."""
        lines = text.split('\n')[:10]  # Check first 10 lines
        
        potential_names = []
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Skip lines with email, phone, or URLs
            if email and email in line:
                continue
            if re.search(r'@|\d{3}[-.\s]\d{3}|http|www\.', line):
                continue
            
            # Skip section headers
            if self._identify_section_header(line):
                continue
            
            # Check if it looks like a name
            # Names typically have 2-4 words, start with capital letters
            words = line.split()
            if 2 <= len(words) <= 4:
                # Check if all words start with capital letters (allowing for middle initials)
                if all(word[0].isupper() or (len(word) <= 2 and word.endswith('.')) for word in words):
                    # Check if words are mostly alphabetic
                    if all(re.match(r'^[A-Za-z\'\-\.]+$', word) for word in words):
                        # Additional check: avoid common non-name patterns
                        lower_line = line.lower()
                        if not any(keyword in lower_line for keyword in 
                                 ['summary', 'objective', 'highlights', 'focused', 'driven', 'results']):
                            potential_names.append(line)
        
        # Return the first valid name found
        return potential_names[0] if potential_names else None

    def extract_experience(self, sections: Dict[SectionType, str]) -> List[Experience]:
        """Extract work experience with improved parsing."""
        experiences = []
        
        exp_text = sections.get(SectionType.EXPERIENCE, "")
        if not exp_text:
            # Try to find experience in other sections
            full_text = '\n'.join(sections.values())
            exp_pattern = r'(?:experience|employment)[:\-\s]*\n(.+?)(?=\n(?:education|skills|certifications)|$)'
            match = re.search(exp_pattern, full_text, re.IGNORECASE | re.DOTALL)
            if match:
                exp_text = match.group(1)
        
        if not exp_text:
            return experiences
        
        # Split into job entries
        job_entries = self._split_job_entries(exp_text)
        
        for entry in job_entries:
            exp = self._parse_job_entry(entry)
            if exp and (exp.company or exp.title):
                experiences.append(exp)
        
        return experiences

    def _split_job_entries(self, text: str) -> List[str]:
        """Split experience text into individual job entries."""
        entries = []
        
        # Look for patterns that indicate new job entry
        # Pattern 1: Date at the beginning of line
        # Pattern 2: Company name pattern
        # Pattern 3: Job title pattern
        
        lines = text.split('\n')
        current_entry = []
        
        for line in lines:
            # Check if this starts a new entry
            is_new_entry = False
            
            # Check for date range at start
            if re.match(r'^\s*(?:\d{1,2}/\d{4}|\w+\s+\d{4})', line):
                is_new_entry = True
            
            # Check for job title patterns
            for title_pattern in self.job_titles[:5]:  # Check first few patterns
                if re.search(title_pattern, line, re.IGNORECASE):
                    is_new_entry = True
                    break
            
            # Check for company indicators
            if any(re.search(pattern, line, re.IGNORECASE) for pattern in self.company_indicators[:3]):
                is_new_entry = True
            
            if is_new_entry and current_entry:
                entries.append('\n'.join(current_entry))
                current_entry = [line]
            else:
                current_entry.append(line)
        
        if current_entry:
            entries.append('\n'.join(current_entry))
        
        return entries

    def _parse_job_entry(self, entry: str) -> Optional[Experience]:
        """Parse a single job entry."""
        exp = Experience(raw_text=entry[:500])
        
        lines = entry.split('\n')
        first_line = lines[0] if lines else ""
        
        # Extract dates
        dates = self._extract_date_range(entry)
        if dates:
            exp.start_date, exp.end_date = dates
        
        # Extract job title
        for pattern in self.job_titles:
            match = re.search(pattern, first_line, re.IGNORECASE)
            if match:
                # Get the full title context
                title_match = re.search(r'([A-Za-z\s]+?' + pattern + r'[A-Za-z\s]*)', first_line, re.IGNORECASE)
                if title_match:
                    exp.title = title_match.group(1).strip()
                break
        
        # Extract company
        exp.company = self._extract_company(entry)
        
        # Extract location
        location_pattern = r'[-–]\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),?\s*([A-Z]{2})\b'
        location_match = re.search(location_pattern, first_line)
        if location_match:
            exp.location = f"{location_match.group(1)}, {location_match.group(2)}"
        
        # Extract bullet points
        bullets = []
        for line in lines[1:]:
            if line.strip().startswith('•') or re.match(r'^\s*[-*]\s+', line):
                bullet_text = re.sub(r'^\s*[•\-*]\s*', '', line).strip()
                if bullet_text:
                    bullets.append(bullet_text)
        
        exp.description = bullets
        
        return exp

    def _extract_date_range(self, text: str) -> Optional[Tuple[str, str]]:
        """Extract date range from text."""
        # Look for date range pattern (e.g., Jan 2020 - Mar 2022, 01/2019 to Present)
        range_pattern = r'(\w+\s+\d{4}|\d{1,2}/\d{4})\s*(?:-|–|—|to)\s*(\w+\s+\d{4}|\d{1,2}/\d{4}|Present|Current)'
        match = re.search(range_pattern, text, re.IGNORECASE)
        if match:
            return (match.group(1), match.group(2))
        
        # Look for individual dates
        dates = []
        for pattern_name, pattern in self.date_patterns.items():
            if pattern_name != 'date_range':
                matches = re.findall(pattern, text, re.IGNORECASE)
                dates.extend(matches)
        
        if len(dates) >= 2:
            return (dates[0], dates[1])
        elif len(dates) == 1:
            return (dates[0], "Present")
        
        return None

    def _extract_company(self, text: str) -> Optional[str]:
        """Extract company name from job entry."""
        # Look for company after "at" or "@"
        at_pattern = r'(?:at|@)\s+([A-Z][^\n,]+?)(?:\s*[-–]|\s*\n|$)'
        match = re.search(at_pattern, text)
        if match:
            return match.group(1).strip()
        
        # Look for company indicators
        for indicator in self.company_indicators:
            pattern = r'([A-Z][^,\n]*' + indicator + r'[^,\n]*)'
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                company = match.group(1).strip()
                # Clean up company name
                company = re.sub(r'\s*[-–]\s*.*$', '', company)  # Remove location suffix
                return company
        
        # Look for "Company Name" placeholder
        company_pattern = r'Company\s+Name\b'
        if re.search(company_pattern, text, re.IGNORECASE):
            return "Company Name (Placeholder)"
        
        return None

    def extract_education(self, sections: Dict[SectionType, str]) -> List[Education]:
        """Extract education with improved parsing."""
        education_list = []
        
        edu_text = sections.get(SectionType.EDUCATION, "")
        if not edu_text:
            # Try to find education in full text
            full_text = '\n'.join(sections.values())
            edu_pattern = r'(?:education)[:\-\s]*\n(.+?)(?=\n(?:experience|skills|certifications)|$)'
            match = re.search(edu_pattern, full_text, re.IGNORECASE | re.DOTALL)
            if match:
                edu_text = match.group(1)
        
        if not edu_text:
            return education_list
        
        # Split into education entries
        entries = self._split_education_entries(edu_text)
        
        for entry in entries:
            edu = self._parse_education_entry(entry)
            if edu and (edu.degree or edu.school):
                education_list.append(edu)
        
        return education_list

    def _split_education_entries(self, text: str) -> List[str]:
        """Split education text into individual entries."""
        entries = []
        
        # Common degree patterns
        degree_pattern = r'\b(Bachelor|Master|Ph\.?D|Doctor|Associate|Diploma|Certificate|MBA|B\.[A-Z]|M\.[A-Z])\b'
        
        lines = text.split('\n')
        current_entry = []
        
        for line in lines:
            # Check if this starts a new entry
            if re.search(degree_pattern, line, re.IGNORECASE) and current_entry:
                entries.append('\n'.join(current_entry))
                current_entry = [line]
            else:
                current_entry.append(line)
        
        if current_entry:
            entries.append('\n'.join(current_entry))
        
        return entries if entries else [text]

    def _parse_education_entry(self, entry: str) -> Optional[Education]:
        """Parse a single education entry."""
        edu = Education(raw_text=entry[:300])
        
        # Extract degree
        degree_patterns = [
            # Bachelor variants
            r"(Bachelor(?:'?s)?|B\.?Sc\.?|BSc|BS|B\.?S\.?|B\.?Eng\.?|BEng)\b\s*(?:of\s+)?([A-Za-z\s]+?)(?:\s*[-,]|$)",
            # Master variants
            r"(Master(?:'?s)?|M\.?Sc\.?|MSc|MS|M\.?S\.?|M\.?Eng\.?|MEng)\b\s*(?:of\s+)?([A-Za-z\s]+?)(?:\s*[-,]|$)",
            # Doctoral variants
            r"(Ph\.?D\.?|Doctor(?:ate)?)\b\s*(?:in\s+)?([A-Za-z\s]+?)(?:\s*[-,]|$)",
            # Associate
            r"(Associate(?:'?s)?)\b\s*(?:of\s+)?([A-Za-z\s]+?)(?:\s*[-,]|$)",
            # Professional degrees
            r"(MBA|MFA|MEd|MPH|MPA|JD|MD)\b",
        ]
        
        for pattern in degree_patterns:
            match = re.search(pattern, entry, re.IGNORECASE)
            if match:
                edu.degree = match.group(1)
                if match.lastindex > 1:
                    edu.field = match.group(2).strip()
                break
        
        # Extract school
        school_pattern = r'([A-Z][^\n]*(?:University|College|Institute|School)[^\n]*)'
        school_match = re.search(school_pattern, entry)
        if school_match:
            edu.school = school_match.group(1).strip()
            # Clean up school name
            edu.school = re.sub(r'\s*[-–]\s*.*$', '', edu.school)
        
        # Extract year (use non-capturing group to return the full year match)
        year_pattern = r'\b(?:19|20)\d{2}\b'
        years = re.findall(year_pattern, entry)
        if years:
            edu.graduation_year = max(years)  # Usually the latest year
        
        # Extract GPA
        gpa_pattern = r'(?:GPA|Grade|Score)[:\s]*([0-9]\.[0-9]+)(?:\s*/\s*([0-9]\.[0-9]+))?'
        gpa_match = re.search(gpa_pattern, entry, re.IGNORECASE)
        if gpa_match:
            if gpa_match.group(2):
                edu.gpa = f"{gpa_match.group(1)}/{gpa_match.group(2)}"
            else:
                edu.gpa = gpa_match.group(1)
        
        # Extract honors
        honors_patterns = [
            r'(cum laude|magna cum laude|summa cum laude)',
            r"(Dean'?s List|President'?s List|Honor Roll)",
            r'(Valedictorian|Salutatorian)',
        ]
        
        for pattern in honors_patterns:
            matches = re.findall(pattern, entry, re.IGNORECASE)
            edu.honors.extend(matches)
        
        return edu

    def extract_skills(self, text: str) -> Dict[str, List[str]]:
        """Extract skills with categorization."""
        skills = {
            'all': [],
            'technical': [],
            'soft': [],
            'languages': [],
            'tools': [],
            'databases': []
        }
        
        # Technical skills database
        tech_skills = {
            'languages': ['Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'Ruby', 'Go', 
                         'Rust', 'Swift', 'Kotlin', 'R', 'SQL', 'PHP', 'Perl', 'Scala'],
            'frameworks': ['React', 'Angular', 'Vue', 'Django', 'Flask', 'Spring', 'Node.js', 
                          'Express', '.NET', 'Rails', 'Laravel'],
            'databases': ['MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Oracle', 'SQL Server', 
                         'Cassandra', 'DynamoDB', 'Elasticsearch'],
            'tools': ['Git', 'Docker', 'Kubernetes', 'Jenkins', 'AWS', 'Azure', 'GCP', 
                     'Terraform', 'Ansible', 'JIRA', 'Confluence'],
        }

        # Common variants/synonyms -> canonical name
        variant_patterns = {
            'REST': [r'\bREST\b', r'\bRESTful\b'],
            'GraphQL': [r'\bGraph\s?QL\b'],
            'NoSQL': [r'\bNo\s?SQL\b'],
            'CI/CD': [r'\bCI\s*/\s*CD\b', r'\bCI[- ]?CD\b'],
            'Microservices': [r'\bmicroservices?(?:\s+architecture)?\b'],
        }
        
        # Soft skills
        soft_skills = ['Leadership', 'Communication', 'Problem Solving', 'Team', 'Collaboration',
                      'Management', 'Analytical', 'Creative', 'Strategic', 'Critical Thinking',
                      'Project Management', 'Time Management', 'Presentation']
        
        # Extract from text
        for category, skill_list in tech_skills.items():
            for skill in skill_list:
                if re.search(r'\b' + re.escape(skill) + r'\b', text, re.IGNORECASE):
                    skills['technical'].append(skill)
                    skills['all'].append(skill)
                    if category == 'databases':
                        skills['databases'].append(skill)
                    elif category == 'languages':
                        skills['languages'].append(skill)
                    elif category in ['tools', 'frameworks']:
                        skills['tools'].append(skill)
        
        # Add canonical skills when any variant matches
        for canonical, patterns in variant_patterns.items():
            for pat in patterns:
                if re.search(pat, text, re.IGNORECASE):
                    skills['technical'].append(canonical)
                    skills['all'].append(canonical)
                    break

        for skill in soft_skills:
            if re.search(r'\b' + skill + r'\b', text, re.IGNORECASE):
                skills['soft'].append(skill)
                skills['all'].append(skill)
        
        # Deduplicate
        for key in skills:
            skills[key] = list(set(skills[key]))
        
        return skills

    def parse(self, text: str) -> Dict[str, Any]:
        """Main parsing method."""
        try:
            # Clean text
            text = self.clean_text(text)
            
            # Detect sections
            sections = self.detect_sections(text)
            
            # Extract components
            contact = self.extract_contact_info(text)
            skills = self.extract_skills(text)
            experience = self.extract_experience(sections)
            education = self.extract_education(sections)
            
            # Build result
            result = {
                'contact': {
                    'name': contact.name,
                    'email': contact.email,
                    'phone': contact.phone,
                    'linkedin': contact.linkedin,
                    'github': contact.github,
                    'location': contact.location,
                    'website': contact.website
                },
                'summary': sections.get(SectionType.SUMMARY, "")[:500] if SectionType.SUMMARY in sections else None,
                'skills': skills,
                'experience': [
                    {
                        'company': exp.company,
                        'title': exp.title,
                        'location': exp.location,
                        'start_date': exp.start_date,
                        'end_date': exp.end_date,
                        'description': exp.description
                    } for exp in experience
                ],
                'education': [
                    {
                        'degree': edu.degree,
                        'field': edu.field,
                        'school': edu.school,
                        'location': edu.location,
                        'graduation_year': edu.graduation_year,
                        'gpa': edu.gpa,
                        'honors': edu.honors
                    } for edu in education
                ],
                'sections': {k.value: v for k, v in sections.items()},
                'metadata': {
                    'sections_detected': [k.value for k in sections.keys()],
                    'parsing_success': True
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error parsing resume: {str(e)}")
            return {
                'error': str(e),
                'contact': {},
                'skills': {'all': []},
                'experience': [],
                'education': [],
                'metadata': {'parsing_success': False}
            }


def load_csv_and_parse(csv_path: str, num_resumes: int = 5) -> Dict[str, Any]:
    """
    Load CSV file and parse the specified number of resumes.
    Returns simple JSON output with essential info only.
    """
    import pandas as pd
    import json
    from pathlib import Path
    
    print(f"📁 Loading CSV from: {csv_path}")
    
    try:
        # Load CSV
        df = pd.read_csv(csv_path)
        print(f"✅ Loaded {len(df)} resumes from CSV")
        
        # Initialize parser
        parser = ResumeParser()
        print("🔧 Parser initialized")
        
        # Process resumes
        results = []
        print(f"📋 Processing first {num_resumes} resumes...")
        
        for i in range(min(num_resumes, len(df))):
            row = df.iloc[i]
            resume_text = str(row['Resume_str'])
            
            print(f"--- Processing Resume {i+1}/{num_resumes} ---")
            print(f"ID: {row['ID']}, Category: {row['Category']}")
            print(f"Text length: {len(resume_text)} characters")
            
            # Parse resume
            parsed = parser.parse(resume_text)
            
            # Create simple output
            simple_result = {
                'resume_id': int(row['ID']),
                'category': str(row['Category']),
                'name': parsed['contact'].get('name'),
                'email': parsed['contact'].get('email'),
                'phone': parsed['contact'].get('phone'),
                'location': parsed['contact'].get('location'),
                'skills': parsed['skills'].get('all', []),
                'total_skills': len(parsed['skills'].get('all', [])),
                'experience_count': len(parsed.get('experience', [])),
                'education_count': len(parsed.get('education', [])),
                'parsing_success': parsed['metadata'].get('parsing_success', False)
            }
            
            results.append(simple_result)
            print(f"✅ Success - Name: {simple_result['name']}")
            print(f"   Skills: {simple_result['total_skills']}, Experience: {simple_result['experience_count']}, Education: {simple_result['education_count']}")
        
        # Create final output
        output = {
            'metadata': {
                'total_processed': len(results),
                'successful_parses': sum(1 for r in results if r['parsing_success']),
                'csv_file': csv_path,
                'timestamp': str(pd.Timestamp.now())
            },
            'resumes': results
        }
        
        return output
        
    except Exception as e:
        print(f"❌ Error processing CSV: {e}")
        return {
            'error': str(e),
            'metadata': {'total_processed': 0, 'successful_parses': 0},
            'resumes': []
        }


def save_results_to_json(results: Dict[str, Any], output_file: str = "simple_parsed_results.json"):
    """Save results to JSON file."""
    import json
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"💾 Results saved to: {output_file}")
        print("✅ Success!")
        return True
    except Exception as e:
        print(f"❌ Error saving results: {e}")
        return False


if __name__ == "__main__":
    # Load and parse resumes
    csv_file = "data/all_resumes.csv"
    results = load_csv_and_parse(csv_file, num_resumes=5)
    
    # Save to JSON
    save_results_to_json(results)
    
    # Print summary
    print(f"\n📊 Summary:")
    print(f"   Processed: {results['metadata']['total_processed']}")
    print(f"   Successful: {results['metadata']['successful_parses']}")
    
    if results['resumes']:
        avg_skills = sum(r['total_skills'] for r in results['resumes']) / len(results['resumes'])
        print(f"   Average skills per resume: {avg_skills:.1f}")