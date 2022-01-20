from operator import not_
from . import wordle_solution_words, get_valid_scrabble_words, get_valid_wordle_words


def test_all_wordle_solutions_are_valid():
    valid_set = get_valid_wordle_words()
    for wordle_word in wordle_solution_words:
        assert wordle_word in valid_set


def test_all_scrabble_words_are_valid():
    valid_set = get_valid_wordle_words()
    for word in get_valid_scrabble_words():
        assert word in valid_set
    
