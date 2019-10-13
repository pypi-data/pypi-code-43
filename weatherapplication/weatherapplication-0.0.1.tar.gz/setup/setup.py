import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utilities.user_input_file import main


if __name__ == '__main__':
    print('******************************************************************')
    print('*                                                                *')
    print('*                        WEATHER API                             *')
    print('*                                                                *')
    print('******************************************************************')

    while 1:
        main()
        print('Press Q for quiting. Else press any other key to continue')
        user_input = input()
        if user_input.lower() == 'q':
            print('Thank you for using the Weather API. ')
            break
