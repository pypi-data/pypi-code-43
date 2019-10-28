from time import sleep
def isprime(num):
    try:
        if(num==1 or num==0):
            return "not a prime number or a composite number"
        if(num<0):
            raise Exception("must be a positive number")
        srnum=int(num**0.5+1)
        tem=srnum
        for i in range(srnum):
            if((num%tem) == 0):break
            tem-=1
        if(tem==1):return True
        else:return False
    except ValueError as e:
        raise ValueError
    except SyntaxError as e:
        raise SyntaxError    
    except:
        print("unknown error")
if __name__ == "__main__" :
    isprime(3)


