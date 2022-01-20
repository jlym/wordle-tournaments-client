from solvers import CharFreqSolver, is_eligible, FixedStartingWordThenArbirarySolver
from wordle_tournaments_client import MemoryGameRunner

def test_is_eligible():
    assert is_eligible("apple", 'aeaea', 'gywww')

    assert is_eligible("ccccc", "bbbbb", "wwwww")
    assert not is_eligible("ccccb", "bbbbb", "wwwww")

    assert is_eligible("aaaaa", "aaaaa", "ggggg")
    assert not is_eligible("aaaab", "aaaaa", "ggggg")

    assert is_eligible("baaac", "caaab", "ygggy")

def test_char_freq_solver():
    solver = CharFreqSolver()
    runner = MemoryGameRunner("apple", solver, 10)
    result = runner.play_game()
    print(result)
    assert result.won

def test_char_freq_solver_2():
    solver = CharFreqSolver()
    runner = MemoryGameRunner("proxy", solver, 10)
    result = runner.play_game()
    print(result)
    assert result.won

def test_char_freq_solver_3():
    solver = FixedStartingWordThenArbirarySolver("bread")
    runner = MemoryGameRunner("proxy", solver, 10)
    result = runner.play_game()
    print(result)
    assert result.won