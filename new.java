import java.util.Scanner;

public class FirstJavaProgram {
    public static void main(String[] args) {
        // Create a Scanner object to read user input
        Scanner scanner = new Scanner(System.in);

        // Prompt the user to enter their name
        System.out.print("Enter your name: ");

        // Read the user's input
        String name = scanner.nextLine();

        // Greet the user with a personalized message
        System.out.println("Hello, " + name + "! This is your first Java program.");

        // Close the scanner to avoid resource leaks
        scanner.close();
    }
}
