__version__ = "0.0.1"

from typing import Dict, List, Optional
from dataclasses import dataclass
import requests
from abc import ABC, abstractmethod

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
class Guess:
    game_id: int
    num: int
    word: str
    score: str
    letter_info: Dict[str, List[int]]
    done: bool


class Client:
    base_url: str
    auth_code: str

    def __init__(self, auth_code: str, url: str = "https://wordle-tournaments.vercel.app/api") -> None:
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

class Solver(ABC):
    @abstractmethod
    def get_guess(
        self, 
        last_word_valid: bool,
        last_word_score: str,
        letter_info: Dict[str, List[int]]) -> str:
        pass 

class TournamentRunner:

    solver: Solver
    client: Client
    user_id: int

    def __init__(
        self,
        solver: Solver,
        auth_code: str,
        user_id: int,
        server_url: Optional[str] = None ) -> None:

        self.solver = solver
        self.user_id = user_id
        self.client = \
            Client(auth_code, server_url) \
            if server_url \
            else Client(auth_code) 

    def play_tournament(self) -> None:
        for seed in (range(2000)):
            game = self.client.create_game(self.user_id, seed)
            self._play_game(game.game_id)

    def _play_game(self, game_id: int) -> None:
        num_turns = 0
        done = False

        last_word_valid = True
        last_word_score = ""
        letter_info: Dict[str, List[int]] = {}

        while not done and num_turns < 100:
            num_turns += 1
            word = self.solver.get_guess(last_word_valid, last_word_score, letter_info)

            try:
                guess_result = self.client.create_guess(game_id, word)

            except requests.HTTPError as err:
                if err.response.status_code == 422:
                    last_word_valid = False
                    continue
                raise

            done = guess_result.done
            last_word_score = guess_result.score
            last_word_valid = True
            letter_info = guess_result.letter_info



            