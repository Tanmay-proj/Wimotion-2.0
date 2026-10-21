# -*- coding: utf-8 -*-
"""
build_complete_integrated_report.py
Builds the complete, final, professional dissertation for MCTE:
1. Section 1: Preserves the official MCTE Academy Cover Page & DS Comments pages
   from PROJECT_REPORT_FILE(TNM&RSR).docx (elements 0 to 102: title banners, shapes,
   textboxes with OC Tanmay Mugale TES-4312 & OC Rishabh Rathore TES-4316,
   DS Guide Lt Col Rajat Gaur, DS Co-Guide Maj Vaibhav Kukreti, and DS Comments).
2. Sections 2 & 3:
   - Header is strictly linked to previous across all sections: uses the template's native
     top-centered page numbers (1, 2, 3...) with NO top-right header text.
   - Footers are completely empty (no duplicate footer page numbers).
   - Uniform continuous Arabic page numbering (1, 2, 3...) throughout the entire report.
   - College name strictly: Military College of Telecommunication Engineering (MCTE).
   - Certificate of Approval & Student Declaration removed per user request.
   - Keywords section removed completely from text and Table of Contents per user request.
   - Appendix I and Appendix J removed completely from text and Table of Contents per user request.
   - Front matter starts cleanly with Acknowledgements (thanking MCTE, Lt Col Rajat Gaur, Maj Vaibhav Kukreti).
   - Dynamic Table of Contents field code (F9 to refresh) + formatted structured TOC.
   - ALL 19 Figure Insertion Boxes (clean dashed boxes with instructions & formal captions).
   - ALL 15 Markdown Tables with Navy headers and alternate zebra shading.
   - ALL Code Blocks and ASCII Architecture Diagrams in shaded Consolas monospace boxes.
   - True Word Heading styles (Heading 1, Heading 2, Heading 3).
   - Page layout: Subsections flow continuously on pages without artificial page breaks.
3. Saves to:
   - E:\WIFI_INTERFEROMETRIC_NEURAL_SENSING\Project_Report_File.docx
   - E:\WIFI_INTERFEROMETRIC_NEURAL_SENSING\PROJECT_REPORT_FILE(TNM&RSR)_UPDATED.docx
   - E:\WIFI_INTERFEROMETRIC_NEURAL_SENSING\PROJECT_REPORT_FILE(TNM&RSR).docx (if not locked by Word)
"""
import os
import re
import sys
from pathlib import Path

import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

REPO_ROOT = Path(r"e:\WIFI_INTERFEROMETRIC_NEURAL_SENSING\wimotion_2.0")
PARENT_DIR = Path(r"e:\WIFI_INTERFEROMETRIC_NEURAL_SENSING")
MD_PATH = REPO_ROOT / "docs" / "MASTER_DISSERTATION_FINAL.md"
TNM_BASE_PATH = PARENT_DIR / "PROJECT_REPORT_FILE(TNM&RSR).docx"

COLOR_NAVY = RGBColor(27, 54, 93)       # #1B365D - Deep Navy
COLOR_SLATE = RGBColor(51, 65, 85)      # #334155 - Slate Grey
COLOR_MUTED = RGBColor(100, 116, 139)   # #64748B - Muted Grey
COLOR_BODY = RGBColor(30, 41, 59)       # #1E293B - Off-Black


def configure_styles(doc):
    styles = doc.styles

    try:
        norm = styles['Normal']
        norm.font.name = 'Times New Roman'
        norm.font.size = Pt(12)
        norm.font.color.rgb = COLOR_BODY
        norm.paragraph_format.line_spacing = 1.35
        norm.paragraph_format.space_after = Pt(6)
        norm.paragraph_format.space_before = Pt(0)
    except Exception as e:
        print("Note on Normal style:", e)

    h_configs = [
        ('Heading 1', 16, True, False, COLOR_NAVY, 18, 8),
        ('Heading 2', 14, True, False, COLOR_SLATE, 14, 6),
        ('Heading 3', 12, True, True, COLOR_SLATE, 10, 4),
    ]

    for name, sz, b, it, col, sb, sa in h_configs:
        try:
            h = styles[name]
        except KeyError:
            h = styles.add_style(name, docx.enum.style.WD_STYLE_TYPE.PARAGRAPH)
        h.font.name = 'Times New Roman'
        h.font.size = Pt(sz)
        h.font.bold = b
        h.font.italic = it
        h.font.color.rgb = col
        h.paragraph_format.space_before = Pt(sb)
        h.paragraph_format.space_after = Pt(sa)
        h.paragraph_format.keep_with_next = True


def apply_page_margins(section):
    section.top_margin = Inches(1.0)
    section.bottom_margin = Inches(1.0)
    section.left_margin = Inches(1.0)
    section.right_margin = Inches(1.0)


def set_cell_background(cell, hex_color):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tc_pr.append(shd)


def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_mar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tc_pr.append(tc_mar)


def add_toc_field(p):
    fld_char1 = parse_xml(r'<w:fldChar %s w:fldCharType="begin"/>' % nsdecls('w'))
    instr_text = parse_xml(r'<w:instrText %s xml:space="preserve"> TOC \o "1-3" \h \z \u </w:instrText>' % nsdecls('w'))
    fld_char2 = parse_xml(r'<w:fldChar %s w:fldCharType="separate"/>' % nsdecls('w'))
    fld_char3 = parse_xml(r'<w:fldChar %s w:fldCharType="end"/>' % nsdecls('w'))
    run = p.add_run()
    run._r.append(fld_char1)
    run._r.append(instr_text)
    run._r.append(fld_char2)
    run._r.append(fld_char3)


def add_formatted_text(paragraph, text, font_size=12, default_bold=False, default_italic=False, default_color=COLOR_BODY):
    tokens = re.split(r'(\*\*.*?\*\*|\*.*?\*|`.*?`)', text)
    for tok in tokens:
        if not tok:
            continue
        is_bold = default_bold
        is_italic = default_italic
        is_code = False
        tok_clean = tok

        if tok.startswith('**') and tok.endswith('**') and len(tok) >= 4:
            is_bold = True
            tok_clean = tok[2:-2]
        elif tok.startswith('*') and tok.endswith('*') and len(tok) >= 2:
            is_italic = True
            tok_clean = tok[1:-1]
        elif tok.startswith('`') and tok.endswith('`') and len(tok) >= 2:
            is_code = True
            tok_clean = tok[1:-1]

        run = paragraph.add_run(tok_clean)
        run.font.size = Pt(font_size)
        run.bold = is_bold
        run.italic = is_italic
        if is_code:
            run.font.name = "Consolas"
            run.font.color.rgb = RGBColor(180, 40, 40)
        else:
            run.font.name = "Times New Roman"
            run.font.color.rgb = default_color


def render_code_block(doc, code_lines):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_background(cell, "F5F7FA")
    set_cell_margins(cell, top=120, bottom=120, left=180, right=180)

    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:left w:val="single" w:sz="18" w:space="0" w:color="1B365D"/>'
        f'<w:top w:val="single" w:sz="4" w:space="0" w:color="E0E0E0"/>'
        f'<w:bottom w:val="single" w:sz="4" w:space="0" w:color="E0E0E0"/>'
        f'<w:right w:val="single" w:sz="4" w:space="0" w:color="E0E0E0"/>'
        f'</w:tblBorders>'
    )
    tbl._tbl.tblPr.append(borders)

    cp = cell.paragraphs[0]
    cp.paragraph_format.line_spacing = 1.05
    cp.paragraph_format.space_after = Pt(0)
    cp.alignment = WD_ALIGN_PARAGRAPH.LEFT

    code_text = "\n".join(code_lines)
    run = cp.add_run(code_text)
    run.font.name = "Consolas"
    run.font.size = Pt(8.5)
    run.font.color.rgb = RGBColor(30, 40, 50)

    sp = doc.add_paragraph()
    sp.paragraph_format.space_after = Pt(4)


def render_image_placeholder(doc, line):
    caption_text = re.sub(r'[\*\[\]]', '', line).strip()
    if caption_text.startswith("- ") or caption_text.startswith("* "):
        caption_text = caption_text[2:].strip()

    m_fig = re.search(r'(Figure\s+[0-9A-Za-z\.]+)', caption_text, re.IGNORECASE)
    fig_tag = m_fig.group(1).upper() if m_fig else "FIGURE"

    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_background(cell, "F8FAFC")
    set_cell_margins(cell, top=240, bottom=240, left=320, right=320)

    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="dashed" w:sz="8" w:space="0" w:color="94A3B8"/>'
        f'<w:bottom w:val="dashed" w:sz="8" w:space="0" w:color="94A3B8"/>'
        f'<w:left w:val="dashed" w:sz="8" w:space="0" w:color="94A3B8"/>'
        f'<w:right w:val="dashed" w:sz="8" w:space="0" w:color="94A3B8"/>'
        f'</w:tblBorders>'
    )
    tbl._tbl.tblPr.append(borders)

    cp = cell.paragraphs[0]
    cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cp.paragraph_format.line_spacing = 1.2
    cp.paragraph_format.space_after = Pt(2)

    r1 = cp.add_run(f"📷  [ INSERT {fig_tag} HERE ]\n")
    r1.font.name = "Times New Roman"
    r1.font.size = Pt(11)
    r1.bold = True
    r1.font.color.rgb = COLOR_NAVY

    r2 = cp.add_run("Suggested Format: High-Resolution Landscape Image (Width: ~5.5 inches)\n(Word Action: Click inside this box ➔ Insert ➔ Pictures ➔ This Device)")
    r2.font.name = "Times New Roman"
    r2.font.size = Pt(9.0)
    r2.italic = True
    r2.font.color.rgb = COLOR_MUTED

    cap_p = doc.add_paragraph()
    cap_p.paragraph_format.space_before = Pt(4)
    cap_p.paragraph_format.space_after = Pt(8)
    cap_p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    parts = caption_text.split(":", 1)
    if len(parts) == 2:
        r_label = cap_p.add_run(parts[0].strip() + ": ")
        r_label.font.name = "Times New Roman"
        r_label.font.size = Pt(10)
        r_label.bold = True
        r_label.font.color.rgb = COLOR_NAVY

        r_desc = cap_p.add_run(parts[1].strip())
        r_desc.font.name = "Times New Roman"
        r_desc.font.size = Pt(10)
        r_desc.italic = True
        r_desc.font.color.rgb = COLOR_BODY
    else:
        r_desc = cap_p.add_run(caption_text)
        r_desc.font.name = "Times New Roman"
        r_desc.font.size = Pt(10)
        r_desc.bold = True
        r_desc.font.color.rgb = COLOR_NAVY

    return True


def render_table(doc, table_buffer):
    if not table_buffer or len(table_buffer) < 2:
        return

    cleaned_rows = []
    for r in table_buffer:
        r_str = r.strip()
        if r_str.startswith("|"):
            r_str = r_str[1:]
        if r_str.endswith("|"):
            r_str = r_str[:-1]
        cols = [c.strip() for c in r_str.split("|")]
        cleaned_rows.append(cols)

    if not cleaned_rows:
        return

    header_cols = cleaned_rows[0]
    data_rows = []
    for r in cleaned_rows[1:]:
        if all(re.match(r'^:?-+:?$', c) for c in r if c):
            continue
        data_rows.append(r)

    num_cols = len(header_cols)
    if num_cols == 0:
        return

    num_rows = 1 + len(data_rows)
    tbl = doc.add_table(rows=num_rows, cols=num_cols)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER

    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="8" w:space="0" w:color="1B365D"/>'
        f'<w:bottom w:val="single" w:sz="8" w:space="0" w:color="1B365D"/>'
        f'<w:insideH w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>'
        f'<w:left w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'<w:insideV w:val="none"/>'
        f'</w:tblBorders>'
    )
    tbl._tbl.tblPr.append(borders)

    for c_idx, col_text in enumerate(header_cols):
        cell = tbl.cell(0, c_idx)
        set_cell_background(cell, "1B365D")
        set_cell_margins(cell, top=120, bottom=120, left=140, right=140)
        p = cell.paragraphs[0]
        p.paragraph_format.line_spacing = 1.15
        p.paragraph_format.space_after = Pt(0)
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        run = p.add_run(col_text)
        run.font.name = "Times New Roman"
        run.font.size = Pt(10)
        run.bold = True
        run.font.color.rgb = RGBColor(255, 255, 255)

    for r_idx, row_cols in enumerate(data_rows):
        bg = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
        for c_idx in range(num_cols):
            cell = tbl.cell(r_idx + 1, c_idx)
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=90, bottom=90, left=140, right=140)
            p = cell.paragraphs[0]
            p.paragraph_format.line_spacing = 1.15
            p.paragraph_format.space_after = Pt(0)
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            txt = row_cols[c_idx] if c_idx < len(row_cols) else ""
            add_formatted_text(p, txt, font_size=9.5, default_color=COLOR_BODY)

    sp = doc.add_paragraph()
    sp.paragraph_format.space_after = Pt(4)


def build_integrated_dissertation():
    print(f"[*] Reading master markdown: {MD_PATH}")
    with open(MD_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Load base template document
    print(f"[*] Loading base document: {TNM_BASE_PATH}")
    doc = Document(str(TNM_BASE_PATH))
    configure_styles(doc)

    # Clean up base document: keep elements 0 to 102 (Cover Page, textboxes & DS comments)
    # and preserve final root sectPr (body[-1])
    body = doc._body._element
    print(f"[*] Initial base elements: {len(body)}")
    while len(body) > 104:
        body.remove(body[103])
    print(f"[+] Preserved official cover & comments. Trimmed elements to: {len(body)}")

    # Clean any MCEME occurrences in preserved base elements
    for el in body[:103]:
        for t in el.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'):
            if 'MCEME' in t.text or 'Mechanical' in t.text:
                t.text = t.text.replace('Military College of Electronics and Mechanical Engineering (MCEME)', 'Military College of Telecommunication Engineering (MCTE)')
                t.text = t.text.replace('MCEME', 'MCTE')

    # SECTION 1: Cover Page & DS Comments (elements 0 to 102)
    sec_cover = doc.sections[0]
    apply_page_margins(sec_cover)
    sec_cover.different_first_page_header_footer = True
    for p in sec_cover.footer.paragraphs:
        p.text = ""

    lines = content.splitlines()
    total_lines = len(lines)
    i = 0

    in_code_block = False
    code_buffer = []
    table_buffer = []
    in_table = False
    in_front_matter_figure_list = False
    current_section = 1  # 1 = Cover, 2 = Front Matter, 3 = Chapters

    # Skip lines until "## 2. ACKNOWLEDGEMENTS" in markdown because Cover Page & DS comments are already in base doc
    while i < total_lines:
        if "## 2. ACKNOWLEDGEMENTS" in lines[i]:
            break
        i += 1

    # Transition to Section 2 (Front Matter)
    current_section = 2
    sec_front = doc.add_section()
    apply_page_margins(sec_front)
    sec_front.different_first_page_header_footer = False
    sec_front.header.is_linked_to_previous = True
    sec_front.footer.is_linked_to_previous = True

    front_matter_page_breaks = [
        "## 2. ACKNOWLEDGEMENTS",
        "## 3. ABSTRACT",
        "## 4. TABLE OF CONTENTS",
        "## 5. LIST OF FIGURES",
        "## 6. LIST OF TABLES",
        "## 7. LIST OF ABBREVIATIONS"
    ]

    while i < total_lines:
        line = lines[i]
        line_stripped = line.strip()

        # Transition from Front Matter to Chapter 1 (Section 3)
        if line_stripped.startswith("# CHAPTER 1:") and current_section == 2:
            current_section = 3
            sec_chapters = doc.add_section()
            apply_page_margins(sec_chapters)
            sec_chapters.different_first_page_header_footer = False
            sec_chapters.header.is_linked_to_previous = True
            sec_chapters.footer.is_linked_to_previous = True

        # Code Blocks (```)
        if line_stripped.startswith("```"):
            if in_code_block:
                in_code_block = False
                render_code_block(doc, code_buffer)
                code_buffer = []
            else:
                in_code_block = True
                code_buffer = []
            i += 1
            continue

        if in_code_block:
            code_buffer.append(line)
            i += 1
            continue

        # Tables (| col | col |)
        if "|" in line_stripped and (line_stripped.startswith("|") or line_stripped.endswith("|")):
            in_table = True
            table_buffer.append(line_stripped)
            i += 1
            continue
        else:
            if in_table:
                render_table(doc, table_buffer)
                table_buffer = []
                in_table = False

        # Horizontal rules / Page Break delimiters
        if line_stripped in ("---", "***", "___") or "page-break-after" in line_stripped:
            if current_section == 2:
                next_line = ""
                for k in range(i + 1, min(i + 6, total_lines)):
                    if lines[k].strip():
                        next_line = lines[k].strip()
                        break

                if any(sec in next_line for sec in front_matter_page_breaks):
                    doc.add_page_break()

            i += 1
            continue

        # Track Front Matter List of Figures
        if "5. LIST OF FIGURES" in line_stripped or "LIST OF FIGURES" in line_stripped:
            in_front_matter_figure_list = True
        elif in_front_matter_figure_list and ("LIST OF TABLES" in line_stripped or line_stripped == "---"):
            in_front_matter_figure_list = False

        # Figure Placeholders & Captions
        if not in_front_matter_figure_list and re.match(r'^[\*\-\s]*(\*\*)?\[?Figure\s+[A-Za-z0-9\.]+', line_stripped, re.IGNORECASE):
            if render_image_placeholder(doc, line_stripped):
                i += 1
                continue

        # Dynamic Table of Contents Field
        if line_stripped.startswith("## 4. TABLE OF CONTENTS"):
            p = doc.add_paragraph(style='Heading 2')
            run = p.add_run("4. TABLE OF CONTENTS")
            run.font.name = "Times New Roman"
            run.font.size = Pt(14)
            run.bold = True
            run.font.color.rgb = COLOR_SLATE

            toc_box = doc.add_paragraph()
            toc_box.paragraph_format.line_spacing = 1.25
            toc_box.paragraph_format.space_after = Pt(10)
            add_toc_field(toc_box)
            i += 1
            continue

        # Skip any Keywords section
        if "KEYWORDS" in line_stripped.upper() and (line_stripped.startswith("##") or line_stripped.startswith("#")):
            while i + 1 < total_lines:
                next_l = lines[i + 1].strip()
                if next_l.startswith("#") or next_l == "---":
                    break
                i += 1
            i += 1
            continue

        # Skip Appendix I or Appendix J
        if any(app in line_stripped.upper() for app in ["APPENDIX I:", "APPENDIX I ", "APPENDIX J:", "APPENDIX J "]) and line_stripped.startswith("##"):
            while i + 1 < total_lines:
                next_l = lines[i + 1].strip()
                if (next_l.startswith("## APPENDIX") or next_l.startswith("# ")) and not any(app in next_l.upper() for app in ["APPENDIX I", "APPENDIX J"]):
                    break
                i += 1
            i += 1
            continue

        # Heading 1: Chapters and Part Titles
        if line_stripped.startswith("# "):
            h_text = line_stripped[2:].strip()
            p = doc.add_paragraph(style='Heading 1')
            if current_section == 3 and not line_stripped.startswith("# CHAPTER 1:"):
                p.paragraph_format.page_break_before = True
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if ("PART" in h_text or "REFERENCES" in h_text) else WD_ALIGN_PARAGRAPH.LEFT
            run = p.add_run(h_text)
            run.font.name = "Times New Roman"
            run.font.size = Pt(16)
            run.bold = True
            run.font.color.rgb = COLOR_NAVY
            i += 1
            continue

        # Heading 2: Sections
        if line_stripped.startswith("## "):
            h_text = line_stripped[3:].strip()
            p = doc.add_paragraph(style='Heading 2')
            run = p.add_run(h_text)
            run.font.name = "Times New Roman"
            run.font.size = Pt(14)
            run.bold = True
            run.font.color.rgb = COLOR_SLATE
            i += 1
            continue

        # Heading 3: Subsections
        if line_stripped.startswith("### "):
            h_text = line_stripped[4:].strip()
            p = doc.add_paragraph(style='Heading 3')
            run = p.add_run(h_text)
            run.font.name = "Times New Roman"
            run.font.size = Pt(12)
            run.bold = True
            run.font.italic = True
            run.font.color.rgb = COLOR_SLATE
            i += 1
            continue

        # Blockquote / Callout (> [!NOTE] or > Text)
        if line_stripped.startswith(">"):
            b_text = re.sub(r'^>\s*(\[!.*?\])?', '', line_stripped).strip()
            if b_text:
                tbl = doc.add_table(rows=1, cols=1)
                tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
                cell = tbl.cell(0, 0)
                set_cell_background(cell, "F0F4F8")
                set_cell_margins(cell, top=100, bottom=100, left=180, right=140)

                borders = parse_xml(
                    f'<w:tblBorders {nsdecls("w")}>'
                    f'<w:left w:val="single" w:sz="18" w:space="0" w:color="1B365D"/>'
                    f'<w:top w:val="none"/>'
                    f'<w:bottom w:val="none"/>'
                    f'<w:right w:val="none"/>'
                    f'</w:tblBorders>'
                )
                tbl._tbl.tblPr.append(borders)

                cp = cell.paragraphs[0]
                cp.paragraph_format.line_spacing = 1.2
                cp.paragraph_format.space_after = Pt(0)
                add_formatted_text(cp, b_text, font_size=11, default_italic=True, default_color=COLOR_SLATE)
                sp = doc.add_paragraph()
                sp.paragraph_format.space_after = Pt(3)

            i += 1
            continue

        # Bullet lists (- or *)
        if line_stripped.startswith("- ") or line_stripped.startswith("* "):
            item_text = line_stripped[2:].strip()
            # Filter out unwanted items
            if any(term in item_text for term in ["Keywords", "Appendix I:", "Appendix J:", "Certificate of Approval", "Student Declaration"]):
                i += 1
                continue
            p = doc.add_paragraph(style='List Bullet')
            p.paragraph_format.left_indent = Inches(0.25)
            p.paragraph_format.line_spacing = 1.25
            p.paragraph_format.space_after = Pt(2)
            add_formatted_text(p, item_text, font_size=11.5)
            i += 1
            continue

        # Numbered lists (1. or 2.)
        m_num = re.match(r'^(\d+)\.\s+(.*)$', line_stripped)
        if m_num:
            num_str = m_num.group(1)
            item_text = m_num.group(2)
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.3)
            p.paragraph_format.line_spacing = 1.25
            p.paragraph_format.space_after = Pt(2)
            nrun = p.add_run(f"{num_str}.  ")
            nrun.font.name = "Times New Roman"
            nrun.font.size = Pt(11.5)
            nrun.bold = True
            nrun.font.color.rgb = COLOR_SLATE
            add_formatted_text(p, item_text, font_size=11.5)
            i += 1
            continue

        # Empty lines
        if not line_stripped:
            i += 1
            continue

        # Standard Body Paragraph
        p = doc.add_paragraph()
        p.paragraph_format.line_spacing = 1.3
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        add_formatted_text(p, line_stripped, font_size=11.5)
        i += 1

    if in_table and table_buffer:
        render_table(doc, table_buffer)

    # =========================================================================
    # POST-PROCESSING: Strict Header & Page Number Cleanup Across All Sections
    # =========================================================================
    print("[*] Running strict header and page number post-processing...")
    for idx, sec in enumerate(doc.sections):
        sectPr = sec._sectPr
        # Remove any pgNumType so numbering is continuous Arabic (1, 2, 3...) throughout
        for pg in sectPr.findall(qn('w:pgNumType')):
            sectPr.remove(pg)

        if idx == 0:
            sec.different_first_page_header_footer = True
        else:
            sec.different_first_page_header_footer = False
            sec.header.is_linked_to_previous = True
            sec.footer.is_linked_to_previous = True
            # Remove any explicit headerReference/footerReference so Word strictly inherits from Section 0
            for hr in sectPr.findall(qn('w:headerReference')):
                sectPr.remove(hr)
            for fr in sectPr.findall(qn('w:footerReference')):
                sectPr.remove(fr)

        # Clear any text runs in headers and footers
        for p in sec.header.paragraphs:
            for r in p.runs:
                if any(w in r.text for w in ['WiMotion', 'Dissertation', 'Sensing', 'Final', 'Multi-Link']):
                    r.text = ''
        for p in sec.footer.paragraphs:
            for r in p.runs:
                r.text = ''

    # Clean any residual text in all related parts (header2.xml, header3.xml, footer2.xml, etc.)
    for rId, part in doc.part.related_parts.items():
        if 'header' in part.partname or 'footer' in part.partname:
            if hasattr(part, '_element'):
                for p in part._element.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
                    for t in p.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'):
                        if any(w in t.text for w in ['WiMotion', 'Dissertation', 'Sensing', 'Final', 'Page']):
                            t.text = ''

    # Save exclusively to the final report destination: PROJECT_REPORT_FILE(TNM&RSR).docx
    final_target = TNM_BASE_PATH

    try:
        print(f"[*] Saving finalized integrated dissertation to: {final_target}")
        doc.save(str(final_target))
        print(f"[+] Saved final report: {final_target} ({os.path.getsize(final_target):,} bytes)")
    except PermissionError:
        alt_target = PARENT_DIR / "PROJECT_REPORT_FILE(TNM&RSR)_UPDATED.docx"
        print(f"[!] Note: {final_target} is currently open in Microsoft Word!")
        print(f"[*] Saving updated copy to: {alt_target}")
        doc.save(str(alt_target))
        print(f"[+] Saved cleanly to: {alt_target} ({os.path.getsize(alt_target):,} bytes)")
    print("[+] All done successfully!")


if __name__ == "__main__":
    build_integrated_dissertation()
