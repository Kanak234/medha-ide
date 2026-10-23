// Exception handling: divide two numbers safely.
import java.util.Scanner;
public class ExceptionDemo {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        System.out.print("Enter two integers: ");
        try {
            int a = sc.nextInt(), b = sc.nextInt();
            System.out.println("a / b = " + (a / b));
        } catch (ArithmeticException e) {
            System.out.println("Cannot divide by zero");
        } catch (java.util.InputMismatchException e) {
            System.out.println("Please type whole numbers");
        }
    }
}
