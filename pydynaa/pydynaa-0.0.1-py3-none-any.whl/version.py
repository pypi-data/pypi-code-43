major = 0
minor = 0
patch = 1
phase = "alpha"
version = "{}.{}.{}".format(major, minor, patch)
full_version = "{}-{}".format(version, phase)


if __name__ == "__main__":
    print(version)
