from fat32.fat.image import FatImage


def test_put_and_ls(fat_image, host_file):
    img = FatImage(fat_image)

    img.put(host_file, "/hello.txt")

    files = img.listdir("/")
    names = [f["name"] for f in files]

    assert "hello.txt" in names

    img.close()


def test_cat_file(fat_image, host_file):
    img = FatImage(fat_image)

    img.put(host_file, "/hello.txt")
    data = img.read_file("/hello.txt")

    assert data.decode() == "Hello FAT32!"

    img.close()
