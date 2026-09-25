#!/usr/bin/env python3
"""
check_rps.py  (INSTRUCTOR AND TF USE ONLY. Do not give this to students.)

The grader for CS 104 Project 2 (Rock, Paper, Scissors).

USAGE
    Grade one student (run from their repo folder, or pass the folder):
        python3 check_rps.py
        python3 check_rps.py path/to/student_repo
        python3 check_rps.py path/to/student_repo --points 70 --verbose

    Grade a whole class (a folder that holds one repo folder per student):
        python3 check_rps.py --batch path/to/all_repos --points 70
        This writes grades.csv into that folder.

    --points N   Also show the grade as points out of N (the code portion)
    --verbose    Also list every check that passed
    --csv        Print one CSV line and nothing else (used by --batch)

WHAT IT DOES
    1. Coverage          Is every function written, and does the program
                         actually call it?
    2. Function checks   Each function alone, with scripted input
    3. Whole game        Runs the student's start.py (which runs rps.py) and
                         plays full games, then compares the output with
                         the spec. If start.py is missing it runs the
                         official copy so the game is still graded.
    4. Structure/style   Decomposition, docstrings, constants, provided code
                         untouched, no global variables, line length, naming
    5. Review flags      Constructs beyond what has been taught. These are
                         conversation starters for office hours. They carry
                         no penalty.

GRADE (edit the weights below to change it)
    Code grade = 60% behavior + 40% structure and style
    Behavior   = 50% function checks + 50% whole game
    Structure and style is multiplied by the share of the 10 student
    functions that are actually written, so an untouched starter file
    earns nothing for style.

NOTES
    - Output is compared with extra spaces and blank lines ignored.
      Spelling, punctuation and capitalization must match exactly.
    - A crash, a hang or a request for extra input is reported as a failure.
      The grader itself will not crash on student errors.
    - The grade is a SUGGESTION. Read the failures before you record it.
      Late penalties and the video grade are not included.
    - Hang protection for the function checks uses a Mac/Linux feature. On
      Windows a hang inside a function check can freeze the grader. The
      whole-game runs are protected on every system.
"""
import ast
import builtins
import contextlib
import csv
import io
import importlib.util
import os
import re
import signal
import subprocess
import sys

# ---------------------------------------------------------------------
# Settings you may want to change
# ---------------------------------------------------------------------
WEIGHT_BEHAVIOR = 0.60
WEIGHT_STRUCTURE = 0.40
WEIGHT_FUNCTIONS_IN_BEHAVIOR = 0.50
WEIGHT_GAME_IN_BEHAVIOR = 0.50

CHECK_TIMEOUT_SECONDS = 4   # per function check
GAME_TIMEOUT_SECONDS = 3    # per full game run
BATCH_TIMEOUT_SECONDS = 90  # per student in --batch mode

# Scripted games for the whole-game section. Each entry is
# (label, typed input lines, expected output with whitespace collapsed).
GOLDEN_RUNS = [('Sample Run 1: a normal game',
  ['Anna Mae', 'David Nunez', '1', 'r', 'p', 'r', 'r', 'p', 's', '3'],
  '---------------------------------------- CS 104 Rock, Paper, Scissors '
  '---------------------------------------- Player 1, enter your name: '
  'Player 2, enter your name: Menu Options ------------ 1) Play rock, '
  'paper, scissors 2) Play rock, paper, scissors, lizard, spock 3) Quit '
  'Choice --> Anna Mae, enter your move: David Nunez, enter your move: '
  'David Nunez wins the round! Anna Mae, enter your move: David Nunez, '
  'enter your move: This round is a draw! Anna Mae, enter your move: David '
  'Nunez, enter your move: David Nunez wins the round! Congratulations '
  'David Nunez! You won CS 104 Rock, Paper, Scissors! Menu Options '
  '------------ 1) Play rock, paper, scissors 2) Play rock, paper, '
  'scissors, lizard, spock 3) Quit Choice --> '
  '---------------------------------------- Thanks for playing Rock, '
  'Paper, Scissors! ----------------------------------------'),
 ('Sample Run 2: invalid menu choice and lizard-spock',
  ['Anna Mae', 'David Nunez', '4', '2', '3'],
  '---------------------------------------- CS 104 Rock, Paper, Scissors '
  '---------------------------------------- Player 1, enter your name: '
  'Player 2, enter your name: Menu Options ------------ 1) Play rock, '
  'paper, scissors 2) Play rock, paper, scissors, lizard, spock 3) Quit '
  'Choice --> Invalid menu choice Menu Options ------------ 1) Play rock, '
  'paper, scissors 2) Play rock, paper, scissors, lizard, spock 3) Quit '
  'Choice --> Under Construction No winner! Menu Options ------------ 1) '
  'Play rock, paper, scissors 2) Play rock, paper, scissors, lizard, spock '
  '3) Quit Choice --> ---------------------------------------- Thanks for '
  'playing Rock, Paper, Scissors! '
  '----------------------------------------'),
 ('Sample Run 3: default names, mixed case, tied game',
  ['', '', '1', 'R', 'p', 's', 'S', 'S', 'P', '3'],
  '---------------------------------------- CS 104 Rock, Paper, Scissors '
  '---------------------------------------- Player 1, enter your name: '
  'ERROR: Illegal name given, using default Player 2, enter your name: '
  'ERROR: Illegal name given, using default Menu Options ------------ 1) '
  'Play rock, paper, scissors 2) Play rock, paper, scissors, lizard, spock '
  '3) Quit Choice --> Rocky, enter your move: Creed, enter your move: '
  'Creed wins the round! Rocky, enter your move: Creed, enter your move: '
  'This round is a draw! Rocky, enter your move: Creed, enter your move: '
  'Rocky wins the round! No winner! Menu Options ------------ 1) Play '
  'rock, paper, scissors 2) Play rock, paper, scissors, lizard, spock 3) '
  'Quit Choice --> ---------------------------------------- Thanks for '
  'playing Rock, Paper, Scissors! '
  '----------------------------------------'),
 ('Invalid move plays as rock',
  ['Anna Mae', 'David Nunez', '1', 'r', 'a', 'r', 'r', 's', 'r', '3'],
  '---------------------------------------- CS 104 Rock, Paper, Scissors '
  '---------------------------------------- Player 1, enter your name: '
  'Player 2, enter your name: Menu Options ------------ 1) Play rock, '
  'paper, scissors 2) Play rock, paper, scissors, lizard, spock 3) Quit '
  'Choice --> Anna Mae, enter your move: David Nunez, enter your move: '
  'ERROR: Illegal move given, using default This round is a draw! Anna '
  'Mae, enter your move: David Nunez, enter your move: This round is a '
  'draw! Anna Mae, enter your move: David Nunez, enter your move: David '
  'Nunez wins the round! Congratulations David Nunez! You won CS 104 Rock, '
  'Paper, Scissors! Menu Options ------------ 1) Play rock, paper, '
  'scissors 2) Play rock, paper, scissors, lizard, spock 3) Quit Choice '
  '--> ---------------------------------------- Thanks for playing Rock, '
  'Paper, Scissors! ----------------------------------------'),
 ('Two games in a row, then quit',
  ['Ana',
   'Ben',
   '1',
   'r',
   's',
   'r',
   's',
   'r',
   's',
   '1',
   'p',
   's',
   'p',
   's',
   'p',
   's',
   '3'],
  '---------------------------------------- CS 104 Rock, Paper, Scissors '
  '---------------------------------------- Player 1, enter your name: '
  'Player 2, enter your name: Menu Options ------------ 1) Play rock, '
  'paper, scissors 2) Play rock, paper, scissors, lizard, spock 3) Quit '
  'Choice --> Ana, enter your move: Ben, enter your move: Ana wins the '
  'round! Ana, enter your move: Ben, enter your move: Ana wins the round! '
  'Ana, enter your move: Ben, enter your move: Ana wins the round! '
  'Congratulations Ana! You won CS 104 Rock, Paper, Scissors! Menu Options '
  '------------ 1) Play rock, paper, scissors 2) Play rock, paper, '
  'scissors, lizard, spock 3) Quit Choice --> Ana, enter your move: Ben, '
  'enter your move: Ben wins the round! Ana, enter your move: Ben, enter '
  'your move: Ben wins the round! Ana, enter your move: Ben, enter your '
  'move: Ben wins the round! Congratulations Ben! You won CS 104 Rock, '
  'Paper, Scissors! Menu Options ------------ 1) Play rock, paper, '
  'scissors 2) Play rock, paper, scissors, lizard, spock 3) Quit Choice '
  '--> ---------------------------------------- Thanks for playing Rock, '
  'Paper, Scissors! ----------------------------------------'),
 ('Non-numeric menu input is invalid',
  ['Ana', 'Ben', 'abc', '', '3'],
  '---------------------------------------- CS 104 Rock, Paper, Scissors '
  '---------------------------------------- Player 1, enter your name: '
  'Player 2, enter your name: Menu Options ------------ 1) Play rock, '
  'paper, scissors 2) Play rock, paper, scissors, lizard, spock 3) Quit '
  'Choice --> Invalid menu choice Menu Options ------------ 1) Play rock, '
  'paper, scissors 2) Play rock, paper, scissors, lizard, spock 3) Quit '
  'Choice --> Invalid menu choice Menu Options ------------ 1) Play rock, '
  'paper, scissors 2) Play rock, paper, scissors, lizard, spock 3) Quit '
  'Choice --> ---------------------------------------- Thanks for playing '
  'Rock, Paper, Scissors! ----------------------------------------'),
 ('Same name for both players, 1-1 tie',
  ['Sam', 'Sam', '1', 'r', 's', 's', 'r', 'p', 'p', '3'],
  '---------------------------------------- CS 104 Rock, Paper, Scissors '
  '---------------------------------------- Player 1, enter your name: '
  'Player 2, enter your name: Menu Options ------------ 1) Play rock, '
  'paper, scissors 2) Play rock, paper, scissors, lizard, spock 3) Quit '
  'Choice --> Sam, enter your move: Sam, enter your move: Sam wins the '
  'round! Sam, enter your move: Sam, enter your move: Sam wins the round! '
  'Sam, enter your move: Sam, enter your move: This round is a draw! No '
  'winner! Menu Options ------------ 1) Play rock, paper, scissors 2) Play '
  'rock, paper, scissors, lizard, spock 3) Quit Choice --> '
  '---------------------------------------- Thanks for playing Rock, '
  'Paper, Scissors! ----------------------------------------')]

# The provided code exactly as students received it.
PROVIDED_FUNCTIONS_SOURCE = ('def print_initial_header():\n'
 '    """Prints a pretty header to introduce the user to the game."""\n'
 '    print("----------------------------------------")\n'
 '    print("                CS 104")\n'
 '    print("          Rock, Paper, Scissors")\n'
 '    print("----------------------------------------")\n'
 '\n'
 '\n'
 'def print_menu():\n'
 '    """Prints the menu options (not the prompt)."""\n'
 '    print()\n'
 '    print("Menu Options")\n'
 '    print("------------")\n'
 '    print("1) Play rock, paper, scissors")\n'
 '    print("2) Play rock, paper, scissors, lizard, spock")\n'
 '    print("3) Quit")\n'
 '    print()\n'
 '\n'
 '\n'
 'def print_error_message(error_number):\n'
 '    """Prints the error for ERROR_NAME or ERROR_MOVE."""\n'
 '    if error_number == ERROR_NAME:\n'
 '        print()\n'
 '        print("ERROR: Illegal name given, using default")\n'
 '        print()\n'
 '    elif error_number == ERROR_MOVE:\n'
 '        print()\n'
 '        print("ERROR: Illegal move given, using default")\n'
 '    else:\n'
 '        print("This should never print!")\n'
 '\n'
 '\n'
 'def print_closer():\n'
 '    """Prints out the final greeting for the program."""\n'
 '    print()\n'
 '    print("----------------------------------------")\n'
 '    print("           Thanks for playing")\n'
 '    print("          Rock, Paper, Scissors!")\n'
 '    print("----------------------------------------")\n')
START_PY_SOURCE = ('"""\n'
 'start.py (PROVIDED: do not modify)\n'
 'Runs your game. Run it with: python3 start.py\n'
 '"""\n'
 'from rps import rps\n'
 '\n'
 '\n'
 'def main():\n'
 '    rps()\n'
 '\n'
 '\n'
 'if __name__ == "__main__":\n'
 '    main()\n')

STUDENT_FUNCS = {
    "is_move_good": 1, "is_round_winner": 2, "get_name": 1,
    "get_menu_choice": 0, "get_move": 1, "announce_round_winner": 1,
    "do_round": 2, "announce_winner": 1, "do_game": 3, "rps": 0,
}
PROVIDED_FUNCS = {
    "print_initial_header": 0, "print_menu": 0,
    "print_error_message": 1, "print_closer": 0,
}
EXPECTED_CONSTANTS = {
    "COURSE_NAME": "CS 104", "MAX_ROUNDS": 3, "ROCK": "r", "PAPER": "p",
    "SCISSORS": "s", "DEFAULT_MOVE": "r", "DEFAULT_NAME_1": "Rocky",
    "DEFAULT_NAME_2": "Creed", "PLAYER_1": 1, "PLAYER_2": 2, "DRAW": 0,
    "ERROR_NAME": 1, "ERROR_MOVE": 2, "PLAY_RPS": 1, "PLAY_RPSLS": 2,
    "QUIT_CHOICE": 3,
}
# Which functions each function should call (from the spec's function table)
EXPECTED_CALLS = {
    "rps": ["print_initial_header", "get_name", "get_menu_choice",
            "do_game", "announce_winner", "print_closer"],
    "get_name": ["print_error_message"],
    "get_menu_choice": ["print_menu"],
    "get_move": ["is_move_good", "print_error_message"],
    "do_round": ["get_move", "is_round_winner"],
    "do_game": ["do_round", "announce_round_winner"],
}
BEATS = {("r", "s"), ("p", "r"), ("s", "p")}

SECTION_BEHAVIOR = "Function checks"
SECTION_GAME = "Whole game"
SECTION_STRUCTURE = "Structure and style"

FOLDER = ""      # the student's repo folder
STUDENT = None   # the imported student module
SOURCE = ""      # the student's source text
TREE = None      # the student's parsed source


# ---------------------------------------------------------------------
# Harness
# ---------------------------------------------------------------------
class OutOfInput(Exception):
    """Raised when student code asks for more input than the script has."""


class Timeout(Exception):
    pass


class Outcome:
    def __init__(self, value, output, prompts, left):
        self.value = value
        self.output = output
        self.prompts = prompts
        self.left = left


def norm(text):
    """Collapse all whitespace so spacing and blank lines are ignored."""
    return " ".join(str(text).split())


def run_with_input(func, typed, *args):
    """Call func(*args) with scripted input and captured output."""
    feed = list(typed)
    prompts = []
    out = io.StringIO()

    def fake_input(prompt=""):
        if not feed:
            raise OutOfInput("asked for more input than the test supplied")
        prompts.append(prompt)
        out.write(prompt)
        return feed.pop(0)

    real_input = builtins.input
    builtins.input = fake_input
    try:
        with contextlib.redirect_stdout(out):
            value = func(*args)
    finally:
        builtins.input = real_input
    return Outcome(value, out.getvalue(), prompts, len(feed))


def expect(condition, message):
    if not condition:
        raise AssertionError(message)


def student_func(name):
    func = getattr(STUDENT, name, None)
    expect(callable(func), f"function {name}() is missing")
    return func


def _on_alarm(signum, frame):
    raise Timeout(f"took longer than {CHECK_TIMEOUT_SECONDS} seconds "
                  "(possible infinite loop)")


CHECKS = []


def check(section, name):
    def register(func):
        CHECKS.append((section, name, func))
        return func
    return register


# ---------------------------------------------------------------------
# Function checks
# ---------------------------------------------------------------------
@check(SECTION_BEHAVIOR, "is_move_good accepts r, p, s in either case")
def _():
    func = student_func("is_move_good")
    bad = [m for m in "rpsRPS" if func(m) is not True]
    expect(not bad, f"should return True for {bad}")


@check(SECTION_BEHAVIOR, "is_move_good rejects other single characters")
def _():
    func = student_func("is_move_good")
    bad = [m for m in ["q", "t", "a", "x", "1", " ", "Q", "T", "?"]
           if func(m) is not False]
    expect(not bad, f"should return False for {bad}")


@check(SECTION_BEHAVIOR, "is_move_good rejects empty and multi-character text")
def _():
    func = student_func("is_move_good")
    bad = [m for m in ["", "rp", "rock", "SS", "r ", " r", "ps"]
           if func(m) is not False]
    expect(not bad, f"should return False for {bad}")


@check(SECTION_BEHAVIOR, "is_round_winner: all lowercase combinations")
def _():
    func = student_func("is_round_winner")
    bad = []
    for a in "rps":
        for b in "rps":
            if func(a, b) is not ((a, b) in BEATS):
                bad.append(f"{a} vs {b}")
    expect(not bad, "wrong answer for " + ", ".join(bad))


@check(SECTION_BEHAVIOR, "is_round_winner: uppercase and mixed case")
def _():
    func = student_func("is_round_winner")
    bad = []
    for a in "rpsRPS":
        for b in "rpsRPS":
            if a.islower() and b.islower():
                continue
            if func(a, b) is not ((a.lower(), b.lower()) in BEATS):
                bad.append(f"{a} vs {b}")
    expect(not bad, "wrong answer for " + ", ".join(bad[:6]))


@check(SECTION_BEHAVIOR, "get_name returns the name typed (spaces kept)")
def _():
    func = student_func("get_name")
    result = run_with_input(func, ["Anna Mae"], 1)
    expect(result.value == "Anna Mae",
           f"returned {result.value!r} instead of 'Anna Mae'")
    expect("ERROR" not in result.output,
           "printed an error for a valid name")


@check(SECTION_BEHAVIOR, "get_name prompts match the spec")
def _():
    func = student_func("get_name")
    first = run_with_input(func, ["A"], 1)
    second = run_with_input(func, ["B"], 2)
    expect(norm(first.prompts[0]) == "Player 1, enter your name:",
           f"player 1 prompt was {first.prompts[0]!r}")
    expect(norm(second.prompts[0]) == "Player 2, enter your name:",
           f"player 2 prompt was {second.prompts[0]!r}")


@check(SECTION_BEHAVIOR, "get_name uses defaults and prints the error")
def _():
    func = student_func("get_name")
    first = run_with_input(func, [""], 1)
    second = run_with_input(func, [""], 2)
    expect(first.value == "Rocky", f"player 1 default was {first.value!r}")
    expect(second.value == "Creed", f"player 2 default was {second.value!r}")
    expect("ERROR: Illegal name given, using default" in norm(first.output),
           "error message missing or misspelled")


@check(SECTION_BEHAVIOR, "get_menu_choice returns 1, 2 and 3 as ints")
def _():
    func = student_func("get_menu_choice")
    for typed, wanted in [("1", 1), ("2", 2), ("3", 3)]:
        result = run_with_input(func, [typed])
        expect(type(result.value) is int and result.value == wanted,
               f"typed {typed!r} but got {result.value!r}")


@check(SECTION_BEHAVIOR, "get_menu_choice shows the menu and the right prompt")
def _():
    func = student_func("get_menu_choice")
    result = run_with_input(func, ["1"])
    text = norm(result.output)
    expect("Menu Options" in text and "3) Quit" in text, "menu not shown")
    expect(norm(result.prompts[0]) == "Choice -->",
           f"prompt was {result.prompts[0]!r}")


@check(SECTION_BEHAVIOR, "get_menu_choice re-prompts after invalid input")
def _():
    func = student_func("get_menu_choice")
    result = run_with_input(func, ["4", "2"])
    text = norm(result.output)
    expect(result.value == 2, f"returned {result.value!r} instead of 2")
    expect(text.count("Invalid menu choice") == 1,
           "should print 'Invalid menu choice' once")
    expect(text.count("Menu Options") == 2,
           "should show the menu again after invalid input")


@check(SECTION_BEHAVIOR, "get_menu_choice survives many bad entries")
def _():
    func = student_func("get_menu_choice")
    result = run_with_input(func, ["0", "-1", "10", "abc", "", "3"])
    expect(result.value == 3, f"returned {result.value!r} instead of 3")
    expect(norm(result.output).count("Invalid menu choice") == 5,
           "should print 'Invalid menu choice' for each of the 5 bad entries")


@check(SECTION_BEHAVIOR, "get_move returns a valid move and uses the prompt")
def _():
    func = student_func("get_move")
    result = run_with_input(func, ["P"], "Sam")
    expect(str(result.value).lower() == "p",
           f"returned {result.value!r} for 'P'")
    expect("ERROR" not in result.output, "error printed for a valid move")
    expect(norm(result.prompts[0]) == "Sam, enter your move:",
           f"prompt was {result.prompts[0]!r}")


@check(SECTION_BEHAVIOR, "get_move falls back to 'r' with the error message")
def _():
    func = student_func("get_move")
    for typed in ["a", "", "rock"]:
        result = run_with_input(func, [typed], "Sam")
        expect(result.value == "r",
               f"typed {typed!r} but returned {result.value!r}")
        expect("ERROR: Illegal move given, using default"
               in norm(result.output),
               f"error message missing or misspelled for {typed!r}")


@check(SECTION_BEHAVIOR, "announce_round_winner prints winner or draw")
def _():
    func = student_func("announce_round_winner")
    win = norm(run_with_input(func, [], "Anna Mae").output)
    draw = norm(run_with_input(func, [], "").output)
    expect(win == "Anna Mae wins the round!", f"printed {win!r}")
    expect(draw == "This round is a draw!", f"printed {draw!r}")


@check(SECTION_BEHAVIOR, "do_round returns 0 (draw), 1 (player 1) or 2")
def _():
    func = student_func("do_round")
    cases = [(["r", "s"], 1), (["s", "r"], 2), (["p", "r"], 1),
             (["r", "r"], 0), (["R", "S"], 1), (["P", "s"], 2)]
    bad = []
    for typed, wanted in cases:
        result = run_with_input(func, typed, "Ann", "Dave")
        if type(result.value) is not int or result.value != wanted:
            bad.append(f"{typed} gave {result.value!r} not {wanted!r}")
    expect(not bad, "; ".join(bad[:3]))


@check(SECTION_BEHAVIOR, "do_round asks player 1 first then player 2")
def _():
    func = student_func("do_round")
    result = run_with_input(func, ["r", "s"], "Ann", "Dave")
    prompts = [norm(p) for p in result.prompts]
    expect(prompts == ["Ann, enter your move:", "Dave, enter your move:"],
           f"prompts were {prompts}")


@check(SECTION_BEHAVIOR, "do_round plays the default move for invalid input")
def _():
    func = student_func("do_round")
    first = run_with_input(func, ["a", "s"], "Ann", "Dave")
    second = run_with_input(func, ["q", "p"], "Ann", "Dave")
    expect(first.value == 1, "invalid move should play as rock and beat s")
    expect(second.value == 2, "rock should lose to p")


@check(SECTION_BEHAVIOR, "do_round does not announce the result itself")
def _():
    func = student_func("do_round")
    result = run_with_input(func, ["r", "s"], "Ann", "Dave")
    text = norm(result.output)
    expect("wins the round" not in text and "draw" not in text,
           "do_round printed a result. do_game should announce it")


@check(SECTION_BEHAVIOR, "announce_winner prints congratulations")
def _():
    func = student_func("announce_winner")
    text = norm(run_with_input(func, [], "Anna Mae").output)
    expect("Congratulations Anna Mae!" in text, f"printed {text!r}")
    expect("You won CS 104 Rock, Paper, Scissors!" in text,
           "second line missing or misspelled")
    expect("No winner" not in text, "printed 'No winner' for a real winner")


@check(SECTION_BEHAVIOR, "announce_winner prints 'No winner!' for no winner")
def _():
    func = student_func("announce_winner")
    text = norm(run_with_input(func, [], "").output)
    expect(text == "No winner!", f"printed {text!r}")


@check(SECTION_BEHAVIOR, "do_game returns the player with more round wins")
def _():
    func = student_func("do_game")
    result = run_with_input(func, ["r", "p", "r", "r", "p", "s"],
                            "Ann", "Dave", 1)
    expect(result.value == "Dave", f"returned {result.value!r} not 'Dave'")
    text = norm(result.output)
    expect(text.count("Dave wins the round!") == 2
           and text.count("This round is a draw!") == 1,
           "round announcements are wrong")


@check(SECTION_BEHAVIOR, "do_game always plays all three rounds")
def _():
    func = student_func("do_game")
    result = run_with_input(func, ["r", "s", "r", "s", "s", "r"],
                            "Ann", "Dave", 1)
    expect(result.left == 0,
           "stopped early. All three rounds must be played")
    expect(result.value == "Ann", f"returned {result.value!r} not 'Ann'")


@check(SECTION_BEHAVIOR, "do_game returns empty string for a tie")
def _():
    func = student_func("do_game")
    split = run_with_input(func, ["r", "s", "s", "r", "r", "r"],
                           "Ann", "Dave", 1)
    draws = run_with_input(func, ["r", "r", "p", "p", "s", "s"],
                           "Ann", "Dave", 1)
    expect(split.value == "", f"1-1 game returned {split.value!r}")
    expect(draws.value == "", f"all-draw game returned {draws.value!r}")


@check(SECTION_BEHAVIOR, "do_game keeps score by player, not by name")
def _():
    func = student_func("do_game")
    # Both players are named Sam. Sam(1) wins a round, Sam(2) wins a round
    # and one round is a draw. That is a 1-1 tie, so there is no winner.
    tie = run_with_input(func, ["r", "s", "s", "r", "p", "p"],
                         "Sam", "Sam", 1)
    win = run_with_input(func, ["r", "s", "r", "s", "s", "r"],
                         "Sam", "Sam", 1)
    expect(tie.value == "",
           f"two players named Sam tied 1-1 but returned {tie.value!r}. "
           "Score by do_round's result, not by comparing names")
    expect(win.value == "Sam", f"2-1 game returned {win.value!r}")


@check(SECTION_BEHAVIOR, "do_game with game type 2 is 'Under Construction'")
def _():
    func = student_func("do_game")
    result = run_with_input(func, [], "Ann", "Dave", 2)
    expect("Under Construction" in norm(result.output),
           "did not print 'Under Construction'")
    expect(result.value == "", f"returned {result.value!r} not ''")


# ---------------------------------------------------------------------
# Whole game (runs the student's start.py, which runs rps.py)
# ---------------------------------------------------------------------
def first_difference(actual, expected):
    a_words = actual.split()
    e_words = expected.split()
    spot = min(len(a_words), len(e_words))
    for index, (a, e) in enumerate(zip(a_words, e_words)):
        if a != e:
            spot = index
            break
    low = max(0, spot - 5)
    got = " ".join(a_words[low:spot + 6])
    want = " ".join(e_words[low:spot + 6])
    return f"first difference near: got '...{got}...' wanted '...{want}...'"


def play_through_start_py(typed):
    """Runs `python3 start.py` in the student's folder with scripted input."""
    if os.path.isfile(os.path.join(FOLDER, "start.py")):
        command = [sys.executable, "start.py"]
    else:
        # start.py is missing. Run the official copy so the game itself is
        # still graded. The missing file is penalized under structure.
        command = [sys.executable, "-c", START_PY_SOURCE]
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    try:
        done = subprocess.run(
            command, cwd=FOLDER, env=env,
            input="\n".join(typed) + "\n", capture_output=True, text=True,
            timeout=GAME_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        raise Timeout(f"the game ran longer than {GAME_TIMEOUT_SECONDS} "
                      "seconds (possible infinite loop)")
    return done


def make_game_check(typed, expected):
    def run_game():
        done = play_through_start_py(typed)
        if done.returncode != 0:
            last = (done.stderr.strip().splitlines() or ["unknown error"])[-1]
            if "EOFError" in done.stderr:
                raise AssertionError("asked for more input than a normal "
                                     "game needs (EOFError)")
            raise AssertionError(f"crashed: {last}")
        actual = norm(done.stdout)
        expect(actual == expected, first_difference(actual, expected))
    return run_game


for _label, _typed, _expected in GOLDEN_RUNS:
    CHECKS.append((SECTION_GAME, _label, make_game_check(_typed, _expected)))


# ---------------------------------------------------------------------
# Structure and style
# ---------------------------------------------------------------------
def function_nodes():
    return {n.name: n for n in TREE.body if isinstance(n, ast.FunctionDef)}


def called_names(node):
    names = set()
    for child in ast.walk(node):
        if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
            names.add(child.func.id)
    return names


@check(SECTION_STRUCTURE, "All 14 functions exist with the right parameters")
def _():
    nodes = function_nodes()
    problems = []
    for name, arity in {**STUDENT_FUNCS, **PROVIDED_FUNCS}.items():
        if name not in nodes:
            problems.append(f"{name} missing")
        elif len(nodes[name].args.args) != arity:
            problems.append(f"{name} should take {arity} parameter(s)")
    expect(not problems, "; ".join(problems))


@check(SECTION_STRUCTURE, "Every function keeps its docstring")
def _():
    nodes = function_nodes()
    missing = []
    for name in STUDENT_FUNCS:
        if name in nodes:
            doc = ast.get_docstring(nodes[name]) or ""
            if not doc or "TO FILL IN" in doc:
                missing.append(name)
    expect(not missing, "docstring removed or still a placeholder: "
           + ", ".join(missing))


@check(SECTION_STRUCTURE, "Provided constants are unchanged")
def _():
    problems = []
    for name, wanted in EXPECTED_CONSTANTS.items():
        actual = getattr(STUDENT, name, "<missing>")
        if actual != wanted:
            problems.append(f"{name} is {actual!r} not {wanted!r}")
    expect(not problems, "; ".join(problems))


@check(SECTION_STRUCTURE,
       "Provided code is unchanged (start.py and the print_ functions)")
def _():
    problems = []
    canonical = {n.name: ast.dump(n)
                 for n in ast.parse(PROVIDED_FUNCTIONS_SOURCE).body
                 if isinstance(n, ast.FunctionDef)}
    nodes = function_nodes()
    for name, wanted in canonical.items():
        if name in nodes and ast.dump(nodes[name]) != wanted:
            problems.append(f"{name} was edited")
    start_path = os.path.join(FOLDER, "start.py")
    if not os.path.isfile(start_path):
        problems.append("start.py is missing")
    else:
        with open(start_path, encoding="utf-8") as handle:
            try:
                same = (ast.dump(ast.parse(handle.read()))
                        == ast.dump(ast.parse(START_PY_SOURCE)))
            except SyntaxError:
                same = False
        if not same:
            problems.append("start.py was edited")
    expect(not problems, "; ".join(problems))


@check(SECTION_STRUCTURE, "Functions call the helpers the spec assigns")
def _():
    nodes = function_nodes()
    problems = []
    for name, wanted in EXPECTED_CALLS.items():
        if name not in nodes:
            continue
        calls = called_names(nodes[name])
        for helper in wanted:
            if helper not in calls:
                problems.append(f"{name} does not call {helper}")
    expect(not problems, "; ".join(problems))


@check(SECTION_STRUCTURE, "Uses the constants instead of magic numbers")
def _():
    nodes = function_nodes()
    problems = []
    for name in ["rps", "get_name", "do_round", "do_game"]:
        if name not in nodes:
            continue
        # Numbers that are fine: a starting value of 0 and "+= 1".
        fine = set()
        for child in ast.walk(nodes[name]):
            if isinstance(child, ast.AugAssign):
                fine.add(id(child.value))
            if isinstance(child, ast.Assign) and \
                    isinstance(child.value, ast.Constant) and \
                    child.value.value == 0:
                fine.add(id(child.value))
        for child in ast.walk(nodes[name]):
            if (isinstance(child, ast.Constant)
                    and isinstance(child.value, int)
                    and not isinstance(child.value, bool)
                    and id(child) not in fine):
                problems.append(f"{name} uses the number {child.value}")
    expect(not problems, "; ".join(problems[:4])
           + ". Use PLAYER_1, PLAYER_2, DRAW, MAX_ROUNDS and so on")


@check(SECTION_STRUCTURE, "No global variables (constants are fine)")
def _():
    problems = []
    for node in TREE.body:
        if isinstance(node, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
            targets = (node.targets if isinstance(node, ast.Assign)
                       else [node.target])
            for target in targets:
                if isinstance(target, ast.Name) and \
                        not re.fullmatch(r"[A-Z][A-Z0-9_]*", target.id):
                    problems.append(f"global variable {target.id}")
    for node in ast.walk(TREE):
        if isinstance(node, ast.Global):
            problems.append("uses the global keyword")
    expect(not problems, "; ".join(problems[:4]))


@check(SECTION_STRUCTURE, "Lines are 80 characters or fewer")
def _():
    long_lines = [str(i) for i, line in enumerate(SOURCE.splitlines(), 1)
                  if len(line) > 80]
    expect(not long_lines, "too long on line(s) " + ", ".join(long_lines[:8]))


@check(SECTION_STRUCTURE, "Names use snake_case")
def _():
    problems = set()
    for node in ast.walk(TREE):
        if isinstance(node, ast.FunctionDef):
            names = [node.name] + [a.arg for a in node.args.args]
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            names = [node.id]
        else:
            continue
        for name in names:
            if not (re.fullmatch(r"[a-z_][a-z0-9_]*", name)
                    or re.fullmatch(r"[A-Z][A-Z0-9_]*", name)):
                problems.add(name)
    expect(not problems, "not snake_case: " + ", ".join(sorted(problems)))


@check(SECTION_STRUCTURE, "Header docstring has a real name and description")
def _():
    header = ast.get_docstring(TREE) or ""
    expect(header, "no header docstring at the top of the file")
    expect("TO FILL IN" not in header,
           "header still says TO FILL IN")


@check(SECTION_STRUCTURE, "No leftover TODO or NOTE comments from the starter")
def _():
    hits = [str(i) for i, line in enumerate(SOURCE.splitlines(), 1)
            if "TODO: implement" in line
            or "replace this return statement" in line]
    expect(not hits, "starter comments still on line(s) "
           + ", ".join(hits[:8]))


# ---------------------------------------------------------------------
# Review flags (never counted as failures)
# ---------------------------------------------------------------------
def review_flags():
    flags = []
    kinds = [
        (ast.Import, "an import statement"),
        (ast.ImportFrom, "an import statement"),
        (ast.ClassDef, "a class"),
        (ast.Try, "try/except"),
        (ast.Lambda, "a lambda"),
        (ast.ListComp, "a comprehension"),
        (ast.DictComp, "a comprehension"),
        (ast.SetComp, "a comprehension"),
        (ast.GeneratorExp, "a generator expression"),
        (ast.Dict, "a dictionary"),
        (ast.Set, "a set"),
        (ast.Global, "the global keyword"),
    ]
    for node in ast.walk(TREE):
        for kind, label in kinds:
            if isinstance(node, kind):
                flags.append((getattr(node, "lineno", 0), label))
    return sorted(set(flags))


# ---------------------------------------------------------------------
# Coverage table
# ---------------------------------------------------------------------
def looks_like_stub(node):
    """True if the function body is still the starter placeholder."""
    text = ast.get_source_segment(SOURCE, node) or ""
    body = [n for n in node.body
            if not (isinstance(n, ast.Expr)
                    and isinstance(n.value, ast.Constant)
                    and isinstance(n.value.value, str))]
    if not body or all(isinstance(n, ast.Pass) for n in body):
        return True
    # A placeholder return with both starter comments still in place
    return ("TODO: implement" in text
            and "replace this return statement" in text)


def start_py_calls_rps():
    path = os.path.join(FOLDER, "start.py")
    if not os.path.isfile(path):
        return False
    try:
        with open(path, encoding="utf-8") as handle:
            return "rps" in called_names(ast.parse(handle.read()))
    except SyntaxError:
        return False


def coverage_rows(results):
    """One row per function: written? called by? function checks passed."""
    nodes = function_nodes()
    callers = {}
    for name, node in nodes.items():
        for called in called_names(node):
            callers.setdefault(called, []).append(name)
    rows = []
    for name in list(STUDENT_FUNCS) + list(PROVIDED_FUNCS):
        if name not in nodes:
            written = "MISSING"
        elif name in PROVIDED_FUNCS:
            written = "provided"
        elif looks_like_stub(nodes[name]):
            written = "NOT WRITTEN"
        else:
            written = "yes"
        used = sorted(c for c in callers.get(name, []) if c != name)
        if name == "rps":
            used = ["start.py"] if start_py_calls_rps() else []
        used_text = ", ".join(used) if used else "NOT CALLED"
        mine = [ok for section, check_name, ok, _ in results
                if section == SECTION_BEHAVIOR
                and check_name.split()[0].rstrip(":") == name]
        if name == "rps":
            behavior = "see whole game"
        elif name in PROVIDED_FUNCS:
            behavior = "n/a"
        else:
            behavior = f"{sum(mine)}/{len(mine)}" if mine else "none"
        rows.append((name, written, used_text, behavior))
    return rows


# ---------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------
def load_student(folder):
    global FOLDER, STUDENT, SOURCE, TREE
    FOLDER = os.path.abspath(folder)
    path = os.path.join(FOLDER, "rps.py")
    if not os.path.isfile(path):
        return f"could not find rps.py in {FOLDER}"
    with open(path, encoding="utf-8") as handle:
        SOURCE = handle.read()
    try:
        TREE = ast.parse(SOURCE)
    except SyntaxError as error:
        return f"rps.py has a syntax error: {error}"
    spec = importlib.util.spec_from_file_location("student_rps", path)
    STUDENT = importlib.util.module_from_spec(spec)
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            spec.loader.exec_module(STUDENT)
    except BaseException as error:
        return f"rps.py crashed on import: {type(error).__name__}: {error}"
    return None


def run_check(func):
    """Returns None on pass or a message on failure."""
    has_alarm = hasattr(signal, "SIGALRM")
    if has_alarm:
        signal.signal(signal.SIGALRM, _on_alarm)
        signal.alarm(CHECK_TIMEOUT_SECONDS)
    try:
        func()
        return None
    except AssertionError as error:
        return str(error) or "check failed"
    except (OutOfInput, Timeout) as error:
        return str(error)
    except KeyboardInterrupt:
        raise
    except BaseException as error:   # includes SystemExit from sys.exit()
        return f"crashed: {type(error).__name__}: {error}"
    finally:
        if has_alarm:
            signal.alarm(0)


def grade_folder(folder):
    """Runs every check. Returns a dict of results, or a dict with 'error'."""
    problem = load_student(folder)
    if problem:
        return {"error": problem}
    results = []
    for section, name, func in CHECKS:
        message = run_check(func)
        results.append((section, name, message is None, message))
    tally = {}
    for section, name, ok, message in results:
        passed, total = tally.get(section, (0, 0))
        tally[section] = (passed + (1 if ok else 0), total + 1)

    def fraction(section):
        passed, total = tally.get(section, (0, 0))
        return passed / total if total else 0.0

    functions = fraction(SECTION_BEHAVIOR)
    game = fraction(SECTION_GAME)
    behavior = (WEIGHT_FUNCTIONS_IN_BEHAVIOR * functions
                + WEIGHT_GAME_IN_BEHAVIOR * game)
    structure_checks = fraction(SECTION_STRUCTURE)
    written = sum(1 for row in coverage_rows(results)
                  if row[0] in STUDENT_FUNCS and row[1] == "yes")
    written_share = written / len(STUDENT_FUNCS)
    structure = structure_checks * written_share
    total = WEIGHT_BEHAVIOR * behavior + WEIGHT_STRUCTURE * structure
    return {
        "results": results, "tally": tally, "functions": functions,
        "game": game, "behavior": behavior, "structure": structure,
        "structure_checks": structure_checks, "written": written,
        "total": total, "flags": review_flags(),
    }


def pct(value):
    return f"{round(100 * value)}%"


def csv_line(folder, graded, points):
    name = os.path.basename(os.path.abspath(folder))
    if "error" in graded:
        return [name, "", "", "", "", "0%", "0" if points else "", "",
                "needs manual review: " + graded["error"]]
    failed = sum(1 for _, _, ok, _ in graded["results"] if not ok)
    return [name, pct(graded["functions"]), pct(graded["game"]),
            pct(graded["behavior"]), pct(graded["structure"]),
            pct(graded["total"]),
            f"{graded['total'] * points:.1f}" if points else "",
            len(graded["flags"]), f"{failed} failed checks"]


CSV_HEADER = ["student_folder", "function_checks", "whole_game", "behavior",
              "structure_style", "code_grade", "points", "review_flags",
              "notes"]


def print_report(folder, graded, points, verbose):
    print("CS 104 Project 2 grader")
    print(f"Folder: {os.path.abspath(folder)}")
    if "error" in graded:
        print(f"\nCannot run checks: {graded['error']}")
        print("Code grade: 0% (needs manual review)")
        return
    results = graded["results"]

    print("\nFUNCTION COVERAGE")
    print(f"{'Function':<24}{'Written':<13}{'Called by':<30}Function checks")
    for name, written, used, behavior in coverage_rows(results):
        print(f"{name:<24}{written:<13}{used:<30}{behavior}")

    print("\nRESULTS")
    for section in (SECTION_BEHAVIOR, SECTION_GAME, SECTION_STRUCTURE):
        passed, total = graded["tally"].get(section, (0, 0))
        print(f"{section:<22} {passed:>2}/{total:<2} "
              f"({pct(passed / total if total else 0)})")

    print("\nSUGGESTED CODE GRADE")
    print(f"Behavior ({round(100 * WEIGHT_BEHAVIOR)}%)"
          f"             {pct(graded['behavior'])}"
          f"   (function checks {pct(graded['functions'])},"
          f" whole game {pct(graded['game'])})")
    print(f"Structure and style ({round(100 * WEIGHT_STRUCTURE)}%)"
          f"  {pct(graded['structure'])}"
          f"   (checks {pct(graded['structure_checks'])} x "
          f"{graded['written']}/{len(STUDENT_FUNCS)} functions written)")
    line = f"Code grade                 {pct(graded['total'])}"
    if points:
        line += f"   =  {graded['total'] * points:.1f} / {points:g} points"
    print(line)
    print("(A suggestion only. Read the failures below before you record it."
          " Late penalty and video grade are not included.)")

    for section in (SECTION_BEHAVIOR, SECTION_GAME, SECTION_STRUCTURE):
        failed = [(n, m) for s, n, ok, m in results if s == section and not ok]
        if failed:
            print(f"\n--- {section}: needs attention ---")
            for name, message in failed:
                print(f"FAIL  {name}")
                print(f"      {message}")
        if verbose:
            passed = [n for s, n, ok, m in results if s == section and ok]
            if passed:
                print(f"\n--- {section}: passed ---")
                for name in passed:
                    print(f"PASS  {name}")

    print("\nSUBMISSION CHECKLIST (not graded here)")
    readme = os.path.join(FOLDER, "README.md")
    has_link = False
    if os.path.isfile(readme):
        with open(readme, encoding="utf-8") as handle:
            has_link = bool(re.search(r"https?://\S+", handle.read()))
    has_start = os.path.isfile(os.path.join(FOLDER, "start.py"))
    print(f"  start.py present:            {'yes' if has_start else 'NO'}")
    print(f"  video link found in README:  {'yes' if has_link else 'NO'}"
          " (watch the video to grade it)")

    if graded["flags"]:
        print("\n--- Review flags (conversation starters, not penalties) ---")
        for line_number, label in graded["flags"]:
            print(f"line {line_number}: uses {label}")


def run_batch(root, points):
    root = os.path.abspath(root)
    folders = sorted(d for d in os.listdir(root)
                     if os.path.isfile(os.path.join(root, d, "rps.py")))
    if not folders:
        print(f"No student folders with an rps.py found in {root}")
        return
    rows = []
    for name in folders:
        cmd = [sys.executable, os.path.abspath(__file__),
               os.path.join(root, name), "--csv"]
        if points:
            cmd += ["--points", str(points)]
        try:
            done = subprocess.run(cmd, capture_output=True, text=True,
                                  timeout=BATCH_TIMEOUT_SECONDS)
            row = next(csv.reader([done.stdout.strip().splitlines()[-1]]))
        except Exception as error:
            row = [name, "", "", "", "", "0%", "", "",
                   f"needs manual review: grader problem ({error})"]
        rows.append(row)
        print(f"{name:<32} {row[5]:>5}   {row[8]}")
    out_path = os.path.join(root, "grades.csv")
    with open(out_path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(CSV_HEADER)
        writer.writerows(rows)
    print(f"\nWrote {out_path}")


def main():
    argv = sys.argv[1:]
    points = None
    if "--points" in argv:
        index = argv.index("--points")
        points = float(argv[index + 1])
        del argv[index:index + 2]
    verbose = "--verbose" in argv
    as_csv = "--csv" in argv
    batch = "--batch" in argv
    args = [a for a in argv if not a.startswith("--")]

    if batch:
        run_batch(args[0] if args else os.getcwd(), points)
        return

    folder = args[0] if args else os.getcwd()
    graded = grade_folder(folder)
    if as_csv:
        writer = csv.writer(sys.stdout, lineterminator="\n")
        writer.writerow(csv_line(folder, graded, points))
        return
    print_report(folder, graded, points, verbose)


if __name__ == "__main__":
    main()
