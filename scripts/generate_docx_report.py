"""
WiMotion 2.0 - Publication-Grade Master Dissertation Word Document (.docx) Generator
Compiles docs/MASTER_DISSERTATION_FINAL.md into a beautifully formatted 100-page academic thesis.
"""

import os
import re
from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

ROOT = Path(__file__).resolve().parent.parent
PARENT_DIR = ROOT.parent
MD_PATH = ROOT / "docs" / "MASTER_DISSERTATION_FINAL.md"
OUTPUT_DOCX = PARENT_DIR / "Project_Report_File.docx"

IMAGE_ASSETS = {
    "Figure 1.1": PARENT_DIR / "echo" / "tactical_hud_preview.png",
    "Figure 1.2": PARENT_DIR / "SHADOW" / "simulation" / "shadow_neural_model_training_curves.png",
    "Figure 3.1": PARENT_DIR / "wimotion" / "dashboard" / "assets" / "user_setup" / "corridor_testbed_wide.jpg",
    "Figure 3.2": PARENT_DIR / "wimotion" / "dashboard" / "assets" / "user_setup" / "esp32_devkit_closeup.jpg",
    "Figure 3.3": PARENT_DIR / "wimotion" / "dashboard" / "assets" / "user_setup" / "esp32_active_node_table.jpg",
    "Figure 3.4": PARENT_DIR / "wimotion" / "dashboard" / "assets" / "user_setup" / "testbed_dual_node_setup.jpg",
    "Figure 3.5": PARENT_DIR / "wimotion" / "dashboard" / "assets" / "user_setup" / "cadet_uniform_in_zone.jpg",
    "Figure 3.6": PARENT_DIR / "wimotion" / "dashboard" / "assets" / "esp32_hardware_testbed.jpg",
    "Figure 7.1": PARENT_DIR / "wimotion" / "dashboard" / "assets" / "user_setup" / "laptop_live_observatory.jpg",
    "Figure 7.2": PARENT_DIR / "wimotion" / "docs" / "assets" / "screen_wide.png",
    "Figure 7.3": PARENT_DIR / "wimotion" / "docs" / "assets" / "screen.png",
    "Figure H.1": PARENT_DIR / "wimotion" / "docs" / "assets" / "screen_wide.png",
    "Figure H.2": PARENT_DIR / "wimotion" / "dashboard" / "assets" / "user_setup" / "laptop_live_observatory.jpg",
    "Figure H.3": PARENT_DIR / "wimotion" / "dashboard" / "assets" / "esp32_hardware_testbed.jpg",
}

# Color Palette: Deep Academic Navy, Slate Gray, Neutral Dark
COLOR_NAVY = RGBColor(27, 54, 93)      # #1B365D
COLOR_SLATE = RGBColor(44, 62, 80)     # #2C3E50
COLOR_MUTED = RGBColor(100, 110, 120)  # #646E78
COLOR_BODY = RGBColor(30, 30, 30)      # #1E1E1E


def set_cell_background(cell, fill_hex):
    """Sets background shading of a table cell."""
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:val="clear" w:color="auto" w:fill="{fill_hex}"/>')
    tc_pr.append(shd)


def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Sets cell padding in twentieths of a point (dxa)."""
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


def add_page_number(run):
    """Inserts a dynamic Word page number field."""
    fld_char1 = parse_xml(r'<w:fldChar %s w:fldCharType="begin"/>' % nsdecls('w'))
    instr_text = parse_xml(r'<w:instrText %s xml:space="preserve"> PAGE </w:instrText>' % nsdecls('w'))
    fld_char2 = parse_xml(r'<w:fldChar %s w:fldCharType="separate"/>' % nsdecls('w'))
    fld_char3 = parse_xml(r'<w:fldChar %s w:fldCharType="end"/>' % nsdecls('w'))
    run._r.append(fld_char1)
    run._r.append(instr_text)
    run._r.append(fld_char2)
    run._r.append(fld_char3)


def setup_document():
    doc = Document()

    # Page Margins: Standard Academic (A4, Left=1.25" for binding, Right=1.0", Top=1.0", Bottom=1.0")
    for section in doc.sections:
        section.page_width = Inches(8.27)    # A4 Width
        section.page_height = Inches(11.69)  # A4 Height
        section.left_margin = Inches(1.25)
        section.right_margin = Inches(1.0)
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)

        # Header
        header = section.header
        hp = header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hrun = hp.add_run("WiMotion 2.0 — Multi-Link RF Spatial Sensing Dissertation")
        hrun.font.name = "Times New Roman"
        hrun.font.size = Pt(8.5)
        hrun.font.color.rgb = COLOR_MUTED

        # Footer
        footer = section.footer
        fp = footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        frun1 = fp.add_run("Page ")
        frun1.font.name = "Times New Roman"
        frun1.font.size = Pt(9.5)
        frun1.font.color.rgb = COLOR_MUTED
        add_page_number(frun1)

    # Base Normal Style
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Times New Roman'
    normal_style.font.size = Pt(12)
    normal_style.font.color.rgb = COLOR_BODY
    normal_style.paragraph_format.line_spacing = 1.35
    normal_style.paragraph_format.space_after = Pt(6)
    normal_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    return doc


def add_formatted_text(p, text, font_size=12, italic_default=False):
    """Parses inline bold (**text**) and code (`text`) formatting."""
    # Split by bold markers
    tokens = re.split(r'(\*\*.*?\*\*|`.*?`|\$.*?\$)', text)
    for tok in tokens:
        if not tok:
            continue
        run = p.add_run()
        run.font.name = "Times New Roman"
        run.font.size = Pt(font_size)
        run.italic = italic_default

        if tok.startswith("**") and tok.endswith("**"):
            run.text = tok[2:-2]
            run.bold = True
        elif tok.startswith("`") and tok.endswith("`"):
            run.text = tok[1:-1]
            run.font.name = "Consolas"
            run.font.size = Pt(font_size - 1.5)
            run.font.color.rgb = RGBColor(160, 40, 40)
        elif tok.startswith("$") and tok.endswith("$"):
            run.text = tok[1:-1]
            run.italic = True
        else:
            run.text = tok


def render_table(doc, table_lines):
    """Renders a parsed markdown table into a styled Word table."""
    rows_data = []
    for line in table_lines:
        line_clean = line.strip().strip("|")
        # Check if separator row
        if re.match(r'^[\s\:\-\|]+$', line_clean):
            continue
        cells = [c.strip() for c in line_clean.split("|")]
        if cells:
            rows_data.append(cells)

    if not rows_data:
        return

    num_rows = len(rows_data)
    num_cols = max(len(r) for r in rows_data)

    table = doc.add_table(rows=num_rows, cols=num_cols)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    # Apply borders
    tbl_pr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="4" w:space="0" w:color="CCCCCC"/>'
        f'<w:bottom w:val="single" w:sz="8" w:space="0" w:color="1B365D"/>'
        f'<w:insideH w:val="single" w:sz="4" w:space="0" w:color="E0E0E0"/>'
        f'<w:insideV w:val="none"/>'
        f'<w:left w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'</w:tblBorders>'
    )
    tbl_pr.append(borders)

    for row_idx, row in enumerate(rows_data):
        is_header = (row_idx == 0)
        for col_idx in range(num_cols):
            cell = table.cell(row_idx, col_idx)
            val = row[col_idx] if col_idx < len(row) else ""
            set_cell_margins(cell, top=120, bottom=120, left=150, right=150)

            cp = cell.paragraphs[0]
            cp.alignment = WD_ALIGN_PARAGRAPH.CENTER if is_header else WD_ALIGN_PARAGRAPH.LEFT
            cp.paragraph_format.line_spacing = 1.15
            cp.paragraph_format.space_after = Pt(2)

            if is_header:
                set_cell_background(cell, "1B365D")
                run = cp.add_run(val)
                run.bold = True
                run.font.name = "Times New Roman"
                run.font.size = Pt(10.5)
                run.font.color.rgb = RGBColor(255, 255, 255)
            else:
                bg = "F9FBFD" if (row_idx % 2 == 1) else "FFFFFF"
                set_cell_background(cell, bg)
                add_formatted_text(cp, val, font_size=10)

    # Empty spacing after table
    sp = doc.add_paragraph()
    sp.paragraph_format.space_after = Pt(8)


def render_code_block(doc, code_lines):
    """Renders formatted code or console block."""
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_background(cell, "F5F7FA")
    set_cell_margins(cell, top=140, bottom=140, left=180, right=180)

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
    run.font.size = Pt(9.0)
    run.font.color.rgb = RGBColor(30, 40, 50)

    sp = doc.add_paragraph()
    sp.paragraph_format.space_after = Pt(6)


def render_image_if_matched(doc, line):
    """Checks if line contains a Figure callout that matches our available image assets."""
    for fig_key, img_path in IMAGE_ASSETS.items():
        if fig_key in line and os.path.exists(img_path):
            ip = doc.add_paragraph()
            ip.alignment = WD_ALIGN_PARAGRAPH.CENTER
            ip.paragraph_format.space_before = Pt(14)
            ip.paragraph_format.space_after = Pt(4)
            irun = ip.add_run()
            try:
                # Add picture scaled to 5.6 inches width
                irun.add_picture(str(img_path), width=Inches(5.6))
                # Add clean caption
                cp = doc.add_paragraph()
                cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
                cp.paragraph_format.space_after = Pt(14)
                caption_text = re.sub(r'[\*\[\]]', '', line).strip()
                if caption_text.startswith("- ") or caption_text.startswith("* "):
                    caption_text = caption_text[2:].strip()
                crun = cp.add_run(caption_text)
                crun.font.name = "Times New Roman"
                crun.font.size = Pt(10)
                crun.font.color.rgb = COLOR_SLATE
                crun.bold = True
                crun.italic = True
                print(f"[+] Successfully embedded {fig_key}: {img_path.name}")
                return True
            except Exception as e:
                print(f"[!] Warning: Could not embed image {img_path}: {e}")
    return False


def convert_markdown_to_docx():
    print(f"[*] Reading master markdown dissertation: {MD_PATH}")
    with open(MD_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    doc = setup_document()
    lines = content.splitlines()

    in_code_block = False
    code_buffer = []
    table_buffer = []
    in_table = False
    in_list_of_figures = False

    total_lines = len(lines)
    i = 0

    while i < total_lines:
        line = lines[i]
        line_stripped = line.strip()

        # Handle Code Blocks (```)
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

        # Handle Markdown Tables (| col | col |)
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

        # Page Break delimiters (--- or <div style="page-break-after: always;"></div>)
        if line_stripped in ("---", "***", "___") or "page-break-after" in line_stripped:
            doc.add_page_break()
            i += 1
            continue

        # Track if we are inside Front Matter List of Figures to avoid prematurely inserting images
        if "8. LIST OF FIGURES" in line_stripped:
            in_list_of_figures = True
        elif in_list_of_figures and (line_stripped.startswith("## 9.") or line_stripped == "---"):
            in_list_of_figures = False

        # Check for Image placeholders (e.g. * **[Figure 3.1: ...]**, - **[Figure 7.1: ...]**, * **Figure H.1:**)
        if not in_list_of_figures and re.match(r'^[\*\-\s]*(\*\*)?\[?Figure\s+[A-Za-z0-9\.]+', line_stripped, re.IGNORECASE):
            if render_image_if_matched(doc, line_stripped):
                i += 1
                continue

        # Heading 1: Chapters & Part Titles (# CHAPTER ... or # PART ...)
        if line_stripped.startswith("# "):
            h_text = line_stripped[2:].strip()
            # If not the very first heading, add a page break before chapter
            p = doc.add_paragraph()
            p.paragraph_format.page_break_before = True
            p.paragraph_format.space_before = Pt(24)
            p.paragraph_format.space_after = Pt(12)
            p.paragraph_format.keep_with_next = True
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if ("PART" in h_text or "REFERENCES" in h_text) else WD_ALIGN_PARAGRAPH.LEFT

            run = p.add_run(h_text)
            run.font.name = "Times New Roman"
            run.font.size = Pt(18)
            run.bold = True
            run.font.color.rgb = COLOR_NAVY
            i += 1
            continue

        # Heading 2: Sections (## 1.1 ...)
        if line_stripped.startswith("## "):
            h_text = line_stripped[3:].strip()
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(14)
            p.paragraph_format.space_after = Pt(6)
            p.paragraph_format.keep_with_next = True
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT

            run = p.add_run(h_text)
            run.font.name = "Times New Roman"
            run.font.size = Pt(14)
            run.bold = True
            run.font.color.rgb = COLOR_SLATE
            i += 1
            continue

        # Heading 3: Subsections (### 1.1.1 ...)
        if line_stripped.startswith("### "):
            h_text = line_stripped[4:].strip()
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(10)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.keep_with_next = True
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT

            run = p.add_run(h_text)
            run.font.name = "Times New Roman"
            run.font.size = Pt(12)
            run.bold = True
            run.italic = True
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
                    f'<w:left w:val="single" w:sz="24" w:space="0" w:color="1B365D"/>'
                    f'<w:top w:val="none"/>'
                    f'<w:bottom w:val="none"/>'
                    f'<w:right w:val="none"/>'
                    f'</w:tblBorders>'
                )
                tbl._tbl.tblPr.append(borders)
                cp = cell.paragraphs[0]
                cp.paragraph_format.line_spacing = 1.2
                cp.paragraph_format.space_after = Pt(0)
                add_formatted_text(cp, b_text, font_size=11, italic_default=True)
                doc.add_paragraph().paragraph_format.space_after = Pt(4)
            i += 1
            continue

        # Bullet List Items (- or * or •)
        if re.match(r'^[\-\*\•]\s+', line_stripped):
            bullet_text = re.sub(r'^[\-\*\•]\s+', '', line_stripped)
            p = doc.add_paragraph(style='List Bullet')
            p.paragraph_format.line_spacing = 1.3
            p.paragraph_format.space_after = Pt(3)
            add_formatted_text(p, bullet_text, font_size=11.5)
            i += 1
            continue

        # Numbered List Items (1. or 2.)
        m_num = re.match(r'^(\d+)\.\s+(.*)', line_stripped)
        if m_num:
            item_text = m_num.group(2)
            p = doc.add_paragraph(style='List Number')
            p.paragraph_format.line_spacing = 1.3
            p.paragraph_format.space_after = Pt(3)
            add_formatted_text(p, item_text, font_size=11.5)
            i += 1
            continue

        # Empty lines
        if not line_stripped:
            i += 1
            continue

        # Standard Body Paragraph
        p = doc.add_paragraph()
        p.paragraph_format.line_spacing = 1.35
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        add_formatted_text(p, line_stripped, font_size=12)
        i += 1

    # In case trailing table was left
    if in_table and table_buffer:
        render_table(doc, table_buffer)

    print(f"[*] Saving finalized .docx dissertation to: {OUTPUT_DOCX}")
    doc.save(str(OUTPUT_DOCX))
    print(f"[+] SUCCESS! File generated successfully. Size: {os.path.getsize(OUTPUT_DOCX):,} bytes")


if __name__ == "__main__":
    convert_markdown_to_docx()
