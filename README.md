# Rock, Paper, Scissors

A two-player Rock, Paper, Scissors game for the terminal, written in Python. Players enter their names, pick from a simple menu and play games of three rounds. The player who wins more rounds wins the game.

*Built for CS 104 at Alabama A&M University, Fall 2026.*

## Features

- Two players with their own names
- Three rounds per game, with a winner announced after every round and at the end of the game
- A menu to play another game or quit
- Friendly handling of invalid names, moves and menu choices
- A menu option for a Rock, Paper, Scissors, Lizard, Spock variant (coming soon)

## How to run it

You need Python 3 installed. From the project folder, run:

```
python3 start.py
```

## Project structure

| File | What it does |
|---|---|
| `rps.py` | The game logic, built from small functions that each do one job |
| `start.py` | Starts the game |

## How it is built

The game is broken into small functions for input handling, move validation, scoring, announcements and the game loop. Each function does one job and is documented with a docstring.

## 🛠️ Built with

- Python 3

## note
hii