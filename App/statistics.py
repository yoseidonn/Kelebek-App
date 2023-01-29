import sqlite3

db = sqlite3.connect("database.db")
cur = db.cursor()

#########
#########


if __name__ == '__main__':
    infos = get_school_infos()
    for attr in infos:
        print(f"{attr}: {infos[attr]}")