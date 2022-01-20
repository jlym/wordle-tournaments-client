from solvers import CharFreqSolver, FixedStartingWordThenArbirarySolver
from wordle_tournaments_client import TournamentRunner
import os
import sys

auth_code = os.getenv("AUTH_CODE")
if not auth_code:
    print("Expected AUTH_CODE environment variable to be set")
    sys.exit(1)


solver = FixedStartingWordThenArbirarySolver("solar")
runner = TournamentRunner(solver, auth_code, "jeffrey_fixed_starting_wordle_solns", "Starting word: solar, Dictionary: Wordle solutions")
runner.play_tournament()
