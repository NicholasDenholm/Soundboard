import os

# --------------- Path Making --------------- #

def get_script_directory():
    return os.path.dirname(os.path.abspath(__file__))

def make_dir_path(upper_dir:str, lower_dir:str) -> str:
    return os.path.join(upper_dir, lower_dir)

def find_geckodriver(search_path):
    """
    Search for the GeckoDriver executable in the specified directory and its subdirectories.
    Returns the absolute path to geckodriver if found, otherwise None.
    """
    target_name = "geckodriver.exe" if os.name == 'nt' else "geckodriver"

    for root, dirs, files in os.walk(search_path):
        if target_name in files:
            return os.path.join(root, target_name)
    
    return None
