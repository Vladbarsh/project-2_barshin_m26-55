import prompt


def welcome():
    """Показывает приветствие и доступные команды."""
    print("\n***База данных***")
    print("help - справочная информация")
    print("exit - выход из программы\n")


def run():
    """Читает команды до выхода из программы."""
    welcome()
    while True:
        try:
            command = prompt.string("Введите команду: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if command == "exit":
            break
        if command == "help":
            welcome()
        else:
            print(f"Функции {command} нет. Попробуйте снова.")
