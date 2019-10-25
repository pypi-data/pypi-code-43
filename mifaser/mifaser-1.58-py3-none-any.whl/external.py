"""
External code used in mi-faser.

Instead of supplying an entire library
ony required parts are added here.

References to source of external scripts
can be found below.
"""


"""
source: biopython (http://biopython.org)
        Bio/SeqIO/QualityIO.py
"""


def FastqGeneralIterator(handle):
    # We need to call handle.readline() at least four times per record,
    # so we'll save a property look up each time:
    handle_readline = handle.readline

    line = handle_readline()
    if not line:
        return  # Premature end of file, or just empty?
    if isinstance(line[0], int):
        raise ValueError("Is this handle in binary mode not text mode?")

    while line:
        if line[0] != "@":
            raise ValueError(
                "Records in Fastq files should start with '@' character")
        title_line = line[1:].rstrip()
        # Will now be at least one line of quality data - in most FASTQ files
        # just one line! We therefore use string concatenation (if needed)
        # rather using than the "".join(...) trick just in case it is multiline:
        seq_string = handle_readline().rstrip()
        # There may now be more sequence lines, or the "+" quality marker line:
        while True:
            line = handle_readline()
            if not line:
                raise ValueError("End of file without quality information.")
            if line[0] == "+":
                # The title here is optional, but if present must match!
                second_title = line[1:].rstrip()
                if second_title and second_title != title_line:
                    raise ValueError("Sequence and quality captions differ.")
                break
            seq_string += line.rstrip()  # removes trailing newlines
        # This is going to slow things down a little, but assuming
        # this isn't allowed we should try and catch it here:
        if " " in seq_string or "\t" in seq_string:
            raise ValueError("Whitespace is not allowed in the sequence.")
        seq_len = len(seq_string)

        # Will now be at least one line of quality data...
        quality_string = handle_readline().rstrip()
        # There may now be more quality data, or another sequence, or EOF
        while True:
            line = handle_readline()
            if not line:
                break  # end of file
            if line[0] == "@":
                # This COULD be the start of a new sequence. However, it MAY just
                # be a line of quality data which starts with a "@" character.  We
                # should be able to check this by looking at the sequence length
                # and the amount of quality data found so far.
                if len(quality_string) >= seq_len:
                    # We expect it to be equal if this is the start of a new record.
                    # If the quality data is longer, we'll raise an error below.
                    break
                # Continue - its just some (more) quality data.
            quality_string += line.rstrip()

        if seq_len != len(quality_string):
            raise ValueError("Lengths of sequence and quality values differs "
                             " for %s (%i and %i)."
                             % (title_line, seq_len, len(quality_string)))

        # Return the record and then continue...
        yield (title_line, seq_string, quality_string)


"""
source: biopython (http://biopython.org)
        Bio/SeqIO/_convert.py
"""


def fastq_convert_fasta(in_handle, out_handle, alphabet=None):
    """Fast FASTQ to FASTA conversion (PRIVATE).
    Avoids dealing with the FASTQ quality encoding, and creating SeqRecord and
    Seq objects in order to speed up this conversion.
    NOTE - This does NOT check the characters used in the FASTQ quality string
    are valid!
    """
    # from Bio.SeqIO.QualityIO import FastqGeneralIterator
    # For real speed, don't even make SeqRecord and Seq objects!
    count = 0
    for title, seq, _qual in FastqGeneralIterator(in_handle):
        count += 1
        out_handle.write(">%s\n" % title)
        # Do line wrapping
        for i in range(0, len(seq), 60):
            out_handle.write(seq[i:i + 60] + "\n")
    return count


"""
source: biopython (http://biopython.org)
        Bio/SeqUtils/CheckSum
"""

import codecs


def _as_bytes(s):
    """Turn byte string or unicode string into a bytes string.

    The Python 2 version returns a (byte) string.
    """
    if isinstance(s, bytes):
        return s
    # Assume it is a unicode string
    # Note ISO-8859-1 aka Latin-1 preserves first 256 chars

    return codecs.latin_1_encode(s)[0]


def seguid(seq):
    """Return the SEGUID (string) for a sequence (string or Seq object).

    Given a nucleotide or amino-acid secuence (or any string),
    returns the SEGUID string (A SEquence Globally Unique IDentifier).
    seq type = str.

    Note that the case is not important:

    >>> seguid("ACGTACGTACGT")
    'If6HIvcnRSQDVNiAoefAzySc6i4'
    >>> seguid("acgtACGTacgt")
    'If6HIvcnRSQDVNiAoefAzySc6i4'

    For more information about SEGUID, see:
    http://bioinformatics.anl.gov/seguid/
    https://doi.org/10.1002/pmic.200600032
    """
    import hashlib
    import base64
    m = hashlib.sha1()
    try:
        # Assume it's a Seq object
        seq = str(seq)
    except AttributeError:
        # Assume it's a string
        pass
    m.update(_as_bytes(seq.upper()))
    try:
        # For Python 3+
        tmp = base64.encodebytes(m.digest())
        return tmp.decode().replace("\n", "").rstrip("=")
    except AttributeError:
        pass
    # For all other Pythons
    return base64.b64encode(m.digest()).rstrip("=")
