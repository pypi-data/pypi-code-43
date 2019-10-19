# let's do a splash screen when our module is imported and initialized
# feel free to change this
splash = True

# if not main file
if __name__ != "__main__":
    # print a version of the
    module_name = "Junkyard"
    version = "0.0.1a"
    if splash:
        print(f"Powered by {module_name} ({version})")
