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

        grades = layer_function(classrooms)
        bodyContent = html(grades)

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

def html(grades):
    text_array = []

    wrapperStart = '<div class="table-wrapper">'
    wrapperEnd = '</div>'
    
    tableStart = '<table class="fl-table">'
    tableEnd = '</table>'
    
    head = '''<thead>
                    <tr>
                        <th>Sıra</th>
                        <th>Öğrenci</th> 
                        <th>Sınav yeri</th> 
                    </tr>
                </head>'''
                
    bodyOpen = '<tbody>'
    bodyClose = '</tbody>'
    outerOpener = '<div class="outer">'
    outerCloser = '</div>'
    row = '<tr> <td>{}</td> <td>{}</td> <td>{}</td> </tr>'
    
    
    for gradeName in grades:
        i = 1
        text_array.append(outerOpener)
        text_array.append(f'<h2>{gradeName}</h2>')
        text_array.append(wrapperStart)
        text_array.append(tableStart)
        text_array.append(head)
        text_array.append(bodyOpen)
    
        for info in grades[gradeName]:
            if info[2] == "Öğretmen masası":
                grade, name, placeInfo = info
                newRow = row.format(str(i), name, placeInfo)
                text_array.append(newRow)
                i += 1
                continue
            
            student = info[1]
            fullName = f'{student[1]} {student[2]}'
            examClassroom, examDeskNo = info[2], info[3]
            placeInfo = f'{examClassroom} {examDeskNo}'
            newRow = row.format(str(i), fullName, placeInfo)
            text_array.append(newRow)
            i += 1

        text_array.append(bodyClose)
        text_array.append(tableEnd)
        text_array.append(wrapperEnd)
        text_array.append("<br><br><br>")
        text_array.append(outerCloser)

    html_text = " ".join(text_array)

    return html_text 

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
        
    print("Sınıf sayısı:", len(seperated))
    print("Öğrenci sayısı:", len(mixed))
    return seperated

            
if __name__ == '__main__':
    pass