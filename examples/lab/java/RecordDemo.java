// Modern Java: record + switch expression (Java 16+/21).
public class RecordDemo {
    record Point(int x, int y) {}
    static String quadrant(Point p) {
        return switch (Integer.signum(p.x()) * 2 + Integer.signum(p.y())) {
            case 3 -> "I"; case -1 -> "II"; case -3 -> "III"; case 1 -> "IV"; default -> "on an axis";
        };
    }
    public static void main(String[] args) {
        Point p = new Point(3, -4);
        System.out.println(p + " is in quadrant " + quadrant(p));
    }
}
