import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from fat32.fat.image import FatImage
from fat32.fat_utils import human_size
from fs import ResourceType


class FatGui(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FAT32 Viewer")
        self.geometry("800x400")

        self.img = None
        self.current_path = "/"

        toolbar = tk.Frame(self)
        toolbar.pack(fill="x")

        tk.Button(toolbar, text="Open image", command=self.open_image).pack(side="left")
        tk.Button(toolbar, text="Up", command=self.go_up).pack(side="left")
        tk.Button(toolbar, text="Rename", command=self.rename_file).pack(side="left")
        tk.Button(toolbar, text="Delete", command=self.delete_file).pack(side="left")

        self.tree = ttk.Treeview(self, columns=("name", "type", "size"), show="headings")
        self.tree.heading("name", text="Name")
        self.tree.heading("type", text="Type")
        self.tree.heading("size", text="Size")
        self.tree.pack(fill="both", expand=True)

        self.tree.bind("<Double-1>", self.on_open)

    def open_image(self):
        path = filedialog.askopenfilename()
        if not path:
            return
        self.img = FatImage(path)
        self.current_path = "/"
        self.refresh()

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        for e in self.img.listdir(self.current_path):
            t = "DIR" if e["is_dir"] else "FILE"
            s = "" if e["is_dir"] else human_size(e["size"])
            self.tree.insert("", "end", values=(e["name"], t, s))

    def on_open(self, _):
        if not self.tree.selection():
            return
        item = self.tree.selection()[0]
        name = self.tree.item(item, "values")[0]
        full = self.current_path.rstrip("/") + "/" + name

        info = self.img.pf.getinfo(full)
        if info.type == ResourceType.directory:
            self.current_path = full
            self.refresh()
        else:
            data = self.img.read_file(full)
            messagebox.showinfo(name, data[:1000].decode(errors="replace"))

    def go_up(self):
        if self.current_path != "/":
            self.current_path = "/".join(self.current_path.rstrip("/").split("/")[:-1]) or "/"
            self.refresh()

    def rename_file(self):
        if not self.tree.selection():
            return
        item = self.tree.selection()[0]
        old_name = self.tree.item(item, "values")[0]
        new_name = simpledialog.askstring("Rename", f"Enter new name for {old_name}:")
        if not new_name:
            return

        old_path = self.current_path.rstrip("/") + "/" + old_name
        new_path = self.current_path.rstrip("/") + "/" + new_name

        try:
            self.img.pf.move(old_path, new_path)
            self.refresh()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_file(self):
        if not self.tree.selection():
            return
        item = self.tree.selection()[0]
        name = self.tree.item(item, "values")[0]
        full_path = self.current_path.rstrip("/") + "/" + name

        if messagebox.askyesno("Delete", f"Are you sure you want to delete {name}?"):
            try:
                info = self.img.pf.getinfo(full_path)
                if info.type == ResourceType.directory:
                    self.img.pf.removetree(full_path)
                else:
                    self.img.pf.remove(full_path)
                self.refresh()
            except Exception as e:
                messagebox.showerror("Error", str(e))
