#!/usr/bin/env python


import os

import numpy as np
import pandas as pd

from ngs_toolkit import _LOGGER
from ngs_toolkit.analysis import Analysis
from ngs_toolkit.decorators import check_has_attributes


class CRISPRAnalysis(Analysis):
    """
    Class to model analysis of CRISPR screening data.
    Inherits from the :class:`~ngs_toolkit.analysis.Analysis` class.

    Parameters
    ----------
    name : :obj:`str`, optional
        Name of the analysis.

        Defaults to "analysis".
    from_pep : :obj:`str`, optional
        PEP configuration file to initialize analysis from.
        The analysis will adopt as much attributes from the PEP as possible
        but keyword arguments passed at initialization will still have priority.

        Defaults to :obj:`None` (no PEP used).
    from_pickle : :obj:`str`, optional
        Pickle file of an existing serialized analysis object
        from which the analysis should be loaded.

        Defaults to :obj:`None` (will not load from pickle).
    root_dir : :obj:`str`, optional
        Base directory for the project.

        Defaults to current directory or to what is specified in PEP
        if :attr:`~ngs_toolkit.analysis.Analysis.from_pep`.
    data_dir : :obj:`str`, optional
        Directory containing processed data (e.g. by looper) that will
        be input to the analysis. This is in principle not required.

        Defaults to "data".
    results_dir : :obj:`str`, optional
        Directory to contain outputs produced by the analysis.

        Defaults to "results".
    prj : :class:`peppy.Project`, optional
        A :class:`peppy.Project` object that this analysis is tied to.

        Defaults to :obj:`None`.
    samples : :obj:`list`, optional
        List of :class:`peppy.Sample` objects that this analysis is tied to.

        Defaults to :obj:`None`.
    kwargs : :obj:`dict`, optional
        Additional keyword arguments will be passed to
        parent class :class:`~ngs_toolkit.analysis.Analysis`.

    Examples
    --------
    >>> from ngs_toolkit.crispr import CRISPRAnalysis

    This is an example of a CRISPR analysis:

    >>> pep = "metadata/project_config.yaml"
    >>> a = CRISPRAnalysis(from_pep=pep)
    >>> # Get consensus peak set from all samples
    >>> a.get_CRISPR_data()
    >>> # Normalize
    >>> a.normalize(method="median")
    >>> # General plots
    >>> a.plot_all_data()
    >>> a.plot_segmentation_stats()
    >>> # Unsupervised analysis
    >>> a.unsupervised_analysis()
    >>> # Save object
    >>> a.to_pickle()
    """
    _data_type = "CRISPR"

    def __init__(
        self,
        name=None,
        from_pep=False,
        from_pickle=False,
        root_dir=None,
        data_dir="data",
        results_dir="results",
        prj=None,
        samples=None,
        **kwargs
    ):
        # The check for existance is to make sure other classes
        # can inherit from this one
        default_args = {
            "data_type": "CRISPR",
            "__data_type__": "CRISPR",
            "var_unit_name": "gRNA",
            "quantity": "counts",
            "norm_units": "enrichment"}
        for k, v in list(default_args.items()):
            if not hasattr(self, k):
                setattr(self, k, v)

        super(CRISPRAnalysis, self).__init__(
            name=name,
            from_pep=from_pep,
            from_pickle=from_pickle,
            root_dir=root_dir,
            data_dir=data_dir,
            results_dir=results_dir,
            prj=prj,
            samples=samples,
            **kwargs
        )

        attrs = ['guide_reference', 'neg_control', 'pos_control']
        for attr in attrs:
            if not hasattr(self, attr):
                setattr(self, attr, None)

    def set_guide_reference(
            self,
            guide_reference,
            guide_type_column="guide_type",
            neg_control="negative_control",
            pos_control="essential",
            guide_score_col=None):
        """

        if file path, MUST BE CSV!

        """
        if isinstance(guide_reference, str):
            guide_reference = pd.read_csv(guide_reference)

        # Drop duplicates
        cols = ['gene_id', 'guide_sequence']
        guide_reference = guide_reference.drop_duplicates(
            subset=cols).sort_values(cols).reset_index(drop=True)

        # if "guide_id" in guide_reference.columns:
        #     guide_reference = guide_reference.set_index("guide_id")
        # else:
        order = (
            guide_reference.groupby('gene_id', sort=False)
            ['guide_sequence'].count()
            .apply(np.arange)
            .apply(pd.Series).stack()
            .astype(int).values + 1)
        guide_reference.loc[:, "guide_order"] = order
        guide_reference = guide_reference.set_index(
            guide_reference.loc[:, "gene_id"] +
            "__" +
            guide_reference.loc[:, "guide_order"].astype(str).str.zfill(2))
        guide_reference.index.name = "guide_id"

        self.guide_reference = guide_reference.sort_index()
        self.neg_control = neg_control
        self.pos_control = pos_control
        self.guide_score_col = guide_score_col

    def get_count_matrix(
            self,
            samples=None,
            n_top=None,
            save=True,
            assign=True):
        import multiprocessing
        import parmap

        if samples is None:
            samples = self.samples
        n_top = int(1e9) or n_top

        counts = pd.concat(
            parmap.map(
                count_grnas,
                [s.data_path for s in samples],
                n_top=n_top),
            axis=1).fillna(0)
        counts.columns = [s.name for s in samples]

        matrix = (
            counts
            .join(
                self.guide_reference
                .reset_index().set_index("guide_sequence")
                [['guide_id']])
            .dropna()
            .set_index('guide_id').sort_index(axis=0)
            .astype(int))
        if assign:
            self.matrix_raw = matrix
        if save:
            matrix.to_csv()
        return matrix

    # TODO: could rewrite to accomodate various guide_references for samples
    def generate_guide_assembly(
            self,
            output_dir="{root_dir}/reference",
            output_prefix=None,
            guide_reference=None,
            bowtie2_index=True,
            overwrite=True):
        """
        """
        import subprocess
        import tempfile

        if guide_reference is None:
            guide_reference = self.guide_reference
        if output_prefix is None:
            output_prefix = self.name
        output_dir = self._format_string_with_attributes(output_dir)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        output_fasta = os.path.join(
            output_dir, output_prefix + ".reference.fa")

        _LOGGER.debug(
            "Writing guide RNA reference to file '{}'.".format(output_fasta))
        with open(output_fasta, "w") as handle:
            for guide, row in guide_reference.iterrows():
                handle.write(
                    ">{}\n{}\n".format(guide, row['guide_sequence']))

        if not bowtie2_index:
            return output_fasta

        cmd = "bowtie2-build {} {}".format(
            output_fasta, os.path.join(output_dir, output_prefix))

        if not overwrite:
            index_file = "{}.1.bt2".format(
                os.path.join(output_dir, output_prefix))
            if os.path.exists(index_file):
                msg = "Overwrite is False and index already exists. Done."
                _LOGGER.info(msg)
                return

        stdout = tempfile.TemporaryFile()
        stderr = tempfile.TemporaryFile()
        code = subprocess.call(cmd.split(" "), stdout=stdout, stderr=stderr)
        if code == 0:
            _LOGGER.debug("Bowtie2 index built successfully!")
        else:
            stdout.seek(0)
            stderr.seek(0)
            _LOGGER.error(
                "Bowtie2 index build failed:\n"
                "{0}\nStdout:\n{1}\n{0}\nStderr:\n{2}\n"
                .format(
                    "".join(["-"] * 40),
                    stdout.read().decode(),
                    stderr.read().decode()))

    def map_samples(
            self,
            trimming_lengths=None,
            samples=None,
            bowtie2_index_prefix=None,
            mapping_quality=30,
            distributed=False,
            **kwargs):
        """
        """
        from ngs_toolkit.utils import submit_job

        if samples is None:
            samples = self.samples

        if bowtie2_index_prefix is None:
            bowtie2_index_prefix = os.path.join(
                self.root_dir, "reference", self.name)

        for i, sample in enumerate(samples):
            if not os.path.exists(sample.paths.sample_root):
                os.makedirs(sample.paths.sample_root)
            job_name = sample.name + ".mapping"
            log_file = os.path.join(
                sample.paths.sample_root, job_name + ".log")
            job_file = os.path.join(
                sample.paths.sample_root, job_name + ".sh")

            if trimming_lengths is None:
                try:
                    trim = (
                        sample.left_trimming, sample.right_trimming)
                except AttributeError:
                    msg = "trimming_lengths not given and not annotated in samples!"
                    trim = guess_crispr_sample_trimming_lengths(sample.data_path)
                    msg += " Guessed trimming_lengths as {} and {}.".format(*trim)
                    _LOGGER.warning(msg)
            else:
                if isinstance(trimming_lengths, list):
                    trim = trimming_lengths[i]
                elif isinstance(trimming_lengths, tuple):
                    trim = trimming_lengths

            cmd = "date\n"
            # Convert to FASTQ if needed
            if sample.data_path.endswith(".bam"):
                unmapped_dir = os.path.join(
                    sample.paths.sample_root, "unmapped")
                input_fastq = os.path.join(
                    unmapped_dir, sample.name + ".fastq.gz")
                cmd += "bedtools bamtofastq -i {} -fq /dev/stdout | gzip > {}\n".format(
                    sample.data_path, input_fastq)
                if not os.path.exists(unmapped_dir):
                    os.makedirs(unmapped_dir)
            else:
                input_fastq = sample.data_path

            mapped_dir = os.path.join(sample.paths.sample_root, "mapped")
            output_bam = os.path.join(mapped_dir, sample.name + ".bowtie2.filtered.bam")
            if not os.path.exists(mapped_dir):
                os.makedirs(mapped_dir)

            cpus = kwargs['cpu'] if "cpu" in kwargs else 4
            cmd += ("bowtie2 -x {i} -p {c} -5 {t5} -3 {t3} -U {fq}" +
                    " | samtools view -q {qual} -b - > {out}\n").format(
                        i=bowtie2_index_prefix, c=cpus,
                        t5=trim[0], t3=trim[1],
                        qual=mapping_quality,
                        fq=input_fastq, out=output_bam)

            cmd += "date\n"

            with open(job_file, 'w') as handle:
                handle.write(cmd)

            if not distributed:
                kwargs.update({"computing_configuration": "localhost"})

            submit_job(
                cmd, job_file,
                jobname=job_name,
                logfile=log_file,
                cores=4, mem=8000, time="06:00:00", **kwargs)

    def run_mageck(
            self,
            samples=None,
            output_prefix="mageck",
            guide_reference=None,
            distributed=False,
            **kwargs):
        """
        """
        from ngs_toolkit.utils import submit_job

        if samples is None:
            samples = self.samples
        if guide_reference is None:
            guide_reference = self.guide_reference

        if guide_reference is None:
            # this still tries to quantify every gRNA without reference
            msg = "No guide RNA annotation was given."
            msg += " Will try to quantify every sequence."
            hint = " Provide a reference containing the 'guide_id',"
            hint += " 'guide_sequence'"
            hint += " and 'gene_id' columns to `guide_reference`."
            _LOGGER.warning(msg)
            guide_reference = pd.DataFrame(
                columns=['guide_sequence', 'gene_id', 'guide_type'])

        # Write guide annotation to disk
        output_dir = os.path.join(self.data_dir, "mageck")
        o_prefix = os.path.join(output_dir, output_prefix)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        guide_file = os.path.join(o_prefix + ".annotation.for_mageck.csv")
        with open(guide_file, 'w') as handle:
            for guide, row in guide_reference.loc[
                    :, ['guide_sequence', 'gene_id']].iterrows():
                handle.write(guide + "," + ",".join(row.fillna("NaN")) + "\n")

        # Write annotation of negative controls to disk
        neg_control_file = os.path.join(
            o_prefix + ".neg_control_annotation.for_mageck.csv")
        if "guide_type" in guide_reference.columns:
            df = guide_reference.query(
                "guide_type == '{}'".format(self.neg_control))
        else:
            df = pd.DataFrame()
        with open(neg_control_file, 'w') as handle:
            for guide in df.index:
                handle.write(guide + "\n")

        for sample in samples:
            mapped_dir = os.path.join(sample.paths.sample_root, "mapped")
            sample.aligned_filered_bam = os.path.join(
                mapped_dir, sample.name + ".bowtie2.filtered.bam")

        cmd = "mageck count --list-seq {}".format(guide_file)
        cmd += " --control-sgrna {}".format(neg_control_file)
        if distributed:
            for sample in samples:
                job_name = sample.name + "." + output_prefix
                job_file = os.path.join(
                    sample.paths.sample_root, job_name + ".sh")
                log_file = os.path.join(
                    sample.paths.sample_root, job_name + ".log")
                output_dir = os.path.join(sample.paths.sample_root, "mageck")
                s_prefix = os.path.join(
                    output_dir, sample.name + "." + output_prefix)
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)

                s_cmd = cmd + " --fastq {} --sample-label {} -n {}".format(
                    sample.aligned_filered_bam, sample.name, s_prefix)

                submit_job(
                    s_cmd, job_file,
                    jobname=job_name,
                    logfile=log_file,
                    cores=4, mem=8000, time="06:00:00", **kwargs)

        else:
            kwargs['computing_configuration'] = "localhost"
            job_name = self.name + "." + output_prefix
            job_file = os.path.join(self.data_dir, job_name + ".sh")
            log_file = os.path.join(self.data_dir, job_name + ".log")

            cmd += " --fastq {} --sample-label {} -n {}".format(
                " ".join([s.aligned_filered_bam for s in samples]),
                " ".join([s.name for s in samples]),
                o_prefix)

            submit_job(
                cmd, job_file,
                jobname=job_name,
                logfile=log_file,
                cores=4, mem=8000, time="06:00:00", **kwargs)

    def collect_mageck_data(
            self,
            samples=None,
            input_prefix="mageck",
            output_file="{results_dir}/{name}.matrix_raw.csv",
            assign=True, save=True,
            permissive=False,
            collect_metrics=True):
        """
        """
        if samples is None:
            samples = self.samples

        output_file = self._format_string_with_attributes(output_file)

        res = list()
        metrics = list()
        for sample in samples:

            # Counts
            output_dir = os.path.join(sample.paths.sample_root, "mageck")
            f = os.path.join(
                output_dir, "{}.{}.count.txt"
                .format(sample.name, input_prefix))
            try:
                r = pd.read_csv(f, sep="\t").assign(sample_name=sample.name)
            except (IOError, OSError):
                if permissive:
                    continue
                else:
                    msg = "Could not open file '{}'.".format(f)
                    _LOGGER.error(msg)
            res.append(r.set_index('sgRNA')[sample.name].rename(sample.name))

            # Metrics
            if collect_metrics:
                metrics_f = os.path.join(
                    output_dir, "{}.{}.countsummary.txt"
                    .format(sample.name, input_prefix))
                try:
                    m = pd.read_csv(metrics_f, sep="\t")
                except (IOError, OSError):
                    if permissive:
                        continue
                    else:
                        msg = "Could not open file '{}'.".format(f)
                        _LOGGER.error(msg)
                metrics.append(m)

        matrix = pd.concat(res, axis=1, sort=True)
        matrix = matrix.loc[~(matrix == 0).all(axis=1)]
        metrics = (
            pd.concat(metrics).drop(['File'], axis=1)
            .rename(columns={"Label": "sample_name"})
            .set_index("sample_name"))

        if assign:
            self.matrix_raw = matrix

        if save:
            matrix.to_csv(output_file)
            if collect_metrics:
                metrics.to_csv(output_file.replace("matrix_raw", "metrics"))

        if collect_metrics:
            return matrix, metrics
        else:
            return matrix

    def normalize_to_reference():
        """
        """
        pass

    def assess_guide_uniformity(
            self,
            matrix="matrix_raw",
            samples=None,
            output_dir="{results_dir}",
            output_prefix="guide_uniformity"):
        """
        """
        # TODO: Plot rank vs Z-score for grnas and genes

        import matplotlib.pyplot as plt
        from ngs_toolkit.graphics import savefig

        def get_mapping_rates(samples):
            mapping_rates = dict()
            for sample in samples:
                mapped_dir = os.path.join(sample.paths.sample_root, "mapped")
                sample.aligned_filered_bam = os.path.join(
                    mapped_dir, sample.name + ".bowtie2.bam")
                job_name = sample.name + ".mapping"
                log_file = os.path.join(
                    sample.paths.sample_root, job_name + ".log")
                with open(log_file, 'r') as handle:
                    log = handle.readlines()
                mapping_rates[sample.name] = float(
                    log[-2].strip().split(" ")[0].replace("%", ""))
            return pd.Series(mapping_rates, name="mapping_rate")

        def gini(array):
            """Calculate the Gini coefficient of a numpy array."""
            array = array.flatten()
            if np.amin(array) < 0:
                array -= np.amin(array)
            # Values cannot be 0:
            array += 0.0000001
            # Values must be sorted:
            array = np.sort(array)
            # Index per array element:
            index = np.arange(1, array.shape[0] + 1)
            # Number of array elements:
            n = array.shape[0]
            # Gini coefficient:
            return ((np.sum((2 * index - n - 1) * array)) / (n * np.sum(array)))

        matrix = self.get_matrix(matrix, samples=samples).sort_index(axis=1)
        # matrix = matrix.reindex(guide_reference.index)
        if samples is None:
            samples = [s for s in self.samples if s.name in matrix.columns]

        output_dir = self._format_string_with_attributes(output_dir)

        # metrics = pd.DataFrame(
        #     [get_mapping_rates(samples),
        #      matrix.apply(gini).rename("gini_coefficient")]).T
        # metrics = metrics.join(self.get_sample_annotation())
        if "metrics" in globals():
            ginis = globals()['metrics'].loc[:, 'GiniIndex']
        else:
            ginis = pd.Series({
                s.name: gini(matrix[s.name].dropna().values)
                for s in samples})

        label = "{}; Gini coefficient: {:.2f}"
        name = "{}\nGini coefficient: {:.2f}"

        # All samples together
        # # jointly
        prefix = os.path.join(output_dir, output_prefix)
        n = int(np.ceil(np.sqrt(len(samples))))

        fig, axis = plt.subplots(1, 1, figsize=(1 * 4, 4), squeeze=True)
        colormap = plt.get_cmap("rainbow")(
            np.linspace(0, 1, matrix.shape[1]))
        axis.plot((0, 1), (0, 1), linestyle="--", color="grey")
        for i, sample in enumerate(matrix.columns):
            vector = matrix[sample].sort_values().dropna()
            axis.plot(
                vector.rank() / vector.shape[0],
                vector.cumsum() / vector.sum(),
                label=label.format(sample, ginis[sample]),
                color=colormap[i], alpha=0.5)
            axis.set_xlabel("ranked gRNAs (fraction)")
            axis.set_ylabel("Cumulative fraction")
        # # shrink axis height by 10% on the bottom
        # # and put a legend below current axis
        box = axis.get_position()
        axis.set_position([box.x0, box.y0 + box.height * 0.1,
                           box.width, box.height * 0.9])
        axis.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15),
                    fancybox=True, shadow=True, ncol=1)
        savefig(
            fig,
            prefix + ".gini_plot.lines.all_together.svg")

        # # separately
        fig, axis = plt.subplots(
            n, n, figsize=(n * 4, n * 4),
            sharex=True, sharey=True, squeeze=False)
        for i, sample in enumerate(matrix.columns):
            vector = matrix[sample].sort_values().dropna()
            axis.flat[i].plot(
                (0, 1), (0, 1),
                linestyle="--", color="grey")
            axis.flat[i].plot(
                vector.rank() / vector.shape[0], vector.cumsum() / vector.sum(),
                label=label.format(sample, ginis[sample]),
                color=colormap[i], alpha=0.5)
            axis.flat[i].set_title(
                name.format(sample, ginis[sample]))
        for ax in axis[-1, :]:
            ax.set_xlabel("ranked gRNAs (fraction)")
        for ax in axis[:, 0]:
            ax.set_ylabel("Cumulative fraction")
        savefig(
            fig,
            prefix + ".gini_plot.lines.separately.svg")

        # Rank vs Z-score
        fig, axis = plt.subplots(1, 1, figsize=(1 * 4, 4), squeeze=True)
        colormap = plt.get_cmap("rainbow")(
            np.linspace(0, 1, matrix.shape[1]))
        axis.axhline(0, linestyle="--", color="grey")
        for i, sample in enumerate(matrix.columns):
            vector = matrix[sample].sort_values().dropna()
            axis.plot(
                vector.rank() / vector.shape[0],
                (vector - vector.mean()) / vector.std(),
                label=sample,
                color=colormap[i], alpha=0.5)
            axis.set_xlabel("gRNAs (fraction of total)")
            axis.set_ylabel("Z-score")
        # # shrink axis height by 10% on the bottom
        # # and put a legend below current axis
        box = axis.get_position()
        axis.set_position([box.x0, box.y0 + box.height * 0.1,
                           box.width, box.height * 0.9])
        axis.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15),
                    fancybox=True, shadow=True, ncol=1)
        savefig(
            fig,
            prefix + ".rank_vs_zscore.lines.all_together.svg")

        # Reads vs gRNAs and fold change
        fig, axis = plt.subplots(1, 1, figsize=(1 * 4, 4), squeeze=True)
        axis.plot((0, 1), (0, 1), linestyle="--", color="grey")
        colormap = plt.get_cmap("rainbow")(
            np.linspace(0, 1, matrix.shape[1]))
        qs = list()
        for q in [0.1, 0.9]:
            axis.axvline(q, linestyle="--", color="grey")
            qs.append(matrix.apply(lambda x: np.quantile(x.dropna(), q=q)))
        qs = qs[1] / qs[0]
        for i, sample in enumerate(matrix.columns):
            vector = matrix[sample].sort_values().dropna()
            axis.plot(
                vector.cumsum() / vector.sum(),
                np.arange(vector.shape[0]) / vector.shape[0],
                label="{}; Fold change: {:.2f}".format(sample, qs[sample]),
                color=colormap[i], alpha=0.5)
            axis.set_xlabel("Cumulative fraction")
            axis.set_ylabel("gRNAs (% of total)")
        # # shrink axis height by 10% on the bottom
        # # and put a legend below current axis
        box = axis.get_position()
        axis.set_position([box.x0, box.y0 + box.height * 0.1,
                           box.width, box.height * 0.9])
        axis.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15),
                    fancybox=True, shadow=True, ncol=1)
        savefig(
            fig,
            prefix + ".reads_vs_gRNAs.lines.all_together.svg")

        # Now separately for each library
        for library in {getattr(s, "guide_reference", None) for s in samples}:
            lib_samples = [
                s for s in samples
                if getattr(s, "guide_reference", None) == library]
            lib_matrix = matrix.loc[:, [s.name for s in lib_samples]].dropna().astype(int)

            prefix = os.path.join(output_dir, ".".join([output_prefix, library]))

            n = int(np.ceil(np.sqrt(len(lib_samples))))

            lib_matrix = lib_matrix.reindex(lib_matrix.median(1).sort_values().index)
            fig, axis = plt.subplots(
                n, n, figsize=(n * 4, n * 4),
                sharex=True, sharey=True, squeeze=False)
            for i, sample in enumerate(lib_matrix.columns):
                vector = lib_matrix[sample].dropna()
                axis.flat[i].plot(
                    (0, 1), (0, 1), linestyle="--", color="grey")
                axis.flat[i].scatter(
                    vector.rank() / vector.shape[0], vector.cumsum() / vector.sum(),
                    label=label.format(sample, ginis[sample]),
                    color=colormap[i], alpha=0.1, s=1,
                    rasterized=True)
                axis.flat[i].set_title(
                    name.format(sample, ginis[sample]))
            for ax in axis[-1, :]:
                ax.set_xlabel("ranked gRNAs (fraction)")
            for ax in axis[:, 0]:
                ax.set_ylabel("Cumulative fraction")
            savefig(
                fig,
                prefix + ".gini_plot.scatter.svg")

            plasmid_control = lib_matrix.columns[0]
            lib_matrix = lib_matrix.reindex(
                lib_matrix[plasmid_control].sort_values().index)
            fig, axis = plt.subplots(
                n, n, figsize=(n * 4, n * 4),
                sharex=True, sharey=True, squeeze=False)
            for i, sample in enumerate(lib_matrix.columns):
                vector = lib_matrix[sample].dropna()
                axis.flat[i].plot((0, 1), (0, 1), linestyle="--", color="grey")
                axis.flat[i].scatter(
                    vector.rank(), vector.cumsum() / vector.sum(),
                    label=sample,
                    color=colormap[i], alpha=0.1, s=1,
                    rasterized=True)
                axis.flat[i].set_title(
                    name.format(sample, ginis[sample]))
            for ax in axis[-1, :]:
                ax.set_xlabel("gRNA (rank)")
            for ax in axis[:, 0]:
                ax.set_ylabel("Cumulative fraction")
            savefig(
                fig,
                prefix + ".gini_plot.scatter.plasmid_control.svg")

    def get_gene_level_matrix(
            self,
            matrix="matrix_norm",
            guide_reference=None,
            reduce_func=np.mean,
            assign=True,
            save=True,
            output_file="{results_dir}/{name}.gene_coverage.csv"):
        """
        Get gene-level measurements of coverage.

        Requires a 'guide_reference' attribute to be set or passed
        containing a mapping between the index of `matrix` and genes
        (guide-gene annotation).

        Parameters
        ----------
        matrix : :obj:`str`, optional
            Quantification matrix to use (e.g. 'matrix_raw' or 'matrix_norm')

            Default is "matrix_norm".
        matrix : :obj:`pd.DataFrame`, optional
            A mapping of guideRNA to genes.

            Defaults to the analysis "guide_reference".
        reduce_func : func
            Function to apply to reduce values.

            Default is mean.
        assign: :obj:`bool`
            Whether to assign the matrix to an attribute named `matrix_gene`.

            Default is :obj:`True`.
        save: :obj:`bool`
            Whether to save the coverage matrix with filename `output_file`.

            Default is :obj:`True`.
        output_file : :obj:`str`
            Path to save a CSV file with coverage output if `save` is `True`.

            Default is `self.results_dir/self.name + ".raw_coverage.csv"`.

        Returns
        ---------
        pandas.DataFrame
            Coverage values reduced per gene.

        Attributes
        ---------
        matrix_gene : :obj:`pandas.DataFrame`
            Coverage values reduced per gene.
        """
        matrix = self.get_matrix(matrix).copy()
        if guide_reference is None:
            guide_reference = self.guide_reference

        matrix2 = (
            matrix.join(guide_reference[['gene_id']])
            .groupby('gene_id')
            .apply(reduce_func))

        if assign:
            self.matrix_gene = matrix2
        if save:
            matrix2.to_csv(self._format_string_with_attributes(output_file))
        return matrix2

    def get_gene_level_changes(
            self,
            differential_results=None,
            guide_reference=None,
            variability_analysis=True,
            output_dir="{results_dir}/differential_analysis_{data_type}",
            output_prefix="differential_analysis.per_gene"):
        """
        """
        from scipy.stats import combine_pvalues
        from statsmodels.stats.multitest import multipletests
        import matplotlib.pyplot as plt
        from ngs_toolkit.graphics import savefig

        output_dir = self._format_string_with_attributes(output_dir)
        output_prefix = self._format_string_with_attributes(output_prefix)

        if differential_results is None:
            differential_results = self.differential_results
        if guide_reference is None:
            guide_reference = self.guide_reference

        # Add guide info
        res = differential_results.join(guide_reference[['gene_id']])
        res_gene = res.groupby(['comparison_name', 'gene_id']).agg(
            {'baseMean': [np.mean, np.std],
             'log2FoldChange': [np.mean, np.std],
             'pvalue': lambda x: combine_pvalues(x)[1]})
        res_gene.columns = [
            'baseMean', 'baseMean_std',
            'log2FoldChange', 'log2FoldChange_std',
            'pvalue']
        res_gene.loc[:, "padj"] = multipletests(res_gene['pvalue'])[1]
        res_gene = res_gene.reset_index()

        # Exclude controls
        ctrls = ['neg_control', 'pos_control']
        for ctrl in ctrls:
            value = str(getattr(self, ctrl, None))
            res_gene = res_gene.loc[
                ~res_gene['gene_id'].str.startswith(value), :]

        # plot rank vs std for gene
        if variability_analysis:
            fig, axis = plt.subplots(1, 2, figsize=(2 * 4, 4))
            axis[0].scatter(
                res_gene['log2FoldChange'], res_gene['log2FoldChange_std'],
                c=np.log10(res_gene['baseMean']),
                alpha=0.2, s=2, rasterized=True)
            axis[1].scatter(
                np.log10(res_gene['baseMean_std']), res_gene['log2FoldChange_std'],
                c=np.log10(res_gene['baseMean']),
                alpha=0.2, s=2, rasterized=True)
            axis[0].set_xlabel("mean(log2(fold-change))")
            axis[0].set_ylabel("std(log2(fold-change))")
            axis[1].set_xlabel("std(log10(mean))")
            axis[1].set_ylabel("std(log2(fold-change))")
            savefig(fig, os.path.join(output_dir, output_prefix + ".svg"))

        res_gene.to_csv(os.path.join(output_dir, output_prefix + ".csv"), index=False)
        return res_gene.set_index("gene_id")

    def plot_sample_stats(
            self,
            matrix="matrix_raw",
            samples=None,
            grna_annotation=None,
            output_dir="{results_dir}",
            output_prefix="sample_stats"):
        """
        """
        import matplotlib.pyplot as plt
        from ngs_toolkit.graphics import savefig

        if isinstance(matrix, str):
            matrix = getattr(self, matrix)

        if grna_annotation is None:
            if hasattr(self, "grna_annotation"):
                grna_annotation = self.grna_annotation
            else:
                msg = ""
                _LOGGER.warning(msg)

        grna_space = (
            matrix.shape[0]
            if grna_annotation is None
            else grna_annotation.shape[0])
        gene_space = (
            matrix.shape[0]
            if grna_annotation is None
            else grna_annotation['Gene'].nunique())

        # reads per sample
        sample_stats = matrix.sum().to_frame(name="reads").assign(
            grnas=(matrix.groupby(level=0).sum() > 0).sum(),
            genes=(matrix.groupby(level=1).sum() > 0).sum())
        sample_stats = sample_stats.assign(
            grna_fraction=sample_stats['grnas'] / grna_space,
            gene_fraction=sample_stats['genes'] / gene_space)

        variables = sample_stats.columns.drop("reads")
        v = len(variables)
        fig, axis = plt.subplots(2, v, figsize=(v * 3, 3 * 2))
        for i, var in enumerate(variables):
            for a in axis[:, i]:
                a.scatter(sample_stats['reads'], sample_stats[var], alpha=0.5)
                a.set_xlabel("Reads")
                a.set_ylabel(var)
            axis[1][i].loglog()
        savefig(
            fig,
            os.path.join(output_dir, self.name + "." + output_prefix + ".svg"))

    def get_screen_metrics(
            self,
            matrix="matrix_raw",
            samples=None,
            grna_annotation=None,
            output_dir="{results_dir}",
            output_prefix="sample_stats"):
        pass

        # if plasmid control, uniformity of guide representation

        # within gene vs between gene variability of gRNAs

        # screen Z-score (diff pos controls vs neg control)


def guess_crispr_sample_trimming_lengths(
        bam_file, n=250, homology_fraction=0.75,
        recursive_count=0, max_recursive=5):
    import pysam

    def failure():
        if max_recursive == recursive_count:
            return np.nan, np.nan
        else:
            return guess_crispr_sample_trimming_lengths(
                bam_file,
                n=int(n * 2),
                homology_fraction=homology_fraction + homology_fraction * 0.1,
                recursive_count=recursive_count + 1,
                max_recursive=max_recursive)

    # Read up N sequences
    bam = pysam.AlignmentFile(bam_file, check_sq=False)
    seqs = list()
    for i, read in enumerate(bam):
        if i == n:
            break
        seqs.append(read.seq)

    fract = (
        pd.Series(seqs).str.split('').apply(pd.Series)  # expand to seqs
        .apply(pd.Series.value_counts, axis=0).fillna(0)  # count bases
        .astype(int)
        .loc[["A", "C", "G", "T"]].iloc[:, 1:-1]  # remove ends which are empty
        .T  # transpose
        / n  # normalize to reads read
    )
    # Get section which has more than `homology_fraction` homology
    consensus = fract[(fract > homology_fraction).any(1)]
    if consensus.empty:
        return failure()
    read_length = consensus.index[-1] - 1

    # Find out where the sequence broke (assumes gRNA is in middle of read!)
    for i, v in consensus.index.to_series().reset_index(drop=True).items():
        if i != v - 1:
            break
    left_trimming = i
    right_trimming = read_length - v + 1
    grna_length = read_length - (left_trimming + right_trimming)

    print((
        os.path.basename(bam_file),
        left_trimming, right_trimming + 1, grna_length))

    # If gRNA length is extreme, repeat with more seqs
    if (grna_length < 18) or (grna_length > 22):
        return failure()
    return left_trimming, right_trimming + 1


def count_grnas(bam_file, n_top):
    import re
    import pysam

    pattern = re.compile(r"AACACCG(.*)GTTTTAG")
    bam = pysam.AlignmentFile(bam_file, check_sq=False)
    res = list()
    for i, read in enumerate(bam):
        if i == n_top:
            break
        m = pattern.search(read.seq)
        if m:
            res.append(m.groups()[0])
    return pd.Series(res).value_counts()
