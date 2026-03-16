from logic_utils import check_guess, parse_guess, get_range_for_difficulty, update_score


# --- check_guess: hint message direction (Bug 4) ---

def test_winning_guess():
    outcome, _ = check_guess(50, 50)
    assert outcome == "Win"

def test_guess_too_high_outcome():
    outcome, _ = check_guess(60, 50)
    assert outcome == "Too High"

def test_guess_too_low_outcome():
    outcome, _ = check_guess(40, 50)
    assert outcome == "Too Low"

def test_too_high_message_says_lower():
    # Bug 4: message was "Go HIGHER!" when guess was too high — should say LOWER
    _, message = check_guess(60, 50)
    assert "LOWER" in message

def test_too_low_message_says_higher():
    # Bug 4: message was "Go LOWER!" when guess was too low — should say HIGHER
    _, message = check_guess(40, 50)
    assert "HIGHER" in message


# --- check_guess: numeric comparison only (Bug 5) ---

def test_check_guess_no_string_comparison():
    # Bug 5: on even attempts secret was cast to str, causing "9" > "10" = True
    # (string ordering), giving wrong hints for certain number pairs
    outcome, _ = check_guess(9, 10)
    assert outcome == "Too Low"  # 9 < 10 numerically; string compare would say Too High

def test_check_guess_two_digit_boundary():
    outcome, _ = check_guess(10, 9)
    assert outcome == "Too High"


# --- parse_guess: bounds validation (Bug 6) ---

def test_parse_guess_above_high_rejected():
    # Bug 6: out-of-bounds inputs were accepted and consumed an attempt
    ok, _, err = parse_guess("101", 1, 100)
    assert ok is False
    assert err is not None

def test_parse_guess_below_low_rejected():
    ok, _, err = parse_guess("0", 1, 100)
    assert ok is False
    assert err is not None

def test_parse_guess_at_boundary_accepted():
    ok, value, _ = parse_guess("1", 1, 100)
    assert ok is True
    assert value == 1

def test_parse_guess_at_high_boundary_accepted():
    ok, value, _ = parse_guess("100", 1, 100)
    assert ok is True
    assert value == 100

def test_parse_guess_valid_in_range():
    ok, value, _ = parse_guess("50", 1, 100)
    assert ok is True
    assert value == 50

def test_parse_guess_empty_rejected():
    ok, _, err = parse_guess("", 1, 100)
    assert ok is False

def test_parse_guess_non_numeric_rejected():
    ok, _, err = parse_guess("abc", 1, 100)
    assert ok is False


# --- get_range_for_difficulty: difficulty-aware range (Bug 3 & 7) ---

def test_range_easy():
    # Bug 3/7: New Game and info string used hardcoded 1–100 ignoring difficulty
    low, high = get_range_for_difficulty("Easy")
    assert (low, high) == (1, 20)

def test_range_normal():
    low, high = get_range_for_difficulty("Normal")
    assert (low, high) == (1, 50)

def test_range_hard():
    low, high = get_range_for_difficulty("Hard")
    assert (low, high) == (1, 100)


# --- update_score: win scoring ---

def test_score_increases_on_win():
    new_score = update_score(0, "Win", 1)
    assert new_score > 0

def test_score_decreases_on_too_low():
    new_score = update_score(50, "Too Low", 1)
    assert new_score < 50
