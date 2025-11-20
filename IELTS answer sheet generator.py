import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import webbrowser
import base64

ANSWER_TYPES = [
    "True/False/Not Given",
    "Yes/No/Not Given",
    "Fill in the Blanks",
    "Matching (Roman)",
    "Matching (A/B/C)",
    "Multiple Choice (A–D)",
]

class IELTSGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("IELTS Answer Sheet Generator")
        self.root.geometry("720x560")
        self.root.resizable(False, False)

        # numbering mode: "amount" or "end"
        self.mode_var = tk.StringVar(value="amount")
        self.sections = []

        # Top: numbering mode radio
        mode_frame = tk.Frame(root, pady=6)
        mode_frame.pack(fill="x", padx=10)
        tk.Label(mode_frame, text="Numbering Mode:", font=("Arial", 10, "bold")).pack(side="left", padx=(0,8))
        tk.Radiobutton(mode_frame, text="Enter Count", variable=self.mode_var, value="amount",
                       command=self._on_mode_change).pack(side="left")
        tk.Radiobutton(mode_frame, text="Enter Final Number", variable=self.mode_var, value="end",
                       command=self._on_mode_change).pack(side="left")

        # Form row
        form = tk.Frame(root, pady=6)
        form.pack(fill="x", padx=10)

        self.count_label = tk.Label(form, text="Number of Questions:")
        self.count_label.grid(row=0, column=0)
        self.count_entry = tk.Entry(form, width=10)
        self.count_entry.grid(row=0, column=1, padx=5)
        self.count_entry.bind("<Return>", lambda e: self.answer_type.focus())

        tk.Label(form, text="Answer Type:").grid(row=0, column=2)
        self.answer_type = ttk.Combobox(form, values=ANSWER_TYPES, width=22, state="readonly")
        self.answer_type.set(ANSWER_TYPES[0])
        self.answer_type.grid(row=0, column=3, padx=5)
        self.answer_type.bind("<<ComboboxSelected>>", self.update_extra_field)
        self.answer_type.bind("<Return>", lambda e: self.extra_entry.focus())

        # extra (for matching)
        self.extra_label = tk.Label(form, text="(extra)", fg="gray")
        self.extra_label.grid(row=0, column=4, padx=5)
        self.extra_entry = tk.Entry(form, width=10, state="disabled")
        self.extra_entry.grid(row=0, column=5)
        self.extra_entry.bind("<Return>", lambda e: self.add_section())

        # add button
        self.add_button = tk.Button(form, text="Add Section", command=self.add_section, width=12)
        self.add_button.grid(row=0, column=6, padx=10)
        self.add_button.bind("<Return>", lambda e: self.add_section())

        # section list
        self.list_frame = tk.Frame(root)
        self.list_frame.pack(pady=10, fill="both", expand=True)

        # bottom buttons: Open in Browser, Save to Disk
        bottom_frame = tk.Frame(root)
        bottom_frame.pack(pady=10)
        tk.Button(bottom_frame, text="Open HTML in Browser", command=self.open_in_browser,
                  bg="#28a745", fg="white", width=22).pack(side="left", padx=6)
        tk.Button(bottom_frame, text="Save HTML to Disk", command=self.save_html_to_disk,
                  bg="#007bff", fg="white", width=22).pack(side="left", padx=6)

        self._on_mode_change()

    def _on_mode_change(self):
        if self.mode_var.get() == "amount":
            self.count_label.config(text="Number of Questions:")
        else:
            self.count_label.config(text="Ending Question Number:")
        self.refresh_sections()

    def update_extra_field(self, _=None):
        atype = self.answer_type.get()
        if "Matching" in atype:
            self.extra_entry.config(state="normal")
            if "Roman" in atype:
                self.extra_label.config(text="Highest Number:", fg="black")
            else:
                self.extra_label.config(text="Highest Letter:", fg="black")
        else:
            self.extra_entry.config(state="disabled")
            self.extra_entry.delete(0, tk.END)
            self.extra_label.config(text="(extra)", fg="gray")

    def add_section(self):
        val_str = self.count_entry.get().strip()
        atype = self.answer_type.get()
        extra = self.extra_entry.get().strip() if "Matching" in atype else ""
        
        # Validation for Matching (Roman)
        if "Matching (Roman)" in atype:
            if not extra:
                messagebox.showerror("Error", "Enter highest Roman number (e.g., 5).")
                return
            if not extra.isdigit():
                messagebox.showerror("Error", "Roman highest number must be numeric.")
                return

        # Validation for Matching (A/B/C)
        if "Matching (A/B/C)" in atype:
            if not extra:
                messagebox.showerror("Error", "Enter highest matching letter (e.g., C).")
                return
            if not extra.isalpha():
                messagebox.showerror("Error", "Matching letter must be A–Z only.")
                return
            if len(extra) != 1:
                messagebox.showerror("Error", "Only one letter allowed (e.g., C).")
                return
            extra = extra.upper()


        if not val_str or not atype:
            messagebox.showerror("Error", "Fill all required fields.")
            return
        if not val_str.isdigit() or int(val_str) <= 0:
            messagebox.showerror("Error", "Enter a positive integer.")
            return

        val = int(val_str)
        if self.mode_var.get() == "end":
            next_q = self._next_question_number()
            if val < next_q:
                messagebox.showerror("Error", f"Ending number must be >= {next_q}.")
                return
            section = {'type': atype, 'input': val, 'extra': extra}
        else:
            section = {'type': atype, 'input': val, 'extra': extra}

        self.sections.append(section)
        self.refresh_sections()

        # reset
        self.count_entry.delete(0, tk.END)
        self.answer_type.set(ANSWER_TYPES[0])
        self.extra_entry.delete(0, tk.END)
        self.extra_entry.config(state="disabled")
        self.extra_label.config(text="(extra)", fg="gray")
        self.count_entry.focus()

    def _next_question_number(self):
        current_q = 1
        for sec in self.sections:
            if self.mode_var.get() == "amount":
                cnt = sec.get('input', 0)
            else:
                end = sec.get('input', current_q - 1)
                cnt = max(0, end - current_q + 1)
            current_q += cnt
        return current_q

    def refresh_sections(self):
        for w in self.list_frame.winfo_children():
            w.destroy()

        current_q = 1
        for i, sec in enumerate(self.sections):
            frame = tk.Frame(self.list_frame, relief="raised", bd=1, pady=5, bg="#f8f9fa")
            frame.pack(fill="x", pady=2, padx=2)

            if self.mode_var.get() == "amount":
                display_text = f"{sec['input']} × {sec['type']}"
            else:
                end = sec.get('input', current_q - 1)
                start = current_q
                display_text = f"{start}–{end} — {sec['type']}"

            tk.Label(frame, text=display_text + (f" (max={sec['extra']})" if sec['extra'] else ""),
                     width=40, anchor="w", bg="#f8f9fa").pack(side="left")

            btn_frame = tk.Frame(frame, bg="#f8f9fa")
            btn_frame.pack(side="right", padx=5)
            if i > 0:
                tk.Button(btn_frame, text="↑", width=3, command=lambda idx=i: self.move_up(idx)).pack(side="left")
            if i < len(self.sections)-1:
                tk.Button(btn_frame, text="↓", width=3, command=lambda idx=i: self.move_down(idx)).pack(side="left")
            tk.Button(btn_frame, text="Remove", width=6, command=lambda idx=i: self.remove_section(idx)).pack(side="left")

            if self.mode_var.get() == "amount":
                current_q += sec.get('input', 0)
            else:
                end = sec.get('input', current_q - 1)
                current_q += max(0, end - current_q + 1)

    def move_up(self, index):
        if index > 0:
            self.sections[index], self.sections[index-1] = self.sections[index-1], self.sections[index]
            self.refresh_sections()

    def move_down(self, index):
        if index < len(self.sections)-1:
            self.sections[index], self.sections[index+1] = self.sections[index+1], self.sections[index]
            self.refresh_sections()

    def remove_section(self, index):
        self.sections.pop(index)
        self.refresh_sections()

    # ---------- HTML generation ----------
    def generate_html_content(self):
        if not self.sections:
            return None

        # CSS: eval elements hidden by default; toggle button hidden in print
        html_head = """<html><head><meta charset="UTF-8"><style>
body { font-family: Arial, sans-serif; padding:20px; background-color:#fff; color:#000; }
h2 { text-align:center; margin-bottom:14px; }
.section-header { font-weight:bold; margin-top:18px; border-bottom:1px solid #000; padding-bottom:5px; }
.qgrid { /* we'll inject column-major content manually */ column-count:2; column-gap:18px; margin-top:10px; }
.qbox { display:block; margin-bottom:8px; break-inside:avoid; }
.qbox b { display:inline-block; width:28px; }
.answer, .correct-answer { width:120px; height:22px; margin-left:6px; border:1px solid #000; padding:3px; box-sizing:border-box; vertical-align:middle; }
.checkbox { display:none; width:20px; height:20px; margin-left:8px; vertical-align:middle; }
.correct-answer { display:none; } /* hidden until evaluation enabled and unchecked */
button { margin-right:8px; padding:6px 12px; font-size:13px; cursor:pointer; border-radius:4px; }
#evalToggle { background:#007bff; color:#fff; border:none; }
#printBtn { background:#28a745; color:#fff; border:none; }
@media print {
    #evalToggle { display:none; } /* hide toggle in print */
    /* keep answers visible for printing */
    .checkbox { display:inline-block; }
    .correct-answer { display:inline-block; }
    #printBtn { display:none; }
}
</style></head><body>"""

        # HTML header with toggle + print
        html_body_start = """
<h2>IELTS Reading – Answer Sheet</h2>
<div style="margin-bottom:10px;">
<button id="printBtn" onclick="window.print()">Print / Save as PDF</button>
<button id="evalToggle" onclick="toggleEvaluation()">Enable Evaluation Mode</button>
<span style="margin-left:14px;">Model Number: <input type="text" id="model" style="width:80px;"></span>
<span style="margin-left:14px;">Total Score: <input type="text" id="totalscore" style="width:60px;" readonly></span>
</div>
"""

        html = html_head + html_body_start

        current_q = 1
        for sec in self.sections:
            if self.mode_var.get() == "amount":
                count = sec.get('input', 0)
            else:
                end = sec.get('input', current_q - 1)
                count = max(0, end - current_q + 1)

            html += f'<div class="section-header">{sec["type"]}</div>\n'
            # We will manually construct column-major blocks; using column-count with qbox block items will flow top->bottom.
            # Prepare boxes list
            boxes = []
            for i in range(count):
                atype = sec['type']
                extra = sec['extra']
                # build the primary answer control html (student)
                if atype == "True/False/Not Given":
                    answer_html = '<select class="answer"><option></option><option>True</option><option>False</option><option>Not Given</option></select>'
                elif atype == "Yes/No/Not Given":
                    answer_html = '<select class="answer"><option></option><option>Yes</option><option>No</option><option>Not Given</option></select>'
                elif atype == "Fill in the Blanks":
                    answer_html = '<input class="answer" type="text">'
                elif "Matching (Roman)" in atype:
                    max_v = int(extra) if extra else 0
                    opts = ''.join(f'<option>{self.to_roman(n)}</option>' for n in range(1, max_v+1))
                    answer_html = '<select class="answer"><option></option>' + opts + '</select>'
                elif "Matching (A/B/C)" in atype:
                    max_letter = extra.strip().upper()[0] if extra else 'A'
                    opts = ''.join(f'<option>{chr(c)}</option>' for c in range(ord('A'), ord(max_letter)+1))
                    answer_html = '<select class="answer"><option></option>' + opts + '</select>'
                elif "Multiple Choice" in atype:
                    answer_html = '<select class="answer"><option></option><option>A</option><option>B</option><option>C</option><option>D</option></select>'
                else:
                    answer_html = '<input class="answer" type="text">'

                # Build a clone for correct-answer: same element markup, with class changed to correct-answer and placeholder where appropriate
                # We'll create the clone by reusing answer_html but replacing class="answer" with class="correct-answer"
                correct_html = answer_html.replace('class="answer"', 'class="correct-answer"')
                # For input text placeholders
                if 'type="text"' in correct_html and 'placeholder' not in correct_html:
                    correct_html = correct_html.replace('type="text"', 'type="text" placeholder="Correct answer"')

                # Construct the qbox: primary answer, a hidden checkbox (for teacher), and the hidden correct-answer clone
                q_html = f'<div class="qbox"><b>{current_q}.</b>{answer_html}'
                # checkbox element (hidden until eval enabled): give it id chk{n}
                q_html += f'<input type="checkbox" class="checkbox" id="chk{current_q}" onchange="onCheckboxChange({current_q})">'
                # correct-answer clone (hidden until eval enabled and only when checkbox unchecked)
                q_html += correct_html
                q_html += '</div>\n'
                boxes.append(q_html)
                current_q += 1

            # Now append all boxes into the HTML. Using column-count:2 and qbox as block-level elements will fill top-to-bottom then to next column.
            html += '<div class="qgrid">\n'
            html += ''.join(boxes)
            html += '</div>\n'

        # JavaScript: toggle evaluation mode, checkbox handler, updateScore
        js = r"""
<script>
let evalMode = false;
function toggleEvaluation(){
    evalMode = !evalMode;
    // toggle label
    document.getElementById('evalToggle').innerText = evalMode ? 'Disable Evaluation Mode' : 'Enable Evaluation Mode';
    // show/hide checkboxes
    document.querySelectorAll('.checkbox').forEach(cb=>{
        cb.style.display = evalMode ? 'inline-block' : 'none';
        // ensure styling inline-block for consistent spacing
    });
    // show/hide correct-answer clones depending on checkbox state
    document.querySelectorAll('.correct-answer').forEach(ca=>{
        // corresponding checkbox is previousElementSibling of the correct-answer in our markup
        let chk = ca.previousElementSibling;
        if(!chk) { ca.style.display = 'none'; return; }
        if(!evalMode){ ca.style.display = 'none'; return; }
        // if checkbox is checked => hide correct answer; else show
        ca.style.display = chk.checked ? 'none' : 'inline-block';
    });
    updateScore();
}
function onCheckboxChange(qid){
    let chk = document.getElementById('chk'+qid);
    let ca = chk.nextElementSibling;
    if(!ca) return;
    if(chk.checked){
        ca.style.display = 'none';
    } else {
        // only show correct input if evalMode active
        if(evalMode) ca.style.display = 'inline-block';
    }
    updateScore();
}
function updateScore(){
    let score = document.querySelectorAll('.checkbox:checked').length;
    document.getElementById('totalscore').value = score;
}
</script>
"""
        html += js
        html += "</body></html>"
        return html

    def open_in_browser(self):
        html = self.generate_html_content()
        if html is None:
            messagebox.showerror("Error", "Add at least one section.")
            return
        # open as base64 data URL (force chrome as before)
        data_url = "data:text/html;base64," + base64.b64encode(html.encode()).decode()
        chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe %s"
        try:
            webbrowser.get(chrome_path).open(data_url)
        except Exception:
            # fallback to default browser if chrome call fails
            webbrowser.open(data_url)

    def save_html_to_disk(self):
        html = self.generate_html_content()
        if html is None:
            messagebox.showerror("Error", "Add at least one section.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".html", filetypes=[("HTML files","*.html")])
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(html)
            messagebox.showinfo("Saved", f"HTML saved to {path}")

    def to_roman(self, num):
        mapping = [
            (1000, 'M'), (900, 'CM'), (500, 'D'), (400, 'CD'),
            (100, 'C'), (90, 'XC'), (50, 'L'), (40, 'XL'),
            (10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I')
        ]
        out = ""
        for v, s in mapping:
            while num >= v:
                out += s
                num -= v
        return out

if __name__ == "__main__":
    root = tk.Tk()
    app = IELTSGenerator(root)
    root.mainloop()
