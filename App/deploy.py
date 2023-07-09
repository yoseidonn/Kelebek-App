from App.HtmlCreater import classrooms_html
from App import database, logs
from App.logs import logger

import random

class Place:
    def __init__(self, columnIndex, rowIndex, placeIndex):
        self.columnIndex = columnIndex
        self.rowIndex = rowIndex
        self.placeIndex = placeIndex

    def infos(self):
        return [self.columnIndex, self.rowIndex, self.placeIndex]
    
def distribute_students(exams, classroomsToUse, grades, rules):
    # Fetch classrooms from the database
    classrooms = database.get_name_given_classrooms(classroomsToUse)

    # Calculate the number of students in each grade
    grade_counts = {grade: len(students) for grade, students in grades.items()}

    # Calculate the number of students to be placed in each classroom
    classroom_counts = {}
    for grade, count in grade_counts.items():
        classroom_counts[grade] = count // len(classroomsToUse)

    for examName in exams:
        exam_grades = exams[examName]
        grades = database.get_grade_given_students(exam_grades)
        for gradeName in grades:
            students = grades[gradeName]
            # Bu şube için tüm dersliklere öğrencileri sırayla dağıt.
            while students:
                count = classroom_counts[gradeName]
                for classroomName in classrooms:
                    teacher_desk_empty = True
                    for _ in range(count):
                        if not students:
                            break
                        arrangement = classrooms[classroomName]["oturma_duzeni"]
                        places = get_places(arrangement)
                        print(f"Ogrenci sayisi: {len(students)}")
                        random_index = random.randint(0, len(students)) - 1
                        student = students[random_index]
                        print(student)
                        
                        is_placed = False
                        if teacher_desk_empty and rules["OgretmenMasasineOgrenciOturabilir"]:
                            if classrooms[classroomName]["ogretmen_masasi"] == None:
                                classrooms[classroomName]["ogretmen_masasi"] = student
                                grade_counts[gradeName] -= 1
                                students.remove(student)
                                print(f"Placed {student} into OGRETMEN MASASI")
                                is_placed = True
                                teacher_desk_empty = False

                        attempt = 20
                        while not is_placed and attempt:
                            random.shuffle(places)
                            placeObject = places[-1]
                            column_index, row_index, place_index = placeObject.infos()
                            desk_no = list(arrangement[column_index][row_index].keys())[place_index]
                            place = arrangement[column_index][row_index][desk_no]
                            
                            suitable = is_place_suitable(arrangement, place, placeObject, student, rules)
                            if suitable:
                                classrooms[classroomName]["oturma_duzeni"][column_index][row_index][desk_no] = student
                                grade_counts[gradeName] -= 1
                                students.remove(student)
                                print(f"Placed {student}")
                                print(f"Ogrenci sayisi: {len(students)}")
                                is_placed = True
                            print("===\n")
                            attempt -= 1
                     
    if is_there_any_student_left(grade_counts):
        return classrooms, False
    return classrooms

def get_places(oturma_duzeni: list) -> list[Place]:
    places = []
    for column_index, column in enumerate(oturma_duzeni):
        for desk_index, desk in enumerate(column):
            for place_index, desk_no in enumerate(desk):
                places.append(Place(column_index, desk_index, place_index))
    random.shuffle(places) 
    return places

def is_place_suitable(arrangement: list, place, placeObject: Place, student: tuple or list, rules: dict) -> bool:
    """_summary_
    Args:
        arrangement (list): The list that contains all the column objects
        place (Noneortupleorlist): The selected place object
        student (tupleorlist): [] or (0: number, 1: name, 2: surname, 3: gender, 4:grade)
        rules (dict): {
                        "SideBySideSitting" -> Ayni sinava giren ogrenciler yan yana oturabilir,
                        "BackToBackSitting" -> “““ ogrenciler arka arkaya oturabilir,
                        "CrossByCrossSitting" -> “““ grenciler capraz oturabilir,
                        "KizErkekYanYanaOturabilir" -> Kız erkek yan yana oturabilir,
                        "OgretmenMasasineOgrenciOturabilir" -> Ogrenciler ogretmen masasina oturabilir.
                    }

    Returns:
        bool: Ogrenci oturabilir ise True, oturamaz ise False dondurur
    """
    
    return True
    if place:
        return False
    
    # Eger tum kurallar 1 ise, ogretmen masasi kurali haric
    if all(rules[:-1]):
        return True
    
    side_by_side, back_to_back, cross_by_cross, different_genders, teacher_desk = rules.values()
    current_col, current_row, current_placeindex = placeObject.infos()
    current_side = "RIGHT" if list(arrangement[current_col][current_row].keys())[current_placeindex] else "LEFT"
    current_gender, current_grade = student[3], student[4].split("/")[0]

    if not side_by_side:
        if current_side == "LEFT":
            try:
                left_student = list(arrangement[current_col-1][current_row].values())[1]
                if not left_student:
                    print(1)
                    return True
                left_student_grade = left_student[4].split("/")[0]
                if current_grade == left_student_grade:
                    print(2)
                    return False
            except Exception as e:
                print(e)
        
        elif current_side == "RIGHT":
            try:
                left_student = list(arrangement[current_col][current_row].values())[0]
                if not left_student:
                    print(3)
                    return True
                left_student_grade = left_student[4].split("/")[0]
                if current_grade == left_student_grade:
                    print(4)
                    return False
            except Exception as e:
                print(e)
            
    if not back_to_back:
        if current_side == "LEFT":
            try:
                fore_student = list(arrangement[current_col][current_row+1].values())[0]
                if not fore_student:
                    print(5)
                    return True
                fore_student_grade = fore_student[4].split("/")[0]
                if current_grade == fore_student_grade:
                    print(6)
                    return False
            except Exception as e:
                print(e)
            
        elif current_side == "RIGHT":
            try:
                fore_student = list(arrangement[current_col][current_row+1].values())[1]
                if not fore_student:
                    return True
                fore_student_grade = fore_student[4].split("/")[0]
                if current_grade == fore_student_grade:
                    return False
            except Exception as e:
                print(e)

    # Capraz 
    if not cross_by_cross:
        if current_side == "LEFT":
            try:
                fore_left_student = list(arrangement[current_col-1][current_row+1].values())[1]
                if not fore_left_student:
                    return True
                fore_left_student_grade = fore_left_student[4].split("/")[0]
                if current_grade == fore_left_student_grade:
                    return False
            except Exception as e:
                print(e)
        
        elif current_side == "RIGHT":
            try:
                fore_left_student = list(arrangement[current_col][current_row+1].values())[1]
                if not fore_left_student:
                    return True
                fore_left_student_grade = fore_left_student[4].split("/")[0]
                if current_grade == fore_left_student_grade:
                    return False
            except Exception as e:
                print(e)
        
    # Cinsiyet
    if not different_genders:
        if current_side == "LEFT":
            try:
                right_student = list(arrangement[current_col][current_row].values())[1]
                if not right_student:
                    return True
                right_student_gender = right_student[3]
                if current_gender == right_student_gender:
                    return False
            except Exception as e:
                print(e)
        
        elif current_side == "RIGHT":
            try:
                left_student = list(arrangement[current_col][current_row+1].values())[0]
                if not left_student:
                    return True
                left_student_gender = left_student[3]
                if current_gender == left_student_gender:
                    return False
            except Exception as e:
                print(e)
    
    return True

def is_there_any_student_left(classroomCounts: dict):
    counts = [count for gradeName, count in classroomCounts.items()]
    if any(counts):
        return True
    return False

def print_classrooms(classrooms: dict or tuple):
    key = 0
    if isinstance(classrooms, tuple):
        key = 1
        classrooms = classrooms[0]
    
    for classroomName, classroom in classrooms.items():
        print(f"{classroomName}:")
        print(f"\tOgretmen masasi:", classroom["ogretmen_masasi"], "\n")
        columns = classroom["oturma_duzeni"]
        for column in columns:
            for desk in column:
                print(f"\t{desk}")
            print("\t---")
        print()
    if key:
        logger.error("\t\t...Yeterli yer yok...\t\t")

def distribute(exam) -> dict or bool:
    exams = exam.exams
    classroomsToUse = exam.classroomNames
    grades = database.get_grade_given_students(exams)
    rules = exam.rules
    return distribute_students(exams, classroomsToUse, grades, rules)

if __name__ == '__main__':
    #from tests import sample_exams
    #exam = sample_exams[0]
    
    #classrooms_result = distribute(exam)
    #print_classrooms(classrooms_result)
    
    #classrooms_html.create(exam_infos, classrooms_result, exam.exams)
    pass