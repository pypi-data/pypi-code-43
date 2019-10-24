import random, time
class card:
    def __init__(self, val, fullName):
        self.val = val
        self.fullName = fullName
class ace(card):
    val2 = 1
plr = [0]
dlr = [0]
def addToHand(hand):
    crd = deck[random.randint(0, len(deck) - 1)]
    hand.insert(-2, crd)
    deck.remove(crd)
    hand[-1] = 0
    for i in hand[0:-1]:
        hand[-1] += i.val
    if hand[-1] > 21:
        for i in hand[0:-1]:
            if isinstance(i, ace):
                hand[-1] -= 10
def clrHand(hnd):
    for i in hnd[0:-1]:
        hnd.remove(i)
    hnd[-1] = 0
def fullHand(hnd):
    cards = list(i.fullName for i in hnd[:-1])
    return(str(', '.join(cards)))
def dlrHand():
    cards = list(i.fullName for i in dlr[1:-1])
    print("Dealer's Cards: [unknown], " + ', '.join(cards))
def prompt():
    mov = input('\nhit, stay, or see cards? ')
    if mov == 'hit' or mov == 'stay' or mov == 'see cards':
        return mov
    else:
        return(prompt())
def plrTurn():
    addToHand(plr)
    addToHand(plr)
    addToHand(dlr)
    addToHand(dlr)
    print('\nYour Cards: ' + fullHand(plr))
    dlrHand()
    if plr[-1] == 21:
        print('BLACKJACK!')
    else:
        print('\nYour Turn!')
        mov = prompt()
        while mov != 'stay':
            if mov == 'hit':
                addToHand(plr)
                print('Your Cards: ' + fullHand(plr))
            if mov == 'see cards':
                print('Your Cards: ' + fullHand(plr))
                dlrHand()
            if plr[-1] == 21:
                print('BLACKJACK!')
                break
            if plr[-1] > 21:
                print('BUST!')
                break
            mov = prompt()
        print('Total: ' + str(plr[-1]))
def dlrTurn():
    print("\nDealer's Turn!")
    time.sleep(2)
    print("Dealer's Cards: " + fullHand(dlr))
    time.sleep(2)
    if plr[-1] > 21:
        print('Dealer Stays!')
    else:
        while dlr[-1] <= 16:
            addToHand(dlr)
            print("Dealer's Cards: " + fullHand(dlr))
            time.sleep(2)
        if dlr[-1] <= 21:
            print('Dealer Stays!')
        if dlr[-1] > 21:
            print('Dealer Busts!')
    print('Total: ' + str(dlr[-1]))
aS = ace(11, "Ace of Spades")
wS = card(2, "Two of Spades")
hS = card(3, "Three of Spades")
fS = card(4, "Four of Spades")
vS = card(5, "Five of Spades")
xS = card(6, "Six of Spades")
sS = card(7, "Seven of Spades")
eS = card(8, "Eight of Spades")
nS = card(9, "Nine of Spades")
tS = card(10, "Ten of Spades")
jS = card(10, "Jack of Spades")
qS = card(10, "Queen of Spades")
kS = card(10, "King of Spades")
aC = ace(11, "Ace of Clubs")
wC = card(2, "Two of Clubs")
hC = card(3, "Three of Clubs")
fC = card(4, "Four of Clubs")
vC = card(5, "Five of Clubs")
xC = card(6, "Six of Clubs")
sC = card(7, "Seven of Clubs")
eC = card(8, "Eight of Clubs")
nC = card(9, "Nine of Clubs")
tC = card(10, "Ten of Clubs")
jC = card(10, "Jack of Clubs")
qC = card(10, "Queen of Clubs")
kC = card(10, "King of Clubs")
aD = ace(11, "Ace of Diamonds")
wD = card(2, "Two of Diamonds")
hD = card(3, "Three of Diamonds")
fD = card(4, "Four of Diamonds")
vD = card(5, "Five of Diamonds")
xD = card(6, "Six of Diamonds")
sD = card(7, "Seven of Diamonds")
eD = card(8, "Eight of Diamonds")
nD = card(9, "Nine of Diamonds")
tD = card(10, "Ten of Diamonds")
jD = card(10, "Jack of Diamonds")
qD = card(10, "Queen of Diamonds")
kD = card(10, "King of Diamonds")
aH = ace(11, "Ace of Hearts")
wH = card(2, "Two of Hearts")
hH = card(3, "Three of Hearts")
fH = card(4, "Four of Hearts")
vH = card(5, "Five of Hearts")
xH = card(6, "Six of Hearts")
sH = card(7, "Seven of Hearts")
eH = card(8, "Eight of Hearts")
nH = card(9, "Nine of Hearts")
tH = card(10, "Ten of Hearts")
jH = card(10, "Jack of Hearts")
qH = card(10, "Queen of Hearts")
kH = card(10, "King of Hearts")
deck = [aS, wS, hS, fS, vS, xS, sS, eS, nS, tS, jS, qS, kS, aC, wC, hC, fC, vC, xC, sC, eC, nC, tC, jC, qC, kC, aD, wD, hD, fD, vD, xD, sD, eD, nD, tD, jD, qD, kD, aH, wH, hH, fH, vH, xH, sH, eH, nH, tH, jH, qH, kH]
