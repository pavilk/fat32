from fat32.fat.image import FatImage


def test_recursive_put_and_remove(fat_image, tmp_path):
    # создаём папку с файлами
    src_dir = tmp_path / "dir"
    src_dir.mkdir()
    (src_dir / "a.txt").write_text("A")
    (src_dir / "b.txt").write_text("B")

    img = FatImage(fat_image)

    img.put(str(src_dir), "/dir", recursive=True)

    files = img.listdir("/dir")
    names = {f["name"] for f in files}

    assert names == {"a.txt", "b.txt"}

    img.remove("/dir", recursive=True)

    root = img.listdir("/")
    assert all(e["name"] != "dir" for e in root)

    img.close()


def test_rename_file(fat_image, host_file):
    img = FatImage(fat_image)

    img.put(host_file, "/old.txt")
    img.rename("/old.txt", "/new.txt")

    names = [e["name"] for e in img.listdir("/")]
    assert "new.txt" in names
    assert "old.txt" not in names

    img.close()


def test_copy_to_host(fat_image, host_file, tmp_path):
    img = FatImage(fat_image)

    img.put(host_file, "/hello.txt")

    out = tmp_path / "out.txt"
    img.copy_to_host("/hello.txt", str(out))

    assert out.read_text() == "Hello FAT32!"

    img.close()
