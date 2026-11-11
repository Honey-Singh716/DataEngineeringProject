"""
doc_generator/build_docx.py
Builds professional DOCX deliverables:
1. RoadInsight_India_Final_Technical_Report.docx
2. RoadInsight_India_Viva_Question_Bank.docx
"""
import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

from scripts.doc_generator.styles import (
    COLOR_NAVY, COLOR_TEAL, COLOR_CHARCOAL, COLOR_SLATE, COLOR_MUTED, COLOR_WHITE,
    HEX_NAVY, HEX_TEAL, HEX_BG_ALT, HEX_BORDER,
    set_cell_background, set_cell_margins, add_callout, add_code_block, add_styled_table
)
from scripts.doc_generator.report_content import REPORT_METADATA, EXECUTIVE_SUMMARY, ALL_REPORT_CHAPTERS
from scripts.doc_generator.viva_content import VIVA_METADATA, ALL_VIVA_CATEGORIES

def _setup_page_layout(doc, title_text: str):
    """Set up 1-inch margins, running headers, and running footers."""
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)
        
        # Header
        hdr = section.header
        hp = hdr.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hrun = hp.add_run(f"RoadInsight India — {title_text}")
        hrun.font.name = "Arial"
        hrun.font.size = Pt(8)
        hrun.font.color.rgb = COLOR_MUTED
        
        # Footer
        ftr = section.footer
        fp = ftr.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.LEFT
        frun = fp.add_run("Confidential — Academic Project Evaluation | Branch: feature/hardening")
        frun.font.name = "Arial"
        frun.font.size = Pt(8)
        frun.font.color.rgb = COLOR_MUTED

def generate_technical_report_docx(output_path: str):
    """Generate the complete 18-chapter Technical Report DOCX."""
    doc = docx.Document()
    _setup_page_layout(doc, "Complete Technical Implementation & Engineering Audit")
    
    # ---------------- COVER PAGE ----------------
    p_pre = doc.add_paragraph()
    p_pre.paragraph_format.space_before = Pt(80)
    
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_title = p_title.add_run("ROADINSIGHT INDIA")
    run_title.font.name = "Arial"
    run_title.font.size = Pt(28)
    run_title.font.bold = True
    run_title.font.color.rgb = COLOR_NAVY
    
    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(40)
    run_sub = p_sub.add_run("Complete Technical Implementation, Testing & Performance Analysis")
    run_sub.font.name = "Arial"
    run_sub.font.size = Pt(13)
    run_sub.font.bold = True
    run_sub.font.color.rgb = COLOR_TEAL
    
    # Divider line
    tbl_div = doc.add_table(rows=1, cols=1)
    tbl_div.alignment = WD_TABLE_ALIGNMENT.CENTER
    c_div = tbl_div.cell(0, 0)
    c_div.width = Inches(4.5)
    set_cell_background(c_div, HEX_TEAL)
    set_cell_margins(c_div, top=10, bottom=10, left=10, right=10)
    
    p_meta = doc.add_paragraph()
    p_meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_meta.paragraph_format.space_before = Pt(60)
    p_meta.paragraph_format.line_spacing = 1.4
    
    run_m = p_meta.add_run("Project Team:\n")
    run_m.font.bold = True
    run_m.font.size = Pt(11)
    run_m.font.color.rgb = COLOR_NAVY
    
    for member in REPORT_METADATA["team"]:
        rm = p_meta.add_run(f"• {member}\n")
        rm.font.size = Pt(10.5)
        rm.font.color.rgb = COLOR_CHARCOAL
        
    p_tech = doc.add_paragraph()
    p_tech.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_tech.paragraph_format.space_before = Pt(24)
    r_tech = p_tech.add_run(f"Technology Stack:\n{REPORT_METADATA['tech_stack']}")
    r_tech.font.size = Pt(9.5)
    r_tech.font.italic = True
    r_tech.font.color.rgb = COLOR_SLATE
    
    doc.add_page_break()
    
    # ---------------- EXECUTIVE SUMMARY ----------------
    p_es_h = doc.add_paragraph()
    run_es_h = p_es_h.add_run("EXECUTIVE SUMMARY")
    run_es_h.font.name = "Arial"
    run_es_h.font.size = Pt(18)
    run_es_h.font.bold = True
    run_es_h.font.color.rgb = COLOR_NAVY
    p_es_h.paragraph_format.space_after = Pt(12)
    
    for block in EXECUTIVE_SUMMARY:
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(8)
        p.paragraph_format.line_spacing = 1.15
        r = p.add_run(block["text"])
        r.font.name = "Arial"
        r.font.size = Pt(10)
        r.font.color.rgb = COLOR_CHARCOAL
        
    # ---------------- TABLE OF CONTENTS ----------------
    p_toc_h = doc.add_paragraph()
    p_toc_h.paragraph_format.space_before = Pt(16)
    p_toc_h.paragraph_format.space_after = Pt(8)
    r_toc_h = p_toc_h.add_run("TABLE OF CONTENTS")
    r_toc_h.font.name = "Arial"
    r_toc_h.font.size = Pt(14)
    r_toc_h.font.bold = True
    r_toc_h.font.color.rgb = COLOR_NAVY
    
    for ch in ALL_REPORT_CHAPTERS:
        p_item = doc.add_paragraph()
        p_item.paragraph_format.space_after = Pt(2)
        p_item.paragraph_format.line_spacing = 1.1
        r_num = p_item.add_run(f"{ch['title']}")
        r_num.font.name = "Arial"
        r_num.font.size = Pt(9.5)
        r_num.font.color.rgb = COLOR_CHARCOAL
        
    doc.add_page_break()
    
    # ---------------- CHAPTERS 1 TO 18 ----------------
    for ch in ALL_REPORT_CHAPTERS:
        # Chapter Heading
        p_h1 = doc.add_paragraph()
        p_h1.paragraph_format.space_before = Pt(14)
        p_h1.paragraph_format.space_after = Pt(10)
        r_h1 = p_h1.add_run(ch["title"])
        r_h1.font.name = "Arial"
        r_h1.font.size = Pt(16)
        r_h1.font.bold = True
        r_h1.font.color.rgb = COLOR_NAVY
        
        # Blocks inside chapter
        for b in ch["blocks"]:
            b_type = b["type"]
            if b_type == "p":
                p = doc.add_paragraph()
                p.paragraph_format.space_after = Pt(6)
                p.paragraph_format.line_spacing = 1.15
                r = p.add_run(b["text"])
                r.font.name = "Arial"
                r.font.size = Pt(9.5)
                r.font.color.rgb = COLOR_CHARCOAL
            elif b_type == "h2":
                p_h2 = doc.add_paragraph()
                p_h2.paragraph_format.space_before = Pt(12)
                p_h2.paragraph_format.space_after = Pt(4)
                r_h2 = p_h2.add_run(b["text"])
                r_h2.font.name = "Arial"
                r_h2.font.size = Pt(12)
                r_h2.font.bold = True
                r_h2.font.color.rgb = COLOR_TEAL
            elif b_type == "callout":
                add_callout(doc, b["text"], badge=b.get("badge", "NOTE"))
            elif b_type == "code":
                add_code_block(doc, b["text"])
            elif b_type == "table":
                add_styled_table(doc, b["headers"], b["rows"])
            elif b_type == "bullets":
                for item in b["items"]:
                    p_b = doc.add_paragraph(style='List Bullet')
                    p_b.paragraph_format.space_after = Pt(3)
                    p_b.paragraph_format.line_spacing = 1.15
                    r_b = p_b.add_run(item)
                    r_b.font.name = "Arial"
                    r_b.font.size = Pt(9.5)
                    r_b.font.color.rgb = COLOR_CHARCOAL
                    
        doc.add_page_break()

    # Save
    doc.save(output_path)
    print(f"[DOCX] Technical Report successfully generated: {output_path}")

def generate_viva_question_bank_docx(output_path: str):
    """Generate the complete 59-question Viva Question Bank DOCX."""
    doc = docx.Document()
    _setup_page_layout(doc, "Viva & Faculty Question Bank")
    
    # ---------------- COVER PAGE ----------------
    p_pre = doc.add_paragraph()
    p_pre.paragraph_format.space_before = Pt(80)
    
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_title = p_title.add_run("ROADINSIGHT INDIA\nVIVA QUESTION BANK")
    run_title.font.name = "Arial"
    run_title.font.size = Pt(26)
    run_title.font.bold = True
    run_title.font.color.rgb = COLOR_NAVY
    
    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(40)
    run_sub = p_sub.add_run("Comprehensive Faculty Preparation: Theory, Implementation & Limitations")
    run_sub.font.name = "Arial"
    run_sub.font.size = Pt(13)
    run_sub.font.bold = True
    run_sub.font.color.rgb = COLOR_TEAL
    
    p_meta = doc.add_paragraph()
    p_meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_meta.paragraph_format.space_before = Pt(50)
    p_meta.paragraph_format.line_spacing = 1.4
    
    run_m = p_meta.add_run("Prepared for University Technical Evaluation\nProject Team:\n")
    run_m.font.bold = True
    run_m.font.size = Pt(11)
    run_m.font.color.rgb = COLOR_NAVY
    
    for member in VIVA_METADATA["team"]:
        rm = p_meta.add_run(f"• {member}\n")
        rm.font.size = Pt(10.5)
        rm.font.color.rgb = COLOR_CHARCOAL
        
    doc.add_page_break()
    
    # ---------------- CATEGORIES A TO H ----------------
    for cat in ALL_VIVA_CATEGORIES:
        p_c = doc.add_paragraph()
        p_c.paragraph_format.space_before = Pt(14)
        p_c.paragraph_format.space_after = Pt(10)
        r_c = p_c.add_run(f"CATEGORY {cat['category']}")
        r_c.font.name = "Arial"
        r_c.font.size = Pt(16)
        r_c.font.bold = True
        r_c.font.color.rgb = COLOR_NAVY
        
        for q_idx, item in enumerate(cat["questions"]):
            # Table card for each question
            tbl = doc.add_table(rows=1, cols=1)
            tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
            tbl.autofit = False
            
            cell = tbl.cell(0, 0)
            set_cell_background(cell, "FFFFFF")
            set_cell_margins(cell, top=140, bottom=140, left=180, right=180)
            
            # Left border in Navy
            tcPr = cell._tc.get_or_add_tcPr()
            borders = parse_xml(f'''
                <w:tcBorders {nsdecls("w")}>
                    <w:top w:val="single" w:sz="6" w:space="0" w:color="{HEX_BORDER}"/>
                    <w:left w:val="single" w:sz="28" w:space="0" w:color="{HEX_NAVY}"/>
                    <w:bottom w:val="single" w:sz="6" w:space="0" w:color="{HEX_BORDER}"/>
                    <w:right w:val="single" w:sz="6" w:space="0" w:color="{HEX_BORDER}"/>
                </w:tcBorders>
            ''')
            tcPr.append(borders)
            
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.line_spacing = 1.15
            
            # Question title
            rq = p.add_run(f"Q{q_idx+1}: {item['q']}\n\n")
            rq.font.name = "Arial"
            rq.font.size = Pt(11)
            rq.font.bold = True
            rq.font.color.rgb = COLOR_NAVY
            
            # 1. Short Answer
            r_s1 = p.add_run("1. SHORT VIVA ANSWER:\n")
            r_s1.font.bold = True
            r_s1.font.size = Pt(9)
            r_s1.font.color.rgb = COLOR_TEAL
            r_s2 = p.add_run(f"{item['short']}\n\n")
            r_s2.font.size = Pt(9.5)
            r_s2.font.color.rgb = COLOR_CHARCOAL
            
            # 2. Detailed Technical
            r_t1 = p.add_run("2. DETAILED TECHNICAL EXPLANATION:\n")
            r_t1.font.bold = True
            r_t1.font.size = Pt(9)
            r_t1.font.color.rgb = COLOR_TEAL
            r_t2 = p.add_run(f"{item['tech']}\n\n")
            r_t2.font.size = Pt(9.5)
            r_t2.font.color.rgb = COLOR_CHARCOAL
            
            # 3. RoadInsight Implementation Reference
            r_r1 = p.add_run("3. ROADINSIGHT IMPLEMENTATION REFERENCE:\n")
            r_r1.font.bold = True
            r_r1.font.size = Pt(9)
            r_r1.font.color.rgb = COLOR_TEAL
            r_r2 = p.add_run(f"{item['ref']}\n\n")
            r_r2.font.size = Pt(9)
            r_r2.font.name = "Consolas"
            r_r2.font.color.rgb = COLOR_NAVY
            
            # 4. Trade-off or Limitation
            r_l1 = p.add_run("4. IMPORTANT TRADE-OFF OR LIMITATION:\n")
            r_l1.font.bold = True
            r_l1.font.size = Pt(9)
            r_l1.font.color.rgb = RGBColor(194, 65, 12) # Rust/Orange
            r_l2 = p.add_run(f"{item['tradeoff']}")
            r_l2.font.size = Pt(9.5)
            r_l2.font.color.rgb = COLOR_CHARCOAL
            
            p_space = doc.add_paragraph()
            p_space.paragraph_format.space_before = Pt(0)
            p_space.paragraph_format.space_after = Pt(6)
            
        doc.add_page_break()

    # Save
    doc.save(output_path)
    print(f"[DOCX] Viva Question Bank successfully generated: {output_path}")

