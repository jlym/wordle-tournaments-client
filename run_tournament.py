from solvers import CharFreqSolver
from wordle_tournaments_client import TournamentRunner
import os
import sys

auth_code = os.getenv("AUTH_CODE")
if not auth_code:
    print("Expected AUTH_CODE environment variable to be set")
    sys.exit(1)

#auth_code="token"

solver = CharFreqSolver()
runner = TournamentRunner(solver, auth_code, "jeffrey_freq_solver_scrabble", "Jeffrey: frequency solver using scrabble list")
runner.play_tournament()
