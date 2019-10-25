import argparse


def main(metagenome, ppath, EC_file, analyzed):
    d_EC = {}
    fh = open(EC_file, 'r')
    for line in fh:
    	line = str.strip(line)
    	(p_id, EC) = line.split('\t')
    	d_EC[p_id] = EC
    fh.close()

    parse_path = ppath
    annotate_file = "%sec_count.tsv" % analyzed

    d_anno = {}
    diamond_file = parse_path + metagenome + '.parsed'

    fh = open(diamond_file, 'r')
    for line in fh:
    	r_id, subject, _hssp = line.split('\t')
    	DNA_r_id = r_id.split(',P_')[0]
    	p_id = subject.split('|')[0]
    	if p_id in d_EC:
    		EC = d_EC[p_id]
    		if not DNA_r_id in d_anno:
    			d_anno[DNA_r_id] = {}
    		d_anno[DNA_r_id][EC] = 0
    fh.close()

    fhw = open(annotate_file, 'w+')
    for DNA_r_id in sorted(d_anno.keys()):
    	to_write = DNA_r_id + '\t' + '\t'.join(sorted(d_anno[DNA_r_id].keys()))
    	fhw.write(to_write + '\n')
    fhw.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser("""This script annotates ECs to reads.""")

    parser.add_argument('-m', '--metagenome', help = "The metagenome id.")
    parser.add_argument('-p', '--ppath', help = "The path to parsed DIAMOND result.")
    parser.add_argument('-e', '--ECfile', help = "The index ECfile (ec_mapping.tsv).")
    parser.add_argument('-a', '--analyzed', help = "The path to the analyzed result.")

    args = parser.parse_args()
    metagenome = args.metagenome
    ppath = args.ppath
    EC_file = args.ECfile
    analyzed = args.analyzed

    if not metagenome:
        metagenome = input("Enter the metagenome id: ")
    if not ppath:
        ppath = input("The path to parsed DIAMOND result.")
    if not EC_file:
        EC_file = input("The index ECfile (ec_mapping.tsv).")

    main(metagenome, ppath, EC_file, analyzed)
