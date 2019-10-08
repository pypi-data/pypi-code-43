import compileall
import sys
import os

def main():
    path = sys.argv[1]
    print(path)
    compileall.compile_dir(r'' + path)

    shell_str = "find " + path + " -name \"*.py\" | xargs rm -rf"
    os.system(shell_str)

if __name__ == "__main__":
    main()