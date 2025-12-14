from pyfatfs.PyFatFS import PyFatFS
import os


def fat_join(*parts):
    """Корректно соединяет пути для FAT (/ вместо \\ и без .)"""
    clean = []
    for p in parts:
        if not p or p == ".":
            continue
        p = p.replace("\\", "/").strip("/")
        if p:
            clean.append(p)
    return "/" + "/".join(clean)


class FatImage:
    def __init__(self, image_path):
        self.image_path = image_path
        self.pf = PyFatFS(image_path)

    def close(self):
        self.pf.close()

    def path_exists(self, path):
        return self.pf.exists(path)

    def listdir(self, path="/"):
        result = []
        try:
            for name in self.pf.listdir(path):
                full = fat_join(path, name)
                info = self.pf.getinfo(full)
                result.append({
                    "name": name,
                    "is_dir": info.is_dir,
                    "size": None if info.is_dir else info.size,
                    "info": info
                })
        except Exception:
            pass
        return result

    def read_file(self, path):
        with self.pf.openbin(path, "r") as f:
            return f.read()

    def copy_to_host(self, src, dst):
        os.makedirs(os.path.dirname(dst) or ".", exist_ok=True)
        with open(dst, "wb") as f:
            f.write(self.read_file(src))

    def mkdir(self, path):
        if not self.path_exists(path):
            self.pf.makedir(path, recreate=True)

    def remove(self, path, recursive=False):
        info = self.pf.getinfo(path)
        if info.is_dir:
            if recursive:
                self.pf.removetree(path)  # удаляет всю папку и содержимое
            else:
                self.pf.removedir(path)  # только пустая папка
        else:
            self.pf.remove(path)

    def put_file(self, host_file, dst_image_path):
        parent = os.path.dirname(dst_image_path.replace("\\", "/"))

        if parent and parent != "/":
            parent = fat_join(parent)
            if not self.path_exists(parent):
                self.mkdir(parent)

        if self.path_exists(dst_image_path):
            self.pf.remove(dst_image_path)

        with open(host_file, "rb") as f:
            data = f.read()

        self.pf.create(dst_image_path, wipe=True)
        with self.pf.openbin(dst_image_path, "r+") as f:
            f.write(data)

    def rename(self, src, dst):
        if not self.pf.exists(src):
            raise FileNotFoundError(src)

        info = self.pf.getinfo(src)
        if info.is_dir:
            if not self.pf.exists(dst):
                self.pf.makedir(dst)

            for entry in self.listdir(src):
                old = fat_join(src, entry["name"])
                new = fat_join(dst, entry["name"])
                self.rename(old, new)

            self.pf.removedir(src)
        else:
            data = self.read_file(src)
            self.pf.create(dst, wipe=True)
            with self.pf.openbin(dst, "r+") as f:
                f.write(data)
            self.pf.remove(src)

    def put(self, src_host_path, dst_image_path, recursive=False):
        dst_image_path = fat_join(dst_image_path)

        if os.path.isdir(src_host_path):
            if not recursive:
                raise IsADirectoryError(src_host_path)

            for root, _, files in os.walk(src_host_path):
                rel = os.path.relpath(root, src_host_path)
                dst_dir = fat_join(dst_image_path, rel)

                if not self.path_exists(dst_dir):
                    self.mkdir(dst_dir)

                for fname in files:
                    self.put_file(
                        os.path.join(root, fname),
                        fat_join(dst_dir, fname)
                    )
        else:
            self.put_file(src_host_path, dst_image_path)
