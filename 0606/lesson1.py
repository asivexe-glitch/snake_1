file = open("0606/student.txt", "r", encoding="utf-8")
print(type(file))
content = file.read()
print(content)
file.close()
print(file.closed)

# =======================

with open("0606/student.txt", "r", encoding="utf-8") as file:
    content = file.read()

print(file.closed)

# =======================
import csv

with open("0606/考試分數 - 3年6班.csv", "r", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    print(type(reader))
    for row in reader:
        if int(row['數學']) >90:
            print(row['學生姓名'])