// Class, constructor, toString and an array of objects.
public class Student {
    private final String name;
    private final int marks;
    Student(String name, int marks) { this.name = name; this.marks = marks; }
    @Override public String toString() { return name + " (" + marks + ")"; }
    public static void main(String[] args) {
        Student[] list = { new Student("Asha", 81), new Student("Ravi", 74), new Student("Kanak", 92) };
        Student top = list[0];
        for (Student s : list) if (s.marks > top.marks) top = s;
        System.out.println("Topper: " + top);
    }
}
