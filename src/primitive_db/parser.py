import shlex


def parse_command(text):
    """Разделяет команду и её аргументы."""
    parts = shlex.split(text)
    if not parts:
        return "", []
    return parts[0].lower(), parts[1:]
