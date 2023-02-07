# This module has bunch of functions to create a html file which consist of a view of created exam
# The create function creates the file,
# which has a list of students for each grade,
# and every student has a number to learn where to go.
# (Sınıf listeleri ve katılım yerleri)
from App import database
import os

# PATHS
BASE = os.path.join('Templates', 'StudentsTemplates', 'base.html')
HEAD = os.path.join('Templates', 'StudentsTemplates', 'head.html')
BODY = os.path.join('Templates', 'StudentsTemplates', 'body.html')
# PRE-DEFINED SEPERATOR FOR HTMLS
SEPERATOR = "{{}}"

def create(examInfos, classrooms, exams):
    # classrooms/sonuc from shuffle.shuffle()

    with open(HEAD, "r", encoding="utf-8") as headHTML:
        head = headHTML.read()
        head = head.split(SEPERATOR)
        masterExamName = examInfos[-1]
        head.insert(1, f'{masterExamName} Sınıf listeleri')
        head = "".join(head)

    with open(BODY, "r", encoding="utf-8") as bodyHTML:
        body = bodyHTML.read()
        body = body.split(SEPERATOR)

        grades = classrooms_to_grades(classrooms)
        bodyContent = create_html_table(grades)

        body.insert(1, bodyContent)
        body = "".join(body)

    with open(BASE, "r", encoding="utf-8") as baseHTML:
        base = baseHTML.read()
        base = base.split(SEPERATOR)
        base.insert(1, head)
        base.insert(2, body)
        fullHtml = "".join(base)

    fileName = "sinif_listeleri.html"
    examName = "_".join([examInfos[-1], examInfos[3], examInfos[4]])
    try:
        os.mkdir(os.path.join('Temp', examName))
    except FileExistsError:
        pass
    
    with open(os.path.join('Temp', examName, fileName), 'w', encoding='utf-8') as newFile:
        newFile.write(fullHtml)

    filePath = os.path.join('Temp', examName, fileName)
    htmlContent = fullHtml
     
    return (filePath, htmlContent)

def create_html_table(grades):
    html = "<body>\n"
    for grade_name, students in grades.items():
        html += f"<table>\n<caption>Table {grade_name}</caption>\n"
        html += "<tr>\n<th>Name</th>\n<th>Classroom and Desk</th>\n</tr>\n"
        for student in students:
            nameSurname, place= student[1][1:3], student[2]
            nameSurname = f"{nameSurname[0]} {nameSurname[1]}"
            html += "<tr>\n"
            html += f"<td>{nameSurname}</td>\n"
            html += f"<td>{place}</td>\n"
            html += "</tr>\n"
        html += "</table>\n"
    html += "</body>"
    
    return html

def classrooms_to_grades(classrooms):
    counter = 0
    mixed = {}
    for classroom in classrooms:
        oturmaDuzeni = classrooms[classroom]["oturma_duzeni"]
        ogretmenMasasi =  classrooms[classroom]["ogretmen_masasi"]
        if ogretmenMasasi is not None:
            student = ogretmenMasasi[1]
            name = student[1] + " " + student[2]
            no = student[0]
            grade = student[4]
            place = "Öğretmen masası"
            mixed.update({no: [grade, name, place]})

        for colIndex in range(len(oturmaDuzeni)):
            for rowIndex in range(len(oturmaDuzeni[colIndex])):
                desk = oturmaDuzeni[colIndex][rowIndex]
                for deskNo in desk:
                    student = desk[deskNo]
                    if student is not None:
                        counter += 1
                        no = student[0]
                        grade = student[4]
                        info = [grade, student, classroom, deskNo]
                        mixed.update({no: info})
    
    
    seperated = {}
    createds = []
    for no in mixed:
        info = mixed[no]
        grade = info[0]
        if grade not in createds:
            createds.append(grade)
            seperated.update({grade: []})

        seperated[grade].append(info)
        
    return seperated

def layer_function(classrooms):
    counter = 0
    mixed = {}
    for classroom in classrooms:
        oturmaDuzeni = classrooms[classroom]["oturma_duzeni"]
        ogretmenMasasi =  classrooms[classroom]["ogretmen_masasi"]
        if ogretmenMasasi is not None:
            student = ogretmenMasasi[1]
            name = student[1] + " " + student[2]
            no = student[0]
            grade = student[4]
            place = "Öğretmen masası"
            mixed.update({no: [grade, name, place]})

        for colIndex in range(len(oturmaDuzeni)):
            for rowIndex in range(len(oturmaDuzeni[colIndex])):
                desk = oturmaDuzeni[colIndex][rowIndex]
                for deskNo in desk:
                    student = desk[deskNo]
                    if student is not None:
                        counter += 1
                        no = student[0]
                        grade = student[4]
                        info = [grade, student, classroom, deskNo]
                        mixed.update({no: info})
    
    seperated = {}
    createds = []
    for no in mixed:
        info = mixed[no]
        grade = info[0]
        if grade not in createds:
            createds.append(grade)
            seperated.update({grade: []})

        seperated[grade].append(info)
        
    return seperated

            
if __name__ == '__main__':
    pass