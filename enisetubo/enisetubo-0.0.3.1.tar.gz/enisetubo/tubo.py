from random import normalvariate, triangular

def boule(poids, diametre, materiau):
    prod={}
    if materiau == 'acier':
        prod['poids']    = normalvariate(poids, .020*poids)
        prod['diametre'] = normalvariate(diametre, .018*diametre)
        prod['materiau'] = materiau
    elif materiau == 'fonte':
        prod['poids']    = triangular(poids-10, poids+10)        
        prod['diametre'] = triangular(diametre-5, diametre+5)
        prod['materiau'] = materiau
    return prod