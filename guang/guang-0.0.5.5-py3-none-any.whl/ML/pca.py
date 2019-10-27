import numpy as np 

def transform(X, dim):
	"""
	A principal component analysis model.
	
	Parameters
	----------
	X : :py:class:`ndarray <numpy.ndarray>` of shape `(Samples,  characteristics)`
		The input samples.
	dim : int
		Take the previous dim principal components.

	return:
	-------
	shape = (Samples, dim)
	"""
	U, S, V = np.linalg.svd(X-X.mean(0),full_matrices=True)
	idx = S.argsort()[::-1][:dim]
	return X.dot(V[idx].T)
