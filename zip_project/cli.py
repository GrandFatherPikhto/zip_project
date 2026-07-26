# cli.py
import argparse

def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Zip Project – сбор файлов проекта и создание архива")
    parser.add_argument("config", nargs="?", help="Путь к файлу конфигурации (YAML)")
    parser.add_argument("--base-dir", help="Переопределить base_working_dir")
    parser.add_argument("--include-dir", action="append", help="Добавить папку для сканирования (можно несколько)")
    parser.add_argument("--exclude", action="append", help="Добавить паттерн исключения (можно несколько)")
    parser.add_argument("--output", help="Переопределить имя файла манифеста")
    parser.add_argument("--zip", action="store_true", default=None, help="Включить создание архива")
    parser.add_argument("--dry-run", action="store_true", default=None, help="Сухой запуск (только вывод информации)")
    return parser.parse_args(argv)