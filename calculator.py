import tkinter as tk
import ast
import operator


_ops = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

def _safe_eval(node):
    if isinstance(node, ast.Expression):
        return _safe_eval(node.body)
    if isinstance(node, ast.BinOp):
        left = _safe_eval(node.left)
        right = _safe_eval(node.right)
        op = type(node.op)
        if op in _ops:
            return _ops[op](left, right)
    if isinstance(node, ast.UnaryOp):
        val = _safe_eval(node.operand)
        op = type(node.op)
        if op in _ops:
            return _ops[op](val)
    if isinstance(node, ast.Num):  # <3.8
        return node.n
    if isinstance(node, ast.Constant):  # 3.8+
        if isinstance(node.value, (int, float)):
            return node.value
    raise ValueError("Unsupported expression")

def evaluate(expr: str) -> str:
    expr = expr.replace("×", "*").replace("÷", "/").replace("^", "**")

    while expr and expr[-1] in "+-*/^.%":
        expr = expr[:-1]
    if not expr:
        return ""
    try:
        tree = ast.parse(expr, mode="eval")
        return str(_safe_eval(tree))
    except Exception:
        raise

# --- GUI ---
class Calculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Calculator")
        self.geometry("320x480")
        self.config(bg="#0E001E")
        self.resizable(False, False)

        self.memory = 0.0
        self.power_on = True

        self._build_ui()
        self._bind_keys()

    def _build_ui(self):
        self.entry = tk.Entry(self, font=("Arial", 24), bd=10, relief=tk.FLAT,
                              justify="right", bg="#48395D", fg="#FEFEFE", insertbackground="white")
        self.entry.grid(row=0, column=0, columnspan=4, sticky="nsew", padx=10, pady=10, ipady=10)

        buttons = [
            ["ON", "OFF", "M+", "MC"],
            ["MR", "C", "CE", "%"],
            ["7", "8", "9", "÷"],
            ["4", "5", "6", "×"],
            ["1", "2", "3", "-"],
            ["00", "0", ".", "+"],
            ["", "", "", "="]
        ]

        button_colors = {
            "=": "#563187",
            "+": "#563187", "-": "#563187", "×": "#563187", "÷": "#563187",
            "ON": "#9F82A0", "OFF": "#9F82A0", "CE": "#310374", "%": "#563187",
        }

        for r, row in enumerate(buttons, start=1):
            for c, label in enumerate(row):
                if not label:
                   
                    frame = tk.Frame(self, bg="#0E001E")
                    frame.grid(row=r, column=c, sticky="nsew", padx=3, pady=3)
                    continue
                color = button_colors.get(label, "#310374")
                btn = tk.Button(self, text=label, font=("Arial", 16, "bold"),
                                bg=color, fg="white", relief="flat", bd=3,
                                activebackground="#06000D", activeforeground="white",
                                command=lambda t=label: self._on_button(t))
                btn.grid(row=r, column=c, sticky="nsew", padx=3, pady=3, ipadx=2, ipady=8)

  
        for i in range(8):  # 0..7 rows
            self.rowconfigure(i, weight=1)
        for j in range(4):
            self.columnconfigure(j, weight=1)

    def _bind_keys(self):
        self.bind("<Return>", lambda e: self._on_button("="))
        self.bind("<BackSpace>", lambda e: self._on_button("CE"))
        self.bind("<Escape>", lambda e: self._on_button("C"))
        for ch in "0123456789.+-*/()":
            self.bind(ch, lambda e, ch=ch: self._insert(ch))

    def _insert(self, text):
        if not self.power_on:
            return
        if text == "*":
            self.entry.insert(tk.END, "×")
            return
        if text == "/":
            self.entry.insert(tk.END, "÷")
            return
 
        if text == ".":
            cur = self.entry.get()
  
            token = ""
            i = len(cur) - 1
            while i >= 0 and (cur[i].isdigit() or cur[i] == "."):
                token = cur[i] + token
                i -= 1
            if "." in token:
                return
        self.entry.insert(tk.END, text)

    def _on_button(self, label):
        if label == "OFF":
            self._set_power(False); return
        if label == "ON":
            self._set_power(True); return
        if not self.power_on:
            return

        if label == "C":
            self.entry.delete(0, tk.END); return
        if label == "CE":
            cur = self.entry.get()
            if cur:
                self.entry.delete(len(cur)-1, tk.END)
            return
        if label == "=":
            expr = self.entry.get()
            try:
                res = evaluate(expr)
                self.entry.delete(0, tk.END)
                self.entry.insert(tk.END, res)
            except Exception:
                self.entry.delete(0, tk.END)
                self.entry.insert(tk.END, "Error")
            return
        if label == "%":

            cur = self.entry.get()
            try:
                val = evaluate(cur) if cur else "0"
                val = float(val) / 100.0
                self.entry.delete(0, tk.END)
                self.entry.insert(tk.END, str(val))
            except Exception:
                self.entry.delete(0, tk.END)
                self.entry.insert(tk.END, "Error")
            return
        if label == "M+":
            try:
                val = float(evaluate(self.entry.get()))
                self.memory += val
            except Exception:
                pass
            return
        if label == "MC":
            self.memory = 0.0
            return
        if label == "MR":
            self.entry.delete(0, tk.END)
            self.entry.insert(tk.END, str(self.memory))
            return


        self.entry.insert(tk.END, label)

    def _set_power(self, on: bool):
        self.power_on = on
        state = "normal" if on else "disabled"
        bg = "#48395D" if on else "#222222"
        self.entry.config(bg=bg)

        for child in self.winfo_children():
            if isinstance(child, tk.Button):
                text = child["text"]
                if text == "ON":
                    child.config(state="normal")
                elif text == "OFF":
                    child.config(state="normal")
                else:
                    child.config(state=state)

if __name__ == "__main__":
    app = Calculator()
    app.mainloop()
