__version__ = "0.0.3"

from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, DefaultDict, Tuple, Set
from collections import defaultdict, Counter
from dataclasses import dataclass
from abc import ABC, abstractmethod
import requests
from .wordle_solution_words import wordle_solution_words
from .wordle_valid_words import wordle_valid_words
from .scrabble_words import scrabble_words
from datetime import datetime


@dataclass(frozen=True)
class User:
    user_id: int
    description: str


@dataclass(frozen=True)
class CompleteGamesGuess:
    word: str
    score: str


@dataclass(frozen=True)
class Game:
    game_id: int
    user_id: int
    seed: int
    solution: str
    guesses: List[CompleteGamesGuess]
    status: int
    num_guesses: int



@dataclass(frozen=True)
class CreateCompleteGameArgs:
    auth_code: str
    user_id: int
    seed: int
    solution: str
    status: int
    guesses: List[CompleteGamesGuess]

@dataclass(frozen=True)
class Guess:
    game_id: int
    num: int
    word: str
    score: str
    guesses: List[CompleteGamesGuess]
    status: int


default_server_url = "https://wordle-tournaments.vercel.app/api"


class Client:
    base_url: str
    auth_code: str

    def __init__(self, auth_code: str, url: str = default_server_url) -> None:
        self.base_url = url
        self.auth_code = auth_code

    def create_user(self, name: str, description: str) -> User:
        params = {
            "auth_code": self.auth_code,
            "name": name,
            "description": description,
        }
        url = f"{self.base_url}/user"
        resp = requests.post(url, params=params)
        resp.raise_for_status()

        json = resp.json()
        return User(json["user_id"], json["description"])

    def create_complete_game(self, args: CreateCompleteGameArgs) -> Game:
        url = f"{self.base_url}/completegame"
        args_dict = asdict(args)
        resp = requests.post(url, json=args_dict)
        resp.raise_for_status()

        json = resp.json()
        return Game(
            game_id=json["game_id"], 
            user_id=json["user_id"],
            seed=json["seed"],
            solution=json["solution"],
            guesses=json["guesses"],
            num_guesses=json["num_guesses"],
            status=json["status"])


def get_valid_wordle_words() -> Set[str]:
    words = set()
    for word in wordle_solution_words:
        words.add(word)
    for word in wordle_valid_words:
        words.add(word)
    return words


def get_valid_scrabble_words() -> List[str]:
    valid_words_set = get_valid_wordle_words()
    return [w for w in scrabble_words if w in valid_words_set]


class Solver(ABC):
    @abstractmethod
    def get_guess(
        self,
        last_guess: str,
        last_guess_valid: bool,
        last_guess_score: str) -> str:
        pass 

    abstractmethod
    def reset(self):
        pass

def _score_guess(guess: str, solution: str) -> str:
    sol_char_counts = Counter(solution)
    score = ["w"] * 5

    for i, guess_c in enumerate(guess):
        sol_c = solution[i]

        if sol_c == guess_c:
            sol_char_counts.subtract(guess_c)
            score[i] = "g"

    for i, guess_c in enumerate(guess):
        sol_c = solution[i]

        if sol_c == guess_c:
            continue

        if sol_char_counts[guess_c] > 0:
            score[i] = "y"
            sol_char_counts.subtract(guess_c)
        
    return "".join(score)

class TournamentRunner:
    solver: Solver
    client: Client
    user_id: int
    seed_start: int
    seed_end: int
    max_num_turns: int
    auth_code: str
    wordle_solutions: List[str]
    user_description: str
    user_name: str

    def __init__(
        self,
        solver: Solver,
        auth_code: str,
        user_name: str,
        user_description: str,
        server_url: Optional[str] = default_server_url,
        seed_start: int = 0,
        seed_end: int = len(wordle_solution_words) - 1,
        max_num_turns: int = 20) -> None:

        self.auth_code = auth_code
        self.solver = solver
        self.user_description = user_description
        self.client = \
            Client(auth_code, server_url) \
            if server_url \
            else Client(auth_code) 
        self.seed_start = seed_start
        self.seed_end = seed_end
        self.max_num_turns = max_num_turns
        self.wordle_solutions = wordle_solution_words.copy()
        self.user_name = user_name


    def play_tournament(self) -> None:
        user = self.client.create_user(self.user_name, self.user_description)
        user_id = user.user_id

        for seed in range(self.seed_start, self.seed_end + 1):
            args = self._play_game(user.user_id, seed)
            game = self.client.create_complete_game(args)

            print(f"completed game, {user_id =}, {seed =}, game_id = {game.game_id}, time = {datetime.now()}")

            self.solver.reset()
            

    def _play_game(self, user_id: int, seed: int) -> CreateCompleteGameArgs:

        solution = self.wordle_solutions[seed]
        guesses: List[CompleteGamesGuess] = []

        num_guesses = 0
        won = False

        last_word_valid = True
        last_word_score = ""
        last_guess = ""

        while not won and num_guesses < self.max_num_turns:
            num_guesses += 1

            guess = self.solver.get_guess(last_guess, last_word_valid, last_word_score)
            last_guess = guess
            last_word_score = _score_guess(guess, solution)
            guesses.append(CompleteGamesGuess(guess, last_word_score))
            won = last_word_score == "ggggg"

        status = 1 if won else 2
        return CreateCompleteGameArgs(
            self.auth_code, user_id, seed, solution, status, guesses)


@dataclass(frozen=True)
class GameResult:
    won: bool
    num_guesses: int
    guesses: List[Tuple[str, str]]


class MemoryGameRunner:
    solution: str
    solver: Solver
    max_num_guesses: int
    letter_info: DefaultDict[str, List[int]]
    guesses: List[Tuple[str, str]]

    def __init__(self, solution: str, solver: Solver, max_num_guesses: int = 100):
        self.solution = solution
        self.solver = solver
        self.max_num_guesses = max_num_guesses
        self.letter_info = defaultdict(list)
        self.guesses = []
    
    def play_game(self) -> GameResult:
        num_guesses = 0
        won = False

        last_word_valid = True
        last_word_score = ""
        last_guess = ""

        while not won and num_guesses < self.max_num_guesses:
            num_guesses += 1

            guess = self.solver.get_guess(last_guess, last_word_valid, last_word_score)
            last_guess = guess
            last_word_score = self._score_guess(guess)
            self.guesses.append((guess, last_word_score))
            won = last_word_score == "ggggg"

        return GameResult(won, num_guesses, self.guesses)


    def _score_guess(self, guess: str) -> str:
        return _score_guess(guess, self.solution)
