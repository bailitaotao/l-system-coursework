"""Branch Studies. Open in IDLE and choose Run > Run Module."""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from functools import partial
from pathlib import Path
from xml.sax.saxutils import escape

from engine import Specimen, project, stroke, FILES, PAPER, INK

SLOTS = ("Plant A", "Plant B", "Plant C", "Plant D", "Plant E", "Plant F", "Koch", "Dragon")
FIELDS = (("generation", "Generation", "← / →"), ("angle", "Turn angle", "A / D"),
          ("length", "Step length", "S / W"), ("heading", "Initial heading", "Q / E"))


class Studio:
    def __init__(self, root):
        self.root = root
        self.specimen = None
        self.pending = None
        self.color = tk.BooleanVar(value=False)
        self.fit = tk.BooleanVar(value=False)
        root.title("Branch Studies | L-System Studio")
        root.geometry("1000x680")
        root.minsize(740, 585)
        root.columnconfigure(1, weight=1)
        root.rowconfigure(0, weight=1)

        panel = ttk.Frame(root, padding=(18, 16))
        panel.grid(row=0, column=0, sticky="ns")
        ttk.Label(panel, text="Branch Studies", font=("Georgia", 23)).pack(anchor="w")
        ttk.Label(panel, text="L-System Studio").pack(anchor="w", pady=(0, 14))
        ttk.Label(panel, text="Models   ·   keys 1–8").pack(anchor="w")
        grid = ttk.Frame(panel)
        grid.pack(fill="x", pady=(4, 12))
        self.selection = tk.IntVar(value=0)
        for slot, name in enumerate(SLOTS):
            button = ttk.Radiobutton(grid, text=f"{slot+1}  {name}", variable=self.selection,
                                     value=slot, command=partial(self.select, slot))
            button.grid(row=slot//2, column=slot%2, sticky="w", padx=(0, 10), pady=2)
        self.values = {}
        for key, label, shortcut in FIELDS:
            row = ttk.Frame(panel)
            row.pack(fill="x", pady=3)
            ttk.Label(row, text=f"{label}   {shortcut}").grid(row=0, column=0, columnspan=3, sticky="w")
            row.columnconfigure(1, weight=1)
            ttk.Button(row, text="−", width=3, command=partial(self.adjust, key, -1)).grid(row=1, column=0)
            self.values[key] = ttk.Label(row, anchor="center", width=9)
            self.values[key].grid(row=1, column=1)
            ttk.Button(row, text="+", width=3, command=partial(self.adjust, key, 1)).grid(row=1, column=2)
        ttk.Checkbutton(panel, text="Colour by branch depth", variable=self.color,
                        command=self.schedule_draw).pack(anchor="w", pady=(12, 2))
        ttk.Checkbutton(panel, text="Fit current drawing", variable=self.fit,
                        command=self.schedule_draw).pack(anchor="w")
        ttk.Button(panel, text="Save drawing as SVG…", command=self.export).pack(fill="x", pady=(8, 0))

        stage = ttk.Frame(root, padding=(0, 16, 16, 12))
        stage.grid(row=0, column=1, sticky="nsew")
        stage.columnconfigure(0, weight=1)
        stage.rowconfigure(1, weight=1)
        self.status = ttk.Label(stage, font=("TkDefaultFont", 13, "bold"))
        self.status.grid(row=0, column=0, sticky="w", pady=(0, 8))
        self.canvas = tk.Canvas(stage, bg=PAPER, highlightthickness=0, width=450, height=380)
        self.canvas.grid(row=1, column=0, sticky="nsew")
        self.rule_label = ttk.Label(stage, justify="left", wraplength=425)
        self.rule_label.grid(row=2, column=0, sticky="w", pady=(8, 0))
        self.canvas.bind("<Configure>", lambda event: self.schedule_draw())
        root.bind("<KeyPress>", self.keypress)
        self.select(0)

    def select(self, slot):
        try:
            candidate = Specimen(slot)
        except (OSError, ValueError, TypeError) as exc:
            if self.specimen:
                self.selection.set(self.specimen.slot)
            messagebox.showerror("Cannot load model", f"{FILES[slot]}.json\n{exc}", parent=self.root)
            return
        self.specimen = candidate
        self.selection.set(slot)
        self.fit.set(False)
        self.schedule_draw()

    def adjust(self, key, sign):
        if self.specimen:
            self.specimen.adjust(key, sign)
            self.schedule_draw()

    def keypress(self, event):
        key = event.keysym.lower()
        if key in tuple("12345678"):
            self.select(int(key)-1)
            return "break"
        bindings = {"left": ("generation",-1), "right": ("generation",1),
                    "a": ("angle",-1), "d": ("angle",1), "s": ("length",-1),
                    "w": ("length",1), "q": ("heading",-1), "e": ("heading",1)}
        if key in bindings:
            self.adjust(*bindings[key])
            return "break"

    def schedule_draw(self):
        if self.pending is None:
            self.pending = self.root.after_idle(self.redraw)

    def drawing(self):
        s = self.specimen
        return project(s.segments(), s.reference, max(1,self.canvas.winfo_width()),
                       max(1,self.canvas.winfo_height()), self.fit.get())

    def redraw(self):
        self.pending = None
        s = self.specimen
        if s is None:
            return
        lines = self.drawing()
        self.canvas.delete("all")
        for x, y, nx, ny, depth in lines:
            self.canvas.create_line(x, y, nx, ny, fill=stroke(depth,self.color.get()), width=1.25)
        if not lines:
            self.canvas.create_text(self.canvas.winfo_width()/2, self.canvas.winfo_height()/2,
                                    text=f"Generation {s.generation} · no F commands to draw", fill=INK)
        for key, widget in self.values.items():
            suffix = "°" if key in ("angle","heading") else ""
            widget.configure(text=f"{getattr(s,key):g}{suffix}")
        self.status.configure(text=f"{s.model.name}   /   Generation {s.generation}   /   {len(lines):,} segments")
        rules = "     ".join(f"{k} → {v}" for k,v in s.model.rules.items())
        self.rule_label.configure(text=f"Axiom   {s.model.axiom}\n{rules}")

    def export(self):
        if not self.specimen:
            return
        filename = filedialog.asksaveasfilename(parent=self.root, defaultextension=".svg",
                       filetypes=[("SVG drawing","*.svg")], initialfile=FILES[self.specimen.slot]+".svg")
        if filename:
            try:
                self.write_svg(Path(filename))
            except OSError as exc:
                messagebox.showerror("Cannot save drawing", str(exc), parent=self.root)

    def write_svg(self, path):
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}">',
               f'<title>{escape(self.specimen.model.name)} - generation {self.specimen.generation}</title>',
               f'<rect width="100%" height="100%" fill="{PAPER}"/>']
        for x,y,nx,ny,depth in self.drawing():
            svg.append(f'<path d="M{x:.3f} {y:.3f} L{nx:.3f} {ny:.3f}" '
                       f'stroke="{stroke(depth,self.color.get())}" stroke-width="1.25" fill="none"/>')
        svg.append("</svg>")
        path.write_text("\n".join(svg), encoding="utf-8")


if __name__ == "__main__":
    window = tk.Tk()
    Studio(window)
    window.mainloop()
