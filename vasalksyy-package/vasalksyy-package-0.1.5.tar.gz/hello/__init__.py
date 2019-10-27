import random

play = 'yes'

given_numbers = []
random_numbers = []

def random_numbers():
    while play == 'yes':
        for i in range(6):
            given_numbers.append(int(input(f"podaj liczbe numer {str(i+1)} : ")))
            random_numbers.append(random.randint(1, 50))
        hitting = 0
