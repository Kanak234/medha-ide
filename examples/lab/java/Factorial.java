// Factorial with a loop and with recursion (long overflows after 20!).
import java.util.Scanner;
public class Factorial {
    static long rec(int n) { return n <= 1 ? 1 : n * rec(n - 1); }
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        System.out.print("Enter n: ");
        int n = sc.nextInt();
        long f = 1;
        for (int i = 2; i <= n; i++) f *= i;
        System.out.println("Loop: " + f + "  Recursion: " + rec(n));
    }
}
