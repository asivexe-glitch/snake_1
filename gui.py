import tkinter as tk
from tkinter import ttk, messagebox


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("簡易 Tkinter 範例")
        self.geometry("400x300")
        self.columnconfigure(0, weight=1)

        frame = ttk.Frame(self, padding=10)
        frame.grid(sticky="nsew")
        frame.columnconfigure(0, weight=1)

        self.entry = ttk.Entry(frame)
        self.entry.grid(row=0, column=0, sticky="ew")

        add_btn = ttk.Button(frame, text="新增到清單", command=self.add_item)
        add_btn.grid(row=0, column=1, padx=5)

        self.listbox = tk.Listbox(frame, height=10)
        self.listbox.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=10)
        frame.rowconfigure(1, weight=1)

        clear_btn = ttk.Button(frame, text="清除", command=self.clear_list)
        clear_btn.grid(row=2, column=0, sticky="w")

        quit_btn = ttk.Button(frame, text="離開", command=self.quit)
        quit_btn.grid(row=2, column=1, sticky="e")

    def add_item(self):
        text = self.entry.get().strip()
        if text:
            self.listbox.insert(tk.END, text)
            self.entry.delete(0, tk.END)
        else:
            messagebox.showinfo("提示", "請輸入文字")

    def clear_list(self):
        self.listbox.delete(0, tk.END)


if __name__ == "__main__":
    app = App()
    app.mainloop()
