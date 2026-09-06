// MEDHĀ STUDIO — Java Stack & Queue Demo
import java.util.Stack;

public class Main {
    public static void main(String[] args) {
        System.out.println("[MEDHĀ Java Demo] Pushing elements to Stack (LIFO)...");

        Stack<Integer> stack = new Stack<>();
        stack.push(10);
        stack.push(25);
        stack.push(42);
        stack.push(88);

        System.out.println("Stack Elements: " + stack);
        System.out.println("Top Element (Peek): " + stack.peek());

        // Emit live __DSA__ JSON Payload for Real-Time Graphical Canvas
        System.out.println("__DSA__:{\"type\": \"stack\", \"name\": \"LIFO_Stack\", \"nodes\": [10, 25, 42, 88]}");
    }
}
