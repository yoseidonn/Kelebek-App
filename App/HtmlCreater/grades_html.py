# This module has bunch of functions to create a html file which consist of a view of created exam
# The create function creates the file,
# which has a list of students for each grade,
# and every student has a number to learn where to go.
# (Sınıf listeleri ve katılım yerleri)
from App import database, logs
from App.logs import logger
from App.database import num_sort, num_sort_dict, num_sort_tuple
import os, datetime, shutil, re

# PATHS
BASE_DIR = os.getenv("BASE_DIR")
BASE = """<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8"/>
        <link href="styles.css" rel="stylesheet" type="text/css">
        <style>
            table {
                width: 100%;
                border-collapse: collapse;
                page-break-after: always;
            }
            @media print {
                @page {
                    size: A4 portrait;
                    margin: 2cm;
                }
            }
            th, td {
                border: 1px solid black;
                padding: 8px;
                text-align: left;
            }
            th {
                background-color: #f2f2f2;
            }
        </style>
    </head>
    <body>
        {{}}
    </body>
</html>"""

# PRE-DEFINED SEPERATOR FOR HTMLS
SEPERATOR = "{{}}"

def create(examInfos, classrooms, exams):
    baseStart, baseEnd = BASE.split(SEPERATOR)
    grades = classrooms_to_grades(classrooms)
    grade_htmls = create_html_tables(grades, baseStart, baseEnd)
    # TODO GRADE_HTMLS Fonksiyonu çalışmıyor. Geriye boş dönüyor dolayısıyla sınıfların dosyaları oluşturulmuyor
    examName = "_".join([examInfos.get('Sinav-Adi'), examInfos.get('Tarih'), examInfos.get('Kacinci-Ders').strip()])
    try:
        os.mkdir(os.path.join(BASE_DIR, 'Temp', examName, "Grades"))
    except Exception as e:
        logger.error(e)
        shutil.rmtree(os.path.join(BASE_DIR, 'Temp', examName, "Grades"))
        os.makedirs(os.path.join(BASE_DIR, 'Temp', examName, "Grades"), exist_ok=True)

    name_template = "{}.html"
    gradePaths = {}
    for gradeName in grade_htmls:
        gradeNameToPath = "".join(gradeName.split("/"))
        gradePath = os.path.join(BASE_DIR, 'Temp', examName, "Grades", name_template.format(gradeNameToPath))
        try:
            with open(gradePath, 'w', encoding='utf-8') as newFile:
                newFile.write(grade_htmls[gradeName])
            gradePaths.update({gradeName: gradePath})
        except Exception as e:
            logger.error(str(e))
            
    sortedGradePaths = {}
    gradeNames = list(gradePaths.keys())
    gradeNames = sorted(sorted(gradeNames), key=num_sort)
    for gradeName in gradeNames:
        sortedGradePaths.update({gradeName: gradePaths[gradeName]})
        
    return sortedGradePaths

def create_html_tables(grades, baseStart, baseEnd):
    print("creating html tables")
    grade_htmls = {}
    for grade_name, students in grades.items():
        print(grade_name, len(students))
        grade_html = [baseStart]
        grade_html.append(f"<table><caption>{grade_name} Listesi</caption>")
        grade_html.append("<tr><th>Öğrenci</th><th>Sınav yeri</th></tr>")
        for student in students:
            nameSurname, classroom, placeNumber = student[1][1:3], student[2], student[3]
            nameSurname = f"{nameSurname[0]} {nameSurname[1]}"
            
            grade_html.append("<tr>")
            grade_html.append(f"<td>{nameSurname}</td>")
            grade_html.append(f"<td>{classroom} - {placeNumber}</td>")
            grade_html.append("</tr>")
        grade_html.append("</table>")
        grade_html.append(baseEnd)
        grade_htmls.update({grade_name: "\n".join(grade_html)})
        print("grade added")
        
    return grade_htmls

def classrooms_to_grades(classrooms: dict):
    counter = 0
    mixed = {}
    for classroomName, classroom in classrooms.items():
        oturmaDuzeni = classroom["oturma_duzeni"]
        ogretmenMasasiOgrenci =  classroom["ogretmen_masasi"]
        if ogretmenMasasiOgrenci is not None:
            # TODO - Check the grade variable if it is necessary or correctly assisgned
            grade = ogretmenMasasiOgrenci[4]
            student = ogretmenMasasiOgrenci[1]
            placeNumber = ogretmenMasasiOgrenci
            mixed.update({no: [grade, student, classroomName, placeNumber]})

        for colIndex in range(len(oturmaDuzeni)):
            for rowIndex in range(len(oturmaDuzeni[colIndex])):
                desk = oturmaDuzeni[colIndex][rowIndex]
                for placeNumber in desk:
                    student = desk[placeNumber].get("student")
                    if student is not None:
                        counter += 1
                        no = student[0]
                        grade = student[4]
                        info = [grade, student, classroomName, placeNumber]
                        mixed.update({no: info})

    seperated = {}
    createds = []
    for no, info in mixed.items():
        grade = info[0]
        if grade not in createds:
            createds.append(grade)
            seperated.update({grade: []})

        seperated[grade].append(info)
        
    return seperated

def num_sort(test_string):
    return list(map(int, re.findall(r'\d+', test_string)))

def num_sort_tuple(tuple_item):
    test_string = tuple_item[0]
    return int(re.findall(r'\d+', test_string)[0])

def num_sort_dict(test_dict: dict):
    order = sorted(sorted(list(test_dict.keys())), key=num_sort)
    sorted_dict = dict(sorted(test_dict.items(), key=lambda item: order.index(item[0])))
    return sorted_dict



if __name__ == '__main__':
    pass