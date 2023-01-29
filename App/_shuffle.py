from .HtmlCreater import classrooms_html
from .Structs import exam_struct
from . import database
import os, sys, random


algorithmNames = [
    "Tam karma: Yan yana ve çapraz oturmasın",
    "Alternatif karma: Yan yana oturmasın (Çapraz oturabilir!)",
    "Karma yok (Yan yana ve çapraz oturabilirler!)"]

def apply_algorithm(exams, classrooms, algorithmName, optionList):
    studentsBackup = []
    for eName in exams:
        for gradeName in exams[eName]:
            result = database.get_all_students(grade = gradeName)
            studentsBackup.extend(result)
            
    random.shuffle(studentsBackup)
    
    if algorithmName == algorithmNames[0]:
        students = studentsBackup.copy()
        tries = 0
        while len(students) != 0 and tries < 5:
            students = students.copy()
            for cName in classrooms:
                oturmaDuzeni = classrooms[cName]["oturma_duzeni"]
                for colIndex in range(len(oturmaDuzeni)):
                    for rowIndex in range(len(oturmaDuzeni[colIndex])):
                        desk = oturmaDuzeni[colIndex][rowIndex] #Dictionary
                        for deskNo in desk:
                            if classrooms[cName]["kacli"] == "1'li":
                                try:
                                    student = students[-1]
                                except:
                                    return classrooms
                                try:
                                    prevDesk = oturmaDuzeni[colIndex - 1][rowIndex] #Sol masadaki öğrenciyi sözlükten buluyor
                                    prevGrade = list(prevDesk.values())[0][4].split("/")[0] #Son öğrencinin 9/10/11 yani grade'sini kontrol et """""""" TO DO -> Sınıfını değil de katıldığı sınavı kontrol et
                                    nextDesk = oturmaDuzeni[colIndex + 1][rowIndex] #Sol masadaki öğrenciyi sözlükten buluyor
                                    nextGrade = list(prevDesk.values())[0][4].split("/")[0] #Son öğrencinin 9/10/11 yani grade'sini kontrol et """""""" TO DO -> Sınıfını değil de katıldığı sınavı kontrol et
                                except:
                                    prevGrade = "Yok"
                                    nextGrade = "Yok"

                                studentGrade = student[4].split("/")[0]
                                #print(prevGrade != studentGrade)
                                if prevGrade != studentGrade:
                                    desk.update({deskNo: student})
                                    students.pop(-1)
                                    
                            else:
                                try:
                                    student = students[-1]
                                except:
                                    return classrooms
                                try:
                                    studentIndex = list(desk.keys()).index(deskNo)
                                    if studentIndex == 0:
                                        prevDesk = oturmaDuzeni[colIndex - 1][rowIndex]
                                        prevGrade = list(prevDesk.values())[1][4].split("/")[0] #Son öğrencinin 9/10/11 yani grade'sini kontrol et """""""" TO DO -> Sınıfını değil de katıldığı sınavı kontrol et
                                    else:
                                        prevChairKey = list(desk.keys())[0]
                                        prevStudent = desk[prevChairKey]
                                        prevGrade = prevStudent[4].split("/")[0] #Son öğrencinin 9/10/11 yani grade'sini kontrol et """""""" TO DO -> Sınıfını değil de katıldığı sınavı kontrol et
                                except:
                                    prevGrade = "Yok"
                                    nextGrade = "Yok"
                                
                                studentGrade = student[4].split("/")[0]
                                #print(prevGrade, studentGrade)
                                if prevGrade != studentGrade:
                                    desk.update({deskNo: student})
                                    students.pop(-1)
            tries += 1
            #print(students)
                            
        if len(students) != 0:
            print(len(students))
            return False

    elif algorithmName == algorithmNames[1]:
        pass
    
    elif algorithmName == algorithmNames[2]:
        students = studentsBackup.copy()
        for cName in classrooms:
            oturmaDuzeni = classrooms[cName]["oturma_duzeni"]
            for colIndex in range(len(oturmaDuzeni)):
                for rowIndex in range(len(oturmaDuzeni[colIndex])):
                    desk = oturmaDuzeni[colIndex][rowIndex]
                    for deskNo in desk:
                        try:
                            student = students[-1]
                        except:
                            [print(student) for student in students]
                            return classrooms
                        students.pop(-1)
                        desk[deskNo] = student
    return classrooms
    
def shuffle(exam):
    exams = exam.exams
    classroomNames = exam.classroomNames
    algorithmName = exam.algorithmName
    optionList = exam.optionList

    # EACH CLASSROOM IS A DICT AND EACH "OTURMA DUZENI" IS A MATRIS
    classrooms = database.get_name_given_classrooms(classroomNames) #USEN FOR APPLY_ALGORITHM FUNCTION
    classrooms = apply_algorithm(exams, classrooms, algorithmName, optionList) #PLACED STUDENTS AND RETURNED A DICTIONARY WHICH IS CONSISTED BY CLASSROOMS

    #show(classrooms)
    if classrooms:
        return classrooms
    else:
        return False

def show(classrooms):
    for cName in classrooms:
            oturmaDuzeni = classrooms[cName]["oturma_duzeni"]
            print(cName)
            for colIndex in range(len(oturmaDuzeni)):
                for rowIndex in range(len(oturmaDuzeni[colIndex])):
                    desk = oturmaDuzeni[colIndex][rowIndex]
                    for deskNo in desk:
                        print(deskNo, ":",desk[deskNo], end=" ")
                    print()
                print("------")
            print()

            
if __name__ == "__main__":
    from HtmlCreater import classrooms_html
    exams = {"10 MAT": {
                "gradeNames": ["10/D"],
                "items": [],
            },
             "11 EDB": {
                "gradeNames": ["11/A", "11/B"]
             }
    }
    classroomNames = ["9/A", "9/D", "10/C", "10/D"]
    algName = algorithmNames[0]
    exam = exam_struct.Exam(exams = exams, classroomNames = classroomNames, algorithmName = algName, optionList = [False, False])
    
    sonuc = shuffle(exam)
    show(sonuc)
    classrooms_html.create("cikti", sonuc, exam.exams)