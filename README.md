## Resume Matcher

AI-powered resume screening assistant for parsing, matching, and scoring resumes against job descriptions.

### Full experience (recommended)
- Open and run `notebooks/workflow.ipynb` end-to-end for the complete pipeline.
- Replace the sample files in `data/resumes/` with your actual resumes (PDF/DOCX).
- Update `data/job_description.json` with the target role's latest description and requirements.

### Project structure
- `AI-Powered Resume Screening Assistant.pdf`: Project overview/report (PDF).
- `AI-Powered Resume Screening Assistant.pptx`: Presentation slide deck for the project.
- `app.py`: Main application entry point for running the resume screening workflow/UI.
- `config.py`: Central configuration for paths, model settings, and runtime options.
- `env.example`: Example environment variables file (copy to `.env` and fill in secrets/paths).
- `requirements.txt`: Python dependencies required to run the project.

- `data/`: Datasets, inputs, and sample outputs used by the pipeline.
  - `all_resumes.csv`: Aggregated metadata or extracted text summaries for resumes.
  - `final_scored_resumes.json`: Final resume scoring results (rule-based or combined).
  - `final_scored_resumes_gpt.json`: Final resume scoring results generated with GPT.
  - `job_description.json`: Job description(s) used for matching and scoring.
  - `parsed_resumes.json`: Parsed resume structures from the standard parsers.
  - `parsed_resumes_gpt.json`: Parsed resume structures produced by GPT-based parsing.
  - `resumes/`: Sample resume documents (PDF/DOCX) for testing and demos.
  - `top10_base_candidates.csv`: Top 10 candidates ranked by baseline/rule-based scoring.
  - `top10_gpt_candidates.csv`: Top 10 candidates ranked by GPT-based scoring.

- `models/`: Semantic matching models and related components.
  - `__init__.py`: Package marker for `models`.
  - `semantic_matcher.py`: Semantic similarity and embedding-based matching logic.

- `notebooks/`: Jupyter notebooks for experiments and end-to-end workflows.
  - `workflow.ipynb`: Demonstration of the parsing, matching, and scoring pipeline.

- `parsers/`: Resume parsing components and interfaces.
  - `__init__.py`: Package marker for `parsers`.
  - `base_parser.py`: Base parser interface and shared parsing utilities.
  - `gpt_parser.py`: GPT-powered parser producing structured resume data.
  - `pdf_parser.py`: PDF text extraction and parsing utilities for resumes.

- `scoring/`: Scoring logic for ranking candidates against job descriptions.
  - `__init__.py`: Package marker for `scoring`.
  - `rule_based.py`: Heuristic/rule-based scoring features and weights.
  - `scorer.py`: Orchestrates scoring using rule-based and/or semantic methods.

- `utils/`: Utility helpers for preprocessing and common tasks.
  - `__init__.py`: Package marker for `utils`.
  - `preprocessing.py`: Text cleaning, normalization, and tokenization utilities.

- `simple_parsed_results.json`: Small sample of parsed resume output for quick inspection.
- `skill_db_relax_20.json`: Curated skill/keyword database for matching.
- `token_dist.json`: Token distribution statistics for analysis or debugging.


