import os.path
import datetime

def get_input(result="",failed=False):
	if failed==False:
		print("Press ENTER to submit.")
		result = input()
	elif failed==True:
		print("Continue writing and press ENTER when you are ready to submit").
		result = result + input()
	print("Press ENTER again to confirm")
	if input() != "":
		get_input(result=result,failed=True)
	else:
		return result


def write():
	if os.path.exists("journal.txt"):
		print("Your journal has been found. Please submit a title to this journal entry.") 
		print("Please type your entry below, and press ENTER to submit.")
		journal_entry = input()
		print(journal_entry)
	else:
		print("Your journal has not been found. Create a new one? [y/n]")
		input()
	print("writer")
	return 1


if __name__ == '__main__':
	write()