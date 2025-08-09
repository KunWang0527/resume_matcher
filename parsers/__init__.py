# Parsers module for extracting text from resumes
from .base_parser import ResumeParser
from .gpt_parser import GPTResumeParser

__all__ = ['ResumeParser', 'GPTResumeParser']