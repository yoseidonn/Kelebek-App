import logging
import os, sys, datetime
BASE_DIR = os.getenv("BASE_DIR")
logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.DEBUG)
stdout_handler.setFormatter(formatter)

#####
year, month, day = datetime.datetime.now().strftime("%Y-%m-%d").split("-")
os.makedirs(os.path.join(BASE_DIR, 'Logs'), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "Logs", year), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "Logs", year, month), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "Logs", year, month, day), exist_ok=True)

#-----------------
try:    
    log_path = os.path.join(BASE_DIR, "Logs", year, month, day, "kayit_defteri.log")
    os.environ["LOG_PATH"] = log_path
except:
    log_path = os.path.join(BASE_DIR, "Logs", "default", "kayit_defteri.log")
    os.environ["LOG_PATH"] = log_path
#####

file_handler = logging.FileHandler(log_path)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)


logger.addHandler(file_handler)
logger.addHandler(stdout_handler)