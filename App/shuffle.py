import random
from App import database

def check(oturmaDuzeni: list, ogrenciler: dict, kacli: str, cinsiyet: str, sinavAdi: str, konum: list, karma: str, kizErk: bool):
    TAM_KARMA = 'Tam karma: Yan yana ve çapraz oturmasın'
    ALTERNATIF_KARMA = 'Alternatif karma: Yan yana oturmasın (Sayıya göre çapraz oturabilir)'
    EN_AZ_KARMA = 'En az karma (Sayıya göre yan yana veya çapraz oturabilirler)'
    colInd, rowInd, desk, deskNo = konum
    
    crossStudents = []
    sideStudents = []
    nextToStudent = None
    if kacli == "1'li":
        try:
            leftDesk = oturmaDuzeni[colInd-1][rowInd]
            key = list(leftDesk.keys())[0]
            student = leftDesk[key]
            if student is not None:
                sideStudents.append(student)
        except Exception as e:
            pass
            #print(e)
            
        try:
            rightDesk = oturmaDuzeni[colInd+1][rowInd]
            key = list(rightDesk.keys())[0]
            student = rightDesk[key]
            if student is not None:
                sideStudents.append(student)
        except Exception as e:
            pass
            #print(e)
        
    elif kacli == "2'li":
        solSag = list(desk.keys()).index(deskNo)
        if solSag:
            #Sağ
            try:
                leftForeDesk = oturmaDuzeni[colInd][rowInd+1]
                key = list(leftForeDesk.keys())[0]
                student = leftForeDesk[key]
                if student is not None:
                    crossStudents.append(student)
            except Exception as e:
                pass
                #print(e)
                
            try:
                leftBackDesk = oturmaDuzeni[colInd][rowInd-1]
                key = list(leftBackDesk.keys())[0]
                student = leftBackDesk[key]
                if student is not None:
                    crossStudents.append(student)
            except Exception as e:
                pass
                #print(e)

            try:
                leftDesk = oturmaDuzeni[colInd][rowInd]
                key = list(leftDesk.keys())[0]
                student = leftDesk[key]
                if student is not None:
                    sideStudents.append(student)
                    nextToStudent = student
            except Exception as e:
                pass
                #print(e)

            try:
                rightDesk = oturmaDuzeni[colInd+1][rowInd]
                key = list(rightDesk.keys())[0]
                student = rightDesk[key]
                if student is not None:
                    sideStudents.append(student)
            except Exception as e:
                pass
                #print(e)

        else:
            try:
                rightForeDesk = oturmaDuzeni[colInd][rowInd+1]
                key = list(rightForeDesk.keys())[1]
                student = rightForeDesk[key]
                if student is not None:
                    crossStudents.append(student)
            except Exception as e:
                pass
                #print(e)

            try:
                rightBackDesk = oturmaDuzeni[colInd][rowInd-1]
                key = list(rightBackDesk.keys())[1]
                student = rightBackDesk[key]
                if student is not None:
                    crossStudents.append(student)
            except Exception as e:
                pass
                #print(e)
                
            try:
                leftDesk = oturmaDuzeni[colInd-1][rowInd]
                key = list(leftDesk.keys())[1]
                student = leftDesk[key]
                if student is not None:
                    sideStudents.append(student)
            except Exception as e:
                pass
                #print(e)
            
            try:
                rightDesk = oturmaDuzeni[colInd+1][rowInd]
                key = list(rightDesk.keys())[0]
                student = rightDesk[key]
                if student is not None:
                    sideStudents.append(student)
                    nextToStudent = student
            except Exception as e:
                pass
                #print(e)
                
            
    if karma == TAM_KARMA and not kizErk:
        for student in sideStudents:
            if ogrenciler[student] == sinavAdi:
                return False
            
        for student in crossStudents:
            if ogrenciler[student] == sinavAdi:
                return False
        
            
    elif karma == TAM_KARMA and kizErk:
        for student in sideStudents:
            if (ogrenciler[student] == sinavAdi):
                return False
            
        for student in crossStudents:
            if (ogrenciler[student] == sinavAdi):
                return False
            
        if nextToStudent is not None:
            if nextToStudent[3] != cinsiyet:
                return False

    elif karma == ALTERNATIF_KARMA and not kizErk:
        for student in sideStudents:
            if ogrenciler[student] == sinavAdi:
                return False
            
    elif karma == ALTERNATIF_KARMA and kizErk:
        for student in sideStudents:
            if (ogrenciler[student] == sinavAdi):
                return False
            
        if nextToStudent is not None:
            if nextToStudent[3] != cinsiyet:
                return False
        
    elif karma == EN_AZ_KARMA and not kizErk:
        pass

    elif karma == EN_AZ_KARMA and kizErk:
        solSag = list(desk.keys()).index(deskNo)
        if solSag:
            #Sağ
            key = list(desk.keys())[0]
            if desk[key][3] != cinsiyet:
                return False

    return True

def get_students_by_exam(exams):
    studentsBackup = {}
    for eName in exams:
        for gradeName in exams[eName]:
            result = database.get_all_students(grade = gradeName)
            for student in result:
                studentsBackup.update({student: eName})
                
    return studentsBackup

def shuffle_and_get_classrooms(exam):
    exams = exam.exams
    classroomNames = exam.classroomNames
    algorithmName = exam.algorithmName
    optionList = exam.optionList
    studentsBackup = get_students_by_exam(exams)
    classroomsBackup = database.get_name_given_classrooms(classroomNames) # This function returns a dictionary which has classrooms consists of informations and layout, named "oturma_duzeni".
    algorithmIndex = algorithmNames[algorithmName]

    karma = algorithmName
    kizErk = True if optionList[0] else False
    omy = optionList[1]

    tried = 1
    ogretmenMasasi = None
    students = studentsBackup
    while len(students) != 0 and tried <= 5:
        print("----try-------")
        classroomsWithStudents = dict()
        classrooms = classroomsBackup.copy()
        students = studentsBackup.copy()
        for cName in classrooms:
            kacli = classrooms[cName]['kacli']
            ogretmenYonu = classrooms[cName]['ogretmen_yonu']
            if omy:
                keys = list(students.keys())
                random.shuffle(keys)
                random.shuffle(keys)
                random.shuffle(keys)
                try:
                    key = keys[-1]
                    student = key
                    eName = students[key]
                    ogretmenMasasi = [eName, student]
                    students.pop(key)
                except IndexError:
                    pass
                    
            oturmaDuzeni = classrooms[cName]['oturma_duzeni']
            for colIndex in range(len(oturmaDuzeni)):
                    for rowIndex in range(len(oturmaDuzeni[colIndex])):
                        desk = oturmaDuzeni[colIndex][rowIndex] #Dictionary
                        for deskNo in desk:
                            keys = list(students.keys())
                            random.shuffle(keys)
                            random.shuffle(keys)
                            random.shuffle(keys)
                            print(len(students))    
                            for key in keys:
                                student = key
                                cinsiyet = student[3]
                                sinavAdi = students[key]
                                location = [colIndex, rowIndex, desk, deskNo]
                                isPassed = check(oturmaDuzeni, studentsBackup, kacli, cinsiyet, sinavAdi, location, karma, kizErk)
                                if isPassed:
                                    desk.update({deskNo: student})
                                    students.pop(student)
                                    print(student, colIndex, rowIndex, deskNo)
                                    break

            classroomsWithStudents.update({cName: {"oturma_duzeni": oturmaDuzeni, "ogretmen_masasi": ogretmenMasasi, "kacli": kacli, "ogretmen_yonu": ogretmenYonu}})
        tried += 1   
        print(students)
    
    if len(students) == 0:
        return classroomsWithStudents
    
    else:
        return False
    
    
algorithmNames = {'Tam karma: Yan yana ve çapraz oturmasın': 0,
                  'Alternatif karma: Yan yana oturmasın (Sayıya göre çapraz oturabilir)': 1,
                  'En az karma (Sayıya göre yan yana veya çapraz oturabilirler)': 2}