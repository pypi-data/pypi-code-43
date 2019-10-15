from __future__ import print_function

ASCII_TEXT = ["""
   _____               _      ______              _          __   ___  
  / ____|             | |    |  ____|            | |        /_ | / _ \ 
 | |  __ _ __ __ _  __| | ___| |__ __ _  __ _ ___| |_  __   _| || | | |
 | | |_ | '__/ _` |/ _` |/ _ \  __/ _` |/ _` / __| __| \ \ / / || | | |
 | |__| | | | (_| | (_| |  __/ | | (_| | (_| \__ \ |_   \ V /| || |_| |
  \_____|_|  \__,_|\__,_|\___|_|  \__,_|\__,_|___/\__|   \_/ |_(_)___/ 
                                                                                                                              
""",
"""
   ___               _        ___               _           _   ___  
  / _ \_ __ __ _  __| | ___  / __\_ _  __ _ ___| |_  __   _/ | / _ \ 
 / /_\/ '__/ _` |/ _` |/ _ \/ _\/ _` |/ _` / __| __| \ \ / / || | | |
/ /_\\| | | (_| | (_| |  __/ / | (_| | (_| \__ \ |_   \ V /| || |_| |
\____/|_|  \__,_|\__,_|\___\/   \__,_|\__,_|___/\__|   \_/ |_(_)___/ 
                                                                     
"""
]

greeting = 'Welcome to "GradeFast v1.0" Interactive Mode'

class GradeFast:
    # TODO: Interactive shell based auto-evaluation
    @staticmethod
    def interactive():
        print(ASCII_TEXT[1])
        print(greeting)

if __name__ == "__main__":
    GradeFast.interactive()
