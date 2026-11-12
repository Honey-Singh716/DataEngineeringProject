"""Comprehensive Script to generate RoadInsight India Project Progress Report in DOCX and PDF formats.
Deliverables:
- /Users/jayantsoni/Desktop/RoadInsight_India/RoadInsight_India_Project_Progress_Report.docx
- /Users/jayantsoni/Desktop/RoadInsight_India/RoadInsight_India_Project_Progress_Report.pdf
"""

import os
import sys
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak, HRFlowable
)
from reportlab.pdfgen import canvas

# Paths
DOCX_PATH = '/Users/jayantsoni/Desktop/RoadInsight_India/RoadInsight_India_Project_Progress_Report.docx'
PDF_PATH = '/Users/jayantsoni/Desktop/RoadInsight_India/RoadInsight_India_Project_Progress_Report.pdf'
ASSETS_DIR = 'report_assets'

# Helper XML styling for docx
def set_cell_background(cell, color_hex):
    shading_xml = f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>'
    cell._tc.get_or_add_tcPr().append(parse_xml(shading_xml))

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)]:
        node = OxmlElement(m)
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def create_callout_box(doc, text, title="NOTE / STATUS", bg_color="F8FAFC", border_color="193C65"):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_background(cell, bg_color)
    set_cell_margins(cell, top=140, bottom=140, left=200, right=200)
    
    tcPr = cell._tc.get_or_add_tcPr()
    borders_xml = f'''
    <w:tcBorders {nsdecls("w")}>
        <w:top w:val="none"/>
        <w:left w:val="single" w:sz="24" w:space="0" w:color="{border_color}"/>
        <w:bottom w:val="none"/>
        <w:right w:val="none"/>
    </w:tcBorders>
    '''
    tcPr.append(parse_xml(borders_xml))
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    run_t = p.add_run(f"[{title}] ")
    run_t.bold = True
    run_t.font.name = 'Calibri'
    run_t.font.size = Pt(10)
    run_t.font.color.rgb = RGBColor(0x19, 0x3C, 0x65) if border_color=="193C65" else RGBColor(0xD9, 0x77, 0x06)
    
    run_b = p.add_run(text)
    run_b.font.name = 'Calibri'
    run_b.font.size = Pt(9.5)
    run_b.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

def format_table(tbl, col_widths, col_alignments=None):
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    for r_idx, row in enumerate(tbl.rows):
        trPr = row._tr.get_or_add_trPr()
        trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
        for c_idx, cell in enumerate(row.cells):
            cell.width = col_widths[c_idx]
            set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
            if r_idx == 0:
                set_cell_background(cell, "193C65")
                p = cell.paragraphs[0]
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                for run in p.runs:
                    run.font.bold = True
                    run.font.name = 'Calibri'
                    run.font.size = Pt(9)
                    run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            else:
                bg = "F1F5F9" if r_idx % 2 == 1 else "FFFFFF"
                set_cell_background(cell, bg)
                p = cell.paragraphs[0]
                align = col_alignments[c_idx] if col_alignments else WD_ALIGN_PARAGRAPH.LEFT
                p.alignment = align
                for run in p.runs:
                    run.font.name = 'Calibri'
                    run.font.size = Pt(8.5)
                    run.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

# Numbered Canvas for ReportLab
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor('#64748B'))
        
        # Running header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 750, "RoadInsight India — Project Progress & Implementation Report")
            self.drawRightString(558, 750, "Cut-off: 10-11-2026 | Status: In Progress")
            self.setStrokeColor(colors.HexColor('#CBD5E1'))
            self.setLineWidth(0.5)
            self.line(54, 742, 558, 742)
            
        # Running footer
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawString(54, 36, "Confidential — Academic & Technical Evaluation Document")
        self.drawRightString(558, 36, page_str)
        self.setStrokeColor(colors.HexColor('#CBD5E1'))
        self.setLineWidth(0.5)
        self.line(54, 46, 558, 46)
        self.restoreState()

print("Helper classes and styling functions initialized.")

