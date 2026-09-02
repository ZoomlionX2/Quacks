from typing import NamedTuple

FINAL_SCORING_SPACE = 53 # The last scoring space before the spoon

class BoardSpace(NamedTuple):
    ruby: bool          # True = awards a ruby, False = does not award a ruby
    victory_points: int
    money: int

# Look-up table for ruby, victory point, and money values of each space on the board
POT_BOARD_SPACES = (
    BoardSpace(False, 0, 0), BoardSpace(False, 0, 1), BoardSpace(False, 0, 2), BoardSpace(False, 0, 3),
    BoardSpace(False, 0, 4), BoardSpace(True, 0, 5), BoardSpace(False, 1, 6), BoardSpace(False, 1, 7),
    BoardSpace(False, 1, 8), BoardSpace(True, 1, 9), BoardSpace(False, 2, 10), BoardSpace(False, 2, 11),
    BoardSpace(False, 2, 12), BoardSpace(True, 2, 13), BoardSpace(False, 3, 14), BoardSpace(False, 3, 15),
    BoardSpace(True, 3, 15), BoardSpace(False, 3, 16), BoardSpace(False, 4, 16), BoardSpace(False, 4, 17),
    BoardSpace(True, 4, 17), BoardSpace(False, 4, 18), BoardSpace(False, 5, 18), BoardSpace(False, 5, 19),
    BoardSpace(True, 5, 19), BoardSpace(False, 5, 20), BoardSpace(False, 6, 20), BoardSpace(False, 6, 21),
    BoardSpace(True, 6, 21), BoardSpace(False, 7, 22), BoardSpace(True, 7, 22), BoardSpace(False, 7, 23),
    BoardSpace(False, 8, 23), BoardSpace(False, 8, 24), BoardSpace(True, 8, 24), BoardSpace(False, 9, 25),
    BoardSpace(True, 9, 25), BoardSpace(False, 9, 26), BoardSpace(False, 10, 26), BoardSpace(False, 10, 27),
    BoardSpace(True, 10, 27), BoardSpace(False, 11, 28), BoardSpace(True, 11, 28), BoardSpace(False, 11, 29),
    BoardSpace(False, 12, 29), BoardSpace(False, 12, 30), BoardSpace(True, 12, 30), BoardSpace(False, 12, 31),
    BoardSpace(False, 13, 31), BoardSpace(False, 13, 32), BoardSpace(True, 13, 32), BoardSpace(False, 14, 33),
    BoardSpace(True, 14, 33), BoardSpace(False, 15, 35)
)

