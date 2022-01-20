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


@dataclass(frozen=True)
class User:
    user_id: int
    description: str


@dataclass(frozen=True)
class Game:
    game_id: int
    user_id: int
    seed: int
    solution: str
    letter_info: Dict[str, List[int]]
    num_guesses: int
    done: bool

@dataclass(frozen=True)
class CompleteGamesGuess:
    word: str
    score: str

@dataclass(frozen=True)
class CreateCompleteGameArgs:
    auth_code: str
    user_id: int
    seed: int
    solution: str
    done: bool
    guesses: List[CompleteGamesGuess]

@dataclass(frozen=True)
class Guess:
    game_id: int
    num: int
    word: str
    score: str
    letter_info: Dict[str, List[int]]
    done: bool


default_server_url = "https://wordle-tournaments.vercel.app/api"


class Client:
    base_url: str
    auth_code: str

    def __init__(self, auth_code: str, url: str = default_server_url) -> None:
        self.base_url = url
        self.auth_code = auth_code

    def create_user(self, description: str) -> User:
        params = {
            "auth_code": self.auth_code,
            "description": description,
        }
        url = f"{self.base_url}/user"
        resp = requests.post(url, params=params)
        resp.raise_for_status()

        json = resp.json()
        return User(json["user_id"], json["description"])

    def create_game(
        self,
        user_id: int,
        seed: Optional[int] = None,
        solution: Optional[str] = None) -> Game:

        params = {
            "auth_code": self.auth_code,
            "user_id": user_id,
        }
        if seed is not None:
            params["seed"] = seed
        if solution is not None:
            params["solution"] = solution

        url = f"{self.base_url}/game"
        resp = requests.post(url, params=params)
        resp.raise_for_status()

        json = resp.json()
        return Game(
            game_id=json["game_id"], 
            user_id=json["user_id"],
            seed=json["seed"],
            solution=json["solution"],
            letter_info=json["letter_info"],
            num_guesses=json["num_guesses"],
            done=json["done"]
        )

    def create_guess(
        self,
        game_id: int,
        word: str) -> Guess:

        params = {
            "auth_code": self.auth_code,
            "game_id": game_id,
            "word": word,
        }

        url = f"{self.base_url}/guess"
        resp = requests.post(url, params=params)
        resp.raise_for_status()

        json = resp.json()
        
        return Guess(
            game_id=json["game_id"], 
            num=1,
            word=json["word"],
            score=json["score"],
            letter_info=json["letter_info"],
            done=json["done"]
        )

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
            letter_info={},
            num_guesses=json["num_guesses"],
            done=json["done"])


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


class TournamentRunner:
    solver: Solver
    client: Client
    user_id: int
    seed_start: int
    seed_end: int
    max_num_turns: int


    def __init__(
        self,
        solver: Solver,
        auth_code: str,
        user_id: int,
        server_url: Optional[str] = default_server_url,
        seed_start: int = 0,
        seed_end: int = len(wordle_solution_words) - 1,
        max_num_turns: int = 20) -> None:

        self.solver = solver
        self.user_id = user_id
        self.client = \
            Client(auth_code, server_url) \
            if server_url \
            else Client(auth_code) 
        self.seed_start = seed_start
        self.seed_end = seed_end
        self.max_num_turns = max_num_turns


    def play_tournament(self) -> None:
        for seed in range(self.seed_start, self.seed_end + 1):
            game = self.client.create_game(self.user_id, seed)
            print(f"starting game with seed {seed}")
            self.solver.reset()
            self._play_game(game.game_id)


    def _play_game(self, game_id: int) -> None:
        num_turns = 0
        done = False

        last_guess = ""
        last_word_valid = True
        last_word_score = ""

        while not done and num_turns < self.max_num_turns:
            num_turns += 1
            word = self.solver.get_guess(last_guess, last_word_valid, last_word_score)

            try:
                guess_result = self.client.create_guess(game_id, word)

            except requests.HTTPError as err:
                if err.response.status_code == 422:
                    last_word_valid = False
                    continue
                raise

            last_guess = guess_result.word
            done = guess_result.done
            last_word_score = guess_result.score
            last_word_valid = True


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
        sol_char_counts = Counter(self.solution)
        score = ["w"] * 5

        for i, guess_c in enumerate(guess):
            sol_c = self.solution[i]

            if sol_c == guess_c:
                sol_char_counts.subtract(guess_c)
                score[i] = "g"

        for i, guess_c in enumerate(guess):
            sol_c = self.solution[i]

            if sol_c == guess_c:
                continue

            if sol_char_counts[guess_c] > 0:
                score[i] = "y"
                sol_char_counts.subtract(guess_c)
            
        return "".join(score)
