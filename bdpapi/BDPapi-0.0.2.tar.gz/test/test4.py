import math

for i in range(101, 201):
    asd = 'asdf'
    sum = 0
    end = int(math.ceil(math.sqrt(i)))
    for j in range(2, end):
        if i % j == 0:
            sum += 1
    if sum > 0:
        print(i)

