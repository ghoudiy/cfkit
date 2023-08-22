import java.util.Scanner;

public class GreetingProgram {
    public static void main(String[] args) {
        // Create a Scanner object to read input from the console
        Scanner scanner = new Scanner(System.in);

        // Prompt the user for their name
        System.out.print("Enter your name: ");

        // Read the user's name
        String userName = scanner.nextLine();

        // Greet the user
        System.out.println("Hello, " + userName + "!");

        // Close the scanner to release resources
        scanner.close();
    }
}
