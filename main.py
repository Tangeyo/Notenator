import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog, font


class NoteTakingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Notenator")
        self.root.geometry("900x800")

        self.custom_font = font.Font(family="Helvetica", size=14)
        self.text_area = tk.Text(root, wrap='word', font=self.custom_font, bg="#f0f0f0", fg="#000000")
        self.text_area.pack(expand=1, fill='both')

        self.menu = tk.Menu(root)
        self.root.config(menu=self.menu)

        self.file_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="New", command=self.new_note)
        self.file_menu.add_command(label="Open", command=self.open_note)
        self.file_menu.add_command(label="Save", command=self.save_note)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=root.quit)

        self.edit_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Edit", menu=self.edit_menu)
        self.edit_menu.add_command(label="Search", command=self.search_note)

        self.status_bar = tk.Label(root, text="Welcome to Note Taking App", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.text_area.tag_config('highlight', background='yellow')

    def new_note(self):
        self.text_area.delete(1.0, tk.END)
        self.status_bar.config(text="New Note")

    def open_note(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if file_path:
            with open(file_path, "r") as file:
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.END, file.read())
            self.status_bar.config(text=f"Opened {file_path}")

    def save_note(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if file_path:
            with open(file_path, "w") as file:
                file.write(self.text_area.get(1.0, tk.END))
            self.status_bar.config(text=f"Saved as {file_path}")

    def search_note(self):
        search_term = simpledialog.askstring("Search", "Enter search term:")
        text = self.text_area.get(1.0, tk.END)
        start_idx = text.find(search_term)
        if start_idx != -1:
            end_idx = start_idx + len(search_term)
            self.text_area.tag_add('highlight', f'1.0+{start_idx}c', f'1.0+{end_idx}c')
            self.text_area.tag_config('highlight', background='yellow')
            self.status_bar.config(text=f"Found '{search_term}'")
        else:
            messagebox.showinfo("Result", "Search term not found.")
            self.status_bar.config(text=f"'{search_term}' not found")


if __name__ == "__main__":
    root = tk.Tk()
    app = NoteTakingApp(root)
    root.mainloop()
