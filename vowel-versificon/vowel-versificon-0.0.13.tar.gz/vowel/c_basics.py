Ans="""
s="Hey there! I live in Mumbai:"
print("the length of string is %d"%len(s))
print("The first occurence of the letter y is ",s.find('y'))
print("the first five characters=%s"%s[:5])
print("no of occurence of a=%d"%s.count("a"))
print("next five chars=%s"%s[5:10])
print("The thirteenth char is=%s"%s[12])
print("The character with odd index=%s"%s[1:2])
print("The string in uppercase=%s"%s.upper())
print("The string in lowercase=%s"%s.lower())

"Remove nth index char"
def r_char(str,n):
    f_p=str[:n]
    l_p=str[n+1:]
    return f_p+l_p
a=r_char("python",0)
print(r_char("python",0))
print(r_char("python",2))
print(r_char("python",5))

"counting no of repeated characters"
import collections
str1="vkkkrishnamenoncollege"
d=collections.defaultdict(int)
for c in str1:
    d[c]+=1
for c in sorted(d,key=d.get):
    if d[c]>1:
        print("%s %d"%(c,d[c]))

"Create a set"
seta=set((2,4,6,1,67))
print("length of set a is %d"%(len(seta)))

"Binomial Coefficients"
def binomcoeff(n,k):
    if k==0 or k==n:
        return 1
    return binomcoeff(n-1,k-1)+binomcoeff(n-1,k)
n=5
k=2
print("Value of C(%d,%d) is %d"%(n,k,binomcoeff(n,k)))
"""