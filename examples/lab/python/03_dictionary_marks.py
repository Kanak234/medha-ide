# Dictionary: subject → marks, then grade.
marks = {"Maths": 88, "C Programming": 92, "DBMS": 75}
for subject, m in marks.items():
    grade = "A" if m >= 85 else "B" if m >= 70 else "C"
    print(f"{subject:15} {m:3}  grade {grade}")
print("Total:", sum(marks.values()))
