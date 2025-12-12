# checkers-engine
CPSC 481 Group Project - KingMaker Checkers Engine
## Directions
1. Make sure you have Python installed.
2. In the terminal, make sure you are pointing to the folder "checkers-engine".
3. Enter `python gui.py` or `python3 gui.py` in the terminal. You will then see the GUI. 
4. To play, click on the red piece and click on the circled blank squares. The circled blank squares signify a legal move. 
5. On the right, you can see options to toggle:
    * Show Best Move (on/off)
    * Forced Capture (on/off)
    * Reset Game
    * Evaluation Function
        *  Simple
        *  Smart
        *  Advanced
    * Depth Scheduler
        *  Static
        *  Iterative Deepening
    * AI Depth (1-20)
    * AI Time Limit (Iterative Deepening Only) [0-10]

## What Each File Does
* **.gitignore** - Git ignored files
* **.python-version** - Python version 3.13
* **LICENSE** - MIT license
* **README.md** - This file; explains how to run our program
* **board.py** - Contains the board game logic and evaluation functions
* **gui.py** - Code for the GUI visualization
* **main.py** - main file
* **minimax.py** - Code for minimax implementation with alpha-beta pruning
* **pyproject.toml**
* **test_board.py** - File for testing purposes
* **uv.lock**

## Libraries Used
* **array** - Used in board.py for memory efficiency. 
   * Link: https://docs.python.org/3/library/array.html
* **tkinter** - Used in gui.py to build the GUI for the checkers board. 
   * Link: https://docs.python.org/3/library/tkinter.html
* **perf_counter (time)** - Used in gui.py to measure AI response time. 
   * Link: https://docs.python.org/3/library/time.html
* **lru_cache (functools)** - Used in minimax.py to cache results from minimax func. More computationally efficient than other options. 
   * Link: https://docs.python.org/3/library/functools.html
* **time (time)** - Used in minimax.py to enforce time limit in IDDFS search. 
   * Link: https://docs.python.org/3/library/time.html
