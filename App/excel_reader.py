### excelReader.py
import xlrd, os, sys

def get_workbook_content(filePath):
    workbook = xlrd.open_workbook(filePath)
    worksheet = workbook.sheet_by_index(0)
    
    ogrencilerList = []
    for rowIdx in range(worksheet.nrows-3):
        cell = str(worksheet.cell_value(rowIdx, 0))
        if "Müdürlüğü" in cell:
            global studentClass
            text = cell.split(" - ")[1].split(" Şubesi")[0]
            grade = text.split(".")[0].strip()
            classs = text.split("/ ")[1]
            studentClass = grade + "/" + classs
            continue
        
        if not ("S" in cell) and not ("K" in cell):
            no = int(worksheet.cell_value(rowIdx, 1))       #no
            name = worksheet.cell_value(rowIdx, 3)          #ad
            surname = worksheet.cell_value(rowIdx, 7)       #soyad
            gender = worksheet.cell_value(rowIdx, 11)       #cinsiyet
            ogrenciList = [no, name, surname, gender, studentClass]
            ogrencilerList.append(ogrenciList)

    return ogrencilerList


if __name__ == "__main__":
    ogrencilerList = get_workbook_content(filePath="/home/yusuf/Masaüstü/Projects/Kelebek/Gerekliler/ogrenciler.xls")
    print(ogrencilerList)

