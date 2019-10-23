import pandas as pd
import os
def add(x, y):
	a = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)),'/1.txt'))
	print(a)
	return x + y
