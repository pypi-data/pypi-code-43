import math
import argparse


def cal_HSSP(pident, length, mismatch):
	numId = int(float(pident) * float(length) / 100)
	seqLength = int(float(length) - (float(length) - numId - float(mismatch)))
	if seqLength <= 10:
		hssp = -100
	else:
		exp = -0.302 * (1 + math.exp(-seqLength/1000.0))
		hssp = float(pident) - (352.3 * (seqLength ** exp))
	return hssp


def main(metagenome, dpath, ppath):

	DIAMOND_file = '%s%s.out' % (dpath, metagenome)
	parse_file = '%s%s.parsed' % (ppath, metagenome)

	cutoff = 20

	fh = open(DIAMOND_file,'r')
	fhw = open(parse_file, 'w+')
	for line in fh:
		line = str.strip(line)
		try:
			# qseqid, sseqid, pident, length, mismatch, gapopen, qstart, qend, sstart, send, evalue, bitscore
			qseqid, sseqid, pident, length, mismatch, *_ = line.split('\t')
		except ValueError as err:
			print(f'WARNING could not parse {line}: {err}')
			# TODO check for bug !!!
		hssp = cal_HSSP(pident, length, mismatch)
		if hssp >= cutoff:
			to_write = '\t'.join([qseqid, sseqid, str(hssp)])
			fhw.write(to_write + "\n")
	fh.close()
	fhw.close()


if __name__ == "__main__":
	parser = argparse.ArgumentParser("""This script parses psiblast results and extract hits from last iteration with rHSSP >= 20.""")

	parser.add_argument('-m', '--metagenome', help = "The metagenome ID.")
	parser.add_argument('-d', '--dpath', help = "The path to DIAMOND result.")
	parser.add_argument('-p', '--ppath', help = "The path to parsed DIAMOND result.")

	args = parser.parse_args()
	metagenome = args.metagenome
	dpath = args.dpath
	ppath = args.ppath

	if not metagenome:
		metagenome = input("Enter the metagenome: ")
	if not dpath:
	    dpath = input("The path to DIAMOND result.")
	if not ppath:
	    ppath = input("The path to parsed DIAMOND result.")

	main(metagenome, dpath, ppath)
