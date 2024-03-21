import os
import logging
import subprocess
import sys

class Tools:
    def __init__(self) -> None:
        pass
    @staticmethod 
    def create_directroy_if_not_exists(directory):
        if not os.path.exists(directory):
            os.makedirs(directory)
            logging.info(f"create dir {directory}")

    @staticmethod
    def open_file_use_system_default(file_path):
        logging.info(f"open file {file_path}")
        if sys.platform.startswith('darwin'):
            subprocess.call(('open', file_path))
        elif os.name == 'nt':
            os.startfile(file_path)
        elif os.name == 'posix':
            subprocess.call(('xdg-open', file_path))

