'''
This class provides a minimal and fast interface for retrieving genotypes
from Plinks's BED/BIM/FAM file trios. The BED file must fit in memory.

    Typical usage:

    pf = PlinkFiles('test.bed', 'test.bim', 'test.fam')

    # fetch by chromosome and position
    pf.get_genotypes(chromosome=1, position=10000)

    # fetch by variant name (often RSID)
    pf.get_genotypes(snp='rs1235123')

    # fetch by SNP integer index
    pf.get_genotypes(snp_index=0)
'''


import numpy as np
import pandas as pd
from numba import jit
import os

@jit(nopython=True)
def _get_genotypes(bytes_, num_indivs):
    ret = np.zeros(num_indivs, dtype=np.float32)
    indiv_idx = 0
    two_bit_filt = 0b11
    for i in range(bytes_.shape[0]):
        this_byte = bytes_[i]
        for j in range(4):
            thisval = this_byte & two_bit_filt
            if thisval == 3:
                ret[indiv_idx] = 2.0
            elif thisval == 2:
                ret[indiv_idx] = 1.0
            elif thisval == 1:
                ret[indiv_idx] = np.nan
            else:
                ret[indiv_idx] = thisval
            indiv_idx += 1
            if indiv_idx == num_indivs:
                break
            this_byte >>= 2
    return ret



class PlinkFiles(object):
    def __init__(self, bed_or_prefix, bim=None, fam=None, individual_id_cols=['iid']):
        '''
        Class representing BED, BIM, and FAM trio.

        Args:
            bed_or_prefix        BED filename or prefix of BED, BIM, and FAM files
            bim                  BIM filename
            fam                  FAM filename
            individual_id_cols   column(s) in FAM file specifying individual ID

        Returns:
            PlinkFiles object from which genotypes can be obtained.
        '''
        if bim is None and fam is None:
            prefix = bed_or_prefix
            bed = prefix + '.bed'
            bim = prefix + '.bim'
            fam = prefix + '.fam'
        else:
            bed = bed_or_prefix
        self.bim = pd.read_csv(bim, sep='\t', header=None)
        self.bim.columns = ['chromosome', 'snp', 'cm', 'pos', 'a0', 'a1']
        self.bim['idx'] = np.arange(self.bim.shape[0])
        self.fam = pd.read_csv(fam, sep=' ', header=None)
        self.fam.columns = ['fid', 'iid', 'father', 'mother', 'gender', 'trait']
        self.fam.set_index(individual_id_cols, inplace=True)
        self.num_snps = self.bim.shape[0]
        self.num_indivs = self.fam.shape[0]
        self._snp_stride = int(np.ceil(self.fam.shape[0]/4.0))
    
        with open(bed, 'rb') as fin:
            # first three bytes are special: magic number and SNP-vs-indiv major
            magic = np.fromfile(fin, dtype=np.dtype('u1'), count=3)
            if not (magic[0] == 0x6c and magic[1] == 0x1b):
                raise ValueError('The specified BED file does not seem '
                                 'to be a BED file.')
            if magic[2] != 0x01:
                raise ValueError('The specified BED file is sample-major. '
                        'Please convert to variant-major using PLINK.')
            fin.seek(3, os.SEEK_SET) 
            self.rawbed = np.fromfile(
                    fin,
                    dtype=np.dtype('u1')).reshape((self.num_snps,
                        self._snp_stride))
            
    def get_genotypes(self, snp_index=None, chromosome=None, position=None,
            snp=None):
        '''
        Obtains additive (i.e., 0/1/2-encoded) genotypes. The variant can be
        specified in one of three ways:

        1) snp_index
        2) chromosome and position
        3) snp (variant name)

        Args:
            snp_index    integer index of SNP to retrieve
            chromosome   name of chromosome 
            position     base-pair position
            snp          variant name

        Returns:
            pd.Series of additive genotypes
        '''

        if chromosome is not None:
            if position is None:
                raise ValueError('must specify position with chromosome')
            snp_index = self.bim.query(
                    'chromosome == @chromosome and pos == @position')['idx'].iloc[0]
        elif position is not None:
            raise ValueError('must specify chromosome with position')
        elif snp is not None:
            snp_index = self.bim.query('snp == @snp')['idx'].iloc[0]
        if snp_index is None:
            raise ValueError(
                    'Must specify chromosome/position, snp, or snp_index')

        genotypes = _get_genotypes(self.rawbed[snp_index], self.num_indivs)
        genotypes = pd.Series(genotypes, index=self.fam.index)
        return genotypes


# example:
# pf = PlinkFiles('test.bed', 'test.bim', 'test.fam')
# pf.get_genotypes(chromosome=1, position=10000)  # fetch by chromosome and position
# pf.get_genotypes(snp='rs1235123')    # fetch by RSID
# pf.get_genotypes(snp_index=0)  # first SNP in bim
