### database.py
from .logs import logger
import sqlite3, re

db = sqlite3.connect("database.db")
cur = db.cursor()

def createTables() -> None:
    """
    Program ilk defa çalıştırılmışsa gerekli tabloları oluşturmak için,
    kayıtlı tablolar silinmişse veya bozulmuşsa onarım için kullanılır.
    """
    
    # OGRENCILER
    cur.execute("""
        CREATE TABLE IF NOT EXISTS "ogrenciler" (
	        "no" INTEGER UNIQUE,
	        "ad" TEXT,
	        "soyad"	TEXT,
	        "cinsiyet"	TEXT,
            "sinif" TEXT)
        """)
    
    # SALONLAR DUZENLERI
    cur.execute("""
        CREATE TABLE IF NOT EXISTS "salonlar" (
	        "derslik_adi"	TEXT UNIQUE,
	        "ogretmen_yonu"	TEXT,
	        "kacli"	TEXT,
	        "oturma_duzeni"	TEXT)
        """)

    # OKUL BİLGİLERİ
    cur.execute("""
        CREATE TABLE IF NOT EXISTS "okul_bilgileri" (
	        "okul_adi"	TEXT,
	        "mudur_adi"	TEXT,
	        "okul_turu"	TEXT,
	        "ogrenci_sayisi"	INTEGER,
	        "sinif_sayisi"	INTEGER,
	        "salon_sayisi"	INTEGER)
        """)
    
    # GEÇMİŞ SINAVLAR
    cur.execute("""
        CREATE TABLE IF NOT EXISTS "sinavlar" (
        	"id"	    INTEGER NOT NULL,
	        "tarih"	    TEXT NOT NULL,
	        "salonlar"	TEXT NOT NULL,
	        PRIMARY KEY("id"))
        """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS "ayarlar" (
        	"id"	INTEGER,
	        "ayar"	TEXT,
	        "deger"	TEXT,
        	PRIMARY KEY("id" AUTOINCREMENT))
        """)

createTables()   

######################### FONKSIYONLAR ############################

#SUBE ISIMLERI
def get_all_grade_names() -> list:
    """
    Kayıtlı tüm öğrencilerin şubelerini tekrarsız bir liste halinde döndürür.
    """

    QUERY = "SELECT sinif FROM ogrenciler"
    tumSiniflar = cur.execute(QUERY)
    siniflar = set()
    [siniflar.add(sinif[0]) for sinif in tumSiniflar]
    siniflar = list(siniflar)
    
    siniflar = sorted(sorted(siniflar), key=num_sort)
    return siniflar

#ÖĞRENCİLER
def add_one_student(student: list) -> None:
    """
    Verilen bilgiler doğrultusunda tek bir öğrenci ekler.
    """

    if len(student) != 0:
        cur.execute("INSERT OR REPLACE INTO ogrenciler VALUES(? ,?, ?, ?, ?)", student)
        db.commit()

def add_multiple_students(students: list) -> None:
    """
    Verilen listede bulunan bilgiler doğrultusunda birden fazla öğrenci ekler.
    """

    if len(students) != 0:
        for student in students:
            cur.execute("INSERT OR REPLACE INTO ogrenciler VALUES(?, ?, ?, ?, ?)", [data for data in student])
        db.commit()

def update_student(student):
    number, name, surname, gender, grade = student
    QUERY = "UPDATE ogrenciler SET ad = ?, soyad = ?, cinsiyet = ?, sinif = ? WHERE no = ?"

    cur.execute(QUERY, (name, surname, gender, grade, number))

    db.commit()

def get_student_counts_per_every_grade() -> list:
    """
    İstatistik tablolarında kullanmak için sırasıyla toplam, 9, 10, 11 ve 12. sınıflardaki öğrenci sayılarını döndürür.
    """

    QUERY_9 = "SELECT * FROM ogrenciler WHERE sinif LIKE '%9%'"
    QUERY_10 = "SELECT * FROM ogrenciler WHERE sinif LIKE '%10%'"
    QUERY_11 = "SELECT * FROM ogrenciler WHERE sinif LIKE '%11%'"
    QUERY_12 = "SELECT * FROM ogrenciler WHERE sinif LIKE '%12%'"
    QUERY_TOTAL = "SELECT ad FROM ogrenciler"
    totalCount = str(len(cur.execute(QUERY_TOTAL).fetchall()))
    count9 = str(len(cur.execute(QUERY_9).fetchall()))
    count10 = str(len(cur.execute(QUERY_10).fetchall()))
    count11 = str(len(cur.execute(QUERY_11).fetchall()))
    count12 = str(len(cur.execute(QUERY_12).fetchall()))
    return [totalCount, count9, count10, count11, count12]
    
def get_all_students(number = False, fullname = False, grade = False, withGrades = False) -> list or dict:
    """
    withGrades = True: Kayıtlı tüm öğrencileri şube isimlerini anahtar olarak tutan bir sözlükte geri döndürür.
    {
        "9/A": [ogr1, ogr2, ogr3],
        "9/B": [ogr4, ogr5, ogr6]
    }
    withGrades = False: Tüm öğrencileri tek bir listede geri döndürür.
    """

    QUERY = "SELECT * FROM ogrenciler ORDER BY sinif, no"
    QUERY_NUM = "SELECT * FROM ogrenciler WHERE no = ? ORDER BY sinif, no"
    QUERY_CLASS = "SELECT * FROM ogrenciler WHERE sinif = ? ORDER BY sinif, no"
    students = cur.execute(QUERY).fetchall()

    if withGrades:
        students = cur.execute(QUERY).fetchall()
        grades = {}
        for grade in get_all_grade_names():
            grades.update({grade: []})

        for student in students:
            studentGrade = student[4]
            grades[studentGrade].append(student)
            
        return grades

    if number:
        students = cur.execute(QUERY_NUM, (number,)).fetchall()
        
    elif fullname:
        fullname = fullname.upper()
        students = cur.execute(QUERY).fetchall()
        students = [student for student in students if (fullname in (student[1] + " " + student[2]))]

    elif grade:
        students = cur.execute(QUERY_CLASS, (grade,)).fetchall()

    return students

def get_grade_given_students(gradeNames: list or tuple or dict, returnType: str = "dict") -> dict:
    """
    Sınıf adı verilen tüm öğrencilerin bulunduğu bir öğrenci havuzu döndürür. -list-
    """
    students = dict()
    QUERY = "SELECT * FROM ogrenciler WHERE sinif = ?"
    
    # Eğer grades bir sözlük ise
    if isinstance(gradeNames, dict):
        grade_names = list()
        for gradeNameList in gradeNames.values():
            grade_names.extend(gradeNameList)
        gradeNames = grade_names
    
    for gradeName in gradeNames:
        result = cur.execute(QUERY, (gradeName,)).fetchall()
        students.update({gradeName: result})

    return students

def remove_students(numbers: list[int]) -> None:
    """
    Numarası verilen öğrenci kaydını siler.
    """

    QUERY = "DELETE FROM ogrenciler WHERE no = ?"
    for number in numbers:
        cur.execute(QUERY, (number,))
    db.commit()

def remove_all_students():
    """
    Kayıtlı tüm öğrencileri siler.
    """

    QUERY = "DELETE FROM ogrenciler WHERE 1=1"
    cur.execute(QUERY)
    db.commit()

################### CLASSROOMS ##############

def add_new_classroom(*values):
    """
    Bilgileri verilen bir derslik ekler.
    """

    QUERY = "INSERT OR REPLACE INTO salonlar VALUES(?, ?, ?, ?)"
    cur.execute(QUERY, values)
    db.commit()

def get_all_classrooms(onlyNames = False) -> list or dict:
    """
    onlyNames = True: Kayıtlı tüm salonların adlarını döndürür.
    onlyNames = False: Kayıtlı tüm salonların özelliklerini, salon adlarını anahtar olarak tutan bir sözlük halinde döndürür.
    {
        "Salon-1": {
            "derslik_adi: "Salon-1",
            "ogretmen_yonu": "Solda",
            "kacli": "2'li",
            "oturma_duzeni": "5,5,4",
            }
        },
        ...        
    }
    """

    QUERY = "SELECT derslik_adi FROM salonlar ORDER BY derslik_adi"
    QUERY_2 = "SELECT derslik_adi, ogretmen_yonu, kacli, oturma_duzeni FROM salonlar ORDER BY derslik_adi"
    
    if onlyNames: #SADECE ADLAR İSE
        salonAdlari = []
        salonAdlariTuple = cur.execute(QUERY).fetchall()
        for salonAdi in salonAdlariTuple:
            salonAdlari.append(salonAdi[0])
            
        return sorted(sorted(salonAdlari), key=num_sort)
        
    # SALON BİLGİLERİ
    salonlar = {}
    salonlarTuples = cur.execute(QUERY_2).fetchall()
    
    for salon in salonlarTuples:
        salonlar.update({salon[0]: list(salon)})

    salonlar = num_sort_dict(salonlar)
    return salonlar

def get_classrooms_counts_per_every_grade() -> list:
    """
    İstatistik tablolarında kullanmak için sırasıyla toplam, 9, 10, 11 ve 12. sınıflara ait şube sayılarını döndürür.
    """

    QUERY_9 = "SELECT * FROM salonlar WHERE derslik_adi LIKE '%9%'"
    QUERY_10 = "SELECT * FROM salonlar WHERE derslik_adi LIKE '%10%'"
    QUERY_11 = "SELECT * FROM salonlar WHERE derslik_adi LIKE '%11%'"
    QUERY_12 = "SELECT * FROM salonlar WHERE derslik_adi LIKE '%12%'"
    QUERY_TOTAL = "SELECT derslik_adi FROM salonlar"
    totalCount = str(len(cur.execute(QUERY_TOTAL).fetchall()))
    count9 = str(len(cur.execute(QUERY_9).fetchall()))
    count10 = str(len(cur.execute(QUERY_10).fetchall()))
    count11 = str(len(cur.execute(QUERY_11).fetchall()))
    count12 = str(len(cur.execute(QUERY_12).fetchall()))
    return [totalCount, count9, count10, count11, count12]

# THESE TWO FUNCTION WORKS TOGETHER
def create_arrangement(kacli: str, ogretmen_yonu: str, oturma_duzeni: str):
    """
    Verilen derslik özelliklerine göre öğrenci dağıtmak için kullanılacak olan bir düzen oluşturur.
    [
        [ 
            {1: {"exam_name": None, "student": None}, 2: {"exam_name": None, "student": None}},
            {3: {"exam_name": None, "student": None}, 4: {"exam_name": None, "student": None}},
            {5: {"exam_name": None, "student": None}, 6: {"exam_name": None, "student": None}},
            {7: {"exam_name": None, "student": None}, 8: {"exam_name": None, "student": None}}
        ],
        [ 
            {9: {"exam_name": None, "student": None}, 10: {"exam_name": None, "student": None}},
            {11: {"exam_name": None, "student": None}, 12: {"exam_name": None, "student": None}},
            {13: {"exam_name": None, "student": None}, 14: {"exam_name": None, "student": None}},
        ],
    ]
    """

    rowCounts = oturma_duzeni.split(",")
    matrix = []
    # KUTUCUKLARI KOY
    for rowCount in rowCounts:
        matrix.append([])
        for _ in range( int(rowCount) ):
            matrix[-1].append({})

    #INDEXLERI YERLESTIR
    deskNo = 1
    if ogretmen_yonu == "Solda":
        for colIndex in range(len(matrix)):
            for rowIndex in range(len(matrix[colIndex])):
                matrix[colIndex][rowIndex].update({deskNo: {"exam_name": None, "student": None}})
                deskNo += 1
                if kacli == "2'li":
                    matrix[colIndex][rowIndex].update({deskNo: {"exam_name": None, "student": None}})
                    deskNo += 1
                              
    else:
        for colIndex in range(len(matrix) - 1 , -1, -1):
            for rowIndex in range(len(matrix[colIndex])):
                if kacli == "1'li":
                    matrix[colIndex][rowIndex].update({deskNo: {"exam_name": None, "student": None}})
                    deskNo += 1
                else:
                    deskNo += 1
                    matrix[colIndex][rowIndex].update({deskNo: {"exam_name": None, "student": None}})
                    deskNo -= 1
                    matrix[colIndex][rowIndex].update({deskNo: {"exam_name": None, "student": None}})
                    deskNo += 2
                    
    return matrix
    
def get_name_given_classrooms(names: list) -> dict:
    """
    Listedeki isimlerin veritabanındaki özelliklerini salon adını anahtar olarak tutan bir sözlük döndürür. 
    """

    classrooms = dict()
    for name in names:
        QUERY = "SELECT * FROM salonlar WHERE derslik_adi = ?"
        result = cur.execute(QUERY, (name,)).fetchone()
        if result:
            classroom = result

        else:
            return classrooms
        
        derslik_adi, ogretmen_yonu, kacli, oturma_duzeni_text = [classroom[indx] for indx in range(len(classroom))]
        duzen = create_arrangement(kacli, ogretmen_yonu, oturma_duzeni_text)
        
        classroom = {"derslik_adi": derslik_adi,
                  "ogretmen_yonu": ogretmen_yonu,
                  "kacli": kacli,
                  "oturma_duzeni": duzen,
                  "oturma_duzeni_text": oturma_duzeni_text,
                  "ogretmen_masasi": None}
        
        classrooms.update({derslik_adi: classroom})

    return classrooms
    
def remove_classroom(classroomName) -> None:
    """
    Adı verilen salonun kaydını siler.
    """
    QUERY = "DELETE FROM salonlar WHERE derslik_adi = ?"
    cur.execute(QUERY, (classroomName,))
    db.commit()

################### THE SCHOOL ##############

def update_all_infos(*values) -> None:
    """
    Okul bilgilerini verilen bilgileri kullanarak günceller.
    """

    QUERY = "DELETE FROM okul_bilgileri WHERE 1=1"
    QUERY_2 = "INSERT INTO okul_bilgileri VALUES(?, ?, ?)"
    cur.execute(QUERY)
    cur.execute(QUERY_2, values)
    db.commit()

def get_all_infos() -> list:
    """
    Tüm okul bilgilerini geri döndürür
    """

    QUERY = "SELECT * FROM okul_bilgileri"
    try:
        bilgiler = cur.execute(QUERY).fetchall()[0]
    except Exception as e:
        logger.error(f"{e} | Okul bilgileri veritabanından çekilemedi")
        bilgiler = ("", "", "")
        
    return bilgiler

def get_table_infos() -> list:
    """
    Okulla ilgili istatistiklerin tutulduğu tabloda kullanılmak üzere gerekli bilgileri döndürür.
    """

    gradeCounts = []
    studentCounts = []
    classroomCounts = []

    grades = get_all_students(withGrades=True)

    total = str(len(grades))
    gradeCounts.append(total)

    gradesList = [gradeName.split("/")[0] for gradeName in grades.keys()]
    gradesSet = set(gradesList)
    for gradeName in gradesSet:
        count = gradesList.count(gradeName)
        gradeCounts.append(str(count))
            
    gradeCounts = ",".join(gradeCounts)

    studentCounts = get_student_counts_per_every_grade()
    studentCounts = ",".join(studentCounts)
    classroomCounts = get_classrooms_counts_per_every_grade()
    classroomCounts = ",".join(classroomCounts)
    
    return [gradeCounts, studentCounts, classroomCounts]

################### SETTINGS ##############

def get_theme():
    QUERY = "SELECT COUNT(*) FROM ayarlar WHERE ayar = ?"
    cur.execute(QUERY, ("theme",))
    result = cur.fetchone()[0]

    if result == 0:
        # Satır yok, yeni satır oluştur
        QUERY = "INSERT INTO ayarlar (ayar, deger) VALUES (?, ?)"
        cur.execute(QUERY, ("theme", "auto"))
    
    QUERY = "SELECT deger FROM ayarlar WHERE ayar = ?"
    theme = cur.execute(QUERY, ("theme",)).fetchone()[0]
    return theme

def set_theme(theme: str):
    QUERY = "SELECT COUNT(*) FROM ayarlar WHERE ayar = ?"
    cur.execute(QUERY, ("theme",))
    result = cur.fetchone()[0]

    if result == 0:
        # Satır yok, yeni satır oluştur
        QUERY = "INSERT INTO ayarlar (ayar, deger) VALUES (?, ?)"
        cur.execute(QUERY, ("theme", theme))
    else:
        # Satır var, değeri güncelle
        QUERY = "UPDATE ayarlar SET deger = ? WHERE ayar = ?"
        cur.execute(QUERY, (theme, "theme"))

    db.commit()

################### EXTRA FUNCS ##############

def num_sort(test_string):
    return list(map(int, re.findall(r'\d+', test_string)))

def num_sort_tuple(tuple_item):
    test_string = tuple_item[0]
    return int(re.findall(r'\d+', test_string)[0])

def num_sort_dict(test_dict: dict):
    order = sorted(sorted(list(test_dict.keys())), key=num_sort)
    sorted_dict = dict(sorted(test_dict.items(), key=lambda item: order.index(item[0])))
    return sorted_dict


if __name__ == "__main__":
    #cur.execute("INSERT INTO ogrenciler VALUES (2949, 'Yusuf', 'Kiriş', 'Erkek', '10/A')")
    #cur.execute("INSERT INTO ogrenciler VALUES (2950, 'A', 'B', 'C', '10/A')")

    students = cur.execute("SELECT * FROM ogrenciler WHERE sinif = ? ORDER BY sinif, no", ("10/A", )).fetchall()
    print(students)