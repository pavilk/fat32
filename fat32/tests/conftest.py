import pytest
from pyfatfs.PyFat import PyFat


@pytest.fixture
def fat_image(tmp_path):
    img_path = tmp_path / "test.img"

    size = 64 * 1024 * 1024 # 64 MB
    with open(img_path, "wb") as f:
        f.truncate(size)

    pf = PyFat()
    pf.mkfs(
        filename=str(img_path),
        fat_type=PyFat.FAT_TYPE_FAT32,
        size=size
    )
    pf.close()

    return str(img_path)


@pytest.fixture
def host_file(tmp_path):
    p = tmp_path / "hello.txt"
    p.write_text("Hello FAT32!")
    return str(p)