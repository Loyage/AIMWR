import sys
from PySide6.QtWidgets import QApplication
from qfluentwidgets import FluentTranslator


class AIMWRApp(QApplication):

    def __init__(self, *args, **kwargs):
        super(AIMWRApp, self).__init__(*args, **kwargs)

        # self.w = widget


if __name__ == "__main__":
    app = AIMWRApp(sys.argv)
    sys.exit(app.exec())
