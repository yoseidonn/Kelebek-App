from App import database
import os

# PATHS
BASE = os.path.join('Templates', 'ClassroomsTemplates', 'base.html')
HEAD = os.path.join('Templates', 'ClassroomsTemplates', 'head.html')
BODY = os.path.join('Templates', 'ClassroomsTemplates', 'body.html')
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
                
    head = HEAD
    with open(head, "r", encoding="utf-8") as headHTML:
        head = headHTML.read()
        head = head.split(SEPERATOR)
        masterExamName = examInfos[-1]
        tarih, ders = headerInfos[3], headerInfos[4]
        head.insert(1, f'{masterExamName} ({tarih} - {ders}) Oturma Düzeni')
        head = "".join(head)

    with open(BODY, "r", encoding="utf-8") as bodyHTML:
        body = bodyHTML.read()
        body = body.split(SEPERATOR)
        innerBodyHTML = get_html(classrooms, student_exam, headerInfos)
        body.insert(1, innerBodyHTML)
        body = "".join(body)

    with open(BASE, "r", encoding="utf-8") as baseHTML:
        base = baseHTML.read()
        base = base.split(SEPERATOR)
        base.insert(1, head)
        base.insert(2, body)
        fullHtml = "".join(base)

    fileName = "salon_oturma_duzenleri.html"
    examName = "_".join([examInfos[-1], examInfos[3], examInfos[4]])
    try:
        os.mkdir(os.path.join('Temp', examName))
    except FileExistsError:
        os.rmdir(os.path.join('Temp', examName))
        os.mkdir(os.path.join('Temp', examName))

    with open(os.path.join('Temp', examName, fileName), 'w', encoding='utf-8') as newFile:
        newFile.write(fullHtml)
    
    filePath = os.path.join('Temp', examName, fileName)
    htmlContent = fullHtml
    
    return (filePath, htmlContent)

def get_html(classrooms, student_exam, headerInfos):
    # student_exam = {2949: "11 MATEMATİK",
    #                 2999: "10 FİZİK"
    #                }
    
    wrapperOpener = '<div class="wrapper">'
    header = '<div class="headerText"> {}  EĞİTİM-ÖĞRETİM YILI {} {} ({} - {})<br> {} ÖĞRENCİ YOKLAMA ÇİZELGESİ <br> <br> </div>'
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
    
    text_array = []
    x = 0
    for cName in classrooms:
        classroom = classrooms[cName]
        oturmaDuzeni = classrooms[cName]["oturma_duzeni"]
        kacli = classrooms[cName]["kacli"]
        yon = classrooms[cName]["ogretmen_yonu"]
        ogretmenMasasiOgrenci = classrooms[cName]["ogretmen_masasi"]
        
        text_array.append(wrapperOpener)
        headerText = header.format(*headerInfos, cName)
        text_array.append(headerText)
        columnStyle, totalCount = get_column_style(classroom)
        rowStyle = get_row_style(classroom)
        container = containerOpener.format(columnStyle)#, rowStyle)
        text_array.append(container)
        
        longestRowCount = 0
        for col in oturmaDuzeni:
            if len(col) > longestRowCount:
                longestRowCount = len(col)

        #### Öğretmen masası yoksa boş, var ise oradaki öğrencinin bilgilerini seç.
        ogretmenMasasiItem = ogretmenMasasiBosItem
        ogretmenMasasiItemDouble = ogretmenMasasiBosDoubleItem
        if ogretmenMasasiOgrenci is not None:
            ogrenci = ogretmenMasasiOgrenci[1]
            sinavAdi = ogretmenMasasiOgrenci[0]
            sinif, no, cinsiyet, full_ad = ogrenci[4], ogrenci[0], ogrenci[3], ogrenci[1:3]

            ogretmenMasasiItem = ogretmenMasasiItem.format(sinavAdi, sinif, no, cinsiyet, full_ad)
            ogretmenMasasiItemDouble = ogretmenMasasiItemDouble.format(sinavAdi, sinif, no, cinsiyet, full_ad)

        #### Kutuları yerleştir
        if yon == "Solda":
            if kacli == "2'li":
                text_array.append(ogretmenMasasiItemDouble)
            else:
                text_array.append(ogretmenMasasiItem)
                text_array.append(blank)

            for _ in range(totalCount-2):
                text_array.append(blank)

        elif yon == "Sağda":
            for _ in range(totalCount-2):
                text_array.append(blank)

            if kacli == "2'li":
                text_array.append(ogretmenMasasiItemDouble)
            else:
                text_array.append(blank)
                text_array.append(ogretmenMasasiItem)
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
                        text_array.append(newItem)
                    text_array.append(newItem)
                    text_array.append(blank)
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
                        text_array.append(student)
                    else:
                        # Sırada öğrenci yoksa boş koy
                        siraBos = itemBos.format(deskNo)
                        text_array.append(siraBos)

                # Son kolon değilse sıradan sonra araya boşluk koy
                if colInd != len(oturmaDuzeni) - 1:
                    text_array.append(blank)
        text_array.append(containerCloser)
        text_array.append(footer)            
        text_array.append(wrapperCloser)
        
    html_text = " ".join(text_array)
    return html_text

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
    import shuffle
    classroom = database.get_all_classrooms("10/A")
    exam = {}
    shuffle.shuffle_and_get_classrooms()