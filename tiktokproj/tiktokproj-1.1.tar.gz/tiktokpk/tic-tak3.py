from random import choice
from platform import system
from time import sleep
import os

user_sign = 'X'
random_sign = 'O'
# noinspection SpellCheckingInspection
prevselected = 0


# noinspection PyUnusedLocal,PyBroadException,PyBroadException,PyBroadException,SpellCheckingInspection,SpellCheckingInspection,SpellCheckingInspection,PyUnboundLocalVariable
class TikTok:

    def __init__(self):
        pass

    @staticmethod
    def osconsoleclean():
        if system().upper() == "WINDOWS":
            os.system('cls')
        elif system().upper() == "UNIX":
            os.system('clear')
        else:
            pass

    @staticmethod
    def displayboard(board):
        #
        # the function accepts one parameter containing the board's current status
        # and prints it out to the console
        #
        print('   |   |')
        print(' ' + board[7] + ' | ' + board[8] + ' | ' + board[9])
        print('   |   |')
        print('-----------')
        print('   |   |')
        print(' ' + board[4] + ' | ' + board[5] + ' | ' + board[6])
        print('   |   |')
        print('-----------')
        print('   |   |')
        print(' ' + board[1] + ' | ' + board[2] + ' | ' + board[3])
        print('   |   |')

    # noinspection SpellCheckingInspection
    @staticmethod
    def diamatrix(board, prevselectedarg):
        """this is only when the user starts and also when computer responds 1st two steps then
        and has any of the corner cell or center cell clicked then
        more obviously the next selection should be either the opposite corner sides or center
        rule will list [1,3] [7,9] priority for 5 if available
        """
        r1 = ['1', '3']
        r2 = ['7', '9']
        r3 = ['5']
        # print("inside diamatrix prev selected value is ", prevSelected)
        chancestaken = board.count(user_sign) + board.count(random_sign)
        # noinspection SpellCheckingInspection
        randomlist = []
        if chancestaken <= 3:
            # it means the game is in the starting phases
            if prevselectedarg == 0:
                # computer has started the game so it should pick at one of the diagonal or x in random so the program
                # should return the selection list
                randomlist = r1 + r2 + r3
            elif board.count(user_sign) == 1 and board.count(random_sign) == 0:

                if prevselectedarg in [1, 3, 7, 9]:
                    randomlist = ['5']
            elif board.count(user_sign) == 1 and board.count(random_sign) <= 2:

                # user has initiated the game
                if str(prevselectedarg) in r1:
                    randomlist = r2 + r3
                elif str(prevselectedarg) in r2:
                    randomlist = r1 + r3
                elif str(prevselectedarg) in r3:
                    randomlist = r1 + r2
                else:
                    randomlist = []

        else:
            randomlist = []
        return randomlist

    # noinspection PyUnboundLocalVariable
    def entermove(self, board):
        #
        # the function accepts the board current status, asks the user about their move,
        # checks the input and updates the board according to the user's decision
        #
        # Lets the player type which letter they want to be.
        cnt = 0
        global prevselected
        availlist = [x for x in board if x in ['1', '2', '3', '4', '5', '6', '7', '8', '9']]
        while True:
            cnt += 1
            inputbool = True
            while inputbool:
                inputnum = input("Enter the respective number available: ")
                try:
                    markedcell = int(inputnum)
                    inputbool = False
                except Exception:
                    print("You have not entered the digits required, please enter the number available. ")

            if isinstance(markedcell, int):
                if str(markedcell) in availlist:

                    board[markedcell] = user_sign
                    self.osconsoleclean()
                    self.displayboard(board)
                    print("User marked box {}".format(markedcell))
                    prevselected = markedcell
                    break
                else:
                    print("Number should be selected from the one available")
                    continue
            else:
                if cnt == 3:
                    print("You did not fulfill the requirement in 3 attempts, forcing you out of game")
                    break
                print("only acceptable value is 0-9, enter the one available")

    def autoselectbox(self, board, argpreselected):

        liforrandom = []
        num = argpreselected

        try:
            try:
                liforrandom = self.diamatrix(board, prevselected)
            except Exception:
                pass

            if not liforrandom:
                pass
            else:
                raise KeyError

            l1 = [1, 2, 3]
            l2 = [1, 4, 7]
            l3 = [1, 5, 9]
            l4 = [3, 6, 9]
            l5 = [7, 8, 9]
            l6 = [7, 5, 3]
            l7 = [4, 5, 6]
            l8 = [8, 5, 2]

            di = {}
            if num in l1:
                di["l1"] = l1
            if num in l2:
                di["l2"] = l2
            if num in l3:
                di["l3"] = l3
            if num in l4:
                di["l4"] = l4
            if num in l5:
                di["l5"] = l5
            if num in l6:
                di["l6"] = l6
            if num in l7:
                di["l7"] = l7
            if num in l8:
                di["l8"] = l8
            # print(di)

            # if somebody mistakenly do not mark you, then we should able to identify ourselves rather than saving
            dmissed = {"l1": l1, "l2": l2, "l3": l3, "l4": l4, "l5": l5, "l6": l6, "l7": l7, "l8": l8}
            dmissed2 = {}

            for k, v in dmissed.items():
                # print("k is :", k)
                newlistmissed = []
                for j in v:
                    # print("type for j :",type(j))
                    if j in board:
                        newlistmissed.append(j)
                    else:
                        # val = board[ j - 1]
                        newlistmissed.append(board[j])

                dmissed2[k] = newlistmissed[:]
                # newList.clear
            if num == 0:
                dm2 = {k: dmissed2[k] for k, v in dmissed2.items()}

            else:
                dm2 = {k: dmissed2[k] for k, v in dmissed2.items() if
                       v.count(random_sign) == 2 and v.count(user_sign) == 0}

            if len(dm2) == 1 or num == 0:

                for k in dm2.values():
                    for j in k:
                        if j != random_sign:
                            # also check that it is not in the list
                            if j not in liforrandom:
                                liforrandom.append(j)

                raise KeyError

            # finished saving

            d2 = {}

            for k, v in di.items():
                newlist = []
                for j in v:
                    # print("type for j :",type(j))
                    if j in board:
                        newlist.append(j)
                    else:
                        # val = board[ j - 1]
                        newlist.append(board[j])

                d2[k] = newlist[:]

            # steps to filter the rules
            # print("di build  before: ", di)
            d21 = {k: d2[k] for k, v in d2.items() if v.count(user_sign) + v.count(random_sign) != 3}
            # rules further filtered to remove all the list which are complete or 3
            # if this is randoms two then this should be the priorty1
            d2q = {k: d21[k] for k, v in d21.items() if v.count(random_sign) == 2}
            if len(d2q) >= 1:
                for k in d2q.values():
                    for j in k:
                        if j != random_sign:
                            # also check that it is not in the list
                            if j not in liforrandom:
                                liforrandom.append(j)

                if len(liforrandom) != 0:
                    raise KeyError

            #   if it is met then exist with the process

            d2x = {k: d21[k] for k, v in d21.items() if v.count(user_sign) == 2}
            if len(d2x) >= 1:
                # liForRandom = [j for j in [k for k in d2X.values()] if j not in (6,7)]
                for k in d2x.values():
                    for j in k:
                        if j != user_sign:
                            # and also it is not already added to list
                            if j not in liforrandom:
                                liforrandom.append(j)

                # print(liForRandom)
                if len(liforrandom) != 0:
                    raise KeyError
            #     if this has met then exit the process with the list
            # if the process continues it means that there are many available for selection
            # so we can build the collection for selection from rest of the list where there is one entry
            # or two mix entry
            d2m = {k: d2[k] for k, v in d21.items() if v.count(user_sign) + v.count(random_sign) == 2}
            if len(d2m) >= 1:
                for k in d2m.values():
                    for j in k:
                        if j not in (user_sign, random_sign):
                            # when the number is not in the board it means it has been taken
                            if j not in liforrandom:
                                liforrandom.append(j)

            d2r = {k: d21[k] for k, v in d21.items() if v.count(user_sign) + v.count(random_sign) < 2}
            if len(d2r) >= 1:

                for k in d2r.values():
                    for j in k:
                        if j not in (user_sign, random_sign):
                            if j not in liforrandom:
                                liforrandom.append(j)

            if not liforrandom:

                # here we need to work again to search from all the available rules
                dmissed2 = {}

                for k, v in dmissed.items():
                    newlistmissed = []
                    for j in v:

                        if j in board:
                            newlistmissed.append(j)
                    dmissed2[k] = newlistmissed[:]

                dm2 = {k: dmissed2[k] for k, v in dmissed2.items()}
                if not dm2:

                    for k in dm2.values():
                        for j in k:
                            if j not in (random_sign, user_sign):
                                # also check that it is not in the list
                                if j not in liforrandom:
                                    liforrandom.append(j)

                    raise KeyError
                # finished here

        except KeyError:
            pass
        finally:
            return liforrandom

    #
    # the function browses the board and builds a list of all the free squares;
    # the list consists of tuples, while each tuple is a pair of row and column numbers
    #
    @staticmethod
    def victoryfor(board):
        """
        victoryfor
        :param board:
        :return:
        """
        sign = "N"
        # rules for win will be

        if (board[1] == user_sign and board[2] == user_sign and board[3] == user_sign) or (
                board[1] == random_sign and board[2] == random_sign and board[3] == random_sign):
            sign = board[1]
        elif (board[1] == user_sign and board[4] == user_sign and board[7] == user_sign) or (
                board[1] == random_sign and board[4] == random_sign and board[7] == random_sign):
            sign = board[1]
        elif (board[1] == user_sign and board[5] == user_sign and board[9] == user_sign) or (
                board[1] == random_sign and board[5] == random_sign and board[9] == random_sign):
            sign = board[1]
        elif (board[3] == user_sign and board[6] == user_sign and board[9] == user_sign) or (
                board[3] == random_sign and board[6] == random_sign and board[9] == random_sign):
            sign = board[3]
        elif (board[7] == user_sign and board[8] == user_sign and board[9] == user_sign) or (
                board[7] == random_sign and board[8] == random_sign and board[9] == random_sign):
            sign = board[7]
        elif (board[7] == user_sign and board[5] == user_sign and board[3] == user_sign) or (
                board[7] == random_sign and board[5] == random_sign and board[3] == random_sign):
            sign = board[7]
        elif (board[4] == user_sign and board[5] == user_sign and board[6] == user_sign) or (
                board[4] == random_sign and board[5] == random_sign and board[6] == random_sign):
            sign = board[4]
        elif (board[8] == user_sign and board[5] == user_sign and board[2] == user_sign) or (
                board[8] == random_sign and board[5] == random_sign and board[2] == random_sign):
            sign = board[8]
        else:
            sign = "N"

        return sign

    # the function analyzes the board status in order to check if
    # the player using 'O's or 'X's has won the game
    #

    def drawmove(self, board):
        """
        the function draws the computer's move and updates the board
        global prevselected
        :param board:
        :return:
        """
        availlist = [x for x in board if x in ['1', '2', '3', '4', '5', '6', '7', '8', '9']]

        randlist = self.autoselectbox(board, prevselected)

        rangenotfound = True

        while rangenotfound:

            if len(randlist) == 1:

                numselected = randlist[0]
                board[int(numselected)] = random_sign
                rangenotfound = False
                break

            else:
                numselected = choice(randlist)

                if numselected in availlist:
                    board[int(numselected)] = random_sign
                    rangenotfound = False
                    break
        self.osconsoleclean()
        self.displayboard(board)
        # noinspection PyUnboundLocalVariable
        print("Computer marked box {}".format(numselected))

    def startgame(self):

        while True:
            try:
                global prevselected
                prevselected = 0
                self.osconsoleclean()
                board = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
                self.displayboard(board)
                inputbool = True
                cnt = 0
                print("Player[X] Computer[O]")

                while inputbool:
                    try:
                        starter = int(input("if you want to start enter 1, else 2 for computer to start: "))
                        if starter not in (1, 2):
                            cnt += 1
                            print("not a valid option, ony three attempt provided, {} option gone".format(cnt))
                            if cnt == 3:
                                print("You are not serious player, throwing you out of game. Start again to continue.")
                                sleep(2)
                                exit(0)
                            continue

                        inputbool = False
                    except Exception:
                        print("valid values are 1(user)/2(computer).")

                for i in range(1, 11, 1):
                    print("Player[X] Computer[O]")
                    if starter == 1:
                        self.entermove(board)
                        starter = 2
                    elif starter == 2:
                        self.drawmove(board)
                        starter = 1

                    availlist = [x for x in board if x in ['1', '2', '3', '4', '5', '6', '7', '8', '9']]

                    # any of the rules met then game over
                    sign = "N"
                    if len(availlist) < 7:
                        sign = self.victoryfor(board)
                        # print("sign returned is {}".format(sign))
                        if sign != "N":
                            if sign == random_sign:
                                winner = "Computer"
                            else:
                                winner = "You"
                            print("victory for {}!!!".format(winner))
                            try:
                                while True:
                                    e = input("Do want to play another game, or want to exit(E(Exit),C(Continue)): ")
                                    if e.upper() == "E":
                                        exit(0)
                                    elif e.upper() == "C":
                                        raise KeyError

                                    else:
                                        print("not a valid option")

                            except KeyError:
                                raise

                    if len(availlist) < 1:
                        print("Match tied")
                        sleep(3)
                        break
                        # exit(0)
            except KeyError:
                continue


newgame = TikTok()
newgame.startgame()
