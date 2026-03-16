# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?

  When I first ran the game, it had several visible problems. The attempt counter showed one fewer attempt than expected, and the history only recorded 6 guesses despite the game allowing 7 attempts. The New Game button reset the attempt count but left the game locked — you could not submit any guesses afterward. The hint direction was also wrong in certain cases, and the game accepted numbers outside the valid range without any feedback.

- List at least two concrete bugs you noticed at the start
  (for example: "the secret number kept changing" or "the hints were backwards").

  - **The New Game button did not fully reset the game.** After winning or losing, clicking New Game reset the attempt counter but never reset the `status` variable, which left the game blocked at the "you already won / game over" screen. The `history` was also never cleared, and the secret was regenerated using a hardcoded range of 1–100 regardless of the selected difficulty.
  - **The hint messages were backwards.** When a guess was too high, the game told the player to go higher, and when a guess was too low, it told the player to go lower. On top of that, on every even-numbered attempt the secret was silently cast to a string, causing string-based comparisons where "9" > "10" evaluates as true, producing entirely wrong hints for certain number pairs.
  - **Out-of-bounds guesses were accepted and counted as attempts.** Entering a number outside the valid range (e.g., 200 in Easy mode) would consume one of the player's limited attempts without any warning, which was unfair and confusing.
  - **The difficulty ranges were incorrectly assigned.** Normal mode used a range of 1–100 and Hard mode used 1–50, meaning Hard was actually easier to guess than Normal. Easy was 1–20, which was correct, but Normal and Hard needed to be swapped so that difficulty scaled properly.
  - **The `st.info` box and guess history showed stale values after every submission.** Because these UI elements were rendered before the submit block ran, they always reflected the state from the previous interaction rather than the current one.

---

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?

  I used Claude (Claude Code) as my primary AI collaborator throughout the project.

- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).

  Claude correctly identified that the hint messages in `check_guess` were flipped — `"Too High"` was paired with "Go HIGHER!" and `"Too Low"` with "Go LOWER!", which is the opposite of the correct behavior. It also identified that the even-attempt string casting was causing additional incorrect comparisons. I verified both fixes by manually testing guesses above and below the secret and confirming the hints matched the expected direction.

- Give one example of an AI suggestion that was incorrect or misleading (including what the AI suggested and how you verified the result).

  When addressing the stale `st.info` display, Claude initially proposed storing the last hint message in session state and triggering an `st.rerun()` after each submission. I recognized that this added unnecessary overhead — an extra session state variable and an extra rerun cycle — when the simpler fix was to just move `st.info` and the debug expander to after the submit block. That way, they render with already-updated state in the same pass, with no additional complexity.

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?

  I started by reading and inspecting the code carefully to understand the intended behavior before running anything. Once I had a hypothesis about a bug, I manually tested the specific scenario — for example, submitting a guess above the range, clicking New Game after a win, or checking hints for numbers where string and numeric ordering diverge (like 9 vs 10). A fix was confirmed when the behavior matched what the game was supposed to do.

- Describe at least one test you ran (manual or using pytest)
  and what it showed you about your code.

  I ran `pytest tests/test_game_logic.py -v` after implementing the functions in `logic_utils.py`. The tests exposed that the difficulty ranges were wrong — `test_range_hard` failed because Hard was returning 1–50 instead of 1–100, which directly confirmed the range bug before I had even caught it manually. Running the full suite also verified that bounds validation, hint messages, and score updates all behaved correctly after the fixes.

- Did AI help you design or understand any tests? How?

  Yes — Claude helped design the test cases by identifying which specific scenarios each bug created. For example, it wrote a test for `check_guess(9, 10)` expecting "Too Low", which specifically targets the string comparison bug: string ordering would evaluate "9" > "10" as true and return "Too High", so this case distinguishes correct numeric behavior from the broken string-based one. Claude also generated boundary tests for `parse_guess` (at exactly `low` and `high`) to confirm the bounds validation worked at the edges, not just in the middle.

---

## 4. What did you learn about Streamlit and state?

- In your own words, explain why the secret number kept changing in the original app.

  The secret number kept changing because Streamlit re-executes the entire script from top to bottom every time a user interacts with the app — including button clicks. Without `st.session_state`, the line `random.randint(low, high)` ran on every rerun, generating a brand new secret each time the player clicked Submit. The fix was to wrap the secret generation in `if "secret" not in st.session_state`, so the number is only generated once and then preserved across all future reruns.

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?

  Imagine every time you click a button on a webpage, the entire page script reloads from scratch — that's essentially what Streamlit does. Every interaction triggers a full top-to-bottom re-execution of your Python file. Session state is like a persistent notepad that survives these reruns: anything you store in `st.session_state` stays intact across each execution cycle. So when `st.rerun()` is called — for example after clicking New Game — Streamlit re-executes the script, but any values we reset (like `status = "playing"` or `history = []`) are already saved in session state before the rerun, so the UI picks them up correctly on the next pass.

- What change did you make that finally gave the game a stable secret number?

  Guarding the secret generation with `if "secret" not in st.session_state` ensured that `random.randint()` only executes once — on the very first load. After that, every rerun reads the existing value from session state rather than generating a new one.

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?

  I want to test edge cases with more granularity going forward. This project showed me that bugs often hide at boundaries — like a guess of exactly `low` or `high`, or the specific pair 9 vs 10 that exposes string-vs-numeric ordering. I also want to keep evaluating code proposals not just for correctness but for the overhead they introduce. A fix that works but adds an extra rerun cycle and an extra session state variable is strictly worse than a fix that reorders two blocks of code to achieve the same result.

- What is one thing you would do differently next time you work with AI on a coding task?

  Next time I would try using the inline AI prompt feature directly in the editor rather than working through a chat interface. Having AI suggestions appear in context — right next to the code — would make it faster to evaluate and accept or reject proposals without switching windows.

- In one or two sentences, describe how this project changed the way you think about AI generated code.

  This project taught me to collaborate with AI as an architect rather than a code reviewer — I directed the design decisions and pushed back when a proposed solution was unnecessarily complex, while Claude handled identifying specific bugs and generating test scaffolding. AI-generated code still needs a human to set the direction and catch cases where a technically correct fix introduces more complexity than the problem warrants.
