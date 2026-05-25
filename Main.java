import java.util.ArrayList;
import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        ArrayList<String> words = new ArrayList<String>();
        Scanner scanner = new Scanner(System.in);
        String input;

        do
        {
            System.out.println("Enter a word, or an empty line to quit: ");
            input = scanner.nextLine();
            if (input.length() > 0) {
                insertAlphabetical(words, input);
                System.out.println("Words: " + words);
            }
        } while (input.length() > 0);
    }

    public static void insertAlphabetical(ArrayList<String> wordList, String newWord) {
        for(int i = 0; i < wordList.size(); i++) {
            if(wordList.get(i).compareTo(newWord) >= 0) {
                wordList.add(i, newWord);
                return;
            }
        }
        wordList.add(newWord);
    }
//        ArrayList<String> myList = new ArrayList<String>();
//
//        myList.add("Han Solo");
//        myList.add("Fei Qi");
//        myList.add("Cheef");
//        System.out.println(myList);
//
//        myList.add(0,"NSC");
//        System.out.println(myList);
//
//        int cheefIndex = myList.indexOf("Cheef");
//        System.out.println(myList.get(cheefIndex));
}
