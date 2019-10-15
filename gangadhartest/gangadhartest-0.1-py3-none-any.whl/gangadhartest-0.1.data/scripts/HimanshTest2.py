#PASS
a = "AlphabeticalOrder"
n = 3
ab = [ [] for i in range(n)]
count1,count2 = 0,n-2
for i in (a):
    if count1 < n:
        ab[count1].append(i)
        count1+=1
    elif count1>=n:
        ab[count2].append(i)
        count2 -= 1
        if count2 == 0:
           count1 = 0
           count2 = n-2
for i in ab:
    print (i)
    
    

