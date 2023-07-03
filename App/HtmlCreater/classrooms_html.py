from App import database
from App import logs
from App.logs import logger
from App.database import num_sort, num_sort_dict, num_sort_tuple
import os, shutil, datetime, re

# PATHS
BASE_DIR = os.environ["BASE_DIR"]
BASE = """<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8"/>
        <link href="styles.css" rel="stylesheet" type="text/css">
        <style>
      .wrapper {
        height: 21cm;
        width: 29.7cm;
        max-height: 21cm;
        max-width: 29.7cm;
        page-break-inside: avoid;
        page-break-after: always;
      }
      .header {
        font-size: large;
        text-align: center;
        height: 2.5cm;
        max-height: 2.5cm;
    }
        .headerText{
            text-align: center;
        }

      .footer {
        height: 4.5cm;
      }
      .row {
        display: flex;
        flex-direction: row;
        justify-content: center;
      }
      .between {
        justify-content: space-between;
      }
      .grid2x3 {
        display: grid;
        max-height: 2cm;
        row-gap: 0.3cm;
        column-gap: 0.1cm;
        grid-template-rows: 1fr 0.1fr 1fr;
        grid-template-columns: 1fr 1fr;
        max-height: 2.2cm;
      }
      .grid-bottom {
        display: grid;
        max-height: 2cm;
        row-gap: 0.1cm;
        column-gap: 0.3cm;
        grid-template-columns: 3fr 1fr 2fr 2fr 1fr 1fr;
        grid-template-rows: 2fr 2fr 2fr;
      }
      .span2 {
        grid-column: span 2;
        display: flex;
        justify-content: center;
      }

      .left {
        display: flex;
        justify-content: flex-start;
      }

      .right {
        display: flex;
        justify-content: flex-end;
      }
      .gap {
        height: 1cm;
      }
      .line {
        height: 1px;
        border-bottom: 1px solid black;
      }

      .container {
        display: grid;
        grid-template-columns: repeat(8, 1fr);
        grid-auto-rows: min-content;
        background-color: green;
        overflow: hidden;
        height: 14cm;
        max-height: 14cm;
      }
      .item {
        background-color: white;
        border: 2px solid rgba(0, 0, 0, 0.8);
        padding: 1%;
        margin: 1%;
        font-size: x-small;
        min-height: 60px;
        max-height: 90px;
      }
      .blank {
        background-color: transparent;
        border: none;
      }
      @media print {
        .wrapper {
          size: A4;
        }
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
    headerInfos = examInfos[0:-1]
    student_exam = {}
    for eName in exams:
        for gradeName in exams[eName]:
            result = database.get_all_students(grade = gradeName)
            for student in result:
                student_exam.update({student: eName})
                
    baseStart, baseEnd = BASE.split(SEPERATOR)
    examName = "_".join([examInfos[-1], examInfos[3], examInfos[4]])
    classroom_htmls = get_htmls(classrooms, student_exam, headerInfos, baseStart, baseEnd)
    
    try:
        os.mkdir(os.path.join(BASE_DIR, 'Temp', examName))
        os.mkdir(os.path.join(BASE_DIR, 'Temp', examName, "Classrooms"))
    except Exception as e:
        logger.error(str(e))
            
        shutil.rmtree(os.path.join(BASE_DIR, 'Temp', examName))
        os.mkdir(os.path.join(BASE_DIR, 'Temp', examName))
        os.mkdir(os.path.join(BASE_DIR, 'Temp', examName, "Clasrooms"))

    name_template = "{}.html"
    classroomPaths = {}
    for classroomName in classroom_htmls:
        classroomNameToPath = "".join(classroomName.split("/"))
        classroomPath = os.path.join(BASE_DIR, 'Temp', examName, "Classrooms", name_template.format(classroomNameToPath))
        try:
            with open(classroomPath, 'w', encoding='utf-8') as newFile:
                newFile.write(classroom_htmls[classroomName])
            classroomPaths.update({classroomName: classroomPath})
        except Exception as e:
            logger.error(str(e))
    
    sortedClassroomPaths = {}
    classroomNames = list(classroomPaths.keys())
    classroomNames = sorted(sorted(classroomNames), key=num_sort)
    for classroomName in classroomNames:
        sortedClassroomPaths.update({classroomName: classroomPaths[classroomName]})
        
    return sortedClassroomPaths

def get_htmls(classrooms, student_exam, headerInfos, baseStart, baseEnd):
    # student_exam = {2949: "11 MATEMATİK",
    #                 2999: "10 FİZİK"
    #                }
    
    wrapperOpener = '<div class="wrapper">'
    header = '<div class="headerText"> {}  EĞİTİM-ÖĞRETİM YILI <strong>{} {}</strong> ({} - {})<br> <strong>{}</strong> SALONUNUN ÖĞRENCİ YOKLAMA ÇİZELGESİ <br> <br> </div>'
    # egitimOgretimYili, donem, kacinciYazili, tarih, kacinciDers, salonAdi
    footer = '<div class="footer"> Müdür adı: </div>'
    # footer ekle
    containerOpener = '<div class="container" style="grid-template-columns: {};">'
    # get_column_style(classroom)
    item = '<div class="item"> <strong> <center> {} </center> <center> {} </center> </strong> <br> {} - {} ({}) <br> {} </div>'
    # deskNo, sinavAdi, sinif, no, cinsiyet, fullAd
    itemBos = '<div class="item"> <center>{}</center> </div>'
    # deskNo
    ogretmenMasasiItem = '<div class="item"> <center>Öğretmen Masası</center> <br> {} <br> {} - {} ({}) <br> {} </div>'
    # sinavAdi, sinif, no, cinsiyet, fullAd
    ogretmenMasasiItemDouble = '<div class="item" style="grid-column: span 2"> <center>Öğretmen Masası</center> <br> {} <br> {} - {} ({}) <br> {} </div>'
    # sinavAdi, sinif, no, cinsiyet, fullAd
    ogretmenMasasiBosItem = '<div class="item"> <center>Öğretmen Masası</center> </div>'
    ogretmenMasasiBosDoubleItem = '<div class="item" style="grid-column: span 2"> <center>Öğretmen Masası</center> </div>'

    blank = '<div class="blank"></div>'
    wrapperCloser, containerCloser = '</div>', '</div>'
    
    classroom_htmls = {}
    x = 0
    for cName in classrooms:
        classroom_array = [baseStart]
        classroom = classrooms[cName]
        oturmaDuzeni = classrooms[cName]["oturma_duzeni"]
        kacli = classrooms[cName]["kacli"]
        yon = classrooms[cName]["ogretmen_yonu"]
        ogretmenMasasiOgrenci = classrooms[cName]["ogretmen_masasi"]
        
        classroom_array.append(wrapperOpener)
        headerText = header.format(*headerInfos, cName)
        classroom_array.append(headerText)
        columnStyle, totalCount = get_column_style(classroom)
        rowStyle = get_row_style(classroom)
        container = containerOpener.format(columnStyle)#, rowStyle)
        classroom_array.append(container)
        
        longestRowCount = 0
        for col in oturmaDuzeni:
            if len(col) > longestRowCount:
                longestRowCount = len(col)

        #### Öğretmen masası yoksa boş, var ise oradaki öğrencinin bilgilerini seç.
        ogretmenMasasiItem = ogretmenMasasiBosItem
        ogretmenMasasiItemDouble = ogretmenMasasiBosDoubleItem
        if ogretmenMasasiOgrenci is not None:
            print(f'OgretmenMasasiOgrenci: ')
            ogrenci = ogretmenMasasiOgrenci[1]
            sinavAdi = ogretmenMasasiOgrenci[0]
            sinif, no, cinsiyet, full_ad = ogrenci[4], ogrenci[0], ogrenci[3], ogrenci[1:3]

            ogretmenMasasiItem = ogretmenMasasiItem.format(sinavAdi, sinif, no, cinsiyet, full_ad)
            ogretmenMasasiItemDouble = ogretmenMasasiItemDouble.format(sinavAdi, sinif, no, cinsiyet, full_ad)

        #### Kutuları yerleştir
        if yon == "Solda":
            if kacli == "2'li":
                classroom_array.append(ogretmenMasasiItemDouble)
            else:
                classroom_array.append(ogretmenMasasiItem)
                classroom_array.append(blank)

            for _ in range(totalCount-2):
                classroom_array.append(blank)

        elif yon == "Sağda":
            for _ in range(totalCount-2):
                classroom_array.append(blank)

            if kacli == "2'li":
                classroom_array.append(ogretmenMasasiItemDouble)
            else:
                classroom_array.append(blank)
                classroom_array.append(ogretmenMasasiItem)
        ####
        
        for rowInd in range(longestRowCount):
            for colInd in range(len(oturmaDuzeni)):
                try:    
                    desk = oturmaDuzeni[colInd][rowInd]
                except Exception as e:
                    # Sıra yoksa boşluk koy
                    # print(e)
                    newItem = blank
                    if kacli == "2'li":
                        classroom_array.append(newItem)
                    classroom_array.append(newItem)
                    classroom_array.append(blank)
                    continue

                # Sıra varsa formatla ve yeni divi ekle
                for deskNo in desk:
                    chair = desk[deskNo]
                    if chair is not None:
                        sinavAdi = student_exam[chair]
                        fullAd = " ".join(chair[1:3])
                        cinsiyet = chair[3]
                        no = chair[0]
                        sinif = chair[4]
                        student = item.format(deskNo, sinavAdi, sinif, no, cinsiyet, fullAd)
                        classroom_array.append(student)
                    else:
                        # Sırada öğrenci yoksa boş koy
                        siraBos = itemBos.format(deskNo)
                        classroom_array.append(siraBos)

                # Son kolon değilse sıradan sonra araya boşluk koy
                if colInd != len(oturmaDuzeni) - 1:
                    classroom_array.append(blank)
        classroom_array.append(containerCloser)
        get_footer(classroom)
        classroom_array.append(footer)            
        classroom_array.append(wrapperCloser)
        classroom_array.append(baseEnd)
        classroom_htmls.update({cName: "\n".join(classroom_array)})
        
    return classroom_htmls

def get_footer(classroom):
    return '<div class="footer"> Müdür adı: </div>'

def get_column_style(classroom):
    oturmaDuzeni = classroom["oturma_duzeni"]
    kacliText = classroom["kacli"]
    kacli = 1
    if kacliText == "2'li":
        kacli = 2
        
    columnCount = len(oturmaDuzeni)
    blankCount = columnCount - 1
    deskCount = 0
    for colIndex in range(len(oturmaDuzeni)):
        # İlk satırdaki sıra sayısı
        desk = oturmaDuzeni[colIndex][0]
        for deskNo in desk:
            deskCount += 1
    
    style = []
    for _ in range(deskCount):
        style.append("2fr ")
    
    # blank count ile gezinip araya blankPercen textleri sıkıştır
    tempStyle = []
    for index in range(len(style)):
        tempStyle.append(style[index])
        if index == len(style) - 1:
            break
        if index % kacli:
            tempStyle.append("1fr ")
            
    style = tempStyle

    styleText = "".join(style)
    totalCount = deskCount + blankCount
    return [styleText, totalCount]
                    
def get_row_style(classroom):
    oturmaDuzeni = classroom["oturma_duzeni"]
    longestRowLen = 0
    for colIndex in range(len(oturmaDuzeni)):
        currentLen = len(oturmaDuzeni[colIndex])
        print(f"CurrentLen: {currentLen}")
        print(f"LongestLen: {longestRowLen}")
        print()
        longestRowLen = currentLen if currentLen > longestRowLen else longestRowLen
    
    style = []
    for _ in range(longestRowLen):
        style.append("1fr ")
    
    styleText = "".join(style)
    return styleText                  

 
if __name__ == '__main__':
    ...