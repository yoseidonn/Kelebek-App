# This module has bunch of functions to create a html file which consist of a view of created exam
# The create function creates the file,
# which has grids for each classroom with students.
# You can preview students layout by the created html file.
# Also used by student if student attended to the exam. 
# (Imzalar ve sınıf düzenleri)

from App import database
import os

# PATHS
BASE = os.path.join('Templates', 'ClassroomsTemplates', 'base.html')
HEAD = os.path.join('Templates', 'ClassroomsTemplates', 'head.html')
BODY = os.path.join('Templates', 'ClassroomsTemplates', 'body.html')
# PRE-DEFINED SEPERATOR FOR HTMLS
SEPERATOR = "{{}}"

def create(examDate, classrooms, exams):
    # classrooms/sonuc, shuffle modülünde oluşturulan ve windows modülünden gönderilen bir shuffle fonksiyonu çıktısıdır.
    """
    tarih = "2022-08-16 10:30"
    sonuc = {
        salon1: {
            "derslik_adi": "10/A",
            "ogretmen_yonu": "Solda",
            "kacli": "1'li",
            "oturma_duzeni": [
                [{1: (ogrenci)},{2: (ogrenci)},{3: (ogrenci)},{4: (ogrenci)}],
                [{5: (ogrenci)},{6: (ogrenci)},{7: (ogrenci)},{8: (ogrenci)}],
                [{9: (ogrenci)},{10: (ogrenci)},{11: (ogrenci)}]
                ]
            }
        }
    """
    student_exam = {}
    for eName in exams:
        for gradeName in exams[eName]:
            result = database.get_all_students(grade = gradeName)
            for student in result:
                student_exam.update({student: eName})
    
    with open(HEAD, "r", encoding="utf-8") as headHTML:
        head = headHTML.read()
        head = head.split(SEPERATOR)
        head.insert(1, f'{examDate} Oturma Düzeni')
        head = "".join(head)

    with open(BODY, "r", encoding="utf-8") as bodyHTML:
        body = bodyHTML.read()
        body = body.split(SEPERATOR)
        innerBodyHTML = html(classrooms, student_exam)
        body.insert(1, innerBodyHTML)
        body = "".join(body)

    with open(BASE, "r", encoding="utf-8") as baseHTML:
        base = baseHTML.read()
        base = base.split(SEPERATOR)
        base.insert(1, head)
        base.insert(2, body)
        fullHtml = "".join(base)
        
    fileName = "salon_oturma_duzenleri.html"
    try:
        os.mkdir(os.path.join('Temp', examDate))
    except FileExistsError:
        # os.rmdir(os.path.join('Temp', examDate))
        # students_html.py bitince burası iki kere çalışmayacak o zaman var olanı silebiliriz.
        pass
        
    with open(os.path.join('Temp', examDate, fileName), 'w', encoding='utf-8') as newFile:
        newFile.write(fullHtml)
    
    filePath = os.path.join('Temp', examDate, fileName)
    htmlContent = fullHtml
        
    return (filePath, htmlContent)
    
def column_setter_text(classroom):
    count = 0
    oturmaDuzeni = classroom["oturma_duzeni"]
    kacli = classroom["kacli"]
    columnCount = len(oturmaDuzeni)
    for colIndex in range(len(oturmaDuzeni)):
        # Adding the first desk is enough to count total column count for table
        desk = oturmaDuzeni[colIndex][0]
        for deskNo in desk:
            count += 1
            
    setter = list()
    i = count + columnCount - 1
    for _ in range(i):
        setter.append(f'auto ')

    setter = "".join(setter)
    return [setter, i]
                    
def html(classrooms, student_exam):
    # student_exam = {2949: "11 MATEMATİK",
    #                 2999: "10 FİZİK"
    #                }
    html_text = str()
    br = '<br><br><br><br>'
    big = '<strong>{}</strong> SALONUNUN YOKLAMA ÇİZELGESİ (Salon Görünümü - Öğrenci)<br>'
    strong = '<strong>{}</strong>'

    containerOpener = '<div style="grid-template-columns: {};" class="container">'
    containerCloser = '</div>'
    item = '<div class="item">{}</div>'

    info = '<strong>{}<br><br>{}</strong><br>{} {} {}<br>{}'
    gap = '<div class="empty"></div>'
    teacher = '<div class="item">Öğretmen masası</div>'

    text_array = []
    x = 0
    for cName in classrooms:
        oturmaDuzeni = classrooms[cName]["oturma_duzeni"]
        kacli = classrooms[cName]["kacli"]
        yon = classrooms[cName]["ogretmen_yonu"]
        ogretmenMasasiOgrenci = classrooms[cName]["ogretmen_masasi"]
            
        name = big.format(cName)
        if not x:   
            x = 1
        else:
            text_array.append(br)
        text_array.append(name)
    
        classroom = classrooms[cName]
        opener = column_setter_text(classroom)
        container = containerOpener.format(opener[0])
        text_array.append(container)
        
        longestRowCount = 0
        for col in oturmaDuzeni:
            if len(col) > longestRowCount:
                longestRowCount = len(col)

        #### Öğretmen masası yoksa boş, var ise oradaki öğrencinin bilgilerini seç.
        ogretmenMasasi = item.format(info.format("", "", "", "", "", ""))    
        if ogretmenMasasiOgrenci is not None:
            eName = ogretmenMasasiOgrenci[0]
            ogrenci = ogretmenMasasiOgrenci[1]
            grade, no, cinsiyet, name = ogrenci[4], ogrenci[0], ogrenci[3], ogrenci[1:3]
            student = info.format("Öğretmen masası", eName, grade, no, cinsiyet, name)
            ogretmenMasasi = item.format(student)

        #### Kutuları yerleştir
        if yon == "Solda":
            text_array.append(ogretmenMasasi)
            if kacli == "2'li":
                text_array.append(gap)
            
            text_array.append(gap)

            for colInd in range(1,len(oturmaDuzeni)):
                text_array.append(gap)
                if kacli == "2'li":
                    text_array.append(gap)
                if colInd != len(oturmaDuzeni) - 1:
                    text_array.append(gap)

        elif yon == "Sağda":
            for colInd in range(len(oturmaDuzeni) - 1):
                text_array.append(gap)
                if kacli == "2'li":
                    text_array.append(gap)
                if colInd != len(oturmaDuzeni) - 1:
                    text_array.append(gap)
            if kacli == "2'li":
                text_array.append(gap)
            text_array.append(ogretmenMasasi)
        ####
        
        for rowInd in range(longestRowCount):
            for colInd in range(len(oturmaDuzeni)):
                try:    
                    desk = oturmaDuzeni[colInd][rowInd]
                except Exception as e:
                    # Sıra yoksa boşluk koy
                    # print(e)
                    newItem = gap
                    if kacli == "2'li":
                        text_array.append(newItem)
                    text_array.append(newItem)
                    text_array.append(gap)
                    continue

                # Sıra varsa formatla ve yeni divi ekle
                for deskNo in desk:
                    chair = desk[deskNo]
                    if chair is not None:
                        eName = student_exam[chair]
                        name = " ".join(chair[1:3])
                        cinsiyet = chair[3]
                        no = chair[0]
                        grade = chair[4]
                        student = info.format(deskNo, eName, grade, no, cinsiyet, name)
                        newItem = item.format(student)
                        text_array.append(newItem)
                    else:
                        # Sırada öğrenci yoksa boş koy
                        i = info.format(deskNo, "", "", "", "", "")
                        newItem = item.format(i)
                        text_array.append(newItem)

                # Son kolon değilse sıradan sonra araya boşluk koy
                if colInd != len(oturmaDuzeni) - 1:
                    text_array.append(gap)
                    
        text_array.append(containerCloser)

    html_text = " ".join(text_array)
    return html_text
        
        
if __name__ == "__main__":
    from Structs import exam_struct
    import shuffle
    exams = {"10 MAT": {
                "gradeNames": ["10/D"],
            },
             "11 EDB": {
                "gradeNames": ["11/A", "11/B"]
             }
    }
    classroomNames = ["9/A", "9/D", "10/C", "10/D"]
    algName = shuffle.algorithmNames[0]
    exam = exam_struct.Exam(exams = exams, classroomNames = classroomNames, algorithmName = algName, optionList = [False, False])
    sonuc = shuffle.shuffle(exam)

    date = "2022-01-01 11:30"
    create(date, sonuc, exams)
