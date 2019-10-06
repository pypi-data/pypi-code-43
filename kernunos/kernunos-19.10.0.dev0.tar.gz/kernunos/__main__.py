import argparse

def show_banner(target):
    print('##############################')
    print('#     Welcome to Kernunos    #')
    print('##############################')
    print('--')
    print('Starting recon on {}'.format(target))

def show_help():
    print("""
    kernunos
    Arguments:
    -t\t --target\t The domain name of your target.

    Examples:
    python -m kernunos --target example.com
    """)    

def initialize_arguments():
    """
    Initializes argument given by the user.
    """
    parser = argparse.ArgumentParser('kernunos')
    parser.add_argument("-t",
                        "--target",
                        type=str,
                        help="The target domain.")
    
    # Parse the arguments
    args= parser.parse_args()

    # Do not proceed further if the target is null
    if args.target == None:
        show_help()		
    
    return args

try:
    # Terminal arguments
    args = initialize_arguments()
    
    # Print application banner
    show_banner(args.target)
    
    # Process the initilaized arguments
    #process_arguments(args)
    
except KeyboardInterrupt:
    print("Exiting Application...")
    exit(0)

except Exception as e:
    print("Exception detected:\n{}".format(e))
    exit(0)