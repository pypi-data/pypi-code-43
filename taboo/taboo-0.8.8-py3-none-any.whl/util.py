MAX_BUFFER = 65536

# Codes for initialization
INIT = 0
ATTACKER_FEEDBACK = 1
DEFENDER_FEEDBACK = 2

# Codes for word selection
WORD_SELECT = 10
RECEIVED = 11

# Codes for playing game
ATTACK = 20
DEFEND = 21
ACTIVELY_GUESS = 22
BEGIN_GUESS = 23
GUESS_LIST = 24
GUESS = 25

# Codes for game ends
GAME_ENDS = 30
ATTACKER_WIN = 31
DEFENDER_WIN = 32
DRAW = 33
ATTACKER_CORRUPT = 34
DEFENDER_CORRUPT = 35
BAD_ATTACKER = 36
BAD_DEFENDER = 37

END_CODE_SET = {GAME_ENDS, ATTACKER_WIN, DEFENDER_WIN, DRAW, ATTACKER_CORRUPT, DEFENDER_CORRUPT, BAD_ATTACKER,
                BAD_DEFENDER}

import time


def time_to_str():
    return time.strftime('%Y_%m_%d_%H_%M_%S', time.localtime(time.time()))
