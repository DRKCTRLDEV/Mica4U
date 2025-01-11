import sys
import atexit
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from utils.system import cleanup_temp, resource_path
from gui.main_window import MainWindow

def main():
    try:
        atexit.register(cleanup_temp)
        app = QApplication(sys.argv)
        app.setWindowIcon(QIcon(resource_path('icon.ico')))
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 