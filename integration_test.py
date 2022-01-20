from wordle_tournaments_client import Client, Solver, TournamentRunner, MemoryGameRunner
from typing import Dict, List, Optional, Tuple

def test_api():
    client = Client("token", "http://localhost:3000/api")

    # Create a user
    description = "python client integration test"
    user = client.create_user("name", description)
    assert user
    assert user.user_id > 0
    assert user.description == description


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
        last_guess_score: str) -> Tuple[str, int]:
        
        word = self.guesses[self.next_guess_index]
        self.next_guess_index = (self.next_guess_index + 1) % len(self.guesses)
            
        return word, 5


def test_tournament_solver():
    auth_code = "token"
    server_url = "http://localhost:3000/api"
    client = Client(auth_code, server_url)

    # Create a user
    user_name = "python client tournament test user"
    description = "python client tournament test user desc"

    solver = FixedGuessSolver(["bread", "cigar"])
    runner = TournamentRunner(solver, auth_code, user_name, description, server_url, 0, 0)
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

