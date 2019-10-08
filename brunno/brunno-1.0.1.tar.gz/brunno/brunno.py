import numpy
import mpmath

def fat(n):
	nn = 1
	res = 1
	while(True):
		if(nn==n):
			break
		else:	
			nn= nn+1
			res *= nn
		#	print(res)
		
	return res


def mac(s):
	n = 0
	for i in range(1,1000):
		n+=(s)**i/fat(i)
	return n
	
'''
if __name__ == '__main__':
	print(atez(7))
'''

