import argparse
import os
from fat32.fat.image import FatImage
from fat32.fat_utils import human_size


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", "--image",
        required=True,
        help="Path to fat32_tool image"
    )

    parser.add_argument(
        "cmd",
        choices=["ls", "cat", "put", "get", "rm", "mv"]
    )

    parser.add_argument("src", nargs="?", default="/")
    parser.add_argument("dst", nargs="?")

    # 🔹 ВОТ ОН — флаг -r
    parser.add_argument(
        "-r", "--recursive",
        action="store_true",
        help="Recursive directory operation"
    )

    args = parser.parse_args()

    img = FatImage(args.image)

    try:
        if args.cmd == "ls":
            for e in img.listdir(args.src):
                t = "DIR" if e["is_dir"] else "FILE"
                s = "" if e["is_dir"] else human_size(e["size"])
                print(f"{t:4} {s:>10} {e['name']}")

        elif args.cmd == "cat":
            data = img.read_file(args.src)
            print(data.decode(errors="replace"))

        elif args.cmd == "put":
            if args.dst is None:
                print("Destination path required for put")
            else:
                img.put(
                    args.src,
                    args.dst,
                    recursive=args.recursive   # 🔹 используем -r
                )

        elif args.cmd == "get":
            if args.dst is None:
                print("Destination path required for get")
            else:
                info = img.pf.getinfo(args.src)
                if info.is_dir:
                    if not args.recursive:
                        raise IsADirectoryError("Use -r for recursive get")
                    # Рекурсивно копируем всю директорию
                    for entry in img.listdir(args.src):
                        src_path = f"{args.src.rstrip('/')}/{entry['name']}"
                        dst_path = os.path.join(args.dst, entry['name'])
                        if entry['is_dir']:
                            os.makedirs(dst_path, exist_ok=True)
                            # рекурсивно вызываем get
                            args_copy = argparse.Namespace(
                                cmd='get',
                                src=src_path,
                                dst=dst_path,
                                recursive=True
                            )
                            main_get(args_copy, img)  # отдельная функция для рекурсии

                        else:

                            img.copy_to_host(src_path, dst_path)

                else:

                    os.makedirs(os.path.dirname(args.dst) or ".", exist_ok=True)

                    img.copy_to_host(args.src, args.dst)

        elif args.cmd == "rm":
            img.remove(args.src, recursive=args.recursive)

        elif args.cmd == "mv":
            if args.dst is None:
                print("Destination path required for mv")
            else:
                img.rename(args.src, args.dst)

    finally:
        img.close()


def main_get(args, img):
    info = img.pf.getinfo(args.src)
    if info.is_dir:
        for entry in img.listdir(args.src):
            src_path = f"{args.src.rstrip('/')}/{entry['name']}"
            dst_path = os.path.join(args.dst, entry['name'])
            if entry['is_dir']:
                os.makedirs(dst_path, exist_ok=True)
                args_copy = argparse.Namespace(
                    cmd='get',
                    src=src_path,
                    dst=dst_path,
                    recursive=True
                )
                main_get(args_copy, img)
            else:
                img.copy_to_host(src_path, dst_path)
    else:
        os.makedirs(os.path.dirname(args.dst) or ".", exist_ok=True)
        img.copy_to_host(args.src, args.dst)


if __name__ == "__main__":
    main()
