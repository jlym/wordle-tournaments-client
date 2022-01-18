from wordle_tournaments_client import Client

def test_api():
    client = Client("token", "http://localhost:3000/api")

    # Create a user
    description = "python client integration test"
    user = client.create_user(description)
    assert user
    assert user.user_id > 0
    assert user.description == description

    # Create a game.
    game = client.create_game(user.user_id)
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
    assert guess.score
