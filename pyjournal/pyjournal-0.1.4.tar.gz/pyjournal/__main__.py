import os.path
import datetime
import getpass
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto import Random
from Crypto.Util import Counter
import binascii
import os
import base64
import pickle
import hashlib
import datetime
from random import random


class AESCipher():
	def __init__(self, key, salt=None): 
		self.bs = AES.block_size
		if salt is None:
			salt = Random.new().read(8)
		self.salt=salt
		self.key = PBKDF2(key, salt, 16)
		# self.key = hashlib.sha256(key.encode()).digest()
	def encrypt(self, raw):
		raw = self._pad(raw)
		iv = Random.new().read(AES.block_size)
		cipher = AES.new(self.key, AES.MODE_CBC, iv)
		return base64.b64encode(iv + cipher.encrypt(raw))
	def decrypt(self, enc):
		enc = base64.b64decode(enc)
		iv = enc[:AES.block_size]
		cipher = AES.new(self.key, AES.MODE_CBC, iv)
		return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

	def _pad(self, s):
		return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

	@staticmethod
	def _unpad(s):
		return s[:-ord(s[len(s)-1:])]

def get_input(result="",failed=False,confirm=False,input_type=None):
	if input_type == "password":
		input_func = getpass.getpass
	else:
		input_func = input
	if confirm==False:
		return input_func()
	else:
		if failed==False:
			result = input_func()
		elif failed==True:
			add_on = input_func()
			if add_on == "":
				return result
			else:
				result = result + " " + add_on
		print("Press ENTER again to submit, or keep typing if you were interrupted.")
		second_result = get_input(result=result,failed=True)
		return second_result	

class JournalEntries:
	def __init__(self,cipher):
		self.entries = []
		title = "Journal Start."
		body = "This is the beginning of " + getpass.getuser() + "'s journal." 
		today = datetime.datetime.today()
		self.entries.append([[cipher.encrypt(title),cipher.encrypt(body)],today])
		self.salt = cipher.salt

class Journal:
	def __init__(self):
		if os.path.exists("journal.pkl"):
			with open("journal.pkl","rb") as f:
				self.journal = pickle.load(f)
				password = self.get_password()
				cipher = AESCipher(key=password,salt=self.journal.salt)
				if cipher.decrypt(self.journal.entries[0][0][0]) != "Journal Start.":
					print("Incorrect password")
				else:					
					print("To add an entry, type 'ENTRY'. To read your journal, type 'READ'.") 
					title = get_input()
					if title=="READ":
						filename = self.retrieve(cipher)
						print("\nYour journal has been opened as " + filename + ". We encourage you to delete after reading, as this is an unprotected file format.\n")
					elif title == "ENTRY":
						entry = self.get_entry()
						self.push_entry(entries=entry, cipher=cipher, entry = entry)
			if title=="ENTRY":
				with open("journal.pkl","wb+") as f:
					pickle.dump(self.journal,f)
		else:
			self.init_journal()
	def get_password(self):
		print("Please enter your password to access the journal.")
		password = get_input(input_type="password")
		return password
	def retrieve(self,cipher):
		self.journal.entries = [ [[cipher.decrypt(field) for field in entry[0] ], entry[1]] for entry in self.journal.entries]
		filename = str(round(random()*100000000000)) + ".txt"
		self.output_to_txt(self.journal.entries,filename=filename)
		return filename

	def output_to_txt(self,list_of_entries,filename):
		with open(filename,"wb+") as f:
			count=0
			for entry in list_of_entries:
				f.write(("\nEntry number " + str(count) + ": " + entry[0][0] + "\n").encode())
				f.write((entry[0][1] + "\n").encode())
				f.write(("Written: " + str(entry[1].strftime("%b")) + ". " + str(entry[1].day) + ", " + str(entry[1].year) + ".\n").encode())
				f.write("________________\n".encode())
				count+=1

	def get_entry(self):
		print("Please write a title")
		title = get_input()
		print("Please write a body")
		body = get_input()
		return [title,body]

	def push_entry(self,entries,cipher, entry):
		entry = [[cipher.encrypt(field) for field in entry]]
		entry.append(datetime.datetime.today())
		self.journal.entries.append(entry)
		print("\nYour entry has been added.\n")

	def init_journal(self):
		print("Your journal has not been found. Create a new one? [y/n]")
		if input() == "y":
			print("Add a password for your journal:")
			password = get_input(input_type="password")
			print("Confirm password:")
			password2 = get_input(input_type="password")
			if password==password2:
				cipher = AESCipher(key=password)
				entries = JournalEntries(cipher=cipher)
				with open("journal.pkl","wb") as f:
					pickle.dump(entries,f)
			print("Your journal has been created. Type 'journal' again to add your first entry.")



def write():
	journal = Journal()


if __name__ == '__main__':
	write()