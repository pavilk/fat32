"""
Вспомогательные функции для fattool
"""


def human_size(n):
    """
    Преобразует размер в байтах в человекочитаемый вид
    """
    if n is None:
        return "-"
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024:
            return f"{n:.0f}{unit}"
        n /= 1024
    return f"{n:.0f}PB"


def safe_decode(name):
    """
    Безопасно декодирует имена файлов (на случай bytes / не-ASCII)
    """
    if isinstance(name, bytes):
        try:
            return name.decode("utf-8")
        except UnicodeDecodeError:
            return name.decode("utf-8", errors="surrogateescape")
    return str(name)
