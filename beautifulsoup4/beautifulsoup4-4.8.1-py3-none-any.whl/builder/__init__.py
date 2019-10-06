# Use of this source code is governed by the MIT license.
__license__ = "MIT"

from collections import defaultdict
import itertools
import sys
from bs4.element import (
    CharsetMetaAttributeValue,
    ContentMetaAttributeValue,
    nonwhitespace_re
    )

__all__ = [
    'HTMLTreeBuilder',
    'SAXTreeBuilder',
    'TreeBuilder',
    'TreeBuilderRegistry',
    ]

# Some useful features for a TreeBuilder to have.
FAST = 'fast'
PERMISSIVE = 'permissive'
STRICT = 'strict'
XML = 'xml'
HTML = 'html'
HTML_5 = 'html5'


class TreeBuilderRegistry(object):

    def __init__(self):
        self.builders_for_feature = defaultdict(list)
        self.builders = []

    def register(self, treebuilder_class):
        """Register a treebuilder based on its advertised features."""
        for feature in treebuilder_class.features:
            self.builders_for_feature[feature].insert(0, treebuilder_class)
        self.builders.insert(0, treebuilder_class)

    def lookup(self, *features):
        if len(self.builders) == 0:
            # There are no builders at all.
            return None

        if len(features) == 0:
            # They didn't ask for any features. Give them the most
            # recently registered builder.
            return self.builders[0]

        # Go down the list of features in order, and eliminate any builders
        # that don't match every feature.
        features = list(features)
        features.reverse()
        candidates = None
        candidate_set = None
        while len(features) > 0:
            feature = features.pop()
            we_have_the_feature = self.builders_for_feature.get(feature, [])
            if len(we_have_the_feature) > 0:
                if candidates is None:
                    candidates = we_have_the_feature
                    candidate_set = set(candidates)
                else:
                    # Eliminate any candidates that don't have this feature.
                    candidate_set = candidate_set.intersection(
                        set(we_have_the_feature))

        # The only valid candidates are the ones in candidate_set.
        # Go through the original list of candidates and pick the first one
        # that's in candidate_set.
        if candidate_set is None:
            return None
        for candidate in candidates:
            if candidate in candidate_set:
                return candidate
        return None

# The BeautifulSoup class will take feature lists from developers and use them
# to look up builders in this registry.
builder_registry = TreeBuilderRegistry()

class TreeBuilder(object):
    """Turn a document into a Beautiful Soup object tree."""

    NAME = "[Unknown tree builder]"
    ALTERNATE_NAMES = []
    features = []

    is_xml = False
    picklable = False
    empty_element_tags = None # A tag will be considered an empty-element
                              # tag when and only when it has no contents.
    
    # A value for these tag/attribute combinations is a space- or
    # comma-separated list of CDATA, rather than a single CDATA.
    DEFAULT_CDATA_LIST_ATTRIBUTES = {}

    DEFAULT_PRESERVE_WHITESPACE_TAGS = set()
    
    USE_DEFAULT = object()

    # Most parsers don't keep track of line numbers.
    TRACKS_LINE_NUMBERS = False
    
    def __init__(self, multi_valued_attributes=USE_DEFAULT,
                 preserve_whitespace_tags=USE_DEFAULT,
                 store_line_numbers=USE_DEFAULT):
        """Constructor.

        :param multi_valued_attributes: If this is set to None, the
        TreeBuilder will not turn any values for attributes like
        'class' into lists. Setting this do a dictionary will
        customize this behavior; look at DEFAULT_CDATA_LIST_ATTRIBUTES
        for an example.

        Internally, these are called "CDATA list attributes", but that
        probably doesn't make sense to an end-user, so the argument name
        is `multi_valued_attributes`.

        :param preserve_whitespace_tags: A list of tags to treat
        the way <pre> tags are treated in HTML. Tags in this list
        will have 

        :param store_line_numbers: If the parser keeps track of the
        line numbers and positions of the original markup, that
        information will, by default, be stored in each corresponding
        `Tag` object. You can turn this off by passing
        store_line_numbers=False. If the parser you're using doesn't 
        keep track of this information, then setting store_line_numbers=True
        will do nothing.
        """
        self.soup = None
        if multi_valued_attributes is self.USE_DEFAULT:
            multi_valued_attributes = self.DEFAULT_CDATA_LIST_ATTRIBUTES
        self.cdata_list_attributes = multi_valued_attributes
        if preserve_whitespace_tags is self.USE_DEFAULT:
            preserve_whitespace_tags = self.DEFAULT_PRESERVE_WHITESPACE_TAGS
        self.preserve_whitespace_tags = preserve_whitespace_tags
        if store_line_numbers == self.USE_DEFAULT:
            store_line_numbers = self.TRACKS_LINE_NUMBERS
        self.store_line_numbers = store_line_numbers
        
    def initialize_soup(self, soup):
        """The BeautifulSoup object has been initialized and is now
        being associated with the TreeBuilder.
        """
        self.soup = soup
        
    def reset(self):
        pass

    def can_be_empty_element(self, tag_name):
        """Might a tag with this name be an empty-element tag?

        The final markup may or may not actually present this tag as
        self-closing.

        For instance: an HTMLBuilder does not consider a <p> tag to be
        an empty-element tag (it's not in
        HTMLBuilder.empty_element_tags). This means an empty <p> tag
        will be presented as "<p></p>", not "<p />".

        The default implementation has no opinion about which tags are
        empty-element tags, so a tag will be presented as an
        empty-element tag if and only if it has no contents.
        "<foo></foo>" will become "<foo />", and "<foo>bar</foo>" will
        be left alone.
        """
        if self.empty_element_tags is None:
            return True
        return tag_name in self.empty_element_tags
    
    def feed(self, markup):
        raise NotImplementedError()

    def prepare_markup(self, markup, user_specified_encoding=None,
                       document_declared_encoding=None, exclude_encodings=None):
        yield markup, None, None, False

    def test_fragment_to_document(self, fragment):
        """Wrap an HTML fragment to make it look like a document.

        Different parsers do this differently. For instance, lxml
        introduces an empty <head> tag, and html5lib
        doesn't. Abstracting this away lets us write simple tests
        which run HTML fragments through the parser and compare the
        results against other HTML fragments.

        This method should not be used outside of tests.
        """
        return fragment

    def set_up_substitutions(self, tag):
        return False

    def _replace_cdata_list_attribute_values(self, tag_name, attrs):
        """Replaces class="foo bar" with class=["foo", "bar"]

        Modifies its input in place.
        """
        if not attrs:
            return attrs
        if self.cdata_list_attributes:
            universal = self.cdata_list_attributes.get('*', [])
            tag_specific = self.cdata_list_attributes.get(
                tag_name.lower(), None)
            for attr in list(attrs.keys()):
                if attr in universal or (tag_specific and attr in tag_specific):
                    # We have a "class"-type attribute whose string
                    # value is a whitespace-separated list of
                    # values. Split it into a list.
                    value = attrs[attr]
                    if isinstance(value, str):
                        values = nonwhitespace_re.findall(value)
                    else:
                        # html5lib sometimes calls setAttributes twice
                        # for the same tag when rearranging the parse
                        # tree. On the second call the attribute value
                        # here is already a list.  If this happens,
                        # leave the value alone rather than trying to
                        # split it again.
                        values = value
                    attrs[attr] = values
        return attrs

class SAXTreeBuilder(TreeBuilder):
    """A Beautiful Soup treebuilder that listens for SAX events."""

    def feed(self, markup):
        raise NotImplementedError()

    def close(self):
        pass

    def startElement(self, name, attrs):
        attrs = dict((key[1], value) for key, value in list(attrs.items()))
        #print "Start %s, %r" % (name, attrs)
        self.soup.handle_starttag(name, attrs)

    def endElement(self, name):
        #print "End %s" % name
        self.soup.handle_endtag(name)

    def startElementNS(self, nsTuple, nodeName, attrs):
        # Throw away (ns, nodeName) for now.
        self.startElement(nodeName, attrs)

    def endElementNS(self, nsTuple, nodeName):
        # Throw away (ns, nodeName) for now.
        self.endElement(nodeName)
        #handler.endElementNS((ns, node.nodeName), node.nodeName)

    def startPrefixMapping(self, prefix, nodeValue):
        # Ignore the prefix for now.
        pass

    def endPrefixMapping(self, prefix):
        # Ignore the prefix for now.
        # handler.endPrefixMapping(prefix)
        pass

    def characters(self, content):
        self.soup.handle_data(content)

    def startDocument(self):
        pass

    def endDocument(self):
        pass


class HTMLTreeBuilder(TreeBuilder):
    """This TreeBuilder knows facts about HTML.

    Such as which tags are empty-element tags.
    """

    empty_element_tags = set([
        # These are from HTML5.
        'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'keygen', 'link', 'menuitem', 'meta', 'param', 'source', 'track', 'wbr',
        
        # These are from earlier versions of HTML and are removed in HTML5.
        'basefont', 'bgsound', 'command', 'frame', 'image', 'isindex', 'nextid', 'spacer'
    ])

    # The HTML standard defines these as block-level elements. Beautiful
    # Soup does not treat these elements differently from other elements,
    # but it may do so eventually, and this information is available if
    # you need to use it.
    block_elements = set(["address", "article", "aside", "blockquote", "canvas", "dd", "div", "dl", "dt", "fieldset", "figcaption", "figure", "footer", "form", "h1", "h2", "h3", "h4", "h5", "h6", "header", "hr", "li", "main", "nav", "noscript", "ol", "output", "p", "pre", "section", "table", "tfoot", "ul", "video"])
    
    # The HTML standard defines these attributes as containing a
    # space-separated list of values, not a single value. That is,
    # class="foo bar" means that the 'class' attribute has two values,
    # 'foo' and 'bar', not the single value 'foo bar'.  When we
    # encounter one of these attributes, we will parse its value into
    # a list of values if possible. Upon output, the list will be
    # converted back into a string.
    DEFAULT_CDATA_LIST_ATTRIBUTES = {
        "*" : ['class', 'accesskey', 'dropzone'],
        "a" : ['rel', 'rev'],
        "link" :  ['rel', 'rev'],
        "td" : ["headers"],
        "th" : ["headers"],
        "td" : ["headers"],
        "form" : ["accept-charset"],
        "object" : ["archive"],

        # These are HTML5 specific, as are *.accesskey and *.dropzone above.
        "area" : ["rel"],
        "icon" : ["sizes"],
        "iframe" : ["sandbox"],
        "output" : ["for"],
        }

    DEFAULT_PRESERVE_WHITESPACE_TAGS = set(['pre', 'textarea'])
    
    def set_up_substitutions(self, tag):
        # We are only interested in <meta> tags
        if tag.name != 'meta':
            return False

        http_equiv = tag.get('http-equiv')
        content = tag.get('content')
        charset = tag.get('charset')

        # We are interested in <meta> tags that say what encoding the
        # document was originally in. This means HTML 5-style <meta>
        # tags that provide the "charset" attribute. It also means
        # HTML 4-style <meta> tags that provide the "content"
        # attribute and have "http-equiv" set to "content-type".
        #
        # In both cases we will replace the value of the appropriate
        # attribute with a standin object that can take on any
        # encoding.
        meta_encoding = None
        if charset is not None:
            # HTML 5 style:
            # <meta charset="utf8">
            meta_encoding = charset
            tag['charset'] = CharsetMetaAttributeValue(charset)

        elif (content is not None and http_equiv is not None
              and http_equiv.lower() == 'content-type'):
            # HTML 4 style:
            # <meta http-equiv="content-type" content="text/html; charset=utf8">
            tag['content'] = ContentMetaAttributeValue(content)

        return (meta_encoding is not None)

def register_treebuilders_from(module):
    """Copy TreeBuilders from the given module into this module."""
    # I'm fairly sure this is not the best way to do this.
    this_module = sys.modules['bs4.builder']
    for name in module.__all__:
        obj = getattr(module, name)

        if issubclass(obj, TreeBuilder):
            setattr(this_module, name, obj)
            this_module.__all__.append(name)
            # Register the builder while we're at it.
            this_module.builder_registry.register(obj)

class ParserRejectedMarkup(Exception):
    def __init__(self, message_or_exception):
        """Explain why the parser rejected the given markup, either
        with a textual explanation or another exception.
        """
        if isinstance(message_or_exception, Exception):
            e = message_or_exception
            message_or_exception = "%s: %s" % (e.__class__.__name__, str(e))
        super(ParserRejectedMarkup, self).__init__(message_or_exception)
            
# Builders are registered in reverse order of priority, so that custom
# builder registrations will take precedence. In general, we want lxml
# to take precedence over html5lib, because it's faster. And we only
# want to use HTMLParser as a last result.
from . import _htmlparser
register_treebuilders_from(_htmlparser)
try:
    from . import _html5lib
    register_treebuilders_from(_html5lib)
except ImportError:
    # They don't have html5lib installed.
    pass
try:
    from . import _lxml
    register_treebuilders_from(_lxml)
except ImportError:
    # They don't have lxml installed.
    pass
