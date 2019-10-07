# Use: optinet filename dictname
# Optimizes the flexible net in dictionary dictname of file filename
import argparse
import imp
from fnyzer import FNFactory

def main():
    """Manage parameters"""
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="Python file containing the flexible net dictionary")
    parser.add_argument("dictname", help="Python variable in 'filename' containing the flexible net dictionary")
    args = parser.parse_args()
    if args.filename[-3:] == ".py":
        args.filename = args.filename[:-3]
    
    """Get data"""
    f, path, desc = imp.find_module(args.filename, ["."])
    allnets = imp.load_module(args.filename, f, path, desc)
    netd = getattr(allnets, args.dictname) # Flexible net dictionary
    
    """Build and optimize"""
    print("Building net...")
    net = FNFactory(netd) # Build net object
    print("Optimizing...")
    model = net.optimize() # Optimize net and save results
    print("Done.")
