from collections import defaultdict

class Sampler(object):
    """
    A region sampler class, performs random search, trying to find the least visited region.

    Parameters
    ----------
    calculate_regions : function, required
        Region calculation function, typically, created with imandra.idf.decompose
    random_sequence : function, required
        A random generator of sequences. Ideally, should generate a uniform distribution over
        all allowed input sequences for the model / regions. 

    """
    def __init__(self, calculate_regions, random_sequence):
        self.calculate_regions = calculate_regions
        self.random_sequence = random_sequence
        self.counts = defaultdict(lambda:0, {})
        self.maxCount = 1
        
            
    def generate(self, N, retries=50):
        """
        Runs the input sequence generation, attemting to produce a region-uniform distribution over them.

        Parameters
        ----------
        N : int, required
            Number of many sequences to generate
        retires : int, optional
            Number of rejection retries per an attempt. Defaults to 50. 

        """
        samples = []
        for _ in range(N):
            currentBest, best_query, best_region = self.maxCount, None, None
            for _ in range(retries):
                sequence = self.random_sequence()
                region = tuple(self.calculate_regions(*sequence))
                rcount = self.counts[region]
                if rcount == 0:
                    best_query, best_region = sequence, region
                    break
                if rcount < currentBest:
                    best_query, best_region = sequence, region
                    currentBest = rcount

            if best_query is None:
                best_query, best_region = sequence, region
            self.counts[best_region] += 1
            if self.counts[best_region] > self.maxCount:
                self.maxCount = self.counts[best_region]

            samples.append(best_query)
        return samples

