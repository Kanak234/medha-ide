// Bubble sort on an int array.
import java.util.Arrays;
public class BubbleSort {
    public static void main(String[] args) {
        int[] a = {42, 7, 19, 3, 88, 25};
        for (int i = 0; i < a.length - 1; i++)
            for (int j = 0; j < a.length - 1 - i; j++)
                if (a[j] > a[j + 1]) { int t = a[j]; a[j] = a[j + 1]; a[j + 1] = t; }
        System.out.println(Arrays.toString(a));
    }
}
