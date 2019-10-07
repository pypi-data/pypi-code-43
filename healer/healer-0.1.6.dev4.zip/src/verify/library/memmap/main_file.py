import mmap

relative_path = "tester.txt"

# write a simple example file
with open(relative_path, "wb") as file:
    file.write(b"Hello Python!\n")

with open(relative_path, "r+b") as file:

    # memory-map the file, size 0 means whole file
    memory = mmap.mmap(file.fileno(), 0)

    # read content via standard file methods
    print(memory.readline())  # prints b"Hello Python!\n"

    # read content via slice notation
    print(memory[:5])  # prints b"Hello"

    # update content using slice notation;
    # note that new content must have same size
    memory[6:] = b" world!\n"

    # ... and read again using standard file methods
    memory.seek(0)
    print(memory.readline())  # prints b"Hello  world!\n"

    # close the map
    memory.close()
