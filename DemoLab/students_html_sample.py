import weasyprint

def create_html_table(grade_dict, css):
    html = "<html>\n<head>\n"
    html += css
    html += "</head>\n<body>\n"
    for grade_name, students in grade_dict.items():
        html += f"<table>\n<caption>Table {grade_name}</caption>\n"
        html += "<tr>\n<th>Name</th>\n<th>Classroom and Desk</th>\n</tr>\n"
        for student in students:
            print(student)
            html += "<tr>\n"
            html += f"<td>{student[0]}</td>\n"
            html += f"<td>{student[1]}</td>\n"
            html += "</tr>\n"
        html += "</table>\n"
    html += "</body>\n</html>"
    
    with open("output.html", "w") as file:
        file.write(html)

def html_to_pdf(html_path, pdf_path):
    # create a PDF file from the HTML file
    weasyprint.HTML(html_path).write_pdf(pdf_path)

if __name__ == "__main__":
    grade_dict = {
    "11/A": [("Alice", "11/A 5"), ("Bob", "11/A 12"), ("Charlie", "11/A 3"),
             ("Daisy", "11/A 8"), ("Eva", "11/A 17"), ("Frank", "11/A 1"),             
             ("George", "11/A 22"), ("Holly", "11/A 19"), ("Ivan", "11/A 25")],

    "11/B": [("Kevin", "11/B 4"), ("Liam", "11/B 9"), ("Maggie", "11/B 14"),              
             ("Nathan", "11/B 11"), ("Olivia", "11/B 6"), ("Parker", "11/B 15"),              
             ("Quincy", "11/B 20"), ("Randy", "11/B 19"), ("Steve", "11/B 21")],

    "11/C": [("Ursula", "11/C 2"), ("Victor", "11/C 7"), ("Wendy", "11/C 10"),              
             ("Xander", "11/C 16"), ("Yvonne", "11/C 13"), ("Zach", "11/C 18"),             
             ("Ava", "11/C 24"), ("Benny", "11/C 26"), ("Carla", "11/C 28")]
}
    with open("css", "r", encoding="utf-8") as file:
        css = file.read()
        
    create_html_table(grade_dict, css)
    html_to_pdf("output.html", "output.pdf")