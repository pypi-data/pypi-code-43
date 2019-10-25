import pyconrad.autoinit

def import_grids():
    import edu.stanford.rsl.conrad.data.numeric
    a = edu.stanford.rsl.conrad.data.numeric.Grid2D(20,30)
    from edu.stanford.rsl.conrad.data.numeric import Grid2D
    b = Grid2D(20,30)

    assert a
    assert b



def main():
    import_grids()

if __name__ == '__main__':
    main()
