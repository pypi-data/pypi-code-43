# coding: utf-8

# Classes CompactSpace and FunLipschitz are the two required classe to use bcert
from .bcert import CompactSpace, FunLipschitz

# Main function containing the ecursive algorithm for the bound certification
from .bcert import boundCert, boundCertPar, boundCertUserPar

__version__ = "0.0.3"
