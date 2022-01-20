
from collections import Counter
from typing import List, Dict
from wordle_tournaments_client import Solver, get_valid_scrabble_words

def is_eligible(word: str, guess: str, score: str) -> bool:
    word_char_freq = Counter(word)

    # Process chars in the guess that are in the right position in the solution.
    for i in range(5):
        if score[i] != "g":
            continue

        guess_char = guess[i]       
        word_char = word[i]
        if guess_char != word_char:
            return False

        word_char_freq.subtract(word_char)

    # Process chars in the guess that are in the solution, but are in the wrong position.
    misplaced_chars = []
    for i in range(5):
        if score[i] != "y":
            continue
    
        if guess[i] == word[i]:
            return False

        misplaced_chars.append(guess[i])

    for misplaced_char in misplaced_chars:
        if word_char_freq[misplaced_char] == 0:
            return False
        word_char_freq.subtract(misplaced_char)

    # Process chars that are not in the solution.
    for i in range(5):
        if score[i] != "w":
            continue
        guess_char = guess[i]
        if word_char_freq[guess_char] > 0:
            return False

    return True


class CharFreqSolver(Solver):
    eligible_words: List[str]
    
    def __init__(self) -> None:
        self.eligible_words = get_valid_scrabble_words()

    def reset(self) -> None:
        self.eligible_words = get_valid_scrabble_words()

    def pick_word(self) -> str:
        char_counter: Counter[str] = Counter()
        for word in self.eligible_words:
            char_counter.update(word)

        best_score = 0
        best_word = ""

        for word in self.eligible_words:
            sum = 0
            for c in word:
                sum += char_counter[c]

            if sum > best_score:
                best_word = word
                best_score = sum

        return best_word

    def filter_eligible_words(self, guess: str, score: str):
        new_eligible_words: List[str] = []

        for eligible_word in self.eligible_words:
            if is_eligible(eligible_word, guess, score):
                new_eligible_words.append(eligible_word)

        self.eligible_words = new_eligible_words


    def get_guess(
        self,
        last_word: str,
        last_word_valid: bool,
        last_word_score: str) -> str:

        if not last_word_valid:
            raise ValueError("last word was not valid")

        if last_word:
            self.filter_eligible_words(last_word, last_word_score)

        return self.pick_word()

