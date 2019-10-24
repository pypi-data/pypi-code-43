import pyranges as pr

f = "/mnt/scratch/endrebak/pyranges_benchmark/data/download/annotation_100000.gtf.gz"
gr = pr.read_gtf(f, annotation="ensembl")
print(gr)
n = gr.df.memory_usage(deep=True).sum()

gr = pr.read_gtf(f)
print(gr)
d = gr.df.memory_usage(deep=True).sum()

print(n/d)
