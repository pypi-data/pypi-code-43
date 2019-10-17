import sys


def demo():
	"""Do something
	
	This code may be considered helpful::
	
		print(1, 2, 3)
	
	This line is dedented again.
	"""
	iter({
		"a": int("6",
		         10)
	})
	
	[
		"--arg1",
		"--arg2",
	] + sys.argv[1:]
	
	FAKE_FILE1_HASH = {"value1": "DATA",
	                   "Name": "fsdfgh", "Size": "16"}
	
	# Examples of backslash continuation lines (PEP-8 / “Maximum Line Length”)
	assert len(sys.argv) == 2, \
	       "Maybe pass more args? " \
	       "And more!?"
	with open('/path/to/some/file/you/want/to/read') as file_1, \
	     open('/path/to/some/file/being/written', 'w') as file_2:
		file_2.write(file_1.read())
	if len(sys.argv) == \
	   len(FAKE_FILE1_HASH) \
	   and file_1:
		pass
	
	def download(self, path, args=[], filepath=None, opts={},
	             compress=True, **kwargs):
		return path is not None \
		       or len(args) >= 1
	
	return (
		("bla", FAKE_FILE1_HASH
	))


def foobar(  # A comment here should not cause error ET128
		arg1,
		arg2
):
	pass

def foobar2(arg1,
            arg2):
	pass