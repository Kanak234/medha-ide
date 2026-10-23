// Interface + polymorphism.
interface Shape { double area(); }
class Circle implements Shape { double r; Circle(double r) { this.r = r; } public double area() { return Math.PI * r * r; } }
class Rect implements Shape { double w, h; Rect(double w, double h) { this.w = w; this.h = h; } public double area() { return w * h; } }
public class Shapes {
    public static void main(String[] args) {
        Shape[] shapes = { new Circle(1), new Rect(2, 3) };
        for (Shape s : shapes) System.out.printf("%s area = %.2f%n", s.getClass().getSimpleName(), s.area());
    }
}
