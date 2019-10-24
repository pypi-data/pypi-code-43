# This script must be run with `python -m wizcoin`,
# and not with `python __main__.py`.
import wizcoin

print('Wizard Currency Valuation Program')
galleons = input('Enter number of galleons:')
sickles  = input('Enter number of sickles: ')
knuts    = input('Enter number of knuts:   ')

bag = wizcoin.CoinBag(int(galleons), int(sickles), int(knuts))

print('The value of %s is: %s' % (bag, bag.value))
