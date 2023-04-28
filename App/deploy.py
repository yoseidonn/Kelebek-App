from App.HtmlCreater import classrooms_html
from App import database
import random

class Place:
    def __init__(self, columnIndex, rowIndex, placeIndex):
        self.columnIndex = columnIndex
        self.rowIndex = rowIndex
        self.placeIndex = placeIndex

    def infos(self):
        return (self.columnIndex, self.rowIndex, self.placeIndex)
    
def distribute_students(exams, classroomsToUse, grades, rules):
    # Fetch classrooms from the database
    classrooms = database.get_name_given_classrooms(classroomsToUse)

    # Calculate the number of students in each grade
    grade_counts = {grade: len(students) for grade, students in grades.items()}

    # Calculate the number of students to be placed in each classroom
    classroom_counts = {}
    for grade, count in grade_counts.items():
        classroom_counts[grade] = count // len(classroomsToUse)

    # Calculate the remaining students after distributing equally
    extra_student_counts = {}
    for grade, count in grade_counts.items():
        extra_student_counts[grade] = count % len(classroomsToUse)

    for exam in exams:
        exam_grades = exams[exam]
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
                        student = students[-1]
                        print(student)
                        
                        is_placed = False
                        if teacher_desk_empty and rules[-1]:
                            if classrooms[classroomName]["ogretmen_masasi"] == None:
                                classrooms[classroomName]["ogretmen_masasi"] = student
                                grade_counts[gradeName] -= 1
                                students.remove(student)
                                print(f"Placed {student} into OGRETMEN MASASI")
                                is_placed = True
                                teacher_desk_empty = False

                        attempt = 5
                        while not is_placed and attempt:
                            random.shuffle(places)
                            placeObject = places[-1]
                            column_index, row_index, place_index = placeObject.infos()
                            desk_no = list(arrangement[column_index][row_index].keys())[place_index]
                            place = arrangement[column_index][row_index][desk_no]
                            
                            if is_place_suitable(arrangement, place, student, rules):
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

def is_place_suitable(arrangement: list, place: None or tuple or list, student: tuple or list, rules: list) -> bool:
    """_summary_
    Args:
        arrangement (list): The list that contains all the column objects
        place (Noneortupleorlist): The selected place which contains a student or None
        student (tupleorlist): The student that needs to be placed into that place which is a list or tuple
        rules (list): [
                        Ayni sinava giren ogrenciler yan yana oturabilir,
                                “““       ogrenciler arka arkaya oturabilir,
                                “““       grenciler capraz oturabilir,
                        Iki farkli cinsiyetten herhangi iki ogrenci yan yana oturabilir,
                        Kontrol edilen ogrenci ogretmen masasina oturabilir.
                    ]

    Returns:
        bool: Ogrencinin oturabilir ise True, oturamaz ise False dondurur
    """
    # Returns False if the place is already taken.
    
    if place:
        return False
    
    # Eger tum kurallar 1 ise, ogretmen masasi kurali haric
    if all(rules[:-1]):
        return True
    
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
        print("\t\t...Yeterli yer yok...\t\t")

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