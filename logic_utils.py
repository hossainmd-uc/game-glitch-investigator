def get_range_for_difficulty(difficulty: str) -> tuple[int, int]:
    """Return the inclusive numeric range for a given difficulty level.

    The range defines the lower and upper bounds (inclusive) from which the
    secret number is drawn and within which guesses must fall.

    Args:
        difficulty: One of "Easy", "Normal", or "Hard".

    Returns:
        A tuple (low, high) representing the inclusive guess range.
        Defaults to (1, 100) if an unrecognised difficulty is provided.

    Examples:
        >>> get_range_for_difficulty("Easy")
        (1, 20)
        >>> get_range_for_difficulty("Hard")
        (1, 100)
    """
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Normal":
        return 1, 50
    if difficulty == "Hard":
        return 1, 100
    return 1, 100


def parse_guess(raw: str, low: int, high: int) -> tuple[bool, int | None, str | None]:
    """Parse and validate raw user input as an integer guess within bounds.

    Handles empty input, non-numeric strings, decimal strings, and values
    outside the valid range. Out-of-range inputs are rejected without
    consuming a game attempt.

    Args:
        raw: The raw string entered by the user.
        low: The minimum valid guess value (inclusive).
        high: The maximum valid guess value (inclusive).

    Returns:
        A three-element tuple (ok, guess_int, error_message):
            - ok (bool): True if the input is valid, False otherwise.
            - guess_int (int | None): The parsed integer, or None if invalid.
            - error_message (str | None): A human-readable error string, or
              None if the input is valid.

    Examples:
        >>> parse_guess("42", 1, 100)
        (True, 42, None)
        >>> parse_guess("abc", 1, 100)
        (False, None, 'That is not a number.')
        >>> parse_guess("150", 1, 100)
        (False, None, 'Please enter a number between 1 and 100.')
    """
    if raw is None:
        return False, None, "Enter a guess."

    if raw == "":
        return False, None, "Enter a guess."

    try:
        if "." in raw:
            value = int(float(raw))
        else:
            value = int(raw)
    except Exception:
        return False, None, "That is not a number."

    if value < low or value > high:
        return False, None, f"Please enter a number between {low} and {high}."

    return True, value, None


def check_guess(guess: int, secret: int) -> tuple[str, str]:
    """Compare a numeric guess against the secret number and return feedback.

    Always performs a numeric comparison to avoid string-ordering anomalies
    (e.g. "9" > "10" evaluating as True in lexicographic order).

    Args:
        guess: The player's integer guess.
        secret: The secret integer the player is trying to identify.

    Returns:
        A two-element tuple (outcome, message):
            - outcome (str): One of "Win", "Too High", or "Too Low".
            - message (str): A user-facing hint string corresponding to the
              outcome.

    Examples:
        >>> check_guess(50, 50)
        ('Win', '🎉 Correct!')
        >>> check_guess(60, 50)
        ('Too High', '📉 Go LOWER!')
        >>> check_guess(40, 50)
        ('Too Low', '📈 Go HIGHER!')
    """
    if guess == secret:
        return "Win", "🎉 Correct!"
    if guess > secret:
        return "Too High", "📉 Go LOWER!"
    return "Too Low", "📈 Go HIGHER!"


def update_score(current_score: int, outcome: str, attempt_number: int) -> int:
    """Calculate and return an updated score based on the guess outcome.

    Winning awards points that decrease with each attempt, with a minimum
    of 10 points. Incorrect guesses apply a small penalty or bonus depending
    on the outcome type and attempt parity.

    Args:
        current_score: The player's score before this guess.
        outcome: The result of the guess — one of "Win", "Too High", or
            "Too Low".
        attempt_number: The 1-based index of the current attempt, used to
            scale win points and determine parity bonuses.

    Returns:
        The updated integer score after applying the outcome's point delta.

    Examples:
        >>> update_score(0, "Win", 1)
        80
        >>> update_score(50, "Too Low", 3)
        45
    """
    if outcome == "Win":
        points = 100 - 10 * (attempt_number + 1)
        if points < 10:
            points = 10
        return current_score + points

    if outcome == "Too High":
        if attempt_number % 2 == 0:
            return current_score + 5
        return current_score - 5

    if outcome == "Too Low":
        return current_score - 5

    return current_score
