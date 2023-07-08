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
try:
    os.mkdir(os.path.join(BASE_DIR, 'Logs'))
except FileExistsError as e:
    pass
except Exception as e:
    print("Logger hatası")

try:
    os.mkdir(os.path.join(BASE_DIR, "Logs", year))
except FileExistsError as e:
    pass
except Exception as e:
    print(f"{e} | log oluşturma hatası")

try:
    os.mkdir(os.path.join(BASE_DIR, "Logs", year, month))
except FileExistsError as e:
    pass
except Exception as e:
    print(f"{e} | log oluşturma hatası")
    
try:
    os.mkdir(os.path.join(BASE_DIR, "Logs", year, month, day))
except FileExistsError as e:
    pass
except Exception as e:
    print(f"{e} | log oluşturma hatası")    

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