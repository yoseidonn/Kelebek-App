import random
from App import database

def check(oturmaDuzeni: list, ogrenciler: dict, kacli: str, cinsiyet: str, sinavAdi: str, konum: list, karma: str, kizErk: bool):
    TAM_KARMA = 'Tam karma: Yan yana ve çapraz oturmasın'
    ALTERNATIF_KARMA = 'Alternatif karma: Yan yana oturmasın (Sayıya göre çapraz oturabilir)'
    EN_AZ_KARMA = 'En az karma (Sayıya göre yan yana veya çapraz oturabilirler)'
    colInd, rowInd, desk, deskNo = konum
            
    if karma == TAM_KARMA and not kizErk:
        pass
            
    elif karma == TAM_KARMA and kizErk:
        pass

    elif karma == ALTERNATIF_KARMA and not kizErk:
        pass
            
    elif karma == ALTERNATIF_KARMA and kizErk:
        pass
           
    elif karma == EN_AZ_KARMA and not kizErk:
        pass

    elif karma == EN_AZ_KARMA and kizErk:
        pass
    
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
        from .shuffle import show
        show(classroomsWithStudents)
        print()
        return classroomsWithStudents
    
    else:
        return False
    
    
algorithmNames = {'Tam karma: Yan yana ve çapraz oturmasın': 0,
                  'Alternatif karma: Yan yana oturmasın (Sayıya göre çapraz oturabilir)': 1,
                  'En az karma (Sayıya göre yan yana veya çapraz oturabilirler)': 2}