import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog, font, ttk
import os

class NoteTakingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Notenator")
        self.root.geometry("1200x800")

        self.custom_font = font.Font(family="Helvetica", size=14)

        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=1)

        self.tree_frame = tk.Frame(self.main_frame)
        self.tree_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.text_frame = tk.Frame(self.main_frame)
        self.text_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=1)

        self.text_area = tk.Text(self.text_frame, wrap='word', font=self.custom_font, bg="#f0f0f0", fg="#000000")
        self.text_area.pack(expand=1, fill='both')

        self.menu = tk.Menu(root)
        self.root.config(menu=self.menu)

        self.file_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="New Note", command=self.new_note)
        self.file_menu.add_command(label="New Folder", command=self.new_folder)
        self.file_menu.add_command(label="Open", command=self.open_note)
        self.file_menu.add_command(label="Save", command=self.save_note, accelerator="Ctrl+S")
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=root.quit)

        self.edit_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Edit", menu=self.edit_menu)
        self.edit_menu.add_command(label="Search", command=self.search_note)

        self.status_bar = tk.Label(root, text="Welcome to Notenator", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.text_area.tag_config('highlight', background='yellow')

        self.tree = ttk.Treeview(self.tree_frame)
        self.tree.pack(fill=tk.Y, expand=1)

        self.tree.heading("#0", text="Notes", anchor=tk.W)

        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        self.load_tree()

        #bind Ctrl+S to save_note function
        root.bind("<Control-s>", lambda event: self.save_note())

    def load_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        root_node = self.tree.insert("", "end", text="Notes", open=True)
        self.add_tree_nodes(root_node, "notes")

    def add_tree_nodes(self, parent, path):
        for p in sorted(os.listdir(path)):
            abs_path = os.path.join(path, p)
            if os.path.isdir(abs_path):
                node = self.tree.insert(parent, "end", text=p, open=False)
                self.add_tree_nodes(node, abs_path)
            else:
                self.tree.insert(parent, "end", text=p, open=False)

    def on_tree_select(self, event):
        selected_item = self.tree.selection()[0]
        item_path = self.get_full_path(selected_item)
        print(f"Selected item: {selected_item}, Full path: {item_path}")  # Debug statement
        if os.path.isfile(item_path):
            with open(item_path, "r") as file:
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.END, file.read())
            self.status_bar.config(text=f"Opened {item_path}")

    def new_note(self):
        selected_item = self.tree.selection()
        if selected_item:
            parent = selected_item[0]
            parent_path = self.get_full_path(parent)
            if not os.path.isdir(parent_path):
                parent = self.tree.parent(parent)
                parent_path = self.get_full_path(parent)
        else:
            parent = self.tree.get_children()[0]
            parent_path = "notes"
        note_name = simpledialog.askstring("New Note", "Enter note name:")
        if note_name:
            note_path = os.path.join(parent_path, f"{note_name}.txt")
            open(note_path, "w").close()
            self.load_tree()
            self.status_bar.config(text=f"Created new note {note_path}")

    def new_folder(self):
        selected_item = self.tree.selection()
        if selected_item:
            parent = selected_item[0]
            parent_path = self.get_full_path(parent)
            if not os.path.isdir(parent_path):
                parent = self.tree.parent(parent)
                parent_path = self.get_full_path(parent)
        else:
            parent = self.tree.get_children()[0]
            parent_path = "notes"
        folder_name = simpledialog.askstring("New Folder", "Enter folder name:")
        if folder_name:
            folder_path = os.path.join(parent_path, folder_name)
            try:
                os.makedirs(folder_path)
                self.load_tree()
                self.status_bar.config(text=f"Created new folder {folder_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create folder: {e}")

    def get_full_path(self, item):
        path = []
        while item:
            path.append(self.tree.item(item, "text"))
            item = self.tree.parent(item)
        path.reverse()
        # Remove the root node ("Notes") from the path
        if path[0] == "Notes":
            path.pop(0)
        full_path = os.path.join("notes", *path)
        print(f"Constructed full path: {full_path}")  # Debug statement
        return full_path

    def open_note(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")], initialdir="notes")
        if file_path:
            with open(file_path, "r") as file:
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.END, file.read())
            self.status_bar.config(text=f"Opened {file_path}")

    def save_note(self):
        selected_item = self.tree.selection()
        if selected_item:
            parent = selected_item[0]
            file_path = self.get_full_path(parent)
            if os.path.isfile(file_path):
                with open(file_path, "w") as file:
                    file.write(self.text_area.get(1.0, tk.END))
                self.status_bar.config(text=f"Saved as {file_path}")
            else:
                self.save_as()
        else:
            self.save_as()

    def save_as(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")], initialdir="notes")
        if file_path:
            with open(file_path, "w") as file:
                file.write(self.text_area.get(1.0, tk.END))
            self.load_tree()
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
    if not os.path.exists("notes"):
        os.makedirs("notes")

    root = tk.Tk()
    app = NoteTakingApp(root)
    root.mainloop()
