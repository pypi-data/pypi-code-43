import os
import shutil
# import stat
import sys
import time

"""
JUNKYARD IS A COMPILATION OF TID BIT (probably actual CERTIFIED *garbage*) HELPERS 
CRAFTED DURING PROJECTS TO BE REUSED AT A LATER TIME BY THE AUTHOR.

THIS IS THE HANDLER FILE, OTHERWISE KNOWN AS THE GARBAGE BASKET 
THIS IS WHERE THE DIFFERENT CLASSES AND METHODS/FUNCTIONS CAN BE FOUND 
WITHIN THE MODULE
"""


# DIAGNOSTICS HANDLER
class DiagnosticHandler:
    #
    def __init__(self):
        print("DiagnosticHandler() Initialized")

    # staticmethod for testing the speed difference of two functions
    #
    # usage example:
    # speed_test(example_function(), example_function2())
    #
    # additional arguments:
    # # NUMBER OF TESTS TO RUN IN LOOPS
    # n_tests = 100
    # # FLOATING PRECISION FOR AVERAGES
    # float_precision = 3
    # # TIME TO REST BETWEEN SUBJECT TESTS
    # intermission_time = 1  # seconds
    # loop_time = 0.1  # seconds
    @staticmethod
    def speed_test(subject_1=None, subject_2=None,
                   n_tests=100, float_precision=8, intermission_time=1, loop_time=0.1):

        # make sure subjects have values
        if subject_1 is None:
            print("subject_1 is empty")
            return
        if subject_2 is None:
            print("subject_2 is empty")
            return

        # SUBJECT 1 TEST LOOP
        print("TESTING SUBJECT 1")
        subject_1_times = []
        # start loop for n_tests times
        for x in range(n_tests):
            # start timer
            timer_start = time.perf_counter()
            # call our first test subject from arguments
            subject_1  # will appear dirty, but it works well
            # stop timer
            timer_stop = time.perf_counter()

            # get total time
            subject_1_time = timer_stop - timer_start
            print(f"{subject_1_time} seconds")
            # and append it to our times list
            subject_1_times.append(subject_1_time)
            # take a break
            time.sleep(loop_time)

        # TAKE A BREAK!
        print("")
        print("-- intermission --")
        print("")
        time.sleep(intermission_time)

        # SUBJECT 2 TEST LOOP
        print("TESTING SUBJECT 2")
        subject_2_times = []
        for x in range(n_tests):
            # start timer
            timer_start = time.perf_counter()
            # call our second test subject from arguments
            subject_2  # will appear dirty, but it works well
            # stop timer
            timer_stop = time.perf_counter()

            # get total time
            subject_2_time = timer_stop - timer_start
            print(f"{subject_2_time} seconds")
            # and append it to our times list
            subject_2_times.append(subject_2_time)
            # take a break
            time.sleep(loop_time)

        # get averages of tests
        subject_1_average = round(sum(subject_1_times) / len(subject_1_times), float_precision)
        subject_2_average = round(sum(subject_2_times) / len(subject_2_times), float_precision)

        # get win times for each subject using list comprehensions
        # subject 1
        subject_1_wins = [subject_1_times[index] for index, e in enumerate(subject_1_times)
                          if subject_1_times[index] < subject_2_times[index]]
        #
        # subject 2
        subject_2_wins = [subject_2_times[index] for index, e in enumerate(subject_2_times)
                          if subject_1_times[index] > subject_2_times[index]]

        # get number of wins
        subject_1_n_wins = len(subject_1_wins)
        subject_2_n_wins = len(subject_2_wins)

        # create a line space
        print("")

        # print Subject wins and average time
        print(f"Subject 1 Wins: {subject_1_n_wins} ({round((subject_1_n_wins / n_tests) * 100, 2)}%) with an "
              f"average time of {subject_1_average} seconds")
        print(f"Subject 2 Wins: {subject_2_n_wins} ({round((subject_2_n_wins / n_tests) * 100, 2)}%) with an"
              f" average time of {subject_2_average} seconds")

        # create a line space
        print("")

        # compare subject number of wins
        if subject_1_n_wins > subject_2_n_wins:
            print(f"SUBJECT 1 HAS THE MOST WINS ({subject_1_n_wins} / {n_tests})")
        elif subject_1_n_wins < subject_2_n_wins:
            print(f"SUBJECT 2 HAS THE MOST WINS ({subject_2_n_wins} / {n_tests})")
        elif subject_1_n_wins == subject_2_n_wins:
            print("SUBJECT 1 AND SUBJECT 2 HAVE THE SAME NUMBER OF WINS - TIE!")

        # compare subject average times
        if subject_1_average < subject_2_average:
            print(f"SUBJECT 1 HAD THE FASTEST AVERAGE @ {subject_1_average} SECONDS")
            print(f"or {subject_2_average / subject_1_average} times Subject 2's average")
        elif subject_1_average > subject_2_average:
            print(f"SUBJECT 2 HAD THE FASTEST AVERAGE @ {subject_2_average} SECONDS")
            print(f"or {subject_1_average / subject_2_average} times Subject 1's average")
        elif subject_1_average == subject_2_average:
            print(f"SUBJECT 1 AND SUBJECT 2 HAVE THE SAME AVERAGE @ {subject_1_average} SECONDS")


# ON HOLD
# class to manage encryption and decryption of bytes files
# TODO: ENCRYPTION?
class CryptoHandler:
    def __init__(self):
        pass


# WORK IN PROGRESS
# class to manage basic file system tasks in a safe and reliable way.
#
# TODO: (?)NEXT COMMIT(?) - EXPAND FUNCTIONALITY OF FILEHANDLER?
#                               - CHMOD (ON HOLD)
#                               - CHDIR / CD (Change Directory) (ON HOLD)
#                               - COPY (ON HOLD)
#                               - MOVE (ON HOLD)
#                               - FIND(?) (ON HOLD)
class FileHandler:
    # WORKING
    # Class Initializer method.
    # establishes various class wide variables for now
    #
    # *all methods in class can be silenced with silent=True*
    # * BUT OTHERWISE HAVE INFORMATIVE PRINT STATEMENTS *
    #
    def __init__(self, silent=False):
        self.class_name = "FileHandler()"
        # if silent is false
        if not silent:
            # do a sys.stdout.write and flush at top and bottom to print on same line
            sys.stdout.write(f"\r{self.class_name} initializing")
            sys.stdout.flush()
        
        # initialize all of the class wide variables
        # standard read/write/append modes
        self.write_modes = ("w", "write", "Write", "WRITE")
        self.write_append_modes = ("a", "append", "Append", "APPEND")
        self.read_modes = ("r", "read", "Read", "READ")
        # TODO: do we need this?
        #       do we want to add the r+ / rb+ functionality, or do our current
        #       tools suffice?
        self.read_write_modes = ("r+", "R+", "rw", "RW", "readwrite", "READWRITE")

        # bytes modes
        self.write_bytes_modes = ("wb", "WB", "w_bytes", "W_bytes")
        self.write_append_bytes_modes = ("ab", "AB", "a_bytes", "A_bytes")
        self.read_bytes_modes = ("rb", "RB", "r_bytes", "R_bytes")
        # TODO: do we need this?
        #       do we want to add the r+ / rb+ functionality, or do our current
        #       tools suffice?
        self.read_write_bytes_modes = ("rb+", "RB+", "rw_bytes", "RW_bytes")

        # CHMOD modes
        # TODO: set up variables for our CHMOD
        self.chmod_modes = ("ISUID", "ISGID", "ENFMT", "ISVTX", "IREAD", "IWRITE", "IEXEC", "IRWXU", "IWUSR", "IXUSR"
                            "IRWXG", "IRGRP", "IWGRP", "IXGRP", "IRWXO", "IROTH", "IWOTH", "IXOTH")
        # chmod description dictionary
        self.chmod_descriptions = {"ISUID": "Set user ID on execution.", "ISGID": "Set group ID on execution.",
                                   "ENFMT": "Record locking enforced.",  "ISVTX": "Save text image after execution.",
                                   "IREAD": "Read by owner.",            "IWRITE": "Write by owner.",
                                   "IEXEC": "Execute by owner.",         "IRWXU": "Read, write, and execute by owner.",
                                   "IRUSR": "Read by owner.",            "IWUSR": "Write by owner.",
                                   "IXUSR": "Execute by owner.",         "IRWXG": "Read, write, and execute by group.",
                                   "IRGRP": "Read by group.",            "IWGRP": "Write by group.",
                                   "IXGRP": "Execute by group.",         "IRWXO": "Read, write, and execute by others.",
                                   "IROTH": "Read by others.",           "IWOTH": "Write by others.",
                                   "IXOTH": "Execute by others."}

        # if silent is false
        if not silent:
            # second stdout.write and flush to clear old message
            # and replace it with a new one
            sys.stdout.write(f"\r{self.class_name} initialized \n")
            sys.stdout.flush()

    # WORKING
    # method to return True or False as to whether a directory exists
    #
    # has 2 possible returns (True, False)
    # # True = directory exists
    # # False = directory does not exist
    #
    def is_directory(self, directory, silent=False):
        # load the return of os.path.isdir() into a variable
        # to later be returned as True or False
        try:
            exists = os.path.isdir(directory)
        # account for invalid input in directory
        except TypeError:
            if not silent:
                print(f"{self.class_name}: (({os.getcwd()}\\<{directory}>)) triggered a TypeError in is_directory()")
                print("check your input")
            # and give the exists bool to False
            exists = False

        # if silent is false
        if not silent:
            # and the directory exists
            if exists:
                # say found
                print(f"{self.class_name}: ({os.getcwd()}\\<{directory}>) found")
            # and if the file does not exist
            else:
                # say 'I'm sorry for your loss' -- I mean -- "not found"
                print(f"{self.class_name}: ({os.getcwd()}\\<{directory}>) not found")

        # return the True False nature of our exists variable
        return exists

    # WORKING
    # method to return True or False as to whether a file exists
    #
    # has 2 possible returns (True, False)
    # # True = file exists
    # # False = file does not exist
    #
    def is_file(self, filename, silent=False):
        # load the True/False os.path.isfile() return into our exists variable
        # to later be returned as a file exists or file doesnt exist
        exists = os.path.isfile(filename)

        # if we can blab
        if not silent:
            # and the file exists
            if exists:
                # tell our super fans that files are found, and that
                # they are indeed real
                # -- just like ufo's --
                print(f"{self.class_name}: ({os.getcwd()}\\<{filename}>) found")
            # or if the file doesn't exist
            else:
                # file not found
                print(f"{self.class_name}: ({os.getcwd()}\\<{filename}>) not found")

        # return the True False nature of our exists variable
        return exists

    # # TODO: MAKE CHANGE DIRECTORY METHOD
    # def change_directory(self, destination):
    #     pass
    #
    # # TODO: MAKE CHMOD METHOD
    # def chmod(self, filename, mode, silent=False):
    #     """
    #     help test
    #     """
    #
    #     # CHMOD MODES
    #     if mode == "help":
    #         print(f"{self.chmod_descriptions}")
    #
    #     if mode in self.chmod_modes:
    #         _mode = None
    #
    #         # Set user ID on execution
    #         if mode == "ISUID":
    #             _mode = stat.S_ISUID
    #
    #         # Set group ID on execution
    #         elif mode == "ISGID":
    #             _mode = stat.S_ISGID
    #
    #         # Record locking enforced
    #         elif mode == "ENFMT":
    #             _mode = stat.S_ENFMT
    #
    #         # Save text image after execution
    #         elif mode == "ISVTX":
    #             _mode = stat.S_ISVTX
    #
    #         # Read by owner
    #         elif mode == "IREAD":
    #             _mode = stat.S_IREAD
    #
    #         # Write by owner
    #         elif mode == "IWRITE":
    #             _mode = stat.S_IWRITE
    #
    #         # Execute by owner
    #         elif mode == "IEXEC":
    #             _mode = stat.S_IEXEC
    #
    #         # Read, write, and execute by owner
    #         elif mode == "IRWXU":
    #             _mode = stat.S_IRWXU
    #
    #         # Read by owner
    #         elif mode == "IRUSR":
    #             _mode = stat.S_IRUSR
    #
    #         # Write by owner
    #         elif mode == "IWUSR":
    #             _mode = stat.S_IWUSR
    #
    #         # Execute by owner
    #         elif mode == "IXUSR":
    #             _mode = stat.S_IXUSR
    #
    #         # Read, write, and execute by group
    #         elif mode == "IRWXG":
    #             _mode = stat.S_IRWXG
    #
    #         # Read by group
    #         elif mode == "IRGRP":
    #             _mode = stat.S_IRGRP
    #
    #         # Write by group
    #         elif mode == "IWGRP":
    #             _mode = stat.S_IWGRP
    #
    #         # Execute by group
    #         elif mode == "IXGRP":
    #             _mode = stat.S_IXGRP
    #
    #         # Read, write, an execute by others
    #         elif mode == "IRWXO":
    #             _mode = stat.S_IRWXO
    #
    #         # Read by others
    #         elif mode == "IROTH":
    #             _mode = stat.S_IROTH
    #
    #         # Write by others
    #         elif mode == "IWOTH":
    #             _mode = stat.S_IWOTH
    #
    #         # Execute by others
    #         elif mode == "IXOTH":
    #             _mode = stat.S_IXOTH
    #
    #         # call os.chmod() to carry out our action
    #         os.chmod(filename, _mode)
    #
    #     # TODO: FIND A WAY TO CHECK CHMOD AND VERIFY CHANGE
    #
    #     else:
    #         if not silent:
    #             print(f"{self.class_name}: CHMOD mode out of range")
    #             for key, value in self.chmod_descriptions.items():
    #                 print(f"{key}: {value}")

    # WORKING
    # method to split directories and file names out of file paths and return both directory and file name
    #
    # returns the post split filename on index[0] and directory on index[1]
    #
    def split_filename(self, filename, silent=False):
        # if the filename contains "/"s which are a good indicator
        # that they hold a directory path
        if "/" in filename:
            # split the directory into a list separated by /'s
            new_directory = filename.split("/")
            # create a [:-value] location for the beginning of our actual filename
            # by subtracting the length of the last split against he original length
            # of the filename
            extract_index = len(filename) - len(new_directory[-1])
            directory = filename[:extract_index]
            # declare our new filename as the file index in new_directory
            filename = new_directory[-1]

        # other wise there is no directory hidden in filename, and we can just leave things as they are
        else:
            # and assign a None to directory
            directory = None

        # if not silent
        if not silent:
            # we'll print out the returns
            print(f"{self.class_name}:")
            print(f"working directory: {os.getcwd()}")
            print(f"directory: {directory}")
            print(f"filename: {directory}")

        # and/or return the filename, and directory
        return filename, directory

    # WORKING
    # method to create a file (and associated directories if needed) if it does
    # not already exist.
    #
    # has 3 possible modes "w" and "wb"
    #       "w" to touch a plain-text file into existence
    #       "wb" to touch a bytes file into existence
    #
    # has 2 possible returns (True, False)
    #       True infers that the file exists and that we were otherwise successful
    #
    #       False infers that the file not only did not exists, but continues not existing
    #       and that the method has failed
    #
    def touch_file(self, filename, directory=None, mode=None, silent=False):
        # check if there is a value in the directory field
        # if not we want to double check against the filename
        if directory is None:
            # call our split_filename() method and check index 0 for a filename
            # and index 1 for a directory and load them into temporary variables
            # to preserve our original filename
            temp_filename, temp_directory = self.split_filename(filename, silent=True)

            # we make sure that the directory that split_filename() method
            # returned isn't None, meaning it has a value, and therefore the
            # original filename had a directory in it.
            if temp_directory is not None:
                # make sure the filename is updated to reflect the split
                filename = temp_filename
                # make sure the directory is updated to reflect the split
                directory = temp_directory

                # next we want to make sure that the directory does or does not already exist
                # and create it if it doesn't using our make_directory() method
                self.make_directory(directory, silent=True)

            # no hidden directory so pass out to next phase
            else:
                pass

        # if there is a value in the field
        else:
            # if the directory doesn't exist, create it
            # our make_directory() function automatically checks
            # check if the directory exists first
            self.make_directory(directory, silent=True)

        # if there is some form of value in directory at this point
        # we should append the directory and filename together
        # at this point either way they should be split
        if directory is not None:
            filename = f"{directory}{filename}"

        # set the proper modes and content string type based on mode field argument
        # write
        if mode in self.write_modes:
            mode = "w"
            blank_content = ""

        # write bytes
        elif mode in self.write_bytes_modes:
            mode = "wb"
            # use a bytes string for write bytes
            blank_content = b""

        # if mode is None or w/e just default to write mode
        else:
            mode = "w"
            blank_content = ""

        # if the file doesn't exist
        if not self.is_file(filename, silent=True):
            # protect from errors -- shouldn't get them -- but we're protected if we do.
            try:
                # open it with a context manager as f and write an empty blank line based on our selected mode
                # inserting the respective string type as blank_content
                # - the context manager will automatically close the file for us <3
                with open(filename, mode) as f:
                    f.write(blank_content)
            # take care of all those pesky potential errors due to potential user error
            # and return false to declare method failure
            except ValueError:
                if not silent:
                    print(f"{self.class_name}: ValueError in touch_file('{filename}') in '{mode}' mode")
                return False
            except TypeError:
                if not silent:
                    print(f"{self.class_name}: TypeError in touch_file('{filename}') in '{mode}' mode")
                return False
            except FileNotFoundError:
                if not silent:
                    print(f"{self.class_name}: FileNotFoundError in touch_file('{filename}') in '{mode}' mode")
                return False

            # load the bool of is_file() into a variable to determine whether or not we failed to touch the file
            exists = self.is_file(filename, silent=True)
            # if the file exists, we succeeded
            if exists:
                # if we're chatty cathy
                if not silent:
                    # say "we rule, our genes are on top of shit, we won, everything is good and nothing is bad"
                    print(f"{self.class_name}: successfully touched ({os.getcwd()}\\<{filename}>)")

            # if the file doesn't exist
            else:
                # and we're talking
                if not silent:
                    # say "we suck, and failed a simple task... that we are failures -- just like our ancestors"
                    # let them know that this failure is not only a programmatic failure but also a genetic one
                    print(f"{self.class_name}: failed to touch ({os.getcwd()}\\<{filename}>)")

            # and/or return the exists bool to represent success or failure
            return exists

        # if the file already exists, skip the whole song and dance and write home about it
        else:
            # if we can talk
            if not silent:
                # we will talk, we'll tell them how their precious file already exists
                print(f"{self.class_name}: ({os.getcwd()}\\<{filename}>) already exists")

                # we will return a True value because the file existing, is functionally
                # the same as successfully touching the file
                return True

    # WORKING
    # method to CREATE NEW DIRECTORIES if they don't already exists
    #
    # has 2 possible return values of True and False (bool)
    # True - The directory was successfully created, or otherwise already exists
    #        both are functionally the same
    #
    # False - The directory does not exist, or the method was otherwise unable to
    #         create the directory
    #
    def make_directory(self, directory, silent=False):
        # if the file exists pass
        if self.is_directory(directory, silent=True):
            # if silent == false
            if not silent:
                # let them know that the directory exists and that there is no need
                # to create it
                print(f"{self.class_name}: could not create the directory ({os.getcwd()}\\<{directory}>)")
                print("because it already exists")

            # we'll return with a True, to say that YES the directory is there
            # even though *this method* didn't create it.
            # the goal of having the directory exist is still met.
            return True

        # otherwise create the directory
        else:
            # attempt to create the directory using os.makedirs()
            try:
                os.makedirs(directory)
            # if TypeError
            except TypeError:
                if not silent:
                    print(f"{self.class_name}: ({os.getcwd()}\\<{directory}>) triggered a TypeError in "
                          f"make_directory({directory})")
                    print("check your input")
                # return False to state that the method failed
                return False

            # if ValueError
            except ValueError:
                if not silent:
                    print(f"{self.class_name}: ({os.getcwd()}\\<{directory}>) triggered a ValueError in "
                          f"make_directory({directory})")
                    print("check your input")
                # return False to state that the method failed
                return False
            # check if the directories were successfully created and return the bool into a variable
            exists = self.is_directory(directory, silent)
            # use the exists bool to determine how we continue
            # if directories were successfully created
            if exists:
                # if silent == false
                if not silent:
                    # let them know that it was a success
                    print(f"{self.class_name}: ({os.getcwd()}\\<{directory}>) was successfully created!")
            # if directories were unsuccessfully created
            else:
                # if silent == false
                if not silent:
                    # let them know that it was a failure
                    print(f"{self.class_name}: failed to create ({os.getcwd()}\\<{directory}>) as a directory")

            # return our bool to determine success or failure
            return exists

    # WORKING
    # method to READ return the contents of a file
    #
    # has 3 possible modes ('r', 'rb', 'None')
    # 'None' - Attempts to decide the read mode automatically (Experimental)
    # 'r'    - reads the file in 'r' (plain text) mode
    # 'rb'   - reads the file in 'rb' (bytes) mode
    #
    # has 2 possible returns (Content, None)
    # the method should return the content of the file
    # or if an error is encountered along the way
    # it will return None
    #
    def read_file(self, filename, mode=None, silent=False):
        if self.is_file(filename, silent=True):
            # set mode accordingly
            # TODO: Investigate additional read modes
            # read plain
            if mode in self.read_modes:
                mode = "r"
            # read bytes
            elif mode in self.read_bytes_modes:
                mode = "rb"

            # if the mode is None / unfilled
            elif mode is None:
                #       INCLUDE AUTOMATIC PROCESSING DURING "mode=None" CALLS
                #       -- ENDED UP TAKING A DIFFERENT APPROACH, WE USE TRY/EXCEPT TYPEERROR
                #          TO CATCH IF WE HAVE THE WRONG MODE, IF WE DO WE TRY THE OTHER READ
                #          MODE.
                #          HOPING THIS WORKS!
                #       -- (SEEMS TO BE WORKING)

                try:
                    with open(filename, "r") as f:
                        return f.read()
                except TypeError:
                    with open(filename, "rb") as f:
                        return f.read()

            # use a context manager to open our file and return its contents
            # the context manager will automatically close the file once
            try:
                with open(filename, mode) as f:
                    return f.read()
            # handle pesky errors that may arise for whatever reason and inform the user
            # and then pass out of the method, returning None
            except ValueError:
                if not silent:
                    f"{self.class_name}: ValueError in read_file('{filename}') in '{mode}' mode"
                return None
            except TypeError:
                if not silent:
                    f"{self.class_name}: TypeError in read_file('{filename}') in '{mode}' mode"
                return None

        # if the file doesn't
        else:
            # if we can tell secrets
            if not silent:
                # announce it to the world
                print(f"file not found.")
            # and return None to represent the file doesn't exist
            return None

    # WORKING
    # method to WRITE FILES.
    #
    # has a (True, False) bool return to confirm that the file exists at end of function
    # if it returns false it means that the write has somehow failed.
    #
    # has 5 modes it can write in, 1 automatic and 4 manual:
    #
    # None(Default) mode - will determine if the file exists and make it if it doesn't
    #                      and determine from the content type whether or not to write
    #                      in bytes or plain modes.  --  this is essentially an automatic
    #                      mode.
    #
    # "w" (write) mode - will write the file as a plain text with a new line at the end
    #                    !CAUTION! - THIS WILL WIPE THE FILE'S PREVIOUS CONTENTS, IF ANY
    #                                AND REPLACE IT WITH THE CONTENTS OF THE CONTENT FIELD
    #
    # "wb" (write bytes) mode - this mode is a lot like "w" mode except it writes in bytes
    #                           without a new line, but carries the same content wiping
    #                           warning as "w" mode.
    #
    # "a" (append) mode - this mode should be used on existing files, and will add the "content" field
    #                     to the last line of a plain text type file (such as .txt)
    #
    # "ab" (append bytes) mode - this mode is meant to add bytes type content directly to the end
    #                            of a bytes file (such as .jpg, or other data type) :shrug:
    #
    def write_file(self, content, filename, mode=None, encoding='utf-8', silent=False):
        # we'll set our modes to their proper values based on the user's call
        # and assign the proper content type
        # set mode to standard write
        if mode in self.write_modes:
            mode = "w"
            # create a new line each entry
            content = f'{content}\n'

        # set mode to write bytes
        elif mode in self.write_bytes_modes:
            mode = "wb"
            # make sure our data is bytes type and give it an encoding
            content = bytes(content, encoding)

        # set mode to append standard
        elif mode in self.write_append_modes:
            mode = "a"
            # create a new line each entry
            content = f'{content}\n'

        # set mode to append bytes
        elif mode in self.write_append_bytes_modes:
            mode = "ab"
            # make sure our data is bytes type and give it an encoding
            content = bytes(content, encoding)

        # if the mode field argument is empty
        if mode is None:
            # if the file exists
            if self.is_file(filename, silent=True):
                # and is_bytes is set to zero
                if isinstance(content, bytes):
                    # set to append bytes
                    mode = "ab"
                # if the content isn't bytes
                else:
                    # set to append (plain txt)
                    mode = "a"
                    # set content to string() type
                    content = f'{content}\n'
            # if the file doesnt exist
            else:
                # and is_bytes is set to zero
                if isinstance(content, bytes):
                    # set to write bytes
                    mode = "wb"
                # if is_bytes is anything but 0
                else:
                    # set to write (plain txt)
                    mode = "w"
                    # set content to string() type
                    content = f'{content}\n'

        # let's make sure that we don't get any errors
        try:
            # with the context manager, open the file and write our content
            # the context manager will automatically close the file once
            # it is finished
            # pass in our filename and the filtered out mode
            with open(filename, mode) as f:
                # write the content to the file
                f.write(content)
        # such as value errors or...
        except ValueError:
            if not silent:
                print(f"{self.class_name}: ValueError in writer context manager!")
            return False
        # type errors
        except TypeError:
            if not silent:
                print(f"{self.class_name}: TypeError in writer context manager!")
            return False

        # after we finish our write we can return whether or not the file
        # was successfully created using our is_file() method
        exists = self.is_file(filename, silent=True)
        # if our file is being written in w or wb modes
        # test to make sure the file was created
        if mode == "w" or mode == "wb":
            # if the file exists
            if exists:
                if not silent:
                    print(f"{self.class_name}: successfully wrote {filename} in '{mode}' mode")
            else:
                if not silent:
                    print(f"{self.class_name}: failed write {filename} in '{mode}' mode")
        return exists

    # WORKING
    # method to REMOVE DIRECTORIES
    #
    # method has 2 modes ("single", "all")
    #
    # "single" mode removes the end point target directory
    #
    # "all" mode removes all directories between the working directory
    # and the target directory.
    #
    # "clear" mode removes a directory and all of its children
    # !! CAUTION YOU WILL LOSE ALL CONTENT UNDER THE TARGET DIRECTORY!!
    #
    # the method has 3 possible returns
    # (True, False, None)
    # # True = Directory Removed
    # # False = Directory Removal Failed
    # # None = File Does Not Exist
    #
    def remove_directory(self, directory, mode="single", silent=False):
        # we'll just take a bit of code from our remove_file() method and turn it into
        # a reusable sub method to confirm the success of the main method, across modes
        def confirm_remove(sf_directory, sf_silent):
            # use our is_directory to determine whether or not we successfully deleted the directories
            # and return a bool for success/failure
            _exists = self.is_directory(sf_directory, silent=True)
            if _exists:
                # if silent is false make announcements
                if not sf_silent:
                    print(f"{self.class_name}: ({os.getcwd()}\\<{sf_directory}>) unsuccessfully removed")

            # if the file still exists the function has failed remove it
            else:
                # if silent is false
                if not sf_silent:
                    # make announcements
                    print(f"{self.class_name}: ({os.getcwd()}\\<{sf_directory}>) successfully removed")
            # return the bool exists to determine success or failure
            return _exists

        # begin method logic
        # check if the directory exists
        if self.is_directory(directory, silent=True):
            # and filter modes between single and all

            # "single" mode deletes the end directory only.
            if mode == "single":
                # make sure that the file directory is empty
                try:
                    # use the os.rmdir() function to remove our directory
                    os.rmdir(directory)

                    # return whether or not the directory was deleted
                    # by using our sub method
                    return confirm_remove(directory, silent)

                # if we except with an OSError, it means that the directory has contents
                except OSError:
                    # if silent set to !FALSE! ( ͡ʘ ͜ʖ ͡ʘ) *slowly unwinds*
                    if not silent:
                        # blah blah lah
                        print(f"{self.class_name}: ({os.getcwd()}\\<{directory}>) is not empty")
                        print(f"Consider using 'clear' mode to remove the directory, all sub-directories, and files")

                    # and/or return as False, directory could not be removed.
                    return False

            # "all" mode removes all directories between the working directory and the target directory
            elif mode == "all":
                # make sure that the file directory is empty with try/except statement
                try:
                    # call os.removedirs() with our directory passed in to remove all
                    # directories between working and target
                    os.removedirs(directory)

                    # return whether or not the directory was deleted
                    # by using our sub method
                    return confirm_remove(directory, silent)

                # if we except with an OSError, it means that the directory has contents
                except OSError:
                    # if silent is false
                    if not silent:
                        # squaaawwwk!!
                        print(f"{self.class_name}: ({os.getcwd()}\\<{directory}>) is not empty")
                        print(f"Consider using 'clear' mode to remove the directory, all sub-directories, and files")

                    # and/or return as False, directory could not be removed.
                    return False

            # "clear" mode removes everything under a target directory
            elif mode == "clear":
                # using the shutil.rmtree(directory) method.
                shutil.rmtree(directory)

                # let's check that our directory has been deleted
                exists = self.is_directory(directory, silent=True)
                # FAILURE
                if exists:
                    if not silent:
                        print(f"{self.class_name}: could not clear ({os.getcwd()}\\<{directory}>)")

                # SUCCESS
                else:
                    if not silent:
                        print(f"{self.class_name}: successfully cleared ({os.getcwd()}\\<{directory}>) and "
                              f"all sub-directories, and files")

                # we return the True False bool of exists to indicate success or failure.
                return exists

        # if the directory doesn't exist
        else:
            # if not silent
            if not silent:
                # let the user know that the directory doesn't exist.
                print(f"{self.class_name}: could not remove ({os.getcwd()}\\<{directory}>)")
                print(f"directory does not exist!")

            # return that the directory is None (Does Not Exist)
            return None

    # WORKING
    # method to REMOVE FILES
    #
    # has 3 possible returns (True, False, None)
    # # True = File Removed
    # # False = File Removal Failed
    # # None = File Does Not Exist
    #
    # TODO: add safe delete with some sort of looped overwrite function?  Need to research before diving
    #       into that one.
    def remove_file(self, filename, silent=False):
        # silently make sure the file exists
        if self.is_file(filename, silent=True):
            # if the file exists use the imported os module to remove it
            os.remove(filename)

            # use our is_file to determine whether or not we successfully deleted the file
            # and return a bool for success/failure
            if not self.is_file(filename, silent=True):
                # if silent is false
                if not silent:
                    # make announcements
                    print(f"{self.class_name}: ({os.getcwd()}\\<{filename}>) successfully removed")

                # and/or return that we have removed the file
                return True

            # if the file still exists the function has failed remove it
            else:
                # if silent is false make announcements
                if not silent:
                    print(f"{self.class_name}: ({os.getcwd()}\\<{filename}>) unsuccessfully removed")

                # and/or return that we have failed to remove the file
                return False

        # if the file doesn't exist...
        else:
            # if not silent, let the user know that the file doesn't exist.
            if not silent:
                # if the file doesnt exist, then run away screaming and crying
                print(f"{self.class_name}: could not remove ({os.getcwd()}\\<{filename}>)")
                print(f"file does not exist.")

            # and/or return that the file is None (Does Not Exist)
            return None


#
# If you're reading this...
# Hi!  I'm Billy B. Bobby Bobertson Jr. III. -- my friend's call me Bob...
# I hope you are well, and enjoying yourself wherever you may be. <3
#
# And If you are not reading this... ^^ this ^^ to you ALL the same (@everyone).
#


if __name__ == '__main__':
    print("This file is part of the junkyard pip module and isn't intended to be run from source")
    # TODO: GET FILES READY FOR INITIAL COMMIT! (DONE?)

    # TODO: SECOND COMMIT #
    #   - ADD ABILITY TO GET AND CHANGE WORKING DIRECTORY!
    #   - ADD ABILITY TO COPY FILES / DIRECTORIES?
    #   - ADD ABILITY TO MOVE FILES / DIRECTORIES?
    #   - ADD ABILITY TO CHMOD?
    #   - ADD ENCRYPTION(?)
    #       - GIVE CRYPTOHANDLER() LIFE / FUNCTIONALITY
    #       - INCORPORATE CRYPTOHANDLER() into FILEHANDLER()
    #   - ?
