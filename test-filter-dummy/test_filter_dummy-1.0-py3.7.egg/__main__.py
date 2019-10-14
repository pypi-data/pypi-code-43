import filter
import argparse


print("in")

#if __name__=="main":
#    print("in")
    

parser = argparse.ArgumentParser()
grp = parser.add_argument_group()
grp.add_argument('--a', default=10)
grp.add_argument('--b', default=10)
grp.add_argument('--c', default=10)

options = parser.parse_args()

print(options.a, options.b, options.c)

f = filter.filtermanager(options.a, options.b, options.c)
f.calc()
f.cald()

