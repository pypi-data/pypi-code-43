
def main():
    import os, sys
    from PySide2 import QtWidgets as qw
    os.environ['QT_API'] = 'PYSIDE2'

    instance = qw.QApplication.instance()
    if instance is None:
        instance = qw.QApplication(sys.argv)
    
    from . import junker
    try:
        mainGui = junker.Junker(instance)
    except SystemExit:
        del mainGui
        sys.exit()
        exit
        
# Instantiate a class
if __name__ == '__main__': # Windows multiprocessing safety
    print( "Image Junker" )
    print( "============" )
    print( "    Instructions:" )
    print( "    Right/Left arrow to traverse images" )
    print( "    Space/Del to remove images and associated files to ./junk" )
    print( "    S/Return to move images and associated files to ./salvage" )
    print( "    Z to move files back to current directory (undo)" )
    main()
