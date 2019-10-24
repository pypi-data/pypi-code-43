from utils import utils
winCount = 0
lossCount = 0
tieCount = 0
def getBet():
    try:
        bet = int(input('What would you like to bet? '))
        if bet > int(score):
            print("You don't have enough points!")
            return(getBet())
        if bet < 1:
            print("Nice try")
            return(getBet())
        else:
            return(bet)
    except:
        return getBet()
while len(utils.deck) > 16:
    scr = open('Score/score.txt', 'r')
    score = int(scr.read())
    if input('Would you like to play? ').lower() != 'yes':
        break
    if score == 0:
        print('You ran out of points, so your score is reset.')
        score = 100
    print('Your current score: ' + str(score))
    bet = getBet()
    utils.plrTurn()
    utils.dlrTurn()
    scrw = open('Score/score.txt', 'w')
    if utils.plr[-1] > utils.dlr[-1] and utils.plr[-1] <= 21:
        print('\n\nYou Win!\n\n')
        winCount += 1
        if utils.plr[-1] == 21:
            scrw.write(str(score + (2 * bet)))
        else:
            scrw.write(str(score + bet))
    elif utils.plr[-1] < utils.dlr[-1] and utils.dlr[-1] <= 21:
        print('\n\nThe Dealer Wins!\n\n')
        lossCount += 1
        scrw.write(str(score - bet))
    elif utils.plr[-1] == utils.dlr[-1] and utils.dlr[-1] <= 21:
        print('\n\nTie!\n\n')
        tieCount += 1
        scrw.write(str(score))
    elif utils.plr[-1] > 21 and utils.dlr[-1] <= 21:
        print('\n\nThe Dealer Wins!\n\n')
        lossCount += 1
        scrw.write(str(score - bet))
    elif utils.plr[-1] <= 21 and utils.dlr[-1] > 21:
        print('\n\nYou Win!\n\n')
        winCount += 1
        scrw.write(str(score + bet))
    else:
        print('\n\nTie!\n\n')
        scrw.write(score)
        tieCount += 1
    utils.clrHand(utils.plr)
    utils.clrHand(utils.dlr)
    scr.close()
    scrw.close()
if not len(utils.deck) > 16:
    print('Good Game! Out of cards.')
else:
    print('Good Game!')
print('Wins: {0}, Losses: {1}, Ties: {2}'.format(winCount, lossCount, tieCount))
input('\nPress "Enter" to exit')