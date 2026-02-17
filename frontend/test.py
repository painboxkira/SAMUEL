import random

def choose_word():
    words = ["python", "hangman", "programming", "computer", "developer", "keyboard", "monitor", "algorithm", "variable", "function", "software", "hardware", "internet", "browser", "website", "application"]
    return random.choice(words)

def display_hangman(lives):
    stages = [
        """
           -----
           |   |
           O   |
          /|\\  |
          / \\  |
               |
        ---------
        """,
        """
           -----
           |   |
           O   |
          /|\\  |
          /    |
               |
        ---------
        """,
        """
           -----
           |   |
           O   |
          /|\\  |
               |
               |
        ---------
        """,
        """
           -----
           |   |
           O   |
          /|   |
               |
               |
        ---------
        """,
        """
           -----
           |   |
           O   |
               |
               |
               |
        ---------
        """,
        """
           -----
           |   |
               |
               |
               |
               |
        ---------
        """,
        """
           -----
           |   |
               |
               |
               |
               |
        ---------
        """
    ]
    return stages[lives]

def play_hangman():
    word = choose_word()
    word_letters = set(word)
    guessed_letters = set()
    incorrect_guesses = set()
    lives = 6

    print("Let's play Hangman!")
    print(display_hangman(lives))
    print("_ " * len(word))

    while len(word_letters) > 0 and lives > 0:
        print(f"\nYou have {lives} lives left.")
        
        # Display current word state
        display_list = [letter if letter in guessed_letters else '_' for letter in word]
        print("Current word: " + " ".join(display_list))

        # Display incorrect guesses
        if incorrect_guesses:
            print("Incorrect guesses: " + ", ".join(sorted(list(incorrect_guesses))))
        
        guess = input("Guess a letter: ").lower()

        if len(guess) != 1 or not guess.isalpha():
            print("Invalid input. Please enter a single letter.")
        elif guess in guessed_letters or guess in incorrect_guesses:
            print(f"You've already guessed '{guess}'. Try again.")
        elif guess in word_letters:
            guessed_letters.add(guess)
            word_letters.remove(guess)
            print(f"Good guess! '{guess}' is in the word.")
        else:
            incorrect_guesses.add(guess)
            lives -= 1
            print(f"Sorry, '{guess}' is not in the word.")
        
        print(display_hangman(lives))

    if lives == 0:
        print(f"\nYou ran out of lives! The word was '{word}'.")
        print(display_hangman(0)) # Show final hangman
    else:
        print(f"\nCongratulations! You guessed the word '{word}'!")

if __name__ == "__main__":
    play_hangman()
    while True:
        play_again = input("Do you want to play again? (yes/no): ").lower()
        if play_again == 'yes':
            play_hangman()
        else:
            print("Thanks for playing!")
            break