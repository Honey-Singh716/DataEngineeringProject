"""
doc_generator/styles.py
Styling definitions and formatting helpers for DOCX and PDF generation.
Standardized Palette: Navy Blue (#1A365D), Teal (#0D9488), Slate (#475569), Charcoal (#1E293B).
"""
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

# Color constants
COLOR_NAVY = RGBColor(26, 54, 93)      # #1A365D
COLOR_TEAL = RGBColor(13, 148, 136)   # #0D9488
COLOR_CHARCOAL = RGBColor(30, 41, 59) # #1E293B
COLOR_SLATE = RGBColor(71, 85, 105)   # #475569
COLOR_MUTED = RGBColor(100, 116, 139) # #64748B
COLOR_WHITE = RGBColor(255, 255, 255) # #FFFFFF

HEX_NAVY = "1A365D"
HEX_TEAL = "0D9488"
HEX_BG_ALT = "F8FAFC"
HEX_BORDER = "CBD5E1"
HEX_CODE_BG = "0F172A"
HEX_CALLOUT_BG = "F1F5F9"

def set_cell_background(cell, hex_color: str):
    """Set the background color of a docx table cell."""
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    cell._tc.get_or_add_tcPr().append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Set padding in twips (1/20th pt)."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def add_callout(doc, text: str, badge: str = "IMPLEMENTED AND VERIFIED"):
    """Add a professional styled callout block to a Word document."""
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    
    cell = tbl.cell(0, 0)
    set_cell_background(cell, HEX_CALLOUT_BG)
    set_cell_margins(cell, top=140, bottom=140, left=200, right=200)
    
    # Left border in Teal (#0D9488)
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(f'''
        <w:tcBorders {nsdecls("w")}>
            <w:top w:val="none"/>
            <w:left w:val="single" w:sz="24" w:space="0" w:color="{HEX_TEAL}"/>
            <w:bottom w:val="none"/>
            <w:right w:val="none"/>
        </w:tcBorders>
    ''')
    tcPr.append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.15
    
    b_run = p.add_run(f"[{badge}] ")
    b_run.font.bold = True
    b_run.font.size = Pt(9.5)
    b_run.font.color.rgb = COLOR_TEAL
    
    t_run = p.add_run(text)
    t_run.font.size = Pt(9.5)
    t_run.font.color.rgb = COLOR_CHARCOAL
    
    # Empty trailing spacing
    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_before = Pt(0)
    p_after.paragraph_format.space_after = Pt(6)

def add_code_block(doc, code_str: str):
    """Add a shaded code block with fixed-width font."""
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    
    cell = tbl.cell(0, 0)
    set_cell_background(cell, "1E293B")
    set_cell_margins(cell, top=120, bottom=120, left=180, right=180)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.15
    
    run = p.add_run(code_str.strip())
    run.font.name = "Consolas"
    run.font.size = Pt(8.5)
    run.font.color.rgb = RGBColor(241, 245, 249) # white/ice
    
    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_before = Pt(0)
    p_after.paragraph_format.space_after = Pt(6)

def add_styled_table(doc, headers: list[str], rows: list[list[str]], col_widths: list[float] = None):
    """Add a professional academic table with navy header and alternating rows."""
    tbl = doc.add_table(rows=len(rows) + 1, cols=len(headers))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    
    # Header row
    hdr_row = tbl.rows[0]
    for idx, heading in enumerate(headers):
        cell = hdr_row.cells[idx]
        set_cell_background(cell, HEX_NAVY)
        set_cell_margins(cell, top=120, bottom=120, left=140, right=140)
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        run = p.add_run(heading)
        run.font.bold = True
        run.font.size = Pt(9)
        run.font.color.rgb = COLOR_WHITE
        run.font.name = "Arial"
    
    # Data rows
    for r_idx, row_data in enumerate(rows):
        row = tbl.rows[r_idx + 1]
        bg = HEX_BG_ALT if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, val in enumerate(row_data):
            cell = row.cells[c_idx]
            if bg != "FFFFFF":
                set_cell_background(cell, bg)
            set_cell_margins(cell, top=100, bottom=100, left=140, right=140)
            
            # Subtle cell border
            tcPr = cell._tc.get_or_add_tcPr()
            borders = parse_xml(f'''
                <w:tcBorders {nsdecls("w")}>
                    <w:top w:val="single" w:sz="4" w:space="0" w:color="{HEX_BORDER}"/>
                    <w:left w:val="single" w:sz="4" w:space="0" w:color="{HEX_BORDER}"/>
                    <w:bottom w:val="single" w:sz="4" w:space="0" w:color="{HEX_BORDER}"/>
                    <w:right w:val="single" w:sz="4" w:space="0" w:color="{HEX_BORDER}"/>
                </w:tcBorders>
            ''')
            tcPr.append(borders)
            
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(1)
            p.paragraph_format.line_spacing = 1.15
            run = p.add_run(str(val))
            run.font.size = Pt(8.5)
            run.font.name = "Arial"
            run.font.color.rgb = COLOR_CHARCOAL
    
    # Column widths if specified
    if col_widths:
        for row in tbl.rows:
            for idx, w in enumerate(col_widths):
                row.cells[idx].width = Inches(w)
                
    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_before = Pt(0)
    p_after.paragraph_format.space_after = Pt(8)

PDF_CSS = """
@page {
    size: letter;
    margin: 54pt;
}
body {
    font-family: Helvetica, Arial, sans-serif;
    font-size: 9.5pt;
    line-height: 1.45;
    color: #1e293b;
}
h1 {
    color: #1a365d;
    font-size: 16pt;
    border-bottom: 2pt solid #0d9488;
    padding-bottom: 4pt;
    margin-top: 24pt;
    margin-bottom: 12pt;
    page-break-before: always;
}
h1.first {
    page-break-before: avoid;
}
h2 {
    color: #0d9488;
    font-size: 12.5pt;
    margin-top: 16pt;
    margin-bottom: 8pt;
    border-bottom: 0.5pt solid #cbd5e1;
    padding-bottom: 2pt;
}
h3 {
    color: #1e293b;
    font-size: 10.5pt;
    margin-top: 12pt;
    margin-bottom: 4pt;
}
p {
    margin-top: 0pt;
    margin-bottom: 7pt;
    text-align: justify;
}
ul, ol {
    margin-top: 0pt;
    margin-bottom: 8pt;
    padding-left: 18pt;
}
li {
    margin-bottom: 3pt;
}
table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 8pt;
    margin-bottom: 12pt;
    font-size: 8.5pt;
}
th {
    background-color: #1a365d;
    color: #ffffff;
    font-weight: bold;
    text-align: left;
    padding: 5pt 6pt;
    border: 0.5pt solid #1a365d;
}
td {
    padding: 4pt 6pt;
    border: 0.5pt solid #cbd5e1;
    vertical-align: top;
}
tr:nth-child(even) td {
    background-color: #f8fafc;
}
code {
    font-family: Courier, monospace;
    font-size: 8.5pt;
    background-color: #f1f5f9;
    padding: 1pt 3pt;
    border-radius: 2pt;
    color: #0f172a;
}
pre {
    background-color: #0f172a;
    color: #f8fafc;
    padding: 8pt;
    font-family: Courier, monospace;
    font-size: 8pt;
    line-height: 1.3;
    border-radius: 3pt;
    margin-top: 6pt;
    margin-bottom: 10pt;
    white-space: pre-wrap;
    word-break: break-all;
}
.callout {
    background-color: #f1f5f9;
    border-left: 3pt solid #0d9488;
    padding: 6pt 10pt;
    margin-top: 8pt;
    margin-bottom: 10pt;
    border-radius: 2pt;
}
.callout-badge {
    font-weight: bold;
    color: #0d9488;
    font-size: 8.5pt;
    text-transform: uppercase;
    display: block;
    margin-bottom: 2pt;
}
.cover-title {
    font-size: 26pt;
    font-weight: bold;
    color: #1a365d;
    text-align: center;
    margin-top: 80pt;
    margin-bottom: 12pt;
    line-height: 1.2;
}
.cover-subtitle {
    font-size: 13pt;
    color: #0d9488;
    text-align: center;
    margin-bottom: 40pt;
    font-weight: bold;
}
.cover-meta {
    font-size: 10pt;
    color: #334155;
    text-align: center;
    line-height: 1.8;
    margin-top: 50pt;
}
.cover-divider {
    width: 60%;
    margin: 20pt auto;
    border-top: 2pt solid #0d9488;
}
.viva-card {
    background-color: #ffffff;
    border: 1pt solid #cbd5e1;
    border-left: 3.5pt solid #1a365d;
    padding: 8pt 10pt;
    margin-top: 10pt;
    margin-bottom: 12pt;
    border-radius: 2pt;
}
.viva-q {
    font-size: 10.5pt;
    font-weight: bold;
    color: #1a365d;
    margin-bottom: 6pt;
}
.viva-label {
    font-weight: bold;
    color: #0d9488;
    font-size: 8.5pt;
    text-transform: uppercase;
    margin-top: 4pt;
    margin-bottom: 1pt;
}
"""

