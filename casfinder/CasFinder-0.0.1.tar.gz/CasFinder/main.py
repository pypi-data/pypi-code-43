from position_out import *
import os, subprocess
import glob
import datetime
from casPROTidentification import *
from generateMasterTbl import *
from getCRISPRrepeats import *
#from result_reader import *
from translate import *
from cleaner import get_name,clean_dir,remove_file
import shutil
def Finding(index,working, out, refset='full', date=str(datetime.date.today()), tax='no',cas='T', evalue='1e-6', idcutoff=40.0, lengthcutoff=50.0, repeats='T', summary='T',temp='delete'):
    """INFILE is a csv file with a column called "Path" that has the full path to the genomes of #interest.  Do not include file extensions in this column."""  
    name =  get_name(index)
    shutil.copy2(index,'./genome/'+name+'.fna')
    index = './genome/'+name
    file_name = get_name(index)
    workingdir = working+file_name+'_work'
    outdir = out+file_name
    clean_dir(workingdir)
    clean_dir(outdir)
    os.mkdir(workingdir)
    os.mkdir (outdir)
    subject_locations = [index]
    protein(index)
    if workingdir == os.getcwd():
        if os.path.isdir('raw_files'):
            pass
        else:
            os.mkdir('raw_files/')
        workingdir = 'raw_files/'
    if os.path.isdir(outdir):
        pass
    else:
        os.mkdir(outdir)
    if refset =='full':
        query_locations = glob.glob('./data/fullrefs/*.fasta') 
    elif refset =='typing':
        query_locations = glob.glob('./data/typingrefs/*.fasta')
    if cas =='T':
        print ('Searching for Cas proteins')
        casSearch(query_locations, subject_locations, date, evalue, idcutoff, lengthcutoff, working_outdir=workingdir, final_outdir=outdir)
    else:
        pass
    
    if repeats == 'T':   
        print ('Searching for CRISPRs')
        repeatAnalysis(subject_locations, date, working_outdir=workingdir, final_outdir=outdir, inhouse_setting=False)
    else:
        pass
    
    if summary =='T': 
        print ('Generating Master table')
        if tax == 'no':
            typeAnalysis(date, final_outdir=outdir, working_outdir=workingdir)
        elif tax == 'yes':
            taxinfofile = infile
            masterTblWithStrain(taxinfofile,tax, date, finaloutputdir=outdir,workdir=workingdir)
            
    position_output(workingdir, outdir)
            
    if temp == 'deletes':
        for x in glob.glob((os.path.join(workingdir,'*'))):
            if os.path.isfile(x):
                os.remove(x)
        os.rmdir(workingdir)
    else:
        pass
    clean_dir(workingdir)
    remove_file(index+'.fna')
    remove_file(index+'.faa')
if __name__ == "__main__": 
    print('strat working')
    Finding('./NC_013161','./work','./work')
