"""
doc_generator/viva_content.py
Combines Categories A through H into a single unified Viva Question Bank data model.
"""
from scripts.doc_generator.viva_categories_a_to_d import CATEGORY_A, CATEGORY_B, CATEGORY_C, CATEGORY_D
from scripts.doc_generator.viva_categories_e_to_h import CATEGORY_E, CATEGORY_F, CATEGORY_G, CATEGORY_H

VIVA_METADATA = {
    "title": "ROADINSIGHT INDIA — VIVA & FACULTY QUESTION BANK",
    "subtitle": "Comprehensive Academic Defense, Engineering Mechanics & Technical Trade-offs",
    "domain": "India Road Accident Data Engineering & Analytics Platform",
    "team": [
        "Jayant Soni",
        "Honey Singh",
        "Gautam",
        "Sugam Umale"
    ],
    "tech_stack": "Python 3.13 | PostgreSQL 17 | Streamlit | Groq LLM | Text-to-SQL | sqlglot",
    "branch": "feature/hardening",
    "evaluation": "University Evaluator Preparation & Technical Viva Defense"
}

ALL_VIVA_CATEGORIES = [
    CATEGORY_A,
    CATEGORY_B,
    CATEGORY_C,
    CATEGORY_D,
    CATEGORY_E,
    CATEGORY_F,
    CATEGORY_G,
    CATEGORY_H
]

