def fib_dfs(num):
	if num < 0:
		raise ValueError('Input number cannot be negetive')
	elif num < 2:
		return num
	else:
		return fib_dfs(num - 1) + fib_dfs(num - 2)

def fib_dp(num):
	if num < 0:
		raise ValueError('Input number cannot be negetive')
	elif num < 2:
		return num
	else:
		temp_1, temp_2 = 0, 1
		for i in range(num - 1):
			temp_1, temp_2 = temp_2, temp_1 + temp_2

		return temp_2