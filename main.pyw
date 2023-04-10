import os
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox


class M3UFileGenerator(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("M3U File Generator")
        self.geometry("400x100")

        self.input_dir_var = tk.StringVar()
        self.progress_var = tk.DoubleVar()

        self.create_widgets()
        self.configure_widgets()

    def create_widgets(self):
        self.input_dir_label = ttk.Label(self, text="Input Directory:")
        self.input_dir_entry = ttk.Entry(self, textvariable=self.input_dir_var, state="readonly")
        self.input_dir_button = ttk.Button(self, text="Browse", command=self.browse_input_dir)
        self.generate_button = ttk.Button(self, text="Generate", command=self.on_generate)
        self.progress_bar = ttk.Progressbar(self, variable=self.progress_var, mode="determinate", maximum=100)

    def configure_widgets(self):
        self.input_dir_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.input_dir_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        self.input_dir_button.grid(row=0, column=2, padx=5, pady=5)
        self.generate_button.grid(row=1, column=1, padx=5, pady=5)
        self.progress_bar.grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky=tk.EW)

        self.columnconfigure(1, weight=1)

    def browse_input_dir(self):
        input_dir = filedialog.askdirectory()
        if input_dir:
            self.input_dir_var.set(input_dir)

    def on_generate(self):
        input_dir = self.input_dir_var.get()

        if not input_dir:
            messagebox.showerror("Error", "Please choose an input directory.")
            return

        subdirectories = [d for d in os.listdir(input_dir) if os.path.isdir(os.path.join(input_dir, d))]
        if not subdirectories:
            messagebox.showerror("Error", "No subdirectories found in the input directory.")
            return

        total_dirs = len(subdirectories)
        for idx, subdir in enumerate(subdirectories, start=1):
            m3u_path = os.path.join(input_dir, f"{subdir}.m3u")
            sub_dir_path = os.path.join(input_dir, subdir)

            with open(m3u_path, "w") as m3u_file:
                for root, _, files in os.walk(sub_dir_path):
                    for file in files:
                        relative_path = os.path.relpath(os.path.join(root, file), start=input_dir)
                        m3u_file.write(f"{relative_path}\n")

            progress = (idx / total_dirs) * 100
            self.progress_var.set(progress)
            self.update_idletasks()

        messagebox.showinfo("Success", "M3U files generated successfully.")
        self.progress_var.set(0)


if __name__ == "__main__":
    app = M3UFileGenerator()
    app.mainloop()
