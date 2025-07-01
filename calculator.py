import tkinter as tk

def click(event):
    btn_text = event.widget["text"]
    if btn_text == "=":
        try:
            result = str(eval(entry.get().replace("×", "*").replace("÷", "/")))
            entry.delete(0, tk.END)
            entry.insert(tk.END, result)
        except:
            entry.delete(0, tk.END)
            entry.insert(tk.END, "Error")
    elif btn_text == "C":
        entry.delete(0, tk.END)
    elif btn_text == "CE":
        entry.delete(len(entry.get())-1)
    else:
        entry.insert(tk.END, btn_text)

root = tk.Tk()
root.title("Calculator")
root.geometry("320x480")
root.config(bg="#0E001E")  # Dark purple/navy background

entry = tk.Entry(root, font=("Arial", 24), bd=10, relief=tk.FLAT, justify="right",
                 bg="#48395D", fg="#FEFEFE", insertbackground="white")
entry.pack(fill=tk.BOTH, ipadx=8, ipady=15, padx=10, pady=10)

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
    "ON": "#9F82A0", "OFF": "#9F82A0", "CE": "#310374", "%": "#563187"
}

for row in buttons:
    frame = tk.Frame(root, bg="#0E001E")
    frame.pack(expand=True, fill="both", padx=5, pady=2)
    for btext in row:
        color = button_colors.get(btext, "#310374")
        btn = tk.Button(frame, text=btext, font=("Arial", 16, "bold"),
                        bg=color, fg="white", relief="flat", bd=3,
                        activebackground="#06000D", activeforeground="white")
        btn.pack(side=tk.LEFT, expand=True, fill="both", padx=3, pady=3)
        btn.bind("<Button-1>", click)

root.mainloop()
