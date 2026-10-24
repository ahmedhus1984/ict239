import os

def print_folder_hierarchy(path, prefix=""):
    try:
        # skip node_modules and .git folders
        items = [i for i in os.listdir(path) if i not in ("info", "__init__.py", "__pycache__", "node_modules", ".git", ".gitignore", "venv")]
    except PermissionError:
        return  # skip folders we can't access

    for index, item in enumerate(items):
        item_path = os.path.join(path, item)
        is_last = index == len(items) - 1
        pointer = "|__ " if is_last else "|-- "
        print(prefix + pointer + item)
        if os.path.isdir(item_path):
            new_prefix = prefix + ("    " if is_last else "|   ")
            print_folder_hierarchy(item_path, new_prefix)

if __name__ == "__main__":
    current_path = os.getcwd()
    print(current_path)
    print_folder_hierarchy(current_path)