# File handling: write a file, count words per line.
with open("sample.txt", "w", encoding="utf-8") as f:
    f.write("MEDHA makes labs easy\nPython file handling\n")
with open("sample.txt", encoding="utf-8") as f:
    for i, line in enumerate(f, 1):
        print(i, len(line.split()), "words")
