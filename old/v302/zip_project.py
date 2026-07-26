import os
import sys
import zipfile
import yaml

# Корректное определение папки, где ФИЗИЧЕСКИ лежит экзешник (или скрипт .py)
if getattr(sys, 'frozen', False):
    # Если это скомпилированный EXE, берем путь к самому EXE файлу, а не папку _MEI...
    SCRIPT_DIR = os.path.dirname(os.path.abspath(sys.executable))
else:
    # Если это обычный запуск .py файла
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def get_config_path():
    """
    Определяет путь к конфигу в порядке приоритета:
    1. Аргумент командной строки (если передан).
    2. Папка, где находится сам исполняемый файл (SCRIPT_DIR).
    3. Текущая рабочая директория (os.getcwd()).
    4. Если нигде нет – создаём конфиг в папке с исполняемым файлом.
    """
    # 1. Аргумент командной строки
    if len(sys.argv) > 1:
        return os.path.abspath(sys.argv[1])

    # 2. Рядом с .exe (или .py)
    exe_config = os.path.join(SCRIPT_DIR, "zip_project.yaml")
    if os.path.exists(exe_config):
        return exe_config

    # 3. В текущей рабочей папке
    cwd_config = os.path.join(os.getcwd(), "zip_project.yaml")
    if os.path.exists(cwd_config):
        return cwd_config

    # 4. Если ничего нет – создаём в папке с .exe (чтобы не захламлять Temp)
    return exe_config


def load_config(config_path):
    """Загружает настройки из файла YAML."""
    if not os.path.exists(config_path):
        default_config = {
            "base_working_dir": "",
            "include_dirs": [".", "src", "modules"], 
            "include_files": ["main.py", "config.py"],
            "exclude_dirs": ["__pycache__", ".venv", "venv", ".git", "tests/temp"],
            "exclude_files": ["local_settings.py", ".env"],
            "target_extensions": [".py"], 
            "output_list_file": "project_list.txt",
            "make_zip": False,
            "output_zip_file": "archive.zip",
        }
        # Гарантируем создание папки для конфига, если путь сложный
        config_dir = os.path.dirname(config_path)
        if config_dir:
            os.makedirs(config_dir, exist_ok=True)
            
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(default_config, f, default_flow_style=False, allow_unicode=True)
        print(f"[Инфо] Создан новый шаблон конфигурации: {config_path}")
        return default_config

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        print(f"[Ошибка] Файл конфигурации поврежден: {e}.")
        return {}


def process_files():
    config_path = get_config_path()
    print(f"[Инфо] Используется конфигурация: {config_path}")
    config = load_config(config_path)

    # Точка отсчета — строго папка, в которой НАЙДЕН или СОЗДАН используемый конфиг
    CONFIG_DIR = os.path.dirname(config_path)

    # Определяем главную точку отсчета проекта (Base Directory)
    user_base_dir = config.get("base_working_dir", "")
    if user_base_dir and user_base_dir.strip() not in ("", "."):
        # Если путь в конфиге абсолютный, os.path.join его не изменит.
        # Если относительный — посчитает от папки найденного конфига.
        BASE_DIR = os.path.abspath(os.path.join(CONFIG_DIR, user_base_dir))
    else:
        # Если base_working_dir пустой или ".", работаем прямо в папке конфига
        BASE_DIR = CONFIG_DIR
        
    print(f"[Инфо] Базовая папка проекта: {BASE_DIR}")

    # Теперь все пути вычисляем относительно выбранной BASE_DIR
    output_list = os.path.abspath(os.path.join(BASE_DIR, config.get("output_list_file", "files_list.txt")))
    output_zip = os.path.abspath(os.path.join(BASE_DIR, config.get("output_zip_file", "archive.zip")))
    make_zip = config.get("make_zip", False)
    
    extensions = tuple(ext.lower() for ext in config.get("target_extensions", []))

    exclude_dirs = {os.path.abspath(os.path.join(BASE_DIR, d)) for d in config.get("exclude_dirs", [])}
    exclude_files = {os.path.abspath(os.path.join(BASE_DIR, f)) for f in config.get("exclude_files", [])}
    
    exclude_files.add(output_list)
    exclude_files.add(output_zip)
    exclude_files.add(config_path)

    # Список папок для сканирования (тоже от BASE_DIR)
    base_dirs = [os.path.abspath(os.path.join(BASE_DIR, d)) for d in config.get("include_dirs", [])]

    found_files = set()

    # --- ЧАСТЬ 1: Обработка отдельных файлов ---
    for f_path in config.get("include_files", []):
        abs_path = os.path.abspath(os.path.join(BASE_DIR, f_path))
        if os.path.exists(abs_path) and os.path.isfile(abs_path):
            if abs_path not in exclude_files:
                found_files.add(abs_path)

    # --- ЧАСТЬ 2: Сканирование директорий ---
    for abs_dir in base_dirs:
        if not os.path.exists(abs_dir) or not os.path.isdir(abs_dir):
            print(f"[Предупреждение] Директория не найдена: {abs_dir}")
            continue
            
        for root, dirs, files in os.walk(abs_dir):
            dirs[:] = [d for d in dirs if os.path.abspath(os.path.join(root, d)) not in exclude_dirs]

            for file in files:
                full_path = os.path.abspath(os.path.join(root, file))
                if full_path in exclude_files:
                    continue
                if extensions and not file.lower().endswith(extensions):
                    continue
                found_files.add(full_path)

    # --- ЧАСТЬ 3: Запись результатов и архивация ---
    sorted_files = sorted(list(found_files))

    list_dir = os.path.dirname(output_list)
    if list_dir and not os.path.exists(list_dir):
        os.makedirs(list_dir, exist_ok=True)

    def get_archive_rel_path(full_path, base_dirs):
        """Вычисляет чистый относительный путь для записи в txt и zip."""
        return os.path.relpath(full_path, BASE_DIR)

    with open(output_list, "w", encoding="utf-8") as f:
        for full_path in sorted_files:
            clean_rel_path = get_archive_rel_path(full_path, base_dirs)
            f.write(clean_rel_path + "\n")

    print(f"[Успешно] Список сохранен в: {output_list}")
    print(f"[Инфо] Всего найдено объектов: {len(sorted_files)}")

    if make_zip and sorted_files:
        zip_dir = os.path.dirname(output_zip)
        if zip_dir and not os.path.exists(zip_dir):
            os.makedirs(zip_dir, exist_ok=True)

        with zipfile.ZipFile(output_zip, "w", compression=zipfile.ZIP_DEFLATED) as zipf:
            for full_path in sorted_files:
                clean_rel_path = get_archive_rel_path(full_path, base_dirs)
                zipf.write(full_path, arcname=clean_rel_path)
        print(f"[Успешно] Архив создан: {output_zip}")
    elif make_zip:
        print("[Предупреждение] Файлы не найдены, архив пуст.")


if __name__ == "__main__":
    process_files()
