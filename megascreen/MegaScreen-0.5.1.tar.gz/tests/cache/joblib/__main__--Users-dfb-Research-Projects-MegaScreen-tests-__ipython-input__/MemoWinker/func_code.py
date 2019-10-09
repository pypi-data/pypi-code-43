# first line: 1
@memory.cache
def MemoWinker(
    diameter=32,
    L0Min=16,
    L0Max=8000,
    numL0=20,
    numIter=100,
    maxRadial=2,
    nfftOuter=256,
    nfftInner=256,
    randomSeed=12345,
):
    """Memoised wrapper for the Winker function"""
    np.random.seed(randomSeed)
    return Winker(
        diameter, L0Min, L0Max, numL0, numIter, maxRadial, nfftOuter, nfftInner
    )
