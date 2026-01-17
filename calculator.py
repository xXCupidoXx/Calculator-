from __future__ import annotations

import math
import tkinter as tk
from functools import partial


class ScientificCalculator:
    def __init__(self, root: tk.Tk) -> None:
        self.colors = {
            "background": "#0B0018",
            "panel": "#1A0634",
            "panel_outline": "#2C0B55",
            "display_bg": "#2B0C4E",
            "display_fg": "#F6F3FF",
            "accent": "#6B3FD1",
            "accent_dark": "#4E2BA1",
            "function": "#362152",
            "numeric": "#281541",
            "hover": "#7C52E0",
            "disabled": "#4F3E73",
        }

        self.root = root
        self.root.title("Scientific Calculator")
        self.root.geometry("420x600")
        self.root.resizable(False, False)
        self.root.configure(bg=self.colors["background"])
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.memory = 0.0
        self.last_answer = "0"
        self.reset_entry = False
        self.is_on = True
        self.alpha_buffer = ""

        # limit evaluation scope to trusted math helpers
        self.allowed_names = {name: getattr(math, name) for name in dir(math) if not name.startswith("_")}
        self.allowed_names.update({"abs": abs, "round": round})

        self._build_ui()
        self._bind_shortcuts()

    def _build_ui(self) -> None:
        container = tk.Frame(
            self.root,
            bg=self.colors["panel"],
            bd=0,
            highlightbackground=self.colors["panel_outline"],
            highlightthickness=1,
        )
        container.grid(row=0, column=0, sticky="nsew", padx=22, pady=22)
        container.grid_rowconfigure(2, weight=1)
        container.grid_columnconfigure(0, weight=1)

        title = tk.Label(
            container,
            text="SciCalc",
            font=("Segoe UI", 22, "bold"),
            bg=self.colors["panel"],
            fg=self.colors["display_fg"],
            anchor="w",
        )
        title.grid(row=0, column=0, sticky="ew", padx=18, pady=(16, 6))

        display_frame = tk.Frame(container, bg=self.colors["panel"])
        display_frame.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 10))
        display_frame.grid_columnconfigure(0, weight=1)

        self.entry = tk.Entry(
            display_frame,
            font=("Segoe UI", 26),
            bd=0,
            relief=tk.FLAT,
            justify="right",
            bg=self.colors["display_bg"],
            fg=self.colors["display_fg"],
            insertbackground=self.colors["display_fg"],
            disabledbackground=self.colors["display_bg"],
            disabledforeground=self.colors["display_fg"],
            highlightthickness=0,
        )
        self.entry.grid(row=0, column=0, sticky="ew", ipadx=10, ipady=18)
        self._set_entry("0")

        self.status_label = tk.Label(
            display_frame,
            text="",
            font=("Segoe UI", 10),
            bg=self.colors["panel"],
            fg="#9D8FBA",
            anchor="e",
            pady=6,
        )
        self.status_label.grid(row=1, column=0, sticky="ew")

        self.button_frame = tk.Frame(container, bg=self.colors["panel"])
        self.button_frame.grid(row=2, column=0, sticky="nsew", padx=14, pady=(4, 16))

        self.buttons: list[tk.Button] = []

        button_specs = [
            [
                ("ON", self.power_on),
                ("OFF", self.power_off),
                ("MC", self.clear_memory),
                ("MR", self.recall_memory),
                ("M+", self.add_to_memory),
                ("C", self.clear),
            ],
            [
                ("CE", self.backspace),
                ("sin", partial(self.wrap_function, "sin")),
                ("cos", partial(self.wrap_function, "cos")),
                ("tan", partial(self.wrap_function, "tan")),
                ("log", partial(self.wrap_function, "log10")),
                ("ln", partial(self.wrap_function, "log")),
            ],
            [
                ("π", partial(self.append_constant, "π")),
                ("e", partial(self.append_constant, "e")),
                ("x²", partial(self.apply_unary, lambda x: x**2)),
                ("x³", partial(self.apply_unary, lambda x: x**3)),
                ("√", partial(self.apply_unary, math.sqrt)),
                ("%", self.apply_percentage),
            ],
            [
                ("7", partial(self.append, "7")),
                ("8", partial(self.append, "8")),
                ("9", partial(self.append, "9")),
                ("÷", partial(self.append, "÷")),
                ("^", partial(self.append, "^")),
                ("(", partial(self.append, "(")),
            ],
            [
                ("4", partial(self.append, "4")),
                ("5", partial(self.append, "5")),
                ("6", partial(self.append, "6")),
                ("×", partial(self.append, "×")),
                ("-", partial(self.append, "-")),
                (")", partial(self.append, ")")),
            ],
            [
                ("1", partial(self.append, "1")),
                ("2", partial(self.append, "2")),
                ("3", partial(self.append, "3")),
                ("+", partial(self.append, "+")),
                ("00", partial(self.append, "00")),
                (".", partial(self.append, ".")),
            ],
            [
                ("0", partial(self.append, "0")),
                ("Ans", self.use_last_answer),
                ("=", self.calculate, 4),
            ],
        ]

        for r_index, row in enumerate(button_specs):
            self.button_frame.grid_rowconfigure(r_index, weight=1)
            c_index = 0
            for spec in row:
                text, command, *rest = spec
                colspan = rest[0] if rest else 1
                color = self._button_color(text)
                button = tk.Button(
                    self.button_frame,
                    text=text,
                    font=("Segoe UI", 16, "bold"),
                    bg=color,
                    fg="white",
                    bd=0,
                    relief=tk.FLAT,
                    activebackground=color,
                    activeforeground="white",
                    highlightthickness=0,
                    command=command,
                    disabledforeground=self.colors["disabled"],
                )
                button.grid(
                    row=r_index,
                    column=c_index,
                    columnspan=colspan,
                    sticky="nsew",
                    padx=5,
                    pady=5,
                    ipadx=2,
                    ipady=12,
                )
                if text != "ON":
                    self.buttons.append(button)
                self._add_hover_effect(button, color)
                c_index += colspan

        for c in range(6):
            self.button_frame.grid_columnconfigure(c, weight=1)

        self._update_status()

    def _bind_shortcuts(self) -> None:
        bindings = {
            "<Key>": self._handle_keypress,
            "<Return>": self._handle_return,
            "<KP_Enter>": self._handle_return,
            "<BackSpace>": self._handle_backspace,
            "<Escape>": self._handle_clear,
            "<Delete>": self._handle_clear,
        }
        for sequence, handler in bindings.items():
            self.root.bind_all(sequence, handler, add="+")

    def _button_color(self, label: str) -> str:
        accents = {"=", "+", "-", "×", "÷", "^"}
        specials = {"ON", "OFF", "MC", "MR", "M+", "C", "CE"}
        scientific = {"sin", "cos", "tan", "log", "ln", "x²", "x³", "√", "Ans", "%"}
        if label in accents:
            return self.colors["accent"]
        if label in specials:
            return self.colors["accent_dark"]
        if label in scientific:
            return self.colors["function"]
        return self.colors["numeric"]

    def _add_hover_effect(self, button: tk.Button, base_color: str) -> None:
        def on_enter(_: tk.Event) -> None:
            if str(button["state"]) == tk.DISABLED:
                return
            button.configure(bg=self._hover_color(base_color))

        def on_leave(_: tk.Event) -> None:
            button.configure(bg=base_color)

        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)

    def _hover_color(self, color: str) -> str:
        color = color.lstrip("#")
        r = min(int(color[0:2], 16) + 24, 255)
        g = min(int(color[2:4], 16) + 24, 255)
        b = min(int(color[4:6], 16) + 24, 255)
        return f"#{r:02X}{g:02X}{b:02X}"

    def append(self, value: str) -> None:
        if not self.is_on:
            return
        current = "" if self.reset_entry or self.entry.get() in {"0", "Error"} else self.entry.get()
        self.reset_entry = False
        self._set_entry(current + value)

    def _handle_keypress(self, event: tk.Event) -> str | None:
        specials = {"Return", "KP_Enter", "BackSpace", "Escape", "Delete"}
        if event.keysym in specials:
            return None

        char = event.char
        if not char:
            return "break"

        lower = char.lower()

        if not self.is_on:
            if lower == "o":
                self.power_on()
            return "break"

        if lower == "p":
            self.append_constant("π")
            self.alpha_buffer = ""
            return "break"

        if lower == "e":
            self.append_constant("e")
            self.alpha_buffer = ""
            return "break"

        if lower == "a":
            self.use_last_answer()
            self.alpha_buffer = ""
            return "break"

        if char.isalpha():
            self.alpha_buffer += lower
            self.alpha_buffer = self.alpha_buffer[-3:]

            if self.alpha_buffer.endswith("sin"):
                self.wrap_function("sin")
                self.alpha_buffer = ""
                return "break"
            if self.alpha_buffer.endswith("cos"):
                self.wrap_function("cos")
                self.alpha_buffer = ""
                return "break"
            if self.alpha_buffer.endswith("tan"):
                self.wrap_function("tan")
                self.alpha_buffer = ""
                return "break"
            if self.alpha_buffer.endswith("log"):
                self.wrap_function("log10")
                self.alpha_buffer = ""
                return "break"
            if self.alpha_buffer.endswith("ln"):
                self.wrap_function("log")
                self.alpha_buffer = ""
                return "break"

            return "break"

        self.alpha_buffer = ""

        append_map = {
            "0": "0",
            "1": "1",
            "2": "2",
            "3": "3",
            "4": "4",
            "5": "5",
            "6": "6",
            "7": "7",
            "8": "8",
            "9": "9",
            ".": ".",
            "(": "(",
            ")": ")",
            "+": "+",
            "-": "-",
            "^": "^",
        }

        if char in append_map:
            self.append(append_map[char])
            return "break"

        if char == "*":
            self.append("×")
            return "break"

        if char == "/":
            self.append("÷")
            return "break"

        if char == "%":
            self.apply_percentage()
            return "break"

        if char == "=":
            self.calculate()
            return "break"

        return "break"

    def _handle_return(self, _: tk.Event) -> str:
        if self.is_on:
            self.alpha_buffer = ""
            self.calculate()
        return "break"

    def _handle_backspace(self, _: tk.Event) -> str:
        if self.is_on:
            self.alpha_buffer = ""
            self.backspace()
        return "break"

    def _handle_clear(self, _: tk.Event) -> str:
        if self.is_on:
            self.alpha_buffer = ""
            self.clear()
        return "break"

    def append_constant(self, name: str) -> None:
        if not self.is_on:
            return
        current = "" if self.reset_entry else self.entry.get()
        if current in ("0", "Error"):
            current = ""
        if current and (current[-1].isdigit() or current[-1] in {")", "π", "e"}):
            current += "*"
        self.reset_entry = False
        self._set_entry(current + name)

    def wrap_function(self, name: str) -> None:
        if not self.is_on:
            return
        current = "" if self.reset_entry else self.entry.get()
        if current in ("0", "Error"):
            current = ""
        if current and (current[-1].isdigit() or current[-1] in {")", "π", "e"}):
            current += "*"
        self.reset_entry = False
        self._set_entry(f"{current}{name}(")

    def apply_unary(self, operator) -> None:
        if not self.is_on:
            return
        try:
            value = self._safe_eval(self.entry.get())
            result = operator(value)
            self._display_result(result)
        except Exception:
            self._show_error()

    def apply_percentage(self) -> None:
        if not self.is_on:
            return
        try:
            value = self._safe_eval(self.entry.get())
            self._display_result(value / 100)
        except Exception:
            self._show_error()

    def clear(self) -> None:
        if not self.is_on:
            return
        self.reset_entry = False
        self._set_entry("0")
        self._update_status()
        self.alpha_buffer = ""

    def backspace(self) -> None:
        if not self.is_on:
            return
        if self.reset_entry:
            self.reset_entry = False
            self._set_entry("0")
            self._update_status()
            return
        current = self.entry.get()
        updated = current[:-1] if current else ""
        self._set_entry(updated or "0")
        self.alpha_buffer = ""

    def calculate(self) -> None:
        if not self.is_on:
            return
        expression = self.entry.get()
        if not expression.strip():
            return
        try:
            result = self._safe_eval(expression)
            self._display_result(result)
        except Exception:
            self._show_error()

    def _safe_eval(self, expression: str):
        prepared = (
            expression.replace("×", "*")
            .replace("÷", "/")
            .replace("^", "**")
            .replace("π", "pi")
        )
        return eval(prepared, {"__builtins__": {}}, self.allowed_names)

    def _display_result(self, result) -> None:
        text = self._format_number(result)
        self._set_entry(text)
        self.last_answer = text
        self.reset_entry = True
        self._update_status()
        self.alpha_buffer = ""

    def _format_number(self, value) -> str:
        if isinstance(value, float):
            if value.is_integer():
                return str(int(value))
            return f"{value:.12g}"
        return str(value)

    def _set_entry(self, value: str) -> None:
        self.entry.configure(state=tk.NORMAL)
        self.entry.delete(0, tk.END)
        self.entry.insert(0, value)
        if not self.is_on:
            self.entry.configure(state=tk.DISABLED)

    def _show_error(self) -> None:
        self._set_entry("Error")
        self.reset_entry = True
        self._update_status()
        self.alpha_buffer = ""

    def _update_status(self) -> None:
        mode = "RAD"
        memory_text = self._format_number(self.memory) if self.memory else "0"
        power = "ON" if self.is_on else "OFF"
        self.status_label.configure(
            text=f"Mode: {mode}    Ans: {self.last_answer}    Memory: {memory_text}    Power: {power}"
        )

    def add_to_memory(self) -> None:
        if not self.is_on:
            return
        try:
            value = self._safe_eval(self.entry.get())
            self.memory += value
            self.reset_entry = True
            self._update_status()
            self.alpha_buffer = ""
        except Exception:
            self._show_error()

    def recall_memory(self) -> None:
        if not self.is_on:
            return
        text = self._format_number(self.memory)
        self._set_entry(text)
        self.reset_entry = True
        self._update_status()
        self.alpha_buffer = ""

    def clear_memory(self) -> None:
        if not self.is_on:
            return
        self.memory = 0.0
        self._update_status()
        self.alpha_buffer = ""

    def use_last_answer(self) -> None:
        if not self.is_on:
            return
        if self.reset_entry or self.entry.get() in {"0", "Error"}:
            new_value = self.last_answer
        else:
            new_value = self.entry.get() + self.last_answer
        self.reset_entry = False
        self._set_entry(new_value)
        self.alpha_buffer = ""

    def power_off(self) -> None:
        if not self.is_on:
            return
        self.is_on = False
        for button in self.buttons:
            button.config(state=tk.DISABLED, bg=self.colors["numeric"])
        self._set_entry("0")
        self._update_status()
        self.alpha_buffer = ""

    def power_on(self) -> None:
        if self.is_on:
            self.clear()
            return
        self.is_on = True
        for button in self.buttons:
            base_color = self._button_color(button["text"])
            button.config(state=tk.NORMAL, bg=base_color, activebackground=base_color)
        self.clear()
        self._update_status()
        self.alpha_buffer = ""


if __name__ == "__main__":
    tk_root = tk.Tk()
    ScientificCalculator(tk_root)
    tk_root.mainloop()
