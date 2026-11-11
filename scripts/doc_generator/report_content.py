"""
doc_generator/report_content.py
Combines Chapters 1 through 18 into a single unified report data model.
"""
from scripts.doc_generator.report_chapters_1_to_6 import CHAPTER_1, CHAPTER_2, CHAPTER_3, CHAPTER_4, CHAPTER_5, CHAPTER_6
from scripts.doc_generator.report_chapters_7_to_12 import CHAPTER_7, CHAPTER_8, CHAPTER_9, CHAPTER_10, CHAPTER_11, CHAPTER_12
from scripts.doc_generator.report_chapters_13_to_18 import CHAPTER_13, CHAPTER_14, CHAPTER_15, CHAPTER_16, CHAPTER_17, CHAPTER_18

REPORT_METADATA = {
    "title": "ROADINSIGHT INDIA",
    "subtitle": "Complete Technical Implementation, Testing & Performance Analysis",
    "domain": "India Road Accident Data Engineering & Analytics Platform",
    "team": [
        "Jayant Soni",
        "Honey Singh",
        "Gautam",
        "Sugam Umale"
    ],
    "tech_stack": "Python 3.13 | PostgreSQL 17 | Streamlit | Groq LLM | Text-to-SQL | sqlglot",
    "branch": "feature/hardening",
    "evaluation": "Academic University Project Evaluation"
}

EXECUTIVE_SUMMARY = [
    {
        "type": "p",
        "text": "RoadInsight India is an enterprise-grade data engineering, analytics, and artificial intelligence platform developed to ingest, reconcile, normalize, and visualize road traffic accident data across India. Drawing from official publications of the Ministry of Road Transport and Highways (MoRTH) and the Open Government Data (OGD) platform spanning 1970 to 2023, the platform transforms fragmented, heterogeneous spreadsheets into an atomic, normalized 3NF PostgreSQL 17 data warehouse."
    },
    {
        "type": "p",
        "text": "This comprehensive technical report provides an independent engineering audit of the entire codebase on branch 'feature/hardening'. It details the forensic resolution of long-standing data reconciliation anomalies, the atomic ETL pipeline architecture, PostgreSQL schema design with role-based security isolation, the Streamlit dashboard suite, and the zero-trust Text-to-SQL AI Analyst powered by Groq's high-speed LLaMA-based model (openai/gpt-oss-120b) and sqlglot AST validation."
    },
    {
        "type": "p",
        "text": "In strict adherence to academic standards, all empirical claims are grounded in repository evidence: 50 automated tests verified, 1,272x index scan speedup measured, zero application secrets exposed, and manual test protocols preserved with unexecuted templates pending viva demonstration."
    }
]

ALL_REPORT_CHAPTERS = [
    CHAPTER_1,
    CHAPTER_2,
    CHAPTER_3,
    CHAPTER_4,
    CHAPTER_5,
    CHAPTER_6,
    CHAPTER_7,
    CHAPTER_8,
    CHAPTER_9,
    CHAPTER_10,
    CHAPTER_11,
    CHAPTER_12,
    CHAPTER_13,
    CHAPTER_14,
    CHAPTER_15,
    CHAPTER_16,
    CHAPTER_17,
    CHAPTER_18
]

