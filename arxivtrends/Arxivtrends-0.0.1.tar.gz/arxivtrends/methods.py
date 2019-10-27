import re
import urllib
from PyPDF2 import PdfFileReader, utils
from io import BytesIO
import datetime
import numpy as np



macro_fields = {
    'Elliptic PDE':['35J05', '35J10', '35J15', '35J20', '35J25', '35J30', '35J35', '35J40', '35J45', '35J50', '35J55', '35J60', '35J65', '35J67', '35J70', '35J85'],
    'Fourier Analysis':['42A05', '42A10', '42A15', '42A16', '42A20', '42A24', '42A32', '42A38', '42A45', '42A50', '42A55', '42A61', '42A63', '42A65', '42A70', '42A75', '42A82', '42A85', '42B05', '42B08', '42B10', '42B15', '42B20', '42B25', '42B30', '42B35', '42C10', '42C15', '42C20', '42C25', '42C30', '42C40'],
    'Abstract Fourier Analysis':['43A05', '43A07', '43A10', '43A15', '43A17', '43A20', '43A22', '43A25', '43A30', '43A32', '43A35', '43A40', '43A45', '43A46', '43A50', '43A55', '43A60', '43A62', '43A65', '43A70', '43A75', '43A77', '43A80', '43A85', '43A90'],
    'Fluid Mechanics PDE': ['76A02','76A05','76A10','76A15','76A20','76A25','76A99','76B03','76B07','76B10','76B15','76B20','76B25','76B45','76B47','76B55','76B60','76B65','76B70','76D03','76D05','76D06','76D07','76D08','76D09','76D10','76D17','76D25','76D27','76D33','76D45','76D50','76D55','76E05','76E06','76E07','76E09','76E15','76E17','76E19','76E20','76E25','76E30','76E99','76Fxx','76F02','76F05','76F06','76F10','76F20','76F25','76F30','76F35','76F40','76F45','76F50','76F55','76F60','76F65','76F70','76F99','76G25]','76H05','76J20','76K05','76L05','76M10','76M12','76M15','76M20','76M22','76M23','76M25','76M27','76M28','76M30','76M35','76M40','76M45','76M50','76M55','76M60','76N10','76N15','76N17','76N20','76N25','76N99','76P05','76Q05','76Rxx','76R05','76R10','76R50', '76S05']
}




"""
The function of the url_query method is to build the component of the API request
that contains The MSC codes that fall under the category of the research
field passed in as the parameter for the instantiation of Scraper. These codes
are contained in the dictionary macro_fields. Being the MSC classification not
presently indexed in the search arXiv API, there is currently no alternative way
to the use of the long urls that url_query returns.
"""
def url_query(macro_field):
    if macro_field in macro_fields.keys():
        list = macro_fields.get(macro_field)
        for subfield in list[1:]:
            list[0] = list[0] + '+OR+all:' + subfield
        return 'all:' + list[0]
    else:
        raise ValueError




"""
The get_authors method extracts the names of the authors of a preprint from the
content of the correspondent post-query-response xml tag. A test on the validity
of the parameter authors as a nonempty list is included.
"""
def get_authors(authors):
    if authors == None or len(authors) == 0:
        return None
    else:
        list_authors = [];
        for researcher in authors:
            list_authors.append(researcher.get('name'))
        return list_authors


"""
The get_num_pages method returns the number of pages of a preprint or None if this
data is unavailable - for example, if the preprint was withdrawn. For a significant
majority of preprints this number can be extracted from the content of their
post-query-response xml tags 'arxiv_comment' or 'arxiv_journal_ref', the latter
case (occurring less frequently) through the pages_from_journal method. Either way,
the extraction is implemented via regular expressions (see the find_match method).
Various variants of the pattern 'number of pages' + "pages" are considered in their
order of frequency, which is reflected in the nesting of the if/else statements).
When the number of pages of the preprint is missing or not identifiable in the
aforementioned tags's content, the method pages_from_url is called.
"""

PREPRINT_COMMENT = 'arxiv_comment'
PREPRINT_JOURNAL_REFERENCE = 'arxiv_journal_ref'

def get_num_pages(record, i):
    if record.get(PREPRINT_COMMENT) == None:
        if record.get(PREPRINT_JOURNAL_REFERENCE) == None:
            return pages_from_url(record, i)
        else:
            return pages_from_journal(record)
    else:
        pages = find_match(0, record.get(PREPRINT_COMMENT))
        if pages == None:
            pages = pages_from_journal(record)
            if pages == None:
                pages = find_match(1, record.get(PREPRINT_COMMENT))
                if pages == None:
                    pages = find_match(2, record.get(PREPRINT_COMMENT))
                    if pages == None:
                        pages = pages_from_url(record, i)
    return pages



"""
The pages_from_journal method extracts the number of pages of a preprint when a
final version of the paper has been published and its range of pages in the
journal is included in the content of the post-query-response xml tag
'arxiv_journal_ref'. When this is the case, the range of pages is usually
recognizable by two numbers separated by a '-'. Via regular expressions it's
possible to detect this patern and the number of pages of the paper is simply
the difference between the number on the right and the one on the left.
"""
def pages_from_journal(record):
    if record.get(PREPRINT_JOURNAL_REFERENCE) == None:
        return None
    else:
        pattern = re.compile(r'(.\d\d-\d\d.|\d\d-\d\d|.\d\d-\d\d\d|\d\d\d\d-\d\d\d\d)')
        matches = pattern.findall(record.get(PREPRINT_JOURNAL_REFERENCE))
        if len(matches) == 1 and len(re.findall(r'\d+', matches[0])) == 2:
            pages = int(re.findall(r'\d+', matches[0])[1]) - int(re.findall(r'\d+', matches[0])[0])
        else:
            pages = None
    return pages





"""
The find_match method use pattern matching to search for particular strings of
characters that are likely to contain numbers of pages of arXiv preprints. First
(i=0) it looks for the key word "pages" and checks if there are two or three
digits preceeding it (for example "134 pages" or "12pages"), this being the way
the number of pages is expressed for a significant majority of preprints. If
there are no matches, it applies the same search engine to the key words "pp"
(i=1) and "pgs" (i=2), less frequent variants. In any case, either it retrieves and
returns the number before the key word or returns None if it cannot find one.
"""
def find_match(i, text):
    if i == 0:
        pattern = re.compile(r'(...page|....page)')
    if i == 1:
        pattern = re.compile(r'(...pp|....pp)')
    if i == 2:
        pattern = re.compile(r'(...pgs|....pgs)')
    matches = pattern.findall(text)
    if len(matches) > 0:
        for match in matches:
            pass
        if len(re.findall(r'\d+', match)) > 0:
            return int(re.findall(r'\d+', match)[-1])
        else:
            # no nummber preceeding the alphabetical match
            return None
    else:
        # no alphabetical match in the text
        return None



"""
The pdf_url method takes in the arXiv url of a preprint and returns the url of
its PDF link, necessary if the number of pages of that preprint is not
included in the response we obtained from the arXiv API. It suffices to remove
the substring 'abs' and replace it with 'pdf'.
"""
def pdf_url(url_text):
    return re.sub("abs", "pdf", url_text)



"""
The pages_from_url method takes in the post-query-response xml record of an
arXiv preprint and its index (i), opens the PDF and retrieves the number of
pages of the preprint. Pages_from_url is called only when this number is not
included in the response we obtained from the arXiv API. The index i is used to
halt the execution of the scraping loop for a pseudorandom number of seconds (at
least 3 and at most 7). This is a precaution taken in order to avoid risking to
exceed the requests rate limit set by the arXiv API (see arXiv APIs terms of use).
If the PDf link is not active - typically when the preprint was withdrawn -
pages_from_url returns None.
"""
def pages_from_url(record, i):
    if record.get('id') == None:
        return None
    else:
        url = pdf_url(record.get('id'))
        try:
            time.sleep(np.max([i%7, 3]))
            link = urllib.request.urlopen(url)
            content=link.read()
            memoryFile = BytesIO(content)
            pdfFile = PdfFileReader(memoryFile)
            return pdfFile.getNumPages()
        except utils.PdfReadError:
            return None
        except urllib.error.HTTPError:
            return None





"""
The get_year method extracts the submission year of a preprint from the
content of the post-query-response xml record for that preprint. This content is
almost always a string and the submission year is contained in the first four
characters of this string.
"""
def get_year(record):
    num = record[:4]
    if len(num) == 4 and num.isdigit():
        return int(num)
    else:
        return None




"""
The get_details method returns the second component of the name of the .csv file
that is created at the end of the parsing loop started by the scrape method (the
first one being 'Arxivtrends__'). The whitespace characters in the string contained
in the macro_field parameter are replaced by '_' and both current year and month
are added.
"""
def get_details(macro_field):
    year = datetime.datetime.now().year
    month = datetime.datetime.now().month
    return re.sub(" ", "_", macro_field) + '__' + str(year) + '-' + str(month)
