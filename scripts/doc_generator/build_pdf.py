"""
doc_generator/build_pdf.py
Builds professional PDF deliverables using PyMuPDF (fitz.Story + DocumentWriter + running headers/footers):
1. RoadInsight_India_Final_Technical_Report.pdf
2. RoadInsight_India_Viva_Question_Bank.pdf
"""
import os
import fitz
import html

from scripts.doc_generator.styles import PDF_CSS
from scripts.doc_generator.report_content import REPORT_METADATA, EXECUTIVE_SUMMARY, ALL_REPORT_CHAPTERS
from scripts.doc_generator.viva_content import VIVA_METADATA, ALL_VIVA_CATEGORIES

def _render_html_to_pdf(html_content: str, raw_pdf_path: str, final_pdf_path: str, header_text: str):
    """Render HTML content into multi-page PDF with running headers, footers, and page numbers."""
    writer = fitz.DocumentWriter(raw_pdf_path)
    story = fitz.Story(html_content)
    
    def rectfn(rect_num, filled):
        mediabox = fitz.Rect(0, 0, 612, 792) # Standard Letter
        # Margins: left=54, top=58, right=558, bottom=734 (leaves room for header & footer)
        rect = fitz.Rect(54, 58, 558, 734)
        return mediabox, rect, fitz.Matrix(1, 1)

    story.write(writer, rectfn)
    writer.close()
    
    # Reopen to decorate with running headers, footers, and page numbers
    doc = fitz.open(raw_pdf_path)
    total_pages = doc.page_count
    
    for idx, page in enumerate(doc):
        page_num = idx + 1
        
        # Don't draw headers/footers on page 1 if it's the cover page
        if page_num > 1:
            # Running header
            page.insert_text((54, 38), f"RoadInsight India — {header_text}", fontsize=8, color=(0.4, 0.4, 0.4))
            page.draw_line((54, 44), (558, 44), color=(0.8, 0.8, 0.8), width=0.5)
            
            # Running footer
            page.draw_line((54, 748), (558, 748), color=(0.8, 0.8, 0.8), width=0.5)
            page.insert_text((54, 762), "Confidential — Academic Evaluation | Branch: feature/hardening", fontsize=8, color=(0.5, 0.5, 0.5))
            page.insert_text((490, 762), f"Page {page_num} of {total_pages}", fontsize=8, color=(0.5, 0.5, 0.5))
            
    doc.save(final_pdf_path)
    doc.close()
    
    # Remove raw unadorned intermediate file
    if os.path.exists(raw_pdf_path):
        os.remove(raw_pdf_path)
        
    print(f"[PDF] Successfully generated {final_pdf_path} (Total Pages: {total_pages})")

def generate_technical_report_pdf(output_path: str):
    """Generate the complete Technical Report PDF."""
    raw_path = output_path + ".tmp.pdf"
    
    parts = [f"<style>{PDF_CSS}</style>"]
    
    # Cover page
    parts.append('<div class="cover-title">ROADINSIGHT INDIA</div>')
    parts.append('<div class="cover-subtitle">Complete Technical Implementation, Testing & Performance Analysis</div>')
    parts.append('<div class="cover-divider"></div>')
    
    team_list = "<br>".join([f"• {html.escape(m)}" for m in REPORT_METADATA["team"]])
    parts.append(f'''
    <div class="cover-meta">
        <b>Project Domain:</b> {html.escape(REPORT_METADATA["domain"])}<br><br>
        <b>Project Team:</b><br>{team_list}<br><br>
        <b>Technology Stack:</b><br>{html.escape(REPORT_METADATA["tech_stack"])}<br><br>
        <b>Evaluation:</b> {html.escape(REPORT_METADATA["evaluation"])}<br>
        <b>Active Branch:</b> {html.escape(REPORT_METADATA["branch"])}
    </div>
    ''')
    
    # Executive Summary
    parts.append('<h1>EXECUTIVE SUMMARY</h1>')
    for b in EXECUTIVE_SUMMARY:
        parts.append(f'<p>{html.escape(b["text"])}</p>')
        
    # Table of Contents
    parts.append('<h2>TABLE OF CONTENTS</h2><ul>')
    for ch in ALL_REPORT_CHAPTERS:
        parts.append(f'<li>{html.escape(ch["title"])}</li>')
    parts.append('</ul>')
    
    # Chapters 1 to 18
    for ch in ALL_REPORT_CHAPTERS:
        parts.append(f'<h1>{html.escape(ch["title"])}</h1>')
        for b in ch["blocks"]:
            b_type = b["type"]
            if b_type == "p":
                parts.append(f'<p>{html.escape(b["text"])}</p>')
            elif b_type == "h2":
                parts.append(f'<h2>{html.escape(b["text"])}</h2>')
            elif b_type == "callout":
                badge = html.escape(b.get("badge", "NOTE"))
                text = html.escape(b["text"])
                parts.append(f'<div class="callout"><span class="callout-badge">[{badge}]</span>{text}</div>')
            elif b_type == "code":
                parts.append(f'<pre><code>{html.escape(b["text"].strip())}</code></pre>')
            elif b_type == "table":
                parts.append('<table><thead><tr>')
                for h_cell in b["headers"]:
                    parts.append(f'<th>{html.escape(h_cell)}</th>')
                parts.append('</tr></thead><tbody>')
                for row in b["rows"]:
                    parts.append('<tr>')
                    for cell in row:
                        parts.append(f'<td>{html.escape(str(cell))}</td>')
                    parts.append('</tr>')
                parts.append('</tbody></table>')
            elif b_type == "bullets":
                parts.append('<ul>')
                for item in b["items"]:
                    parts.append(f'<li>{html.escape(item)}</li>')
                parts.append('</ul>')
                
    full_html = "\n".join(parts)
    _render_html_to_pdf(full_html, raw_path, output_path, "Technical Implementation & Engineering Audit")

def generate_viva_question_bank_pdf(output_path: str):
    """Generate the complete Viva Question Bank PDF."""
    raw_path = output_path + ".tmp.pdf"
    
    parts = [f"<style>{PDF_CSS}</style>"]
    
    # Cover page
    parts.append('<div class="cover-title">ROADINSIGHT INDIA</div>')
    parts.append('<div class="cover-subtitle">Viva & Faculty Question Bank</div>')
    parts.append('<div class="cover-divider"></div>')
    
    team_list = "<br>".join([f"• {html.escape(m)}" for m in VIVA_METADATA["team"]])
    parts.append(f'''
    <div class="cover-meta">
        <b>Comprehensive Faculty Preparation: Theory, Implementation & Limitations</b><br><br>
        <b>Project Team:</b><br>{team_list}<br><br>
        <b>Technology Stack:</b><br>{html.escape(VIVA_METADATA["tech_stack"])}<br><br>
        <b>Evaluation:</b> {html.escape(VIVA_METADATA["evaluation"])}<br>
        <b>Active Branch:</b> {html.escape(VIVA_METADATA["branch"])}
    </div>
    ''')
    
    # Categories A to H
    for cat in ALL_VIVA_CATEGORIES:
        parts.append(f'<h1>CATEGORY {html.escape(cat["category"])}</h1>')
        for idx, item in enumerate(cat["questions"]):
            parts.append(f'''
            <div class="viva-card">
                <div class="viva-q">Q{idx+1}: {html.escape(item["q"])}</div>
                <div class="viva-label">1. Short Viva Answer</div>
                <p>{html.escape(item["short"])}</p>
                <div class="viva-label">2. Detailed Technical Explanation</div>
                <p>{html.escape(item["tech"])}</p>
                <div class="viva-label">3. RoadInsight Implementation Reference</div>
                <p><code>{html.escape(item["ref"])}</code></p>
                <div class="viva-label" style="color: #c2410c;">4. Important Trade-off or Limitation</div>
                <p>{html.escape(item["tradeoff"])}</p>
            </div>
            ''')
            
    full_html = "\n".join(parts)
    _render_html_to_pdf(full_html, raw_path, output_path, "Viva & Faculty Question Bank")

