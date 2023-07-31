from PyQt5.QtWidgets import QApplication
import sys
from gui import MyApp


def main():
    app = QApplication(sys.argv)
    ex = MyApp()
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
