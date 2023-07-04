import os

BASE_DIR = os.getcwd()
ActiveDir = os.path.join(BASE_DIR, "Active")
exam_paths = []

for exam_dir in os.listdir(ActiveDir):
    exam_path = os.path.join(ActiveDir, exam_dir)
    if os.path.isdir(exam_path):
        classroom_files = []
        grade_files = []

        for file in os.listdir(exam_path):
            if file.endswith(".html"):
                if file.endswith("A.html") or file.endswith("B.html"):
                    classroom_files.append(file)
                else:
                    grade_files.append(file)

        if classroom_files or grade_files:
            exam_paths.append(exam_path)

print(exam_paths)
print(os.listdir(ActiveDir))
