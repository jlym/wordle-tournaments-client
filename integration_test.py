from cProfile import run
from wordle_tournaments_client import Client, Solver, TournamentRunner, MemoryGameRunner, wordle_words, words
from typing import Dict, List, Optional

def test_api():
    client = Client("token", "http://localhost:3000/api")

    # Create a user
    description = "python client integration test"
    user = client.create_user(description)
    assert user
    assert user.user_id > 0
    assert user.description == description

    # Create a game.
    game = client.create_game(user.user_id, solution="bread")
    assert game
    assert game.user_id == user.user_id
    assert game.game_id
    assert game.solution
    assert game.seed >= 0
    assert game.done == False
    assert game.letter_info is not None
    assert game.num_guesses == 0

    # Make a guess
    guess = client.create_guess(game.game_id, "bread")
    assert guess
    assert guess.game_id == game.game_id
    assert guess.word == "bread"
    assert guess.score == "ggggg"
    assert guess.done
    assert guess.letter_info == {
        "b": [1],
        "r": [2],
        "e": [3],
        "a": [4],
        "d": [5]
    }

class FixedGuessSolver(Solver):
    guesses: List[str]
    next_guess_index: int

    def __init__(self, guesses: List[str]):
        self.guesses = guesses
        self.next_guess_index = 0

    def get_guess(
        self,
        last_guess: str,
        last_guess_valid: bool,
        last_guess_score: str,
        letter_info: Dict[str, List[int]]) -> str:
        
        word = self.guesses[self.next_guess_index]
        self.next_guess_index = (self.next_guess_index + 1) % len(self.guesses)
            
        return word


def test_tournament_solver():
    auth_code = "token"
    server_url = "http://localhost:3000/api"
    client = Client(auth_code, server_url)

    # Create a user
    description = "python client tournament test user"
    user = client.create_user(description)

    solver = FixedGuessSolver(["bread", "cigar"])
    runner = TournamentRunner(solver, auth_code, user.user_id, server_url, 0, 0)
    runner.play_tournament()

def test_memory_game_runner():
    solver = FixedGuessSolver(["bread", "cigar"])
    runner = MemoryGameRunner("cigar", solver, 5)
    result = runner.play_game()
    
    assert result.won
    assert result.num_guesses == 2
    assert result.guesses == [("bread", "wywgw"), ("cigar", "ggggg")] 

def test_memory_game_runner_fail():
    solver = FixedGuessSolver(["bread", "cigar"])
    runner = MemoryGameRunner("joule", solver, 2)
    result = runner.play_game()
    
    assert not result.won
    assert result.num_guesses == 2

def test_all_wordle_words_in_all_words():
    all_words_set = set(words)
    for wordle_word in wordle_words:
        assert wordle_word in all_words_set
