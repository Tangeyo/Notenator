import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog, font, ttk
import os

class NoteTakingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Notenator")
        self.root.geometry("1000x1000")

        self.custom_font = font.Font(family="Helvetica", size=15)

        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=1)

        self.toolbar = tk.Frame(self.main_frame)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

        self.bold_button = tk.Button(self.toolbar, text="Bold", command=self.make_bold)
        self.bold_button.pack(side=tk.LEFT, padx=2, pady=2)

        self.italic_button = tk.Button(self.toolbar, text="Italic", command=self.make_italic)
        self.italic_button.pack(side=tk.LEFT, padx=2, pady=2)

        self.underline_button = tk.Button(self.toolbar, text="Underline", command=self.make_underline)
        self.underline_button.pack(side=tk.LEFT, padx=2, pady=2)

        self.font_size_var = tk.IntVar(value=14)
        self.font_size_menu = tk.OptionMenu(self.toolbar, self.font_size_var, *list(range(8, 33)), command=self.change_font_size)
        self.font_size_menu.pack(side=tk.LEFT, padx=2, pady=2)

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
        self.file_menu.add_command(label="New Note", command=self.new_note, accelerator="Ctrl+N")
        self.file_menu.add_command(label="New Folder", command=self.new_folder, accelerator="Ctrl+F")
        self.file_menu.add_command(label="Open", command=self.open_note, accelerator="Ctrl+O")
        self.file_menu.add_command(label="Save", command=self.save_note, accelerator="Ctrl+S")

        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=root.quit)

        self.edit_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Edit", menu=self.edit_menu)
        self.edit_menu.add_command(label="Search", command=self.search_note, accelerator="Ctrl+E")

        self.status_bar = tk.Label(root, text="Welcome to Notenator", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.text_area.tag_configure('bold', font=(self.custom_font.actual("family"), self.custom_font.actual("size"), 'bold'))
        self.text_area.tag_configure('italic', font=(self.custom_font.actual("family"), self.custom_font.actual("size"), 'italic'))
        self.text_area.tag_configure('underline', font=(self.custom_font.actual("family"), self.custom_font.actual("size"), 'underline'))

        self.tree = ttk.Treeview(self.tree_frame)
        self.tree.pack(fill=tk.Y, expand=1)

        self.tree.heading("#0", text="Notes", anchor=tk.W)

        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # Enable drag and drop
        self.tree.bind("<ButtonPress-1>", self.on_tree_item_press)
        self.tree.bind("<B1-Motion>", self.on_tree_item_drag)
        self.tree.bind("<ButtonRelease-1>", self.on_tree_item_release)

        self.dragging_item = None
        self.drag_image_label = None
        self.is_dragging = False

        self.load_tree()

        #bind Ctrl+S to save_note function
        root.bind("<Control-s>", lambda event: self.save_note())
        root.bind("<Control-o>", lambda event: self.open_note())
        root.bind("<Control-f>", lambda event: self.new_folder())
        root.bind("<Control-n>", lambda event: self.new_note())
        root.bind("<Control-e>", lambda event: self.search_note())

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

    def on_tree_item_press(self, event):
        item = self.tree.identify('item', event.x, event.y)
        if item:
            self.dragging_item = item
            self.drag_data = {"x": event.x, "y": event.y}
            self.drag_start_x = event.x
            self.drag_start_y = event.y
            self.is_dragging = False

    def on_tree_item_drag(self, event):
        if self.dragging_item:
            if not self.is_dragging:
                # Create the drag image label only when dragging starts
                item_text = self.tree.item(self.dragging_item, "text")
                self.drag_image_label = tk.Label(self.tree, text=item_text, relief=tk.SOLID, bg="lightgrey")
                self.drag_image_label.place(x=event.x_root, y=event.y_root)  # Adjust position
                self.is_dragging = True

            # Move the drag image label with the cursor
            x, y = event.x_root - 10, event.y_root - 10  # Adjust position
            self.drag_image_label.place(x=x, y=y)

    def on_tree_item_release(self, event):
        if self.dragging_item:
            target_item = self.tree.identify('item', event.x, event.y)
            if target_item:
                source_path = self.get_full_path(self.dragging_item)
                target_path = self.get_full_path(target_item)
                if os.path.isdir(target_path) and source_path != target_path and not source_path.startswith(target_path + os.sep):
                    new_path = os.path.join(target_path, os.path.basename(source_path))
                    os.rename(source_path, new_path)
                    self.load_tree()
            self.dragging_item = None

        # Remove the drag image label if it exists
        if self.drag_image_label:
            self.drag_image_label.destroy()
            self.drag_image_label = None

        self.is_dragging = False

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
                self.status_bar.config(text=f"Created new sub folder {folder_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create folder: {e}")

    def get_full_path(self, item):
        path = []
        while item:
            path.append(self.tree.item(item, "text"))
            item = self.tree.parent(item)
        path.reverse()
        # Remove the root node ("Notes") from the path
        if path and path[0] == "Notes":
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

    def make_bold(self):
        self.apply_tag('bold')

    def make_italic(self):
        self.apply_tag('italic')

    def make_underline(self):
        self.apply_tag('underline')

    def change_font_size(self, size):
        self.custom_font.configure(size=int(size))
        self.text_area.tag_configure('bold', font=(self.custom_font.actual("family"), self.custom_font.actual("size"), 'bold'))
        self.text_area.tag_configure('italic', font=(self.custom_font.actual("family"), self.custom_font.actual("size"), 'italic'))
        self.text_area.tag_configure('underline', font=(self.custom_font.actual("family"), self.custom_font.actual("size"), 'underline'))

    def apply_tag(self, tag_name):
        try:
            current_tags = self.text_area.tag_names(tk.SEL_FIRST)
            if tag_name in current_tags:
                self.text_area.tag_remove(tag_name, tk.SEL_FIRST, tk.SEL_LAST)
            else:
                self.text_area.tag_add(tag_name, tk.SEL_FIRST, tk.SEL_LAST)
        except tk.TclError:
            messagebox.showerror("Error", "No text selected")


if __name__ == "__main__":
    if not os.path.exists("notes"):
        os.makedirs("notes")

    root = tk.Tk()
    app = NoteTakingApp(root)
    root.mainloop()
