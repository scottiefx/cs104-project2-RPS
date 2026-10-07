"""
rps.py

Redistributed and modified with permission from the
EECS Department at The University of Michigan, Ann Arbor

Name: Faron Matthews (scottie)

CS 104: Project 2
FALL 2026

Description: a rock-paper-scissors game between two players
"""

# ***********************************************************************
# Constants. Global constants are fine. Global variables are not.
# Use these names in your code instead of typing the raw values.
# ***********************************************************************
COURSE_NAME = "CS 104"
MAX_ROUNDS = 3

ROCK = "r"
PAPER = "p"
SCISSORS = "s"
DEFAULT_MOVE = ROCK

PLAYER_1 = 1
PLAYER_2 = 2
DEFAULT_NAME_1 = "Rocky"
DEFAULT_NAME_2 = "Creed"

DRAW = 0

ERROR_NAME = 1
ERROR_MOVE = 2

PLAY_RPS = 1
PLAY_RPSLS = 2
QUIT_CHOICE = 3

# ***********************************************************************
# The following four functions have already been implemented for you.
# You should use them when writing the other functions, but do not edit
# their implementations. You will find them at the bottom of this file.
# ***********************************************************************

# print_initial_header()
#
# Purpose:     Prints a pretty header to introduce the user to the game.
#
#
# print_menu()
#
# Purpose:     Prints the menu.
#                  "1) Play rock, paper, scissors"
#                  "2) Play rock, paper, scissors, lizard, spock"
#                  "3) Quit"
#              It does NOT print the "Choice --> " prompt. Your
#              get_menu_choice() does that with input().
#
#
# print_error_message(error_number)
#
# Purpose:     If error_number is ERROR_NAME, prints an error message
#              indicating an illegal name was entered.
#              If error_number is ERROR_MOVE, prints an error message
#              indicating an illegal move was entered.
# Parameters:  error_number - what error to be printed
# Constraint:  error_number must be ERROR_NAME or ERROR_MOVE
#
#
# print_closer()
#
# Purpose:     Prints out the final greeting for the program.

# ***********************************************************************
# You must implement all of the following functions. Add your
# implementations below rps() as indicated. The specs below tell you what
# each function must do. Write your own def line and give every function
# a short docstring (one or two lines is fine).
# ***********************************************************************

# get_name(player_number) - DONE!!!!!!!!!!!!!!!
#
# Purpose:     Prompts the user to enter their name. Names entered may
#              have spaces within them.
#                  Example: "Kermit the frog"
#
#              If an empty name is given, this is invalid input, so call
#              print_error_message with ERROR_NAME and return a default
#              name.
#              For player 1, the default name is: Rocky
#              For player 2, the default name is: Creed
# Parameters:  player_number - the player whose name will be assigned
# Constraint:  player_number is either PLAYER_1 or PLAYER_2
# Returns:     the name as a string
# Prompt:      Player 1, enter your name:   (Player 2 for the second)
#
#
# get_menu_choice() - Done!!!!!!!!!!!!!
#
# Purpose:     Prints the menu, and reads the input from the user.
#              Checks to make sure the input is within range for the
#              menu. If it is not, prints "Invalid menu choice".
#              Continues to print the menu and read in input until a
#              valid choice is entered, then returns the user's choice
#              of menu options.
#              A user could type anything at this prompt, not only
#              numbers. Anything other than 1, 2 or 3 is invalid.
# Returns:     the choice as an int (1, 2 or 3)
# Prompt:      Choice -->
# Hint:        input() gives you a string. Check the string first. Cast
#              it to an int once you know it is valid.
#
#
# is_move_good(move) done!!!!!!!!!!!!!!
#
# Purpose:     Checks for valid move. Returns True if and only if move
#              represents a valid move: one of "R", "r", "P", "p", "S",
#              "s". Returns False otherwise.
# Parameters:  move - input provided by user. It is a string but it can
#              be any length, even empty.
# Returns:     True or False
#
#
# get_move(player_name) dome ! q!
#
# Purpose:     Prompts the player for their move and returns it. If an
#              illegal move is entered, call print_error_message with
#              ERROR_MOVE and return rock (DEFAULT_MOVE) as a default.
#              You can assume the user presses Enter after typing.
# Parameters:  player_name - the name of the player being prompted for
#              their move
# Returns:     the move as a string, exactly as typed unless it was
#              invalid
# Prompt:      [player_name], enter your move:
#
#
# is_round_winner(move, opponent_move) ODone!!!!!!!!!!!
#
# Purpose:     Returns True if and only if the player who made move won
#              according to the rules of Rock, Paper, Scissors. Returns
#              False otherwise. A tie is not a win.
# Parameters:  move - the move of the player being checked for a win
#              opponent_move - the move of the opponent
# Constraint:  move and opponent_move must both be valid moves
# Returns:     True or False
#
#
# announce_round_winner(winner_name) - DONEE!!!!
#
# Purpose:     If winner_name is empty, prints a message indicating the
#              round is a draw. Otherwise, prints a congratulatory
#              message to the winner.
# Parameters:  winner_name - the name of the player who won the round
#              (an empty string for a draw)
# Constraint:  winner_name must be the correct winner
# Prompt:      This round is a draw!
#              ------------- OR -------------
#              [winner_name] wins the round!
#
#
# do_round(p1_name, p2_name) DOOONEEEEEEEEEEEEEEEEEEEEEEEEEEEEe
#
# Purpose:     Simulates a complete round of rock, paper, scissors,
#              which consists of three steps:
#                1. Get player 1's move
#                2. Get player 2's move
#                3. Return DRAW if the round was a draw; PLAYER_1 if
#                   player 1 won; PLAYER_2 if player 2 won.
#              It does not announce anything. do_game does that.
# Parameters:  p1_name and p2_name - the names of the respective players
# Returns:     DRAW (0), PLAYER_1 (1) or PLAYER_2 (2)
#
#
# announce_winner(winner_name) -- DOOONEE
#
# Purpose:     If winner_name is empty, prints that there was no winner.
#              Otherwise, prints a congratulatory message to the winner.
# Parameters:  winner_name - the name of the player who won the game
# Prompt:      No winner!
#              ------------- OR -------------
#              Congratulations [winner_name]!
#              You won CS 104 Rock, Paper, Scissors!
#              (use COURSE_NAME for "CS 104")
#
#
# do_game(p1_name, p2_name, game_type) - DONE.
#
# Base Project:
# Purpose:     If game_type is PLAY_RPSLS, prints "Under Construction"
#              to indicate that rock, paper, scissors, lizard, spock has
#              not been implemented. Returns an empty string.
#              Otherwise, plays exactly MAX_ROUNDS rounds of
#              rock-paper-scissors while keeping track of the number of
#              round wins for each player. When a round results in a
#              draw, neither player is the winner, so neither player is
#              awarded a point. All rounds are played, even if one
#              player has already won the game.
#              After each round is played, the round winner (or draw) is
#              announced. Returns the name of the winner or an empty
#              string if the game ended in a draw.
# Parameters:  p1_name and p2_name - the names of the respective players
#              game_type - PLAY_RPS for regular rock, paper, scissors
#              or PLAY_RPSLS for rock, paper, scissors, lizard, spock
# Returns:     the winner's name as a string, or "" for no winner
# Prompt:      Under Construction





# ***********************************************************************
# Add all function implementations below this line.
# We have started is_move_good() for you.
# ***********************************************************************

def is_move_good(move):
    #checks if move is valid ; T/F
    valids = ("R", "r", "P", "p", "S", "s")
    if str(move) in valids:
        return True
    else:
        return False

def get_name(player_number):
#gets name for a player (PLAYER_1 or PLAYER_2), returns as string
    if player_number == PLAYER_1:
        pname = str(input("Player 1, enter your name: "))
        if pname.strip() == "":
            print_error_message(ERROR_NAME)
            pname = DEFAULT_NAME_1
    elif player_number == PLAYER_2:
        pname = str(input("Player 2, enter your name: "))
        if pname.strip() == "":
            print_error_message(ERROR_NAME)
            pname = DEFAULT_NAME_2
    return str(pname)

def get_menu_choice():
# prints menu then returns user choice as an int (1-3)
# invalid input reloads menu and displays error
    print_menu()
    choice = int(input())
    while 0 < choice > 3:
        print("Invalid menu choice.")
        print_menu()
        choice = int(input())
    else:
        return choice

def get_move(player_name):
    #gets input of move for designated player, returns string as written unless invalid
    move = input(f"{player_name}, enter your move: ")
    if is_move_good(move) == False:
        print_error_message(ERROR_MOVE)
        move = DEFAULT_MOVE
    return move

def is_round_winner(move, opponent_move):
    # Evaluates if a move wins the round compared to the opponent's move using RPS logic
    # Turns moves Lowercase
    # can remove move validation if it turns out unused
    winner = False
    if is_move_good(move) == False:
        print_error_message(ERROR_MOVE)
        move = DEFAULT_MOVE
    if is_move_good(opponent_move) == False:
        print_error_message(ERROR_MOVE)
        opponent_move = DEFAULT_MOVE
    move = move.lower()
    opponent_move = opponent_move.lower()
    if move == ROCK:
        if opponent_move == ROCK:
            winner = False
        elif opponent_move == PAPER:
            winner = False
        elif opponent_move == SCISSORS:
            winner = True
    elif move == PAPER:
        if opponent_move == ROCK:
            winner = True
        elif opponent_move == PAPER:
            winner = False
        elif opponent_move == SCISSORS:
            winner = False
    elif move == SCISSORS:
        if opponent_move == ROCK:
            winner = False
        elif opponent_move == PAPER:
            winner = True
        elif opponent_move == SCISSORS:
            winner = False
    return winner

def announce_round_winner(winner_name):
    # Congratulates the winner of the round
    # if name is an empty string, calls a draw
    if winner_name == "":
        print("This round is a draw!")
    else:
        print(f"{winner_name} wins the round!")

def do_round(p1_name, p2_name):
    # goes through the necessary logic for an RPS round
    # asks each player for a move
    # compares the moves and returns a value for the winner
    # DRAW = 0, PLAYER_1 = 1, PLAYER_2 = 2
    p1_move = get_move(p1_name)
    p2_move = get_move(p2_name)
    p1_wins = is_round_winner(p1_move, p2_move)
    p2_wins = is_round_winner(p2_move, p1_move)
    if p1_wins == True:
        return PLAYER_1
    elif p2_wins == True:
        return PLAYER_2
    else:
        return DRAW

def announce_winner(winner_name):
    # Congratulates winner of game
    # Prints "No winner" if input is empty string
    if winner_name == "":
        print()
        print("No winner!")
    else:
        print()
        print(f"Congratulations {winner_name}!\nYou won {COURSE_NAME} Rock, Paper, Scissors!")

def do_game(p1_name, p2_name, game_type):
    # runs a game of RPS.
    # returns the name of the winner in a string, empty if no winner.
    if game_type == PLAY_RPSLS:
        print("Under Construction")
        return ""
    else:
        p1_score = 0
        p2_score = 0
        for i in range(MAX_ROUNDS):
            roundresult = do_round(p1_name, p2_name)
            if roundresult == PLAYER_1:
                p1_score += 1
                announce_round_winner(p1_name)
            elif roundresult == PLAYER_2:
                p2_score += 1
                announce_round_winner(p2_name)
            elif roundresult == DRAW:
                announce_round_winner("")
        winner_name = ""
        if p1_score > p2_score:
            winner_name = p1_name
        elif p2_score > p1_score:
            winner_name = p2_name
        return winner_name

# ***********************************************************************
# DO NOT modify the four functions below.
# ***********************************************************************
def print_initial_header():
    """Prints a pretty header to introduce the user to the game."""
    print("----------------------------------------")
    print("                CS 104")
    print("          Rock, Paper, Scissors")
    print("----------------------------------------")


def print_menu():
    """Prints the menu options (not the prompt)."""
    print()
    print("Menu Options")
    print("------------")
    print("1) Play rock, paper, scissors")
    print("2) Play rock, paper, scissors, lizard, spock")
    print("3) Quit")
    print()


def print_error_message(error_number):
    """Prints the error for ERROR_NAME or ERROR_MOVE."""
    if error_number == ERROR_NAME:
        print()
        print("ERROR: Illegal name given, using default")
        print()
    elif error_number == ERROR_MOVE:
        print()
        print("ERROR: Illegal move given, using default")
    else:
        print("This should never print!")


def print_closer():
    """Prints out the final greeting for the program."""
    print()
    print("----------------------------------------")
    print("           Thanks for playing")
    print("          Rock, Paper, Scissors!")
    print("----------------------------------------")

"""
Available Funcs:
print_initial_header
print_closer
print_error_message
print_menu
is_move_good
get_name
get_menu_choice
get_move
is_round_winner
announce_round_winner
do_round
announce_winner
do_game
"""
def rps():
    # Runs the whole program.
    print_initial_header()
    # Gets names for both players
    p1_name = get_name(PLAYER_1)
    p2_name = get_name(PLAYER_2)
    # Displays menu, gets gametype
    gamemode = get_menu_choice()
    if gamemode == 1:
        gamemode = PLAY_RPS
    elif gamemode == 2:
        gamemode = PLAY_RPSLS
    elif gamemode == 3:
        # Ends function if user quits through the menu
        gamemode == QUIT_CHOICE
        return
    winner = do_game(p1_name, p2_name, gamemode)
    announce_winner(winner)
    print_closer()
    
rps()