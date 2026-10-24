#!/usr/bin/env python3
"""
Academic Mini Project Report PDF Generator
Flight Booking and Seat Management System (Using Core Data Structures)
Author: Group 4 (Malhar Mahajan, Shubham Patil, Tejas Wable, Rohit Gondhali)
Course: Data Structures and Algorithms Laboratory | Academic Year: 2026-2027
"""

import sys
import os

class SimplePDF:
    def __init__(self, filename="Project_Report.pdf", pagesize=(595.28, 841.89)):
        self.filename = filename
        self.width, self.height = pagesize  # A4: 595.28 x 841.89 pt
        self.margin_x = 42
        self.printable_width = self.width - (2 * self.margin_x)  # ~511.28 pt
        self.margin_top = 45
        self.margin_bottom = 45
        
        self.pages = []
        self.current_stream = []
        self.y = self.height - self.margin_top
        self.page_number = 1
        
        self.font_name = "F1"
        self.font_size = 10
        self.images = {}  # name -> {'path': path, 'width': px_w, 'height': px_h, 'data': bytes}

    def new_page(self):
        if self.current_stream:
            self.pages.append("\n".join(self.current_stream))
            self.current_stream = []
        self.page_number += 1
        self.y = self.height - self.margin_top
        
        # Running header on pages > 1
        self.set_color_stroke(0.78, 0.82, 0.88)
        self.set_line_width(0.5)
        self.draw_line(self.margin_x, self.height - 28, self.width - self.margin_x, self.height - 28)
        
        self.set_font("F3", 7.5)
        self.set_color_fill(0.40, 0.45, 0.50)
        self.draw_text_line(self.margin_x, self.height - 24, "Flight Booking & Seat Management System | DSA Mini Project Report")
        self.draw_text_line(self.width - self.margin_x - 110, self.height - 24, "Academic Year 2026-2027")

    def check_space(self, needed_pts):
        if self.y - needed_pts < self.margin_bottom:
            self.new_page()

    def set_font(self, font_name, size):
        self.font_name = font_name
        self.font_size = size
        self.current_stream.append(f"BT /{font_name} {size:.2f} Tf ET")

    def set_color_fill(self, r, g, b):
        self.current_stream.append(f"{r:.3f} {g:.3f} {b:.3f} rg")

    def set_color_stroke(self, r, g, b):
        self.current_stream.append(f"{r:.3f} {g:.3f} {b:.3f} RG")

    def set_line_width(self, w):
        self.current_stream.append(f"{w:.2f} w")

    def draw_line(self, x1, y1, x2, y2):
        self.current_stream.append(f"{x1:.2f} {y1:.2f} m {x2:.2f} {y2:.2f} l S")

    def draw_rect(self, x, y, w, h, fill=False, stroke=True):
        op = "B" if fill and stroke else ("f" if fill else "S")
        self.current_stream.append(f"{x:.2f} {y:.2f} {w:.2f} {h:.2f} re {op}")

    def escape_text(self, text):
        replacements = {
            "₹": "Rs. ",
            "—": " -- ",
            "–": "-",
            "“": '"',
            "”": '"',
            "’": "'",
            "‘": "'",
            "≤": "<=",
            "≥": ">=",
            "×": "x",
            "•": "*",
            "→": "->",
            "…": "...",
            "\u200b": ""
        }
        for k, v in replacements.items():
            text = text.replace(k, v)
        text = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        return text

    def draw_text_line(self, x, y, text):
        safe_text = self.escape_text(text)
        self.current_stream.append(f"BT /{self.font_name} {self.font_size:.2f} Tf {x:.2f} {y:.2f} Td ({safe_text}) Tj ET")

    def wrap_text(self, text, max_width_pt, font_size=None):
        if font_size is None:
            font_size = self.font_size
        char_width = font_size * 0.52
        chars_per_line = max(10, int(max_width_pt / char_width))
        
        words = text.split(" ")
        lines = []
        curr_line = []
        curr_len = 0
        
        for w in words:
            w_len = len(w)
            if curr_len + w_len + 1 <= chars_per_line:
                curr_line.append(w)
                curr_len += w_len + 1
            else:
                if curr_line:
                    lines.append(" ".join(curr_line))
                curr_line = [w]
                curr_len = w_len
        if curr_line:
            lines.append(" ".join(curr_line))
        return lines

    def register_jpeg_image(self, img_path):
        if img_path in self.images:
            return self.images[img_path]['name']
        
        with open(img_path, 'rb') as f:
            data = f.read()
        
        # Scan for SOF markers (0xFFC0, 0xFFC1, 0xFFC2) to get dimensions
        w, h = 1200, 584
        for i in range(len(data) - 9):
            if data[i] == 0xFF and data[i+1] in (0xC0, 0xC1, 0xC2):
                h = (data[i+5] << 8) + data[i+6]
                w = (data[i+7] << 8) + data[i+8]
                break
        
        img_name = f"Im{len(self.images) + 1}"
        self.images[img_path] = {
            'name': img_name,
            'path': img_path,
            'width': w,
            'height': h,
            'data': data
        }
        return img_name

    def add_image(self, img_path, display_w=None, caption=None):
        if display_w is None:
            display_w = self.printable_width
        
        img_name = self.register_jpeg_image(img_path)
        img_info = self.images[img_path]
        aspect_ratio = img_info['height'] / img_info['width']
        display_h = display_w * aspect_ratio
        
        extra_h = 24 if caption else 10
        self.check_space(display_h + extra_h)
        
        img_x = self.margin_x + (self.printable_width - display_w) / 2
        box_y = self.y - display_h
        
        # Frame border around image
        self.set_color_stroke(0.80, 0.85, 0.90)
        self.set_line_width(0.8)
        self.draw_rect(img_x - 1, box_y - 1, display_w + 2, display_h + 2, fill=False, stroke=True)
        
        # Draw image operator in PDF
        self.current_stream.append(f"q {display_w:.2f} 0 0 {display_h:.2f} {img_x:.2f} {box_y:.2f} cm /{img_name} Do Q")
        
        curr_y = box_y - 12
        if caption:
            self.set_font("F3", 8)
            self.set_color_fill(0.35, 0.40, 0.45)
            self.draw_text_line(img_x, curr_y, caption)
            curr_y -= 10
            
        self.y = curr_y - 6

    def add_title_header(self, dept, course, title, subtitle, group_members):
        self.check_space(250)
        
        # College / Dept Header
        self.set_font("F2", 10.5)
        self.set_color_fill(0.01, 0.41, 0.63)
        self.draw_text_line(self.margin_x, self.y, dept.upper())
        self.y -= 14
        
        self.set_font("F1", 9)
        self.set_color_fill(0.35, 0.40, 0.45)
        self.draw_text_line(self.margin_x, self.y, course)
        self.y -= 18

        # Badge: Academic Mini Project Report
        self.set_color_fill(0.88, 0.95, 0.99)
        self.draw_rect(self.margin_x, self.y - 4, 195, 18, fill=True, stroke=False)
        self.set_font("F2", 8.5)
        self.set_color_fill(0.01, 0.41, 0.63)
        self.draw_text_line(self.margin_x + 8, self.y + 1, "ACADEMIC MINI PROJECT REPORT")
        self.y -= 22

        # Main Title
        self.set_font("F2", 16)
        self.set_color_fill(0.06, 0.09, 0.16)
        title_lines = self.wrap_text(title, self.printable_width, font_size=16)
        for tl in title_lines:
            self.draw_text_line(self.margin_x, self.y, tl)
            self.y -= 20
        self.y -= 2

        # Subtitle
        self.set_font("F3", 9)
        self.set_color_fill(0.35, 0.40, 0.45)
        sub_lines = self.wrap_text(subtitle, self.printable_width, font_size=9)
        for sl in sub_lines:
            self.draw_text_line(self.margin_x, self.y, sl)
            self.y -= 12
        self.y -= 10

        # Group Members Table
        self.set_font("F2", 9)
        self.set_color_fill(0.01, 0.41, 0.63)
        self.draw_text_line(self.margin_x, self.y, "PROJECT GROUP MEMBERS (GROUP OF 4):")
        self.y -= 14

        table_headers = ["Sr.", "Student Name", "Roll Number / ID", "Project Contribution / Role"]
        col_w = [28, 135, 105, 243]
        
        # Header Row
        self.set_color_fill(0.01, 0.41, 0.63)
        self.draw_rect(self.margin_x, self.y - 5, self.printable_width, 18, fill=True, stroke=False)
        self.set_font("F2", 8.5)
        self.set_color_fill(1, 1, 1)
        cur_x = self.margin_x
        for i, h in enumerate(table_headers):
            self.draw_text_line(cur_x + 6, self.y, h)
            cur_x += col_w[i]
        self.y -= 20

        # Rows
        for r_idx, (sr, name, roll, role) in enumerate(group_members):
            bg_col = (0.97, 0.98, 0.99) if r_idx % 2 == 0 else (1.0, 1.0, 1.0)
            self.set_color_fill(*bg_col)
            self.draw_rect(self.margin_x, self.y - 4, self.printable_width, 17, fill=True, stroke=False)
            
            self.set_color_stroke(0.85, 0.88, 0.92)
            self.set_line_width(0.5)
            self.draw_line(self.margin_x, self.y - 4, self.margin_x + self.printable_width, self.y - 4)

            self.set_color_fill(0.12, 0.16, 0.23)
            cur_x = self.margin_x
            
            self.set_font("F2", 8.5)
            self.draw_text_line(cur_x + 8, self.y + 1, str(sr))
            cur_x += col_w[0]
            
            self.set_font("F2", 8.5)
            self.draw_text_line(cur_x + 6, self.y + 1, name)
            cur_x += col_w[1]
            
            self.set_font("F2", 8.5)
            self.draw_text_line(cur_x + 6, self.y + 1, roll)
            cur_x += col_w[2]
            
            self.set_font("F1", 8)
            self.draw_text_line(cur_x + 6, self.y + 1, role)
            
            self.y -= 17

        # Decorative bar
        self.y -= 8
        self.set_color_stroke(0.01, 0.52, 0.78)
        self.set_line_width(1.5)
        self.draw_line(self.margin_x, self.y, self.margin_x + self.printable_width, self.y)
        self.y -= 14

    def add_section_heading(self, text):
        self.check_space(45)
        self.y -= 6
        self.set_font("F2", 11.5)
        self.set_color_fill(0.01, 0.41, 0.63)
        self.draw_text_line(self.margin_x, self.y, text.upper())
        self.y -= 4
        self.set_color_stroke(0.01, 0.52, 0.78)
        self.set_line_width(1.0)
        self.draw_line(self.margin_x, self.y, self.margin_x + self.printable_width, self.y)
        self.y -= 14

    def add_subheading(self, text):
        self.check_space(28)
        self.y -= 4
        self.set_font("F2", 9.5)
        self.set_color_fill(0.06, 0.09, 0.16)
        self.draw_text_line(self.margin_x, self.y, text)
        self.y -= 13

    def add_paragraph(self, text, prefix=""):
        lines = self.wrap_text(text, self.printable_width, font_size=8.5)
        self.check_space(len(lines) * 11.5 + 4)
        
        for i, line in enumerate(lines):
            self.set_font("F1", 8.5)
            self.set_color_fill(0.12, 0.16, 0.23)
            if i == 0 and prefix:
                self.set_font("F2", 8.5)
                self.draw_text_line(self.margin_x, self.y, prefix)
                pref_len = len(prefix) * 4.9
                self.set_font("F1", 8.5)
                self.draw_text_line(self.margin_x + pref_len, self.y, line)
            else:
                self.draw_text_line(self.margin_x, self.y, line)
            self.y -= 11.5
        self.y -= 3

    def add_bullet(self, bold_prefix, text):
        full_text = f"{bold_prefix} {text}"
        lines = self.wrap_text(full_text, self.printable_width - 16, font_size=8.5)
        self.check_space(len(lines) * 11.5 + 3)
        
        self.set_font("F2", 8.5)
        self.set_color_fill(0.01, 0.52, 0.78)
        self.draw_text_line(self.margin_x + 4, self.y, ">")
        
        for i, line in enumerate(lines):
            self.set_font("F1", 8.5)
            self.set_color_fill(0.12, 0.16, 0.23)
            self.draw_text_line(self.margin_x + 16, self.y, line)
            self.y -= 11.5
        self.y -= 2

    def add_callout_box(self, text, title=None):
        lines = self.wrap_text(text, self.printable_width - 24, font_size=8)
        h = len(lines) * 11 + (22 if title else 16)
        self.check_space(h + 8)
        
        box_y = self.y - h + 8
        self.set_color_fill(0.94, 0.97, 1.0)
        self.draw_rect(self.margin_x, box_y, self.printable_width, h, fill=True, stroke=False)
        
        self.set_color_fill(0.01, 0.52, 0.78)
        self.draw_rect(self.margin_x, box_y, 4, h, fill=True, stroke=False)
        
        curr_y = self.y
        if title:
            self.set_font("F2", 8.5)
            self.set_color_fill(0.01, 0.41, 0.63)
            self.draw_text_line(self.margin_x + 12, curr_y, title)
            curr_y -= 13
            
        for line in lines:
            self.set_font("F1", 8)
            self.set_color_fill(0.15, 0.20, 0.28)
            self.draw_text_line(self.margin_x + 12, curr_y, line)
            curr_y -= 11
            
        self.y = box_y - 8

    def add_table(self, headers, rows, col_widths):
        total_w = sum(col_widths)
        self.check_space(26 + len(rows) * 16)
        
        # Header Row
        self.set_color_fill(0.01, 0.41, 0.63)
        self.draw_rect(self.margin_x, self.y - 4, total_w, 17, fill=True, stroke=False)
        self.set_font("F2", 7.5)
        self.set_color_fill(1, 1, 1)
        cur_x = self.margin_x
        for i, h in enumerate(headers):
            self.draw_text_line(cur_x + 5, self.y, h)
            cur_x += col_widths[i]
        self.y -= 18

        # Rows
        for r_idx, row in enumerate(rows):
            cell_lines = [self.wrap_text(str(c), col_widths[c_idx] - 8, font_size=7.5) for c_idx, c in enumerate(row)]
            max_lines = max(len(cl) for cl in cell_lines)
            row_h = max(15, max_lines * 9.5 + 5)
            
            self.check_space(row_h + 3)
            bg_col = (0.97, 0.98, 0.99) if r_idx % 2 == 0 else (1.0, 1.0, 1.0)
            self.set_color_fill(*bg_col)
            self.draw_rect(self.margin_x, self.y - row_h + 11, total_w, row_h, fill=True, stroke=False)
            
            self.set_color_stroke(0.85, 0.88, 0.92)
            self.set_line_width(0.5)
            self.draw_line(self.margin_x, self.y - row_h + 11, self.margin_x + total_w, self.y - row_h + 11)
            
            cur_x = self.margin_x
            for c_idx, cl in enumerate(cell_lines):
                line_y = self.y
                for l in cl:
                    self.set_font("F2" if c_idx == 0 or c_idx == len(row) - 1 else "F1", 7)
                    self.set_color_fill(0.12, 0.16, 0.23)
                    self.draw_text_line(cur_x + 5, line_y, l)
                    line_y -= 9
                cur_x += col_widths[c_idx]
            self.y -= row_h
        self.y -= 8

    def add_boarding_pass(self, lines):
        h = len(lines) * 9.5 + 14
        self.check_space(h + 8)
        
        box_y = self.y - h + 8
        self.set_color_fill(0.06, 0.09, 0.16)
        self.draw_rect(self.margin_x, box_y, self.printable_width, h, fill=True, stroke=False)
        
        curr_y = self.y
        for l in lines:
            self.set_font("F4", 7.2)
            self.set_color_fill(0.22, 0.74, 0.97)
            self.draw_text_line(self.margin_x + 10, curr_y, l)
            curr_y -= 9.5
        self.y = box_y - 8

    def add_code_snippet(self, code_text):
        lines = code_text.split("\n")
        h = len(lines) * 9 + 12
        self.check_space(h + 6)
        
        box_y = self.y - h + 6
        self.set_color_fill(0.96, 0.97, 0.98)
        self.draw_rect(self.margin_x, box_y, self.printable_width, h, fill=True, stroke=False)
        self.set_color_stroke(0.80, 0.84, 0.88)
        self.set_line_width(0.7)
        self.draw_rect(self.margin_x, box_y, self.printable_width, h, fill=False, stroke=True)
        
        curr_y = self.y
        for l in lines:
            self.set_font("F4", 7)
            self.set_color_fill(0.10, 0.15, 0.25)
            self.draw_text_line(self.margin_x + 10, curr_y, l)
            curr_y -= 9
        self.y = box_y - 8

    def add_placeholder_card(self, title, description, details=None):
        extra = len(details) * 10 if details else 0
        h = 42 + extra
        self.check_space(h + 8)
        
        box_y = self.y - h + 8
        self.set_color_fill(0.97, 0.98, 0.99)
        self.draw_rect(self.margin_x, box_y, self.printable_width, h, fill=True, stroke=False)
        
        self.set_color_stroke(0.65, 0.72, 0.80)
        self.set_line_width(0.8)
        self.draw_rect(self.margin_x, box_y, self.printable_width, h, fill=False, stroke=True)
        
        self.set_font("F2", 8)
        self.set_color_fill(0.20, 0.25, 0.35)
        self.draw_text_line(self.margin_x + 12, self.y, title)
        
        self.set_font("F1", 7.5)
        self.set_color_fill(0.40, 0.45, 0.55)
        self.draw_text_line(self.margin_x + 12, self.y - 12, description)
        
        curr_y = self.y - 23
        if details:
            for d in details:
                self.set_font("F1", 7)
                self.set_color_fill(0.25, 0.30, 0.40)
                self.draw_text_line(self.margin_x + 16, curr_y, f"- {d}")
                curr_y -= 10
                
        self.y = box_y - 10

    def add_architecture_vector_diagram(self):
        h = 96
        self.check_space(h + 10)
        box_y = self.y - h + 10
        
        # 1. UI Layer Box
        self.set_color_fill(0.88, 0.95, 0.99)
        self.draw_rect(self.margin_x + 40, self.y - 18, self.printable_width - 80, 20, fill=True, stroke=False)
        self.set_color_stroke(0.01, 0.52, 0.78)
        self.set_line_width(1.0)
        self.draw_rect(self.margin_x + 40, self.y - 18, self.printable_width - 80, 20, fill=False, stroke=True)
        self.set_font("F2", 8)
        self.set_color_fill(0.01, 0.41, 0.63)
        self.draw_text_line(self.margin_x + 115, self.y - 13, "PRESENTATION LAYER: Modern Web Dashboard (Port 5050) & CLI Terminal")
        
        # Line from UI to Controller
        self.set_color_stroke(0.01, 0.52, 0.78)
        self.draw_line(self.margin_x + (self.printable_width / 2), self.y - 18, self.margin_x + (self.printable_width / 2), self.y - 30)

        # 2. Controller Box
        self.set_color_fill(0.94, 0.96, 0.98)
        self.draw_rect(self.margin_x + 80, self.y - 48, self.printable_width - 160, 18, fill=True, stroke=False)
        self.set_color_stroke(0.35, 0.40, 0.50)
        self.set_line_width(1.0)
        self.draw_rect(self.margin_x + 80, self.y - 48, self.printable_width - 160, 18, fill=False, stroke=True)
        self.set_font("F2", 8)
        self.set_color_fill(0.06, 0.09, 0.16)
        self.draw_text_line(self.margin_x + 135, self.y - 44, "FACADE CONTROLLER: FlightBookingManager (Cross-DS Coordinator)")

        # Lines to 5 Data Structures
        mid_x = self.margin_x + (self.printable_width / 2)
        ds_y_top = self.y - 64
        self.set_color_stroke(0.55, 0.60, 0.68)
        self.set_line_width(0.8)
        
        boxes = [
            ("Doubly Linked List", "Confirmed Tickets", "O(1) Prepend"),
            ("Singly Linked Queue", "Waiting List", "O(1) FIFO Queue"),
            ("LIFO Array Stack", "Cancellation Undo", "O(1) Undo Stack"),
            ("1D Seat Matrix", "Seats 1-12 & Fares", "O(1) Index Lookup"),
            ("Search/Sort Engine", "PNR Binary Search", "O(log N) Lookup")
        ]
        
        bw = (self.printable_width - 32) / 5
        for i, (b_title, b_sub, b_comp) in enumerate(boxes):
            bx = self.margin_x + i * (bw + 8)
            self.draw_line(mid_x, self.y - 48, bx + (bw / 2), ds_y_top + 16)
            
            self.set_color_fill(0.97, 0.98, 0.99)
            self.draw_rect(bx, ds_y_top - 20, bw, 36, fill=True, stroke=False)
            self.set_color_stroke(0.20, 0.45, 0.70)
            self.set_line_width(0.8)
            self.draw_rect(bx, ds_y_top - 20, bw, 36, fill=False, stroke=True)
            
            self.set_font("F2", 6.5)
            self.set_color_fill(0.01, 0.41, 0.63)
            self.draw_text_line(bx + 4, ds_y_top + 6, b_title)
            
            self.set_font("F1", 6)
            self.set_color_fill(0.25, 0.30, 0.38)
            self.draw_text_line(bx + 4, ds_y_top - 4, b_sub)
            
            self.set_font("F2", 6)
            self.set_color_fill(0.10, 0.60, 0.30)
            self.draw_text_line(bx + 4, ds_y_top - 14, b_comp)

        self.y = box_y - 8

    def build_pdf(self):
        if self.current_stream:
            self.pages.append("\n".join(self.current_stream))
            self.current_stream = []

        total_pages = len(self.pages)
        
        final_pages_data = []
        for p_idx, p_content in enumerate(self.pages, 1):
            footer_stream = [
                f"BT /F1 8 Tf 0.40 0.45 0.50 rg",
                f"{self.margin_x:.2f} 24 Td (Flight Booking and Seat Management System | DSA Academic Mini Project) Tj",
                f"ET",
                f"BT /F2 8 Tf 0.01 0.41 0.63 rg",
                f"{(self.width - self.margin_x - 65):.2f} 24 Td (Page {p_idx} of {total_pages}) Tj",
                f"ET",
                f"0.78 0.82 0.88 RG 0.5 w",
                f"{self.margin_x:.2f} 34 m {(self.width - self.margin_x):.2f} 34 l S"
            ]
            final_pages_data.append(p_content + "\n" + "\n".join(footer_stream))

        # Objects list: each item is tuple (obj_type, payload_bytes)
        # 1: Catalog
        # 2: Pages
        # 3 .. 3 + total_pages - 1: Page dicts
        # next total_pages: Content stream dicts
        # next 5: Fonts
        # next len(self.images): Images
        
        objects = []
        
        catalog_obj_id = 1
        pages_obj_id = 2
        page_obj_start = 3
        content_obj_start = page_obj_start + total_pages
        font_obj_start = content_obj_start + total_pages
        
        font_defs = {
            "F1": "/Helvetica",
            "F2": "/Helvetica-Bold",
            "F3": "/Helvetica-Oblique",
            "F4": "/Courier",
            "F5": "/Courier-Bold"
        }
        
        img_obj_start = font_obj_start + len(font_defs)
        img_obj_map = {}
        for idx, (img_path, img_info) in enumerate(self.images.items()):
            img_obj_map[img_info['name']] = img_obj_start + idx

        # Font resources string
        font_resources = " ".join([f"/{fname} {font_obj_start + f_idx} 0 R" for f_idx, fname in enumerate(font_defs)])
        
        # XObject resources string
        if img_obj_map:
            xobj_entries = " ".join([f"/{iname} {ioid} 0 R" for iname, ioid in img_obj_map.items()])
            xobject_resources = f"/XObject << {xobj_entries} >>"
        else:
            xobject_resources = ""

        # 1: Catalog
        catalog_dict = f"<< /Type /Catalog /Pages {pages_obj_id} 0 R >>".encode("latin1")
        
        # 2: Pages
        kids_refs = " ".join([f"{page_obj_start + i} 0 R" for i in range(total_pages)])
        pages_dict = f"<< /Type /Pages /Kids [{kids_refs}] /Count {total_pages} >>".encode("latin1")

        # 3 .. Page objects and Content streams
        page_dicts = []
        content_dicts = []
        for i in range(total_pages):
            p_obj_id = page_obj_start + i
            c_obj_id = content_obj_start + i
            
            p_dict = (
                f"<< /Type /Page /Parent {pages_obj_id} 0 R "
                f"/MediaBox [0 0 {self.width:.2f} {self.height:.2f}] "
                f"/Resources << /Font << {font_resources} >> {xobject_resources} >> "
                f"/Contents {c_obj_id} 0 R >>"
            ).encode("latin1")
            page_dicts.append(p_dict)
            
            stream_bytes = final_pages_data[i].encode("latin1", "replace")
            c_dict = (
                f"<< /Length {len(stream_bytes)} >>\n"
                f"stream\n"
            ).encode("latin1") + stream_bytes + b"\nendstream"
            content_dicts.append(c_dict)

        # Font objects
        font_dicts = []
        for fname, basefont in font_defs.items():
            f_dict = f"<< /Type /Font /Subtype /Type1 /BaseFont {basefont} >>".encode("latin1")
            font_dicts.append(f_dict)

        # Image objects
        image_dicts = []
        for img_path, img_info in self.images.items():
            img_data = img_info['data']
            im_dict = (
                f"<< /Type /XObject /Subtype /Image /Width {img_info['width']} /Height {img_info['height']} "
                f"/ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /DCTDecode /Length {len(img_data)} >>\n"
                f"stream\n"
            ).encode("latin1") + img_data + b"\nendstream"
            image_dicts.append(im_dict)

        all_objs = [catalog_dict, pages_dict] + page_dicts + content_dicts + font_dicts + image_dicts
        
        # Write PDF File
        with open(self.filename, "wb") as f:
            f.write(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
            offsets = []
            
            for idx, obj_bytes in enumerate(all_objs, 1):
                offsets.append(f.tell())
                f.write(f"{idx} 0 obj\n".encode("latin1"))
                f.write(obj_bytes)
                f.write(b"\nendobj\n")
                
            xref_pos = f.tell()
            f.write(f"xref\n0 {len(all_objs) + 1}\n".encode("latin1"))
            f.write(b"0000000000 65535 f \n")
            for off in offsets:
                f.write(f"{off:010d} 00000 n \n".encode("latin1"))
                
            trailer = f"trailer\n<< /Size {len(all_objs) + 1} /Root {catalog_obj_id} 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n"
            f.write(trailer.encode("latin1"))

        print(f"Generated {self.filename} successfully ({total_pages} pages).")


def build_full_report_pdf():
    pdf = SimplePDF(filename="/Users/malharmahajan/Desktop/DSPROJECT/Project_Report.pdf")

    # Cover & Header
    group = [
        (1, "Malhar Mahajan", "25108B0029", "Project Lead, Linked List & Web Interface Integration"),
        (2, "Shubham Patil", "25108B0005", "Waiting List Queue & Seat Allocation Matrix"),
        (3, "Tejas Wable", "25108B0004", "Cancellation Stack & Undo Architecture"),
        (4, "Rohit Gondhali", "25108B0031", "Sorting & Searching Engine, Testing & Documentation")
    ]
    
    pdf.add_title_header(
        dept="Department of Computer Engineering / Information Technology",
        course="Course: Data Structures and Algorithms Laboratory | Academic Year: 2026-2027",
        title="Flight Booking and Seat Management System",
        subtitle="Implemented Using Fundamental Data Structures (Linked Lists, Stacks, Queues, Arrays, and Sorting/Searching Algorithms)",
        group_members=group
    )

    # Table of Contents Summary Box
    toc_text = (
        "1. Abstract  |  2. Introduction (2.1 Problem Statement, 2.2 Objectives, 2.3 Scope)  |  "
        "3. System Analysis & Design (3.1 Requirements, 3.2 Architecture, 3.3 Data Flow, 3.4 Complexity Mapping)  |  "
        "4. Implementation & Module Details (4.1 PassengerRecord, 4.2 TicketList DLL, 4.3 WaitingQueue, 4.4 CancellationStack, 4.5 SeatAllocation, 4.6 Search/Sort, 4.7 FacadeManager, 4.8 Web GUI)  |  "
        "5. Results & Discussion (5.1 Test Cases, 5.2 Boarding Pass, 5.3 UI Walkthrough)  |  "
        "6. Conclusion & Future Scope  |  7. References"
    )
    pdf.add_callout_box(toc_text, title="TABLE OF CONTENTS")

    # 1. Abstract
    pdf.add_section_heading("1. Abstract")
    pdf.add_callout_box(
        "Modern airline passenger reservation systems necessitate low-latency, deterministic data handling for ticket reservations, seat category allocation, cancellations, and waiting list updates. This project presents the design and implementation of a robust Flight Booking and Seat Management System engineered in Python using purely native, fundamental data structures without relying on high-level database engines or black-box collection libraries. "
        "The system utilizes: (1) A Doubly Linked List with an O(1) prepend operation to store confirmed passengers and display latest bookings at the top; (2) A FIFO Singly Linked Queue with head and tail pointers to manage fair passenger waitlisting and automated promotion upon cancellation; (3) A Fixed-Capacity LIFO Stack to record cancellations and provide multi-level undo functionality; (4) A 1D Array Representation for dynamic seat management across Window (Rs. 1,200), Middle (Rs. 1,000), and Aisle (Rs. 900) tiers; and (5) Optimized Binary Search (O(log N)) and Insertion/Bubble Sort routines for rapid passenger lookups by PNR, Name, and Age. "
        "Evaluated through both a terminal-based CLI and an interactive, responsive Web Dashboard running on Python's built-in HTTP server, the system successfully demonstrates complete transaction atomicity, real-time ticket generation, and zero data inconsistency under boundary constraints.",
        title="EXECUTIVE SUMMARY"
    )

    # 2. Introduction
    pdf.add_section_heading("2. Introduction")
    pdf.add_subheading("2.1 Problem Statement")
    pdf.add_paragraph(
        "Commercial flight reservation processes encounter severe operational bottlenecks when processing high-frequency transactions involving seat selection, queue transitions, and last-minute cancellations. Standard enterprise implementations often introduce unnecessary overhead when modeling atomic, in-memory state changes. The primary challenge is to construct an in-memory passenger reservation and inventory control engine that satisfies strict algorithmic time and space complexity constraints:"
    )
    pdf.add_bullet("O(1) Priority Head Addition:", "Instantaneous priority addition and chronological head-placement of newly reserved tickets.")
    pdf.add_bullet("Fair Queue Scheduling:", "Strictly fair, starvation-free First-In-First-Out (FIFO) queue handling for excess passenger overflow.")
    pdf.add_bullet("Reversible Transaction Rollback:", "Reversible Last-In-First-Out (LIFO) transaction rollbacks for ticket cancellation undos.")
    pdf.add_bullet("Real-Time Inventory Mapping:", "Real-time seat inventory mapping with category-based fare computing.")

    pdf.add_subheading("2.2 Project Objectives")
    pdf.add_bullet("1. Pure Data Structure Design:", "Implement all core data storage components from scratch using foundational pointer references and arrays.")
    pdf.add_bullet("2. Automated Queue Promotion:", "Automatically promote the front passenger in the waiting queue into confirmed status whenever a seat is cancelled, immediately assigning the newly vacated seat number.")
    pdf.add_bullet("3. Seat Matrix & Dynamic Pricing:", "Segment an aircraft cabin into distinct seat classifications (Window @ Rs. 1,200, Middle @ Rs. 1,000, Aisle @ Rs. 900) and track real-time occupancy.")
    pdf.add_bullet("4. Fast Searching & Sorting:", "Allow ground crew to search passengers by unique PNR in O(log N) time, and sort manifests dynamically by Age and Name.")
    pdf.add_bullet("5. Interactive User Interfaces:", "Provide an intuitive modern Web Dashboard (Port 5050) and a comprehensive Command-Line Interface (CLI).")

    pdf.add_subheading("2.3 Scope and Significance")
    pdf.add_paragraph(
        "This project bridges theoretical computer science education with real-world software engineering. By mapping distinct real-world requirements to specific data structures, students gain practical insight into algorithmic efficiency, memory references, pointer manipulation, and GUI-backend integration."
    )

    # 3. System Analysis & Design
    pdf.new_page()
    pdf.add_section_heading("3. System Analysis & Design")
    pdf.add_subheading("3.1 Hardware and Software Requirements")
    pdf.add_bullet("Hardware Requirements:", "64-bit Intel Core i3 / AMD Ryzen 3 / Apple Silicon M-series or higher; 2 GB RAM minimum (4 GB recommended); 100 MB free hard drive space.")
    pdf.add_bullet("Software Requirements:", "Operating System: macOS, Windows 10/11, or Linux; Language: Python 3.8 to 3.12 (Standard Library only; zero third-party dependencies); Web Browser: Chrome, Safari, Firefox, or Edge; IDE: VS Code, PyCharm, or Antigravity.")

    pdf.add_subheading("3.2 System Architecture Diagram")
    pdf.add_architecture_vector_diagram()

    pdf.add_subheading("3.3 Data Flow & Component Interaction")
    pdf.add_bullet("Booking Workflow:", "User inputs passenger details. If seat is available, SeatMap marks it occupied. A unique PNR (AI-1001) is assigned. A new TicketNode is prepended to TicketList so newest bookings appear at Row #1. If capacity (12 seats) is full, passenger is enqueued into WaitingQueue (WL-1).")
    pdf.add_bullet("Cancellation & Waitlist Promotion:", "Active ticket is removed from TicketList in O(N) lookup and O(1) pointer splice. The cancelled ticket is pushed onto CancellationStack. Vacated seat is freed in SeatMap. If Queue is non-empty, Queue.dequeue() pops the oldest waitlisted passenger, promotes them to Confirmed status, and assigns the vacated seat.")
    pdf.add_bullet("Undo Cancellation Workflow:", "Top cancelled ticket is popped from CancellationStack and re-validated against SeatMap. If seat is available, ticket is restored to TicketList.")

    pdf.add_subheading("3.4 Data Structure Mapping & Complexity Analysis")
    ds_headers = ["Module / Feature", "Chosen Data Structure", "Primary Mechanism", "Time Complexity", "Space Complexity"]
    ds_col_w = [115, 125, 150, 60, 61]
    ds_rows = [
        ["Confirmed Passengers", "Doubly Linked List (TicketList)", "Head Prepend & Bidirectional Pointers", "O(1) Insert, O(N) Search", "O(N)"],
        ["Waiting List Overflow", "Singly Linked Queue (Queue)", "Head Dequeue & Tail Enqueue", "O(1) Push / Pop", "O(W)"],
        ["Cancellation History", "Array Stack (Stack)", "Fixed-size array, top pointer", "O(1) Push / Pop", "O(K)"],
        ["Seat Map & Inventory", "1D Array (SeatMap)", "Direct index lookup seats[seat_no-1]", "O(1) Lookup / Update", "O(1) [Size 12]"],
        ["PNR Fast Search", "Sorted Array (BinarySearch)", "Divide and Conquer Search", "O(log N) Search", "O(1) aux"],
        ["Manifest Sorting", "In-place Insertion / Bubble Sort", "Pairwise comparison & adjacent swaps", "O(N^2) worst, O(N) best", "O(1) aux"]
    ]
    pdf.add_table(ds_headers, ds_rows, ds_col_w)

    # 4. Implementation Details
    pdf.new_page()
    pdf.add_section_heading("4. Implementation & Module Details")
    
    pdf.add_subheading("4.1 Passenger Record Model (passenger_record.py)")
    pdf.add_paragraph(
        "Encapsulates passenger data fields: pnr_no (e.g., 'AI-1001'), name (string), age (int), seat_no (int 1-12 or None), status ('CONFIRMED' / 'WAITLISTED'), booking_time (timestamp), and fare (numeric ticket price based on seat category)."
    )

    pdf.add_subheading("4.2 Confirmed Tickets via Doubly Linked List (confirmed_tickets.py)")
    pdf.add_paragraph(
        "A custom Doubly Linked List (TicketNode with prev and next pointers) delivers O(1) prepend operations so recent reservations appear at the top of the UI manifest. Linear removal performs O(1) pointer unlinking once the node is identified."
    )
    code = (
        "def prepend(self, record):\n"
        "    \"\"\"Inserts newly booked passenger at the head of the list in O(1) time.\"\"\"\n"
        "    new_node = TicketNode(record)\n"
        "    if self.is_empty():\n"
        "        self.head = self.tail = new_node\n"
        "    else:\n"
        "        new_node.next = self.head\n"
        "        self.head.prev = new_node\n"
        "        self.head = new_node\n"
        "    self._size += 1"
    )
    pdf.add_code_snippet(code)

    pdf.add_subheading("4.3 Waiting List via Singly Linked Queue (waiting_queue.py)")
    pdf.add_paragraph(
        "Maintains FIFO semantics using head_node (front) and tail_node (rear) pointers. Enqueue appends waitlisted passengers in O(1) time; Dequeue pops the front passenger for immediate promotion upon ticket cancellation."
    )

    pdf.add_subheading("4.4 Cancellation & Undo via Array-based LIFO Stack (cancellation_stack.py)")
    pdf.add_paragraph(
        "Fixed-capacity array representing a LIFO Stack. Tracks top pointer. Cancelled tickets are pushed onto the stack; undo_cancellation() pops the top ticket and restores it to the confirmed manifest."
    )

    pdf.add_subheading("4.5 Seat Allocation & Dynamic Fare Engine (seat_allocation.py)")
    pdf.add_bullet("Window Seats (Seats 1, 4, 7, 10, 3, 6, 9, 12):", "Rs. 1,200 (Highest passenger preference).")
    pdf.add_bullet("Middle Seats (Seats 2, 5, 8, 11):", "Rs. 1,000 (Standard economy comfort).")
    pdf.add_bullet("Aisle Classification:", "Rs. 900 (Fast cabin egress). Constant-time direct index lookup seats[seat_no-1] guarantees O(1) checks.")

    pdf.add_subheading("4.6 Search & Sort Subsystem (sorting_searching.py)")
    pdf.add_paragraph(
        "Binary Search on PNR runs in O(log N) time with divide-and-conquer logic, returning matching record and comparison count. Bubble Sort and Insertion Sort organize manifests dynamically by Age and Name."
    )

    pdf.add_subheading("4.7 Core Facade Manager (flight_booking_manager.py)")
    pdf.add_paragraph(
        "Central coordinator orchestrating atomic transactions across TicketList, Queue, Stack, and SeatMap, preventing orphaned data or race conditions."
    )

    pdf.add_subheading("4.8 Modern Web GUI Dashboard (web_app.py)")
    pdf.add_paragraph(
        "Zero-dependency Python HTTP server serving reactive seat grid with color states (Green=Available, Red=Occupied, Amber=Selected) and RESTful JSON endpoints (/api/data, /api/book, /api/cancel, /api/undo, /api/reset, /api/load_demo)."
    )

    # 5. Results & Discussion
    pdf.new_page()
    pdf.add_section_heading("5. Results and Discussion")
    pdf.add_subheading("5.1 Verification Test Cases & Execution Summary")
    tc_headers = ["Test ID", "Test Description", "Input Data", "Expected Output", "Status"]
    tc_col_w = [35, 115, 125, 185, 51]
    tc_rows = [
        ["TC-01", "Booking Available Seat", "Name: Malhar, Age: 20, Seat: 7", "Seat 7 allocated (Rs. 1,200), PNR AI-1001 generated, node prepended.", "PASS"],
        ["TC-02", "Confirmed List Ordering", "Book new passenger", "New passenger appears as Row #1 in confirmed table (O(1) prepend).", "PASS"],
        ["TC-03", "Flight Capacity Saturation", "Book 13th passenger (1-12 full)", "Capacity full prompt; passenger enqueued as WAITLISTED (WL-1).", "PASS"],
        ["TC-04", "Auto Waitlist Promotion", "Cancel ticket (Seat 3)", "Seat 3 freed; front waitlisted passenger dequeued, allocated Seat 3, confirmed.", "PASS"],
        ["TC-05", "Undo Cancellation Stack", "Click Undo Cancellation", "Last cancelled passenger popped from stack and restored to flight manifest.", "PASS"],
        ["TC-06", "Binary Search on PNR", "Search PNR 'AI-1007'", "Record located in <= 4 comparisons using Binary Search (O(log N)).", "PASS"],
        ["TC-07", "Manifest Sorting", "Sort by Age ascending", "Manifest displayed in strictly non-decreasing order of passenger age.", "PASS"]
    ]
    pdf.add_table(tc_headers, tc_rows, tc_col_w)

    pdf.add_subheading("5.2 Sample Boarding Pass Generation")
    bp = [
        "================================================================================",
        "                        AIRWAYS BOARDING PASS",
        "================================================================================",
        " PASSENGER NAME : Malhar Mahajan                  PNR NO     : AI-1007",
        " AGE            : 20 Years                        SEAT NO    : 07 (Window)",
        " FLIGHT         : AI-204 (Mumbai to Delhi)        STATUS     : CONFIRMED",
        " BOARDING TIME  : 09:30 AM                        GATE       : G-04",
        " FARE PAID      : INR 1,200                       CLASS      : Economy Standard",
        "================================================================================",
        " Please be at the boarding gate at least 45 minutes prior to departure.",
        "================================================================================"
    ]
    pdf.add_boarding_pass(bp)

    pdf.add_subheading("5.3 UI Walkthrough & Screenshot Verification")
    
    # Check if optimized screenshot exists to embed
    img_path = "/Users/malharmahajan/Desktop/DSPROJECT/image_web.jpg"
    if os.path.exists(img_path):
        pdf.add_paragraph("Screenshot 1: Web Dashboard -- Aircraft Seat Map and Booking Form (Embedded Live View):")
        pdf.add_image(img_path, display_w=480, caption="Figure 5.1: Web Dashboard showing interactive 12-seat matrix, dynamic fares, and booking form.")
    else:
        pdf.add_placeholder_card(
            "[SCREENSHOT 1: INTERACTIVE WEB DASHBOARD & CABIN SEAT MAP]",
            "Displays 12-seat aircraft cabin layout, color-coded pricing badges (Rs. 1,200 / 1,000 / 900), and occupancy indicators."
        )

    pdf.new_page()
    pdf.add_placeholder_card(
        "[SCREENSHOT 2: CONFIRMED PASSENGER MANIFEST (NEWEST BOOKINGS FIRST)]",
        "Displays confirmed tickets table where newly booked passengers appear at Row #1 with PNR, Name, Age, Seat No., Fare, and Cancel button.",
        details=[
            "Demonstrates Doubly Linked List head-prepend ordering in real-time.",
            "Includes active Cancel button triggering atomic waitlist promotion."
        ]
    )

    pdf.add_placeholder_card(
        "[SCREENSHOT 3: WAITING LIST QUEUE & CANCELLATION STACK]",
        "Displays real-time FIFO Waiting List table and Undo Cancellation action button reflecting real-time stack counter.",
        details=[
            "Visualizes FIFO Singly Linked Queue order (WL-1, WL-2, etc.).",
            "Displays active undo counter with last cancelled passenger snapshot."
        ]
    )

    pdf.add_placeholder_card(
        "[SCREENSHOT 4: PNR SEARCH & DYNAMIC SORTING MODAL]",
        "Shows Binary Search output reporting step-by-step search comparisons and formatted Boarding Pass modal dialog.",
        details=[
            "Displays O(log N) divide-and-conquer comparison count dialog.",
            "Demonstrates multi-key manifest re-ordering by passenger Age and Name."
        ]
    )

    # 6. Conclusion & Future Scope
    pdf.add_section_heading("6. Conclusion and Future Scope")
    pdf.add_subheading("6.1 Conclusion")
    pdf.add_paragraph(
        "The Flight Booking and Seat Management System successfully addresses the challenge of building an efficient, transparent, and deterministic passenger inventory system using foundational data structures. By eliminating reliance on opaque database libraries, the project provides concrete operational proof of how theoretical constructs directly solve industry challenges: "
        "(1) Doubly Linked Lists deliver instantaneous O(1) insertion at the head for displaying active booking feeds; "
        "(2) Singly Linked Queues enforce strict chronological fairness for overbooked passenger waitlists; "
        "(3) Array Stacks ensure robust, single-click transactional rollback for accidental cancellations; and "
        "(4) 1D Direct-Index Arrays model physical seat availability with constant-time validation. "
        "Both the Terminal CLI and the modern browser-based Web Dashboard provide seamless usability, real-time visual feedback, and reliable operational stability."
    )

    pdf.add_subheading("6.2 Future Scope")
    pdf.add_bullet("Multi-Flight & Multi-Sector Scalability:", "Extend the single-flight architecture to support multi-sector connecting flights using Directed Acyclic Graphs (DAG) for flight path routing.")
    pdf.add_bullet("Persistent Storage Backing:", "Integrate custom file serialization or B-Tree disk storage for permanent record persistence across server restarts.")
    pdf.add_bullet("Role-Based Security & Payment Gateway:", "Add role-based authentication (Admin vs. Passenger) and secure payment gateway simulation with promo codes.")
    pdf.add_bullet("Dynamic Surge Pricing:", "Incorporate real-time demand-based surge pricing algorithms using Min/Max Heaps.")

    # 7. References
    pdf.add_section_heading("7. References")
    pdf.add_bullet("1.", "Horowitz, E., Sahni, S., & Anderson-Freed, S., Fundamentals of Data Structures in C, 2nd Edition, Universities Press, 2008.")
    pdf.add_bullet("2.", "Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C., Introduction to Algorithms, 3rd Edition, MIT Press, 2009.")
    pdf.add_bullet("3.", "Goodrich, M. T., Tamassia, R., & Goldwasser, M. H., Data Structures and Algorithms in Python, John Wiley & Sons, 2013.")
    pdf.add_bullet("4.", "Python Software Foundation, Python Standard Library Documentation (Built-in Types & http.server), https://docs.python.org/3/library/")
    pdf.add_bullet("5.", "Mozilla Developer Network (MDN), CSS Grid and Responsive Design Patterns for Interactive UI Components, https://developer.mozilla.org/")

    pdf.build_pdf()

if __name__ == "__main__":
    build_full_report_pdf()
