import argparse

def main(metagenome, ppath, annotation_file):
    count = 0
    count_multiEC = 0

    input_file = "%sec_count.tsv" % ppath
    out_file = "%sanalysis.tsv" % ppath
    multiEC_file = "%smulti_ec.tsv" % ppath ###

    d = {}
    d_multiEC = {} ###
    fh = open(input_file, 'r')
    for line in fh:
    	line = str.strip(line)
    	count = count + 1
    	line_list = line.split('\t')
    	if len(line_list) > 2:
    		count_multiEC = count_multiEC + 1
    ###
    		EC_list = line_list[1:]
    		for i in range(len(EC_list)-1):
    			for j in range(i+1, len(EC_list)):
    				EC_pair = [EC_list[i], EC_list[j]]
    				EC_key = '|'.join(sorted(EC_pair))
    				if EC_key not in d_multiEC:
    					d_multiEC[EC_key] = 0
    				d_multiEC[EC_key] += 1
    ###
    		continue
    	EC = line_list[1]
    	if EC not in d:
    		d[EC] = 0
    	d[EC] = d[EC] + 1
    fh.close()

    # define where EC_annotation file is
    d_anno = {}
    fh = open(annotation_file, 'r')
    for line in fh:
        line = str.strip(line)
        EC = line.split('\t')[0]
        anno = line.split('\t')[1].split('|')[0]
        d_anno[EC] = anno
    fh.close()

    fhw = open(out_file, 'w+')
    # Multi_fraction = '0.0' if count == 0 else '%.1f' % (float(count_multiEC)/count*100)
    # to_write = "#At hssp cutoff of 20, %s reads get annotated and %s reads are annotated with multiple EC (%s%%; excluded from later analysis). This file includes the result total %s reads" % (count, count_multiEC, Multi_fraction, (count-count_multiEC))
    to_write = "%s\t%s" % (count, count_multiEC)
    fhw.write(to_write + "\n")
    for EC in sorted(d.keys()):
    	to_write = EC + "\t" + str(d[EC]) #+ '\t' + d_anno[EC]
    	fhw.write(to_write + "\n")
    fhw.close()

    ####
    fhw = open(multiEC_file, 'w+')
    # for key, value in sorted(d_multiEC.items(), key=lambda (k,v): (v,k), reverse=True):
    for key, value in sorted(d_multiEC.items(), key=lambda kv: (kv[1], kv[0]), reverse=True):
    	to_write = key + "\t" + str(value)
    	fhw.write(to_write + "\n")
    fhw.close()
    ####


if __name__ == "__main__":
    parser = argparse.ArgumentParser("""This script annotates ECs to reads.""")

    parser.add_argument('-m', '--metagenome', help = "The metagenome id.")
    parser.add_argument('-p', '--ppath', help = "The path to parsed DIAMOND result.")
    parser.add_argument('-a', '--annotation', help = "The path to annotation file.")

    args = parser.parse_args()
    metagenome = args.metagenome
    ppath = args.ppath
    annotation_file = args.annotation

    if not metagenome:
        metagenome = input("Enter the metagenome id: ")
    if not ppath:
        ppath = input("The path to parsed DIAMOND result.")

    main(metagenome, ppath, annotation_file)
