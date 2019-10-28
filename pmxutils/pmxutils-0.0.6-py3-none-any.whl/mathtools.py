"""A set of functions aiding in math for ProgModX"""
from numpy import arange
from math import sin, cos, tan, pi
import random

def construct(expression, var="x"):
    """Returns a function computing the given expression"""
    def f(x):
        return eval(expression.replace("^", "**").replace(var, "x"))
    return f

def computeLists(function, low, high, step=1):
    """Returns a touple of two lists containing x values inbetween low and high, and the computed results for y.
    In the format of (x_list, y_list)"""
    #Constructs functions from the griven expressions if the expressions are strins
    if type(function) == type(str()):
        function = construct(function)
    return (arange(low, high+1, step), [function(i) for i in arange(low, high+1, step)])

def newton(function, derivative, low, high, tolerance=1e-8, rounding = 3, iterations = 1000):
    """Uses Newtons way of finding the root of a function using the function and its derivative, within the given limits.
    Returns None if it can't find a solution that satisfies the tolerance after the defined number of terations"""
    xn = random.random()*(high-low)        #Startverdi    #Bruker tilfeldig startverdi
    TOL = tolerance                             #Toleranse
    N = iterations                              #Itereasjoner
    i = 0                                       #Tellevariabel

    #Constructs functions from the griven expressions if the expressions are strins
    if type(function) == type(str()):
        function = construct(function)
    if type(derivative) == type(str()):
        derivative = construct(derivative)
    
    #Beginning of Newtonian solution
    while i <= N and abs(function(xn)) >= TOL:
        xn = xn - function(xn)/derivative(xn)
        i += 1
    #Chech if the found value for x gives a y value within the tolerance
    if (abs(function(xn)) <= TOL) and (isInbetween(xn, low, high)):
        return round(xn, rounding)
    else:
        return None

def isInbetween(number, low, high):
    """Returns True if number is inbetween low and high, returns False otherwise"""
    if low <= number <= high:
        return True
    else:
        return False

def rectangleIntegral(function, low, high, n):
    """Returns the numerically calculated integral of the function f inbetween low and high using n rectangles"""
    if type(function) == type(str()):
        function = construct(function)

    total = 0.0
    h = (high-low)/n
    for i in range(0, n):
        total += function( low+(i*h) )
    return total * h

def trapezoidIntegral(function, low, high, n):
    """Returns the numerically calculated integral of the function inbetween low and high using n trapezoids"""
    if type(function) == type(str()):
        function = construct(function)

    total = (function(low)+function(high))/2.0
    h = (high-low)/n

    for i in range (1, n) :
        total += function(low+(i*h))
    return total * h

def simpsonIntegral(function, low, high, n):
    """Returns the numerically calculated integral of the function inbetween low and high using n quadratic splines"""
    if type(function) == type(str()):
        function = construct(function)
    h = (high-low)/n
    total = function(low) + function(high)

    for i in range(2, n, 2):
        total += function(low+i*h)

    for i in range(1, n, 2):
        total += function(low+i*h)
    return total