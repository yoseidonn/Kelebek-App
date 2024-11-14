from App.logs import logger
import os

BASE_DIR = os.getenv("BASE_DIR")
THEME_PATH = os.path.join(BASE_DIR, "App", "Themes")


try:
    with open(os.path.join(THEME_PATH, "QApplication.css"), "r", encoding="utf-8") as f:
        QApplicationStyleSheet = f.read()
except Exception as e:
    QApplicationStyleSheet = ""
    logger.error(f"{e}\nQApplication stylesheet can not found.")

try:
    with open(os.path.join(THEME_PATH, "QGroupBox.css"), "r", encoding="utf-8") as f:
        QGroupBoxStyleSheet = f.read()
except Exception as e:
    QGroupBoxStyleSheet = ""
    logger.error(f"{e}\nQGroupBox stylesheet can not found.")

try:
    with open(os.path.join(THEME_PATH, "QTableWidget.css"), "r", encoding="utf-8") as f:
        QTableWidgetStyleSheet = f.read()
except Exception as e:
    QTableWidgetStyleSheet = ""
    logger.error(f"{e}\nQTableWidget stylesheet can not found.")

try:
    with open(os.path.join(THEME_PATH, "QToolBar.css"), "r", encoding="utf-8") as f:
        QToolBarStyleSheet = f.read()
except Exception as e:
    QToolBarStyleSheet = ""
    logger.error(f"{e}\nQToolBar stylesheet can not found.")

try:
    with open(os.path.join(THEME_PATH, "QToolBox.css"), "r", encoding="utf-8") as f:
        QToolBoxStyleSheet = f.read()
except Exception as e:
    QToolBoxStyleSheet = ""
    logger.error(f"{e}\nQToolBox stylesheet can not found.")

try:
    with open(os.path.join(THEME_PATH, "QWebEngineView.css"), "r", encoding="utf-8") as f:
        QWebEngineViewStyleSheet = f.read()
except Exception as e:
    QWebEngineViewStyleSheet = ""
    logger.error(f"{e}\nQWebEngineView stylesheet can not found.")

try:
    with open(os.path.join(THEME_PATH, "styles.css"), "r", encoding="utf-8") as f:
        GlobalStyleSheet = f.read()
except Exception as e:
    GlobalStyleSheet = ""
    logger.error(f"{e}\nGlobal stylesheet can not found.")
    