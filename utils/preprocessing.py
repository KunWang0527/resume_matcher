"""Utilities for text cleaning, normalization, and lightweight deduplication."""

import re
from typing import List, Dict, Set, Iterable
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


_WHITESPACE_RE = re.compile(r"\s+")


def clean_text(text: str) -> str:
    """Clean and normalize text while preserving word boundaries."""
    if not text:
        return ""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = _WHITESPACE_RE.sub(" ", text)
    return text.strip()


def normalize_text(text: str) -> str:
    """Lowercase and strip parentheses metadata (e.g., Python (>10,000 lines) -> Python)."""
    if not isinstance(text, str):
        return ""
    base = text.split("(")[0].strip()
    return base.lower()


def normalize_skill_string(skill: str) -> str:
    """Normalize a single skill token (lowercase, remove punctuation and spaces for acronyms like ci/cd)."""
    s = normalize_text(skill)
    # Simplify common separators
    s = s.replace("/", " ").replace("-", " ")
    s = _WHITESPACE_RE.sub(" ", s).strip()
    return s


def expand_skill_synonyms(skills: Iterable[str]) -> Set[str]:
    """Expand skills with a minimal synonym/acronym map suitable for this project."""
    mapping = {
        "rest api development": ["rest", "api", "rest api"],
        "rest api": ["rest", "api"],
        "ci cd pipelines": ["cicd", "ci", "cd", "ci cd"],
        "nosql databases": ["nosql"],
        "amazon web services": ["aws"],
        "aws": ["amazon web services"],
        "graphql": ["graph ql"],
        "microservices architecture": ["microservices"]
    }
    expanded: Set[str] = set()
    for sk in skills:
        expanded.add(sk)
        if sk in mapping:
            expanded.update(mapping[sk])
    return expanded


def normalize_skill_set(raw_skills: Iterable[str]) -> Set[str]:
    """Normalize and expand a set of raw skill strings."""
    normalized = {normalize_skill_string(s) for s in raw_skills if isinstance(s, str) and s.strip()}
    normalized = expand_skill_synonyms(normalized)
    return normalized


def extract_keywords(text: str, top_k: int = 20) -> List[str]:
    """Extract simple keywords using TF-IDF across sentences of a single document."""
    if not text:
        return []
    sentences = [s.strip() for s in re.split(r"[\.!?\n]", text) if s.strip()]
    if not sentences:
        return []
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), max_features=5000)
    X = vectorizer.fit_transform(sentences)
    scores = X.max(axis=0).toarray().ravel()
    terms = vectorizer.get_feature_names_out()
    idxs = scores.argsort()[::-1][:top_k]
    return [terms[i] for i in idxs]


def remove_duplicates(resumes: List[Dict]) -> List[Dict]:
    """Remove exact duplicate resumes by their normalized text payload if present."""
    seen = set()
    unique = []
    for r in resumes:
        key = normalize_text(str(r))[:10000]
        if key not in seen:
            seen.add(key)
            unique.append(r)
    return unique


def deduplicate_resumes(resumes: List[Dict], threshold: float = 0.9) -> List[Dict]:
    """Remove near-duplicate resumes using TF-IDF cosine similarity on serialized dicts."""
    if not resumes:
        return []
    texts = [normalize_text(str(r)) for r in resumes]
    vectorizer = TfidfVectorizer(stop_words="english", max_features=10000)
    X = vectorizer.fit_transform(texts)
    keep_idxs = []
    removed = set()
    for i in range(len(resumes)):
        if i in removed:
            continue
        keep_idxs.append(i)
        sims = cosine_similarity(X[i], X).ravel()
        for j in range(i + 1, len(resumes)):
            if sims[j] >= threshold:
                removed.add(j)
    return [resumes[i] for i in keep_idxs]


def flatten_experience_description(exp_item) -> str:
    """Return a single string description from a resume experience item (dict or string)."""
    if isinstance(exp_item, dict):
        desc = exp_item.get("description", "")
        if isinstance(desc, list):
            return " ".join([d for d in desc if isinstance(d, str)])
        return str(desc)
    if isinstance(exp_item, str):
        return exp_item
    return ""
