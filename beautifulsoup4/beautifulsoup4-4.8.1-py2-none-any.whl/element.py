# Use of this source code is governed by the MIT license.
__license__ = "MIT"

try:
    from collections.abc import Callable # Python 3.6
except ImportError , e:
    from collections import Callable
import re
import sys
import warnings
try:
    import soupsieve
except ImportError, e:
    soupsieve = None
    warnings.warn(
        'The soupsieve package is not installed. CSS selectors cannot be used.'
    )

from bs4.formatter import (
    Formatter,
    HTMLFormatter,
    XMLFormatter,
)

DEFAULT_OUTPUT_ENCODING = "utf-8"
PY3K = (sys.version_info[0] > 2)

nonwhitespace_re = re.compile(r"\S+")

# NOTE: This isn't used as of 4.7.0. I'm leaving it for a little bit on
# the off chance someone imported it for their own use.
whitespace_re = re.compile(r"\s+")

def _alias(attr):
    """Alias one attribute name to another for backward compatibility"""
    @property
    def alias(self):
        return getattr(self, attr)

    @alias.setter
    def alias(self):
        return setattr(self, attr)
    return alias


class NamespacedAttribute(unicode):

    def __new__(cls, prefix, name=None, namespace=None):
        if not name:
            # This is the default namespace. Its name "has no value"
            # per https://www.w3.org/TR/xml-names/#defaulting
            name = None

        if name is None:
            obj = unicode.__new__(cls, prefix)
        elif prefix is None:
            # Not really namespaced.
            obj = unicode.__new__(cls, name)
        else:
            obj = unicode.__new__(cls, prefix + ":" + name)
        obj.prefix = prefix
        obj.name = name
        obj.namespace = namespace
        return obj

class AttributeValueWithCharsetSubstitution(unicode):
    """A stand-in object for a character encoding specified in HTML."""

class CharsetMetaAttributeValue(AttributeValueWithCharsetSubstitution):
    """A generic stand-in for the value of a meta tag's 'charset' attribute.

    When Beautiful Soup parses the markup '<meta charset="utf8">', the
    value of the 'charset' attribute will be one of these objects.
    """

    def __new__(cls, original_value):
        obj = unicode.__new__(cls, original_value)
        obj.original_value = original_value
        return obj

    def encode(self, encoding):
        return encoding


class ContentMetaAttributeValue(AttributeValueWithCharsetSubstitution):
    """A generic stand-in for the value of a meta tag's 'content' attribute.

    When Beautiful Soup parses the markup:
     <meta http-equiv="content-type" content="text/html; charset=utf8">

    The value of the 'content' attribute will be one of these objects.
    """

    CHARSET_RE = re.compile(r"((^|;)\s*charset=)([^;]*)", re.M)

    def __new__(cls, original_value):
        match = cls.CHARSET_RE.search(original_value)
        if match is None:
            # No substitution necessary.
            return unicode.__new__(unicode, original_value)

        obj = unicode.__new__(cls, original_value)
        obj.original_value = original_value
        return obj

    def encode(self, encoding):
        def rewrite(match):
            return match.group(1) + encoding
        return self.CHARSET_RE.sub(rewrite, self.original_value)

    
class PageElement(object):
    """Contains the navigational information for some part of the page
    (either a tag or a piece of text)"""
   
    def setup(self, parent=None, previous_element=None, next_element=None,
              previous_sibling=None, next_sibling=None):
        """Sets up the initial relations between this element and
        other elements."""
        self.parent = parent

        self.previous_element = previous_element
        if previous_element is not None:
            self.previous_element.next_element = self

        self.next_element = next_element
        if self.next_element is not None:
            self.next_element.previous_element = self

        self.next_sibling = next_sibling
        if self.next_sibling is not None:
            self.next_sibling.previous_sibling = self

        if (previous_sibling is None
            and self.parent is not None and self.parent.contents):
            previous_sibling = self.parent.contents[-1]

        self.previous_sibling = previous_sibling
        if previous_sibling is not None:
            self.previous_sibling.next_sibling = self

    def format_string(self, s, formatter):
        """Format the given string using the given formatter."""
        if formatter is None:
            return s
        if not isinstance(formatter, Formatter):
            formatter = self.formatter_for_name(formatter)
        output = formatter.substitute(s)
        return output

    def formatter_for_name(self, formatter):
        """Look up or create a Formatter for the given identifier,
        if necessary.

        :param formatter: Can be a Formatter object (used as-is), a
        function (used as the entity substitution hook for an
        XMLFormatter or HTMLFormatter), or a string (used to look up
        an XMLFormatter or HTMLFormatter in the appropriate registry.
        """
        if isinstance(formatter, Formatter):
            return formatter
        if self._is_xml:
            c = XMLFormatter
        else:
            c = HTMLFormatter
        if callable(formatter):
            return c(entity_substitution=formatter)
        return c.REGISTRY[formatter]

    @property
    def _is_xml(self):
        """Is this element part of an XML tree or an HTML tree?

        This is used in formatter_for_name, when deciding whether an
        XMLFormatter or HTMLFormatter is more appropriate. It can be
        inefficient, but it should be called very rarely.
        """
        if self.known_xml is not None:
            # Most of the time we will have determined this when the
            # document is parsed.
            return self.known_xml

        # Otherwise, it's likely that this element was created by
        # direct invocation of the constructor from within the user's
        # Python code.
        if self.parent is None:
            # This is the top-level object. It should have .known_xml set
            # from tree creation. If not, take a guess--BS is usually
            # used on HTML markup.
            return getattr(self, 'is_xml', False)
        return self.parent._is_xml

    nextSibling = _alias("next_sibling")  # BS3
    previousSibling = _alias("previous_sibling")  # BS3

    def replace_with(self, replace_with):
        if self.parent is None:
            raise ValueError(
                "Cannot replace one element with another when the "
                "element to be replaced is not part of a tree.")
        if replace_with is self:
            return
        if replace_with is self.parent:
            raise ValueError("Cannot replace a Tag with its parent.")
        old_parent = self.parent
        my_index = self.parent.index(self)
        self.extract()
        old_parent.insert(my_index, replace_with)
        return self
    replaceWith = replace_with  # BS3

    def unwrap(self):
        my_parent = self.parent
        if self.parent is None:
            raise ValueError(
                "Cannot replace an element with its contents when that"
                "element is not part of a tree.")
        my_index = self.parent.index(self)
        self.extract()
        for child in reversed(self.contents[:]):
            my_parent.insert(my_index, child)
        return self
    replace_with_children = unwrap
    replaceWithChildren = unwrap  # BS3

    def wrap(self, wrap_inside):
        me = self.replace_with(wrap_inside)
        wrap_inside.append(me)
        return wrap_inside

    def extract(self):
        """Destructively rips this element out of the tree."""
        if self.parent is not None:
            del self.parent.contents[self.parent.index(self)]

        #Find the two elements that would be next to each other if
        #this element (and any children) hadn't been parsed. Connect
        #the two.
        last_child = self._last_descendant()
        next_element = last_child.next_element

        if (self.previous_element is not None and
            self.previous_element is not next_element):
            self.previous_element.next_element = next_element
        if next_element is not None and next_element is not self.previous_element:
            next_element.previous_element = self.previous_element
        self.previous_element = None
        last_child.next_element = None

        self.parent = None
        if (self.previous_sibling is not None
            and self.previous_sibling is not self.next_sibling):
            self.previous_sibling.next_sibling = self.next_sibling
        if (self.next_sibling is not None
            and self.next_sibling is not self.previous_sibling):
            self.next_sibling.previous_sibling = self.previous_sibling
        self.previous_sibling = self.next_sibling = None
        return self

    def _last_descendant(self, is_initialized=True, accept_self=True):
        "Finds the last element beneath this object to be parsed."
        if is_initialized and self.next_sibling is not None:
            last_child = self.next_sibling.previous_element
        else:
            last_child = self
            while isinstance(last_child, Tag) and last_child.contents:
                last_child = last_child.contents[-1]
        if not accept_self and last_child is self:
            last_child = None
        return last_child
    # BS3: Not part of the API!
    _lastRecursiveChild = _last_descendant

    def insert(self, position, new_child):
        if new_child is None:
            raise ValueError("Cannot insert None into a tag.")
        if new_child is self:
            raise ValueError("Cannot insert a tag into itself.")
        if (isinstance(new_child, basestring)
            and not isinstance(new_child, NavigableString)):
            new_child = NavigableString(new_child)

        from bs4 import BeautifulSoup
        if isinstance(new_child, BeautifulSoup):
            # We don't want to end up with a situation where one BeautifulSoup
            # object contains another. Insert the children one at a time.
            for subchild in list(new_child.contents):
                self.insert(position, subchild)
                position += 1
            return
        position = min(position, len(self.contents))
        if hasattr(new_child, 'parent') and new_child.parent is not None:
            # We're 'inserting' an element that's already one
            # of this object's children.
            if new_child.parent is self:
                current_index = self.index(new_child)
                if current_index < position:
                    # We're moving this element further down the list
                    # of this object's children. That means that when
                    # we extract this element, our target index will
                    # jump down one.
                    position -= 1
            new_child.extract()

        new_child.parent = self
        previous_child = None
        if position == 0:
            new_child.previous_sibling = None
            new_child.previous_element = self
        else:
            previous_child = self.contents[position - 1]
            new_child.previous_sibling = previous_child
            new_child.previous_sibling.next_sibling = new_child
            new_child.previous_element = previous_child._last_descendant(False)
        if new_child.previous_element is not None:
            new_child.previous_element.next_element = new_child

        new_childs_last_element = new_child._last_descendant(False)

        if position >= len(self.contents):
            new_child.next_sibling = None

            parent = self
            parents_next_sibling = None
            while parents_next_sibling is None and parent is not None:
                parents_next_sibling = parent.next_sibling
                parent = parent.parent
                if parents_next_sibling is not None:
                    # We found the element that comes next in the document.
                    break
            if parents_next_sibling is not None:
                new_childs_last_element.next_element = parents_next_sibling
            else:
                # The last element of this tag is the last element in
                # the document.
                new_childs_last_element.next_element = None
        else:
            next_child = self.contents[position]
            new_child.next_sibling = next_child
            if new_child.next_sibling is not None:
                new_child.next_sibling.previous_sibling = new_child
            new_childs_last_element.next_element = next_child

        if new_childs_last_element.next_element is not None:
            new_childs_last_element.next_element.previous_element = new_childs_last_element
        self.contents.insert(position, new_child)

    def append(self, tag):
        """Appends the given tag to the contents of this tag."""
        self.insert(len(self.contents), tag)

    def extend(self, tags):
        """Appends the given tags to the contents of this tag."""
        for tag in tags:
            self.append(tag)

    def insert_before(self, *args):
        """Makes the given element(s) the immediate predecessor of this one.

        The elements will have the same parent, and the given elements
        will be immediately before this one.
        """
        parent = self.parent
        if parent is None:
            raise ValueError(
                "Element has no parent, so 'before' has no meaning.")
        if any(x is self for x in args):
                raise ValueError("Can't insert an element before itself.")
        for predecessor in args:
            # Extract first so that the index won't be screwed up if they
            # are siblings.
            if isinstance(predecessor, PageElement):
                predecessor.extract()
            index = parent.index(self)
            parent.insert(index, predecessor)

    def insert_after(self, *args):
        """Makes the given element(s) the immediate successor of this one.

        The elements will have the same parent, and the given elements
        will be immediately after this one.
        """
        # Do all error checking before modifying the tree.
        parent = self.parent
        if parent is None:
            raise ValueError(
                "Element has no parent, so 'after' has no meaning.")
        if any(x is self for x in args):
            raise ValueError("Can't insert an element after itself.")
        
        offset = 0
        for successor in args:
            # Extract first so that the index won't be screwed up if they
            # are siblings.
            if isinstance(successor, PageElement):
                successor.extract()
            index = parent.index(self)
            parent.insert(index+1+offset, successor)
            offset += 1

    def find_next(self, name=None, attrs={}, text=None, **kwargs):
        """Returns the first item that matches the given criteria and
        appears after this Tag in the document."""
        return self._find_one(self.find_all_next, name, attrs, text, **kwargs)
    findNext = find_next  # BS3

    def find_all_next(self, name=None, attrs={}, text=None, limit=None,
                    **kwargs):
        """Returns all items that match the given criteria and appear
        after this Tag in the document."""
        return self._find_all(name, attrs, text, limit, self.next_elements,
                             **kwargs)
    findAllNext = find_all_next  # BS3

    def find_next_sibling(self, name=None, attrs={}, text=None, **kwargs):
        """Returns the closest sibling to this Tag that matches the
        given criteria and appears after this Tag in the document."""
        return self._find_one(self.find_next_siblings, name, attrs, text,
                             **kwargs)
    findNextSibling = find_next_sibling  # BS3

    def find_next_siblings(self, name=None, attrs={}, text=None, limit=None,
                           **kwargs):
        """Returns the siblings of this Tag that match the given
        criteria and appear after this Tag in the document."""
        return self._find_all(name, attrs, text, limit,
                              self.next_siblings, **kwargs)
    findNextSiblings = find_next_siblings   # BS3
    fetchNextSiblings = find_next_siblings  # BS2

    def find_previous(self, name=None, attrs={}, text=None, **kwargs):
        """Returns the first item that matches the given criteria and
        appears before this Tag in the document."""
        return self._find_one(
            self.find_all_previous, name, attrs, text, **kwargs)
    findPrevious = find_previous  # BS3

    def find_all_previous(self, name=None, attrs={}, text=None, limit=None,
                        **kwargs):
        """Returns all items that match the given criteria and appear
        before this Tag in the document."""
        return self._find_all(name, attrs, text, limit, self.previous_elements,
                           **kwargs)
    findAllPrevious = find_all_previous  # BS3
    fetchPrevious = find_all_previous    # BS2

    def find_previous_sibling(self, name=None, attrs={}, text=None, **kwargs):
        """Returns the closest sibling to this Tag that matches the
        given criteria and appears before this Tag in the document."""
        return self._find_one(self.find_previous_siblings, name, attrs, text,
                             **kwargs)
    findPreviousSibling = find_previous_sibling  # BS3

    def find_previous_siblings(self, name=None, attrs={}, text=None,
                               limit=None, **kwargs):
        """Returns the siblings of this Tag that match the given
        criteria and appear before this Tag in the document."""
        return self._find_all(name, attrs, text, limit,
                              self.previous_siblings, **kwargs)
    findPreviousSiblings = find_previous_siblings   # BS3
    fetchPreviousSiblings = find_previous_siblings  # BS2

    def find_parent(self, name=None, attrs={}, **kwargs):
        """Returns the closest parent of this Tag that matches the given
        criteria."""
        # NOTE: We can't use _find_one because findParents takes a different
        # set of arguments.
        r = None
        l = self.find_parents(name, attrs, 1, **kwargs)
        if l:
            r = l[0]
        return r
    findParent = find_parent  # BS3

    def find_parents(self, name=None, attrs={}, limit=None, **kwargs):
        """Returns the parents of this Tag that match the given
        criteria."""

        return self._find_all(name, attrs, None, limit, self.parents,
                             **kwargs)
    findParents = find_parents   # BS3
    fetchParents = find_parents  # BS2

    @property
    def next(self):
        return self.next_element

    @property
    def previous(self):
        return self.previous_element

    #These methods do the real heavy lifting.

    def _find_one(self, method, name, attrs, text, **kwargs):
        r = None
        l = method(name, attrs, text, 1, **kwargs)
        if l:
            r = l[0]
        return r

    def _find_all(self, name, attrs, text, limit, generator, **kwargs):
        "Iterates over a generator looking for things that match."

        if text is None and 'string' in kwargs:
            text = kwargs['string']
            del kwargs['string']

        if isinstance(name, SoupStrainer):
            strainer = name
        else:
            strainer = SoupStrainer(name, attrs, text, **kwargs)

        if text is None and not limit and not attrs and not kwargs:
            if name is True or name is None:
                # Optimization to find all tags.
                result = (element for element in generator
                          if isinstance(element, Tag))
                return ResultSet(strainer, result)
            elif isinstance(name, basestring):
                # Optimization to find all tags with a given name.
                if name.count(':') == 1:
                    # This is a name with a prefix. If this is a namespace-aware document,
                    # we need to match the local name against tag.name. If not,
                    # we need to match the fully-qualified name against tag.name.
                    prefix, local_name = name.split(':', 1)
                else:
                    prefix = None
                    local_name = name
                result = (element for element in generator
                          if isinstance(element, Tag)
                          and (
                              element.name == name
                          ) or (
                              element.name == local_name
                              and (prefix is None or element.prefix == prefix)
                          )
                )
                return ResultSet(strainer, result)
        results = ResultSet(strainer)
        while True:
            try:
                i = next(generator)
            except StopIteration:
                break
            if i:
                found = strainer.search(i)
                if found:
                    results.append(found)
                    if limit and len(results) >= limit:
                        break
        return results

    #These generators can be used to navigate starting from both
    #NavigableStrings and Tags.
    @property
    def next_elements(self):
        i = self.next_element
        while i is not None:
            yield i
            i = i.next_element

    @property
    def next_siblings(self):
        i = self.next_sibling
        while i is not None:
            yield i
            i = i.next_sibling

    @property
    def previous_elements(self):
        i = self.previous_element
        while i is not None:
            yield i
            i = i.previous_element

    @property
    def previous_siblings(self):
        i = self.previous_sibling
        while i is not None:
            yield i
            i = i.previous_sibling

    @property
    def parents(self):
        i = self.parent
        while i is not None:
            yield i
            i = i.parent

    # Old non-property versions of the generators, for backwards
    # compatibility with BS3.
    def nextGenerator(self):
        return self.next_elements

    def nextSiblingGenerator(self):
        return self.next_siblings

    def previousGenerator(self):
        return self.previous_elements

    def previousSiblingGenerator(self):
        return self.previous_siblings

    def parentGenerator(self):
        return self.parents


class NavigableString(unicode, PageElement):

    PREFIX = ''
    SUFFIX = ''

    # We can't tell just by looking at a string whether it's contained
    # in an XML document or an HTML document.

    known_xml = None

    def __new__(cls, value):
        """Create a new NavigableString.

        When unpickling a NavigableString, this method is called with
        the string in DEFAULT_OUTPUT_ENCODING. That encoding needs to be
        passed in to the superclass's __new__ or the superclass won't know
        how to handle non-ASCII characters.
        """
        if isinstance(value, unicode):
            u = unicode.__new__(cls, value)
        else:
            u = unicode.__new__(cls, value, DEFAULT_OUTPUT_ENCODING)
        u.setup()
        return u

    def __copy__(self):
        """A copy of a NavigableString has the same contents and class
        as the original, but it is not connected to the parse tree.
        """
        return type(self)(self)

    def __getnewargs__(self):
        return (unicode(self),)

    def __getattr__(self, attr):
        """text.string gives you text. This is for backwards
        compatibility for Navigable*String, but for CData* it lets you
        get the string without the CData wrapper."""
        if attr == 'string':
            return self
        else:
            raise AttributeError(
                "'%s' object has no attribute '%s'" % (
                    self.__class__.__name__, attr))

    def output_ready(self, formatter="minimal"):
        """Run the string through the provided formatter."""
        output = self.format_string(self, formatter)
        return self.PREFIX + output + self.SUFFIX

    @property
    def name(self):
        return None

    @name.setter
    def name(self, name):
        raise AttributeError("A NavigableString cannot be given a name.")

class PreformattedString(NavigableString):
    """A NavigableString not subject to the normal formatting rules.

    The string will be passed into the formatter (to trigger side effects),
    but the return value will be ignored.
    """

    def output_ready(self, formatter=None):
        """CData strings are passed into the formatter, purely
        for any side effects. The return value is ignored.
        """
        if formatter is not None:
            ignore = self.format_string(self, formatter)
        return self.PREFIX + self + self.SUFFIX

class CData(PreformattedString):

    PREFIX = u'<![CDATA['
    SUFFIX = u']]>'

class ProcessingInstruction(PreformattedString):
    """A SGML processing instruction."""

    PREFIX = u'<?'
    SUFFIX = u'>'

class XMLProcessingInstruction(ProcessingInstruction):
    """An XML processing instruction."""
    PREFIX = u'<?'
    SUFFIX = u'?>'

class Comment(PreformattedString):

    PREFIX = u'<!--'
    SUFFIX = u'-->'


class Declaration(PreformattedString):
    PREFIX = u'<?'
    SUFFIX = u'?>'


class Doctype(PreformattedString):

    @classmethod
    def for_name_and_ids(cls, name, pub_id, system_id):
        value = name or ''
        if pub_id is not None:
            value += ' PUBLIC "%s"' % pub_id
            if system_id is not None:
                value += ' "%s"' % system_id
        elif system_id is not None:
            value += ' SYSTEM "%s"' % system_id

        return Doctype(value)

    PREFIX = u'<!DOCTYPE '
    SUFFIX = u'>\n'


class Tag(PageElement):

    """Represents a found HTML tag with its attributes and contents."""

    def __init__(self, parser=None, builder=None, name=None, namespace=None,
                 prefix=None, attrs=None, parent=None, previous=None,
                 is_xml=None, sourceline=None, sourcepos=None,
                 can_be_empty_element=None, cdata_list_attributes=None,
                 preserve_whitespace_tags=None
    ):
        "Basic constructor."

        if parser is None:
            self.parser_class = None
        else:
            # We don't actually store the parser object: that lets extracted
            # chunks be garbage-collected.
            self.parser_class = parser.__class__
        if name is None:
            raise ValueError("No value provided for new tag's name.")
        self.name = name
        self.namespace = namespace
        self.prefix = prefix
        if ((not builder or builder.store_line_numbers)
            and (sourceline is not None or sourcepos is not None)):
            self.sourceline = sourceline
            self.sourcepos = sourcepos        
        if attrs is None:
            attrs = {}
        elif attrs:
            if builder is not None and builder.cdata_list_attributes:
                attrs = builder._replace_cdata_list_attribute_values(
                    self.name, attrs)
            else:
                attrs = dict(attrs)
        else:
            attrs = dict(attrs)

        # If possible, determine ahead of time whether this tag is an
        # XML tag.
        if builder:
            self.known_xml = builder.is_xml
        else:
            self.known_xml = is_xml
        self.attrs = attrs
        self.contents = []
        self.setup(parent, previous)
        self.hidden = False

        if builder is None:
            # In the absence of a TreeBuilder, use whatever values were
            # passed in here. They're probably None, unless this is a copy of some
            # other tag.
            self.can_be_empty_element = can_be_empty_element
            self.cdata_list_attributes = cdata_list_attributes
            self.preserve_whitespace_tags = preserve_whitespace_tags
        else:
            # Set up any substitutions for this tag, such as the charset in a META tag.
            builder.set_up_substitutions(self)

            # Ask the TreeBuilder whether this tag might be an empty-element tag.
            self.can_be_empty_element = builder.can_be_empty_element(name)

            # Keep track of the list of attributes of this tag that
            # might need to be treated as a list.
            #
            # For performance reasons, we store the whole data structure
            # rather than asking the question of every tag. Asking would
            # require building a new data structure every time, and
            # (unlike can_be_empty_element), we almost never need
            # to check this.
            self.cdata_list_attributes = builder.cdata_list_attributes

            # Keep track of the names that might cause this tag to be treated as a
            # whitespace-preserved tag.
            self.preserve_whitespace_tags = builder.preserve_whitespace_tags
            
    parserClass = _alias("parser_class")  # BS3

    def __copy__(self):
        """A copy of a Tag is a new Tag, unconnected to the parse tree.
        Its contents are a copy of the old Tag's contents.
        """
        clone = type(self)(
            None, self.builder, self.name, self.namespace,
            self.prefix, self.attrs, is_xml=self._is_xml,
            sourceline=self.sourceline, sourcepos=self.sourcepos,
            can_be_empty_element=self.can_be_empty_element,
            cdata_list_attributes=self.cdata_list_attributes,
            preserve_whitespace_tags=self.preserve_whitespace_tags
        )
        for attr in ('can_be_empty_element', 'hidden'):
            setattr(clone, attr, getattr(self, attr))
        for child in self.contents:
            clone.append(child.__copy__())
        return clone

    @property
    def is_empty_element(self):
        """Is this tag an empty-element tag? (aka a self-closing tag)

        A tag that has contents is never an empty-element tag.

        A tag that has no contents may or may not be an empty-element
        tag. It depends on the builder used to create the tag. If the
        builder has a designated list of empty-element tags, then only
        a tag whose name shows up in that list is considered an
        empty-element tag.

        If the builder has no designated list of empty-element tags,
        then any tag with no contents is an empty-element tag.
        """
        return len(self.contents) == 0 and self.can_be_empty_element
    isSelfClosing = is_empty_element  # BS3

    @property
    def string(self):
        """Convenience property to get the single string within this tag.

        :Return: If this tag has a single string child, return value
         is that string. If this tag has no children, or more than one
         child, return value is None. If this tag has one child tag,
         return value is the 'string' attribute of the child tag,
         recursively.
        """
        if len(self.contents) != 1:
            return None
        child = self.contents[0]
        if isinstance(child, NavigableString):
            return child
        return child.string

    @string.setter
    def string(self, string):
        self.clear()
        self.append(string.__class__(string))

    def _all_strings(self, strip=False, types=(NavigableString, CData)):
        """Yield all strings of certain classes, possibly stripping them.

        By default, yields only NavigableString and CData objects. So
        no comments, processing instructions, etc.
        """
        for descendant in self.descendants:
            if (
                (types is None and not isinstance(descendant, NavigableString))
                or
                (types is not None and type(descendant) not in types)):
                continue
            if strip:
                descendant = descendant.strip()
                if len(descendant) == 0:
                    continue
            yield descendant

    strings = property(_all_strings)

    @property
    def stripped_strings(self):
        for string in self._all_strings(True):
            yield string

    def get_text(self, separator=u"", strip=False,
                 types=(NavigableString, CData)):
        """
        Get all child strings, concatenated using the given separator.
        """
        return separator.join([s for s in self._all_strings(
                    strip, types=types)])
    getText = get_text
    text = property(get_text)

    def decompose(self):
        """Recursively destroys the contents of this tree."""
        self.extract()
        i = self
        while i is not None:
            next = i.next_element
            i.__dict__.clear()
            i.contents = []
            i = next

    def clear(self, decompose=False):
        """
        Extract all children. If decompose is True, decompose instead.
        """
        if decompose:
            for element in self.contents[:]:
                if isinstance(element, Tag):
                    element.decompose()
                else:
                    element.extract()
        else:
            for element in self.contents[:]:
                element.extract()

    def smooth(self):
        """Smooth out this element's children by consolidating consecutive strings.

        This makes pretty-printed output look more natural following a
        lot of operations that modified the tree.
        """
        # Mark the first position of every pair of children that need
        # to be consolidated.  Do this rather than making a copy of
        # self.contents, since in most cases very few strings will be
        # affected.
        marked = []
        for i, a in enumerate(self.contents):
            if isinstance(a, Tag):
                # Recursively smooth children.
                a.smooth()
            if i == len(self.contents)-1:
                # This is the last item in .contents, and it's not a
                # tag. There's no chance it needs any work.
                continue
            b = self.contents[i+1]
            if (isinstance(a, NavigableString)
                and isinstance(b, NavigableString)
                and not isinstance(a, PreformattedString)
                and not isinstance(b, PreformattedString)
            ):
                marked.append(i)

        # Go over the marked positions in reverse order, so that
        # removing items from .contents won't affect the remaining
        # positions.
        for i in reversed(marked):
            a = self.contents[i]
            b = self.contents[i+1]
            b.extract()
            n = NavigableString(a+b)
            a.replace_with(n)

    def index(self, element):
        """
        Find the index of a child by identity, not value. Avoids issues with
        tag.contents.index(element) getting the index of equal elements.
        """
        for i, child in enumerate(self.contents):
            if child is element:
                return i
        raise ValueError("Tag.index: element not in tag")

    def get(self, key, default=None):
        """Returns the value of the 'key' attribute for the tag, or
        the value given for 'default' if it doesn't have that
        attribute."""
        return self.attrs.get(key, default)

    def get_attribute_list(self, key, default=None):
        """The same as get(), but always returns a list."""
        value = self.get(key, default)
        if not isinstance(value, list):
            value = [value]
        return value
    
    def has_attr(self, key):
        return key in self.attrs

    def __hash__(self):
        return str(self).__hash__()

    def __getitem__(self, key):
        """tag[key] returns the value of the 'key' attribute for the tag,
        and throws an exception if it's not there."""
        return self.attrs[key]

    def __iter__(self):
        "Iterating over a tag iterates over its contents."
        return iter(self.contents)

    def __len__(self):
        "The length of a tag is the length of its list of contents."
        return len(self.contents)

    def __contains__(self, x):
        return x in self.contents

    def __nonzero__(self):
        "A tag is non-None even if it has no contents."
        return True

    def __setitem__(self, key, value):
        """Setting tag[key] sets the value of the 'key' attribute for the
        tag."""
        self.attrs[key] = value

    def __delitem__(self, key):
        "Deleting tag[key] deletes all 'key' attributes for the tag."
        self.attrs.pop(key, None)

    def __call__(self, *args, **kwargs):
        """Calling a tag like a function is the same as calling its
        find_all() method. Eg. tag('a') returns a list of all the A tags
        found within this tag."""
        return self.find_all(*args, **kwargs)

    def __getattr__(self, tag):
        #print "Getattr %s.%s" % (self.__class__, tag)
        if len(tag) > 3 and tag.endswith('Tag'):
            # BS3: soup.aTag -> "soup.find("a")
            tag_name = tag[:-3]
            warnings.warn(
                '.%(name)sTag is deprecated, use .find("%(name)s") instead. If you really were looking for a tag called %(name)sTag, use .find("%(name)sTag")' % dict(
                    name=tag_name
                )
            )
            return self.find(tag_name)
        # We special case contents to avoid recursion.
        elif not tag.startswith("__") and not tag == "contents":
            return self.find(tag)
        raise AttributeError(
            "'%s' object has no attribute '%s'" % (self.__class__, tag))

    def __eq__(self, other):
        """Returns true iff this tag has the same name, the same attributes,
        and the same contents (recursively) as the given tag."""
        if self is other:
            return True
        if (not hasattr(other, 'name') or
            not hasattr(other, 'attrs') or
            not hasattr(other, 'contents') or
            self.name != other.name or
            self.attrs != other.attrs or
            len(self) != len(other)):
            return False
        for i, my_child in enumerate(self.contents):
            if my_child != other.contents[i]:
                return False
        return True

    def __ne__(self, other):
        """Returns true iff this tag is not identical to the other tag,
        as defined in __eq__."""
        return not self == other

    def __repr__(self, encoding="unicode-escape"):
        """Renders this tag as a string."""
        if PY3K:
            # "The return value must be a string object", i.e. Unicode
            return self.decode()
        else:
            # "The return value must be a string object", i.e. a bytestring.
            # By convention, the return value of __repr__ should also be
            # an ASCII string.
            return self.encode(encoding)

    def __unicode__(self):
        return self.decode()

    def __str__(self):
        if PY3K:
            return self.decode()
        else:
            return self.encode()

    if PY3K:
        __str__ = __repr__ = __unicode__

    def encode(self, encoding=DEFAULT_OUTPUT_ENCODING,
               indent_level=None, formatter="minimal",
               errors="xmlcharrefreplace"):
        # Turn the data structure into Unicode, then encode the
        # Unicode.
        u = self.decode(indent_level, encoding, formatter)
        return u.encode(encoding, errors)

    def decode(self, indent_level=None,
               eventual_encoding=DEFAULT_OUTPUT_ENCODING,
               formatter="minimal"):
        """Returns a Unicode representation of this tag and its contents.

        :param eventual_encoding: The tag is destined to be
           encoded into this encoding. This method is _not_
           responsible for performing that encoding. This information
           is passed in so that it can be substituted in if the
           document contains a <META> tag that mentions the document's
           encoding.
        """

        # First off, turn a non-Formatter `formatter` into a Formatter
        # object. This will stop the lookup from happening over and
        # over again.
        if not isinstance(formatter, Formatter):
            formatter = self.formatter_for_name(formatter)
        attributes = formatter.attributes(self)
        attrs = []
        for key, val in attributes:
            if val is None:
                decoded = key
            else:
                if isinstance(val, list) or isinstance(val, tuple):
                    val = ' '.join(val)
                elif not isinstance(val, basestring):
                    val = unicode(val)
                elif (
                        isinstance(val, AttributeValueWithCharsetSubstitution)
                        and eventual_encoding is not None
                ):
                    val = val.encode(eventual_encoding)

                text = formatter.attribute_value(val)
                decoded = (
                    unicode(key) + '='
                    + formatter.quoted_attribute_value(text))
            attrs.append(decoded)
        close = ''
        closeTag = ''

        prefix = ''
        if self.prefix:
            prefix = self.prefix + ":"

        if self.is_empty_element:
            close = formatter.void_element_close_prefix or ''
        else:
            closeTag = '</%s%s>' % (prefix, self.name)

        pretty_print = self._should_pretty_print(indent_level)
        space = ''
        indent_space = ''
        if indent_level is not None:
            indent_space = (' ' * (indent_level - 1))
        if pretty_print:
            space = indent_space
            indent_contents = indent_level + 1
        else:
            indent_contents = None
        contents = self.decode_contents(
            indent_contents, eventual_encoding, formatter
        )

        if self.hidden:
            # This is the 'document root' object.
            s = contents
        else:
            s = []
            attribute_string = ''
            if attrs:
                attribute_string = ' ' + ' '.join(attrs)
            if indent_level is not None:
                # Even if this particular tag is not pretty-printed,
                # we should indent up to the start of the tag.
                s.append(indent_space)
            s.append('<%s%s%s%s>' % (
                    prefix, self.name, attribute_string, close))
            if pretty_print:
                s.append("\n")
            s.append(contents)
            if pretty_print and contents and contents[-1] != "\n":
                s.append("\n")
            if pretty_print and closeTag:
                s.append(space)
            s.append(closeTag)
            if indent_level is not None and closeTag and self.next_sibling:
                # Even if this particular tag is not pretty-printed,
                # we're now done with the tag, and we should add a
                # newline if appropriate.
                s.append("\n")
            s = ''.join(s)
        return s

    def _should_pretty_print(self, indent_level):
        """Should this tag be pretty-printed?"""
        return (
            indent_level is not None
            and (
                not self.preserve_whitespace_tags
                or self.name not in self.preserve_whitespace_tags
            )
        )

    def prettify(self, encoding=None, formatter="minimal"):
        if encoding is None:
            return self.decode(True, formatter=formatter)
        else:
            return self.encode(encoding, True, formatter=formatter)

    def decode_contents(self, indent_level=None,
                       eventual_encoding=DEFAULT_OUTPUT_ENCODING,
                       formatter="minimal"):
        """Renders the contents of this tag as a Unicode string.

        :param indent_level: Each line of the rendering will be
           indented this many spaces.

        :param eventual_encoding: The tag is destined to be
           encoded into this encoding. decode_contents() is _not_
           responsible for performing that encoding. This information
           is passed in so that it can be substituted in if the
           document contains a <META> tag that mentions the document's
           encoding.

        :param formatter: A Formatter object, or a string naming one of
            the standard Formatters.
        """
        # First off, turn a string formatter into a Formatter object. This
        # will stop the lookup from happening over and over again.
        if not isinstance(formatter, Formatter):
            formatter = self.formatter_for_name(formatter)

        pretty_print = (indent_level is not None)
        s = []
        for c in self:
            text = None
            if isinstance(c, NavigableString):
                text = c.output_ready(formatter)
            elif isinstance(c, Tag):
                s.append(c.decode(indent_level, eventual_encoding,
                                  formatter))
            preserve_whitespace = (
                self.preserve_whitespace_tags and self.name in self.preserve_whitespace_tags
            )
            if text and indent_level and not preserve_whitespace:
                text = text.strip()
            if text:
                if pretty_print and not preserve_whitespace:
                    s.append(" " * (indent_level - 1))
                s.append(text)
                if pretty_print and not preserve_whitespace:
                    s.append("\n")
        return ''.join(s)
       
    def encode_contents(
        self, indent_level=None, encoding=DEFAULT_OUTPUT_ENCODING,
        formatter="minimal"):
        """Renders the contents of this tag as a bytestring.

        :param indent_level: Each line of the rendering will be
           indented this many spaces.

        :param eventual_encoding: The bytestring will be in this encoding.

        :param formatter: The output formatter responsible for converting
           entities to Unicode characters.
        """

        contents = self.decode_contents(indent_level, encoding, formatter)
        return contents.encode(encoding)

    # Old method for BS3 compatibility
    def renderContents(self, encoding=DEFAULT_OUTPUT_ENCODING,
                       prettyPrint=False, indentLevel=0):
        if not prettyPrint:
            indentLevel = None
        return self.encode_contents(
            indent_level=indentLevel, encoding=encoding)

    #Soup methods

    def find(self, name=None, attrs={}, recursive=True, text=None,
             **kwargs):
        """Return only the first child of this Tag matching the given
        criteria."""
        r = None
        l = self.find_all(name, attrs, recursive, text, 1, **kwargs)
        if l:
            r = l[0]
        return r
    findChild = find

    def find_all(self, name=None, attrs={}, recursive=True, text=None,
                 limit=None, **kwargs):
        """Extracts a list of Tag objects that match the given
        criteria.  You can specify the name of the Tag and any
        attributes you want the Tag to have.

        The value of a key-value pair in the 'attrs' map can be a
        string, a list of strings, a regular expression object, or a
        callable that takes a string and returns whether or not the
        string matches for some custom definition of 'matches'. The
        same is true of the tag name."""

        generator = self.descendants
        if not recursive:
            generator = self.children
        return self._find_all(name, attrs, text, limit, generator, **kwargs)
    findAll = find_all       # BS3
    findChildren = find_all  # BS2

    #Generator methods
    @property
    def children(self):
        # return iter() to make the purpose of the method clear
        return iter(self.contents)  # XXX This seems to be untested.

    @property
    def descendants(self):
        if not len(self.contents):
            return
        stopNode = self._last_descendant().next_element
        current = self.contents[0]
        while current is not stopNode:
            yield current
            current = current.next_element

    # CSS selector code
    def select_one(self, selector, namespaces=None, **kwargs):
        """Perform a CSS selection operation on the current element."""
        value = self.select(selector, namespaces, 1, **kwargs)
        if value:
            return value[0]
        return None

    def select(self, selector, namespaces=None, limit=None, **kwargs):
        """Perform a CSS selection operation on the current element.

        This uses the SoupSieve library.

        :param selector: A string containing a CSS selector.

        :param namespaces: A dictionary mapping namespace prefixes
        used in the CSS selector to namespace URIs. By default,
        Beautiful Soup will use the prefixes it encountered while
        parsing the document.

        :param limit: After finding this number of results, stop looking.

        :param kwargs: Any extra arguments you'd like to pass in to
        soupsieve.select().
        """
        if namespaces is None:
            namespaces = self._namespaces
        
        if limit is None:
            limit = 0
        if soupsieve is None:
            raise NotImplementedError(
                "Cannot execute CSS selectors because the soupsieve package is not installed."
            )
            
        return soupsieve.select(selector, self, namespaces, limit, **kwargs)

    # Old names for backwards compatibility
    def childGenerator(self):
        return self.children

    def recursiveChildGenerator(self):
        return self.descendants

    def has_key(self, key):
        """This was kind of misleading because has_key() (attributes)
        was different from __in__ (contents). has_key() is gone in
        Python 3, anyway."""
        warnings.warn('has_key is deprecated. Use has_attr("%s") instead.' % (
                key))
        return self.has_attr(key)

# Next, a couple classes to represent queries and their results.
class SoupStrainer(object):
    """Encapsulates a number of ways of matching a markup element (tag or
    text)."""

    def __init__(self, name=None, attrs={}, text=None, **kwargs):
        self.name = self._normalize_search_value(name)
        if not isinstance(attrs, dict):
            # Treat a non-dict value for attrs as a search for the 'class'
            # attribute.
            kwargs['class'] = attrs
            attrs = None

        if 'class_' in kwargs:
            # Treat class_="foo" as a search for the 'class'
            # attribute, overriding any non-dict value for attrs.
            kwargs['class'] = kwargs['class_']
            del kwargs['class_']

        if kwargs:
            if attrs:
                attrs = attrs.copy()
                attrs.update(kwargs)
            else:
                attrs = kwargs
        normalized_attrs = {}
        for key, value in attrs.items():
            normalized_attrs[key] = self._normalize_search_value(value)

        self.attrs = normalized_attrs
        self.text = self._normalize_search_value(text)

    def _normalize_search_value(self, value):
        # Leave it alone if it's a Unicode string, a callable, a
        # regular expression, a boolean, or None.
        if (isinstance(value, unicode) or isinstance(value, Callable) or hasattr(value, 'match')
            or isinstance(value, bool) or value is None):
            return value

        # If it's a bytestring, convert it to Unicode, treating it as UTF-8.
        if isinstance(value, bytes):
            return value.decode("utf8")

        # If it's listlike, convert it into a list of strings.
        if hasattr(value, '__iter__'):
            new_value = []
            for v in value:
                if (hasattr(v, '__iter__') and not isinstance(v, bytes)
                    and not isinstance(v, unicode)):
                    # This is almost certainly the user's mistake. In the
                    # interests of avoiding infinite loops, we'll let
                    # it through as-is rather than doing a recursive call.
                    new_value.append(v)
                else:
                    new_value.append(self._normalize_search_value(v))
            return new_value

        # Otherwise, convert it into a Unicode string.
        # The unicode(str()) thing is so this will do the same thing on Python 2
        # and Python 3.
        return unicode(str(value))

    def __str__(self):
        if self.text:
            return self.text
        else:
            return "%s|%s" % (self.name, self.attrs)

    def search_tag(self, markup_name=None, markup_attrs={}):
        found = None
        markup = None
        if isinstance(markup_name, Tag):
            markup = markup_name
            markup_attrs = markup
        call_function_with_tag_data = (
            isinstance(self.name, Callable)
            and not isinstance(markup_name, Tag))

        if ((not self.name)
            or call_function_with_tag_data
            or (markup and self._matches(markup, self.name))
            or (not markup and self._matches(markup_name, self.name))):
            if call_function_with_tag_data:
                match = self.name(markup_name, markup_attrs)
            else:
                match = True
                markup_attr_map = None
                for attr, match_against in list(self.attrs.items()):
                    if not markup_attr_map:
                        if hasattr(markup_attrs, 'get'):
                            markup_attr_map = markup_attrs
                        else:
                            markup_attr_map = {}
                            for k, v in markup_attrs:
                                markup_attr_map[k] = v
                    attr_value = markup_attr_map.get(attr)
                    if not self._matches(attr_value, match_against):
                        match = False
                        break
            if match:
                if markup:
                    found = markup
                else:
                    found = markup_name
        if found and self.text and not self._matches(found.string, self.text):
            found = None
        return found
    searchTag = search_tag

    def search(self, markup):
        # print 'looking for %s in %s' % (self, markup)
        found = None
        # If given a list of items, scan it for a text element that
        # matches.
        if hasattr(markup, '__iter__') and not isinstance(markup, (Tag, basestring)):
            for element in markup:
                if isinstance(element, NavigableString) \
                       and self.search(element):
                    found = element
                    break
        # If it's a Tag, make sure its name or attributes match.
        # Don't bother with Tags if we're searching for text.
        elif isinstance(markup, Tag):
            if not self.text or self.name or self.attrs:
                found = self.search_tag(markup)
        # If it's text, make sure the text matches.
        elif isinstance(markup, NavigableString) or \
                 isinstance(markup, basestring):
            if not self.name and not self.attrs and self._matches(markup, self.text):
                found = markup
        else:
            raise Exception(
                "I don't know how to match against a %s" % markup.__class__)
        return found

    def _matches(self, markup, match_against, already_tried=None):
        # print u"Matching %s against %s" % (markup, match_against)
        result = False
        if isinstance(markup, list) or isinstance(markup, tuple):
            # This should only happen when searching a multi-valued attribute
            # like 'class'.
            for item in markup:
                if self._matches(item, match_against):
                    return True
            # We didn't match any particular value of the multivalue
            # attribute, but maybe we match the attribute value when
            # considered as a string.
            if self._matches(' '.join(markup), match_against):
                return True
            return False
        
        if match_against is True:
            # True matches any non-None value.
            return markup is not None

        if isinstance(match_against, Callable):
            return match_against(markup)

        # Custom callables take the tag as an argument, but all
        # other ways of matching match the tag name as a string.
        original_markup = markup
        if isinstance(markup, Tag):
            markup = markup.name

        # Ensure that `markup` is either a Unicode string, or None.
        markup = self._normalize_search_value(markup)

        if markup is None:
            # None matches None, False, an empty string, an empty list, and so on.
            return not match_against

        if (hasattr(match_against, '__iter__')
            and not isinstance(match_against, basestring)):
            # We're asked to match against an iterable of items.
            # The markup must be match at least one item in the
            # iterable. We'll try each one in turn.
            #
            # To avoid infinite recursion we need to keep track of
            # items we've already seen.
            if not already_tried:
                already_tried = set()
            for item in match_against:
                if item.__hash__:
                    key = item
                else:
                    key = id(item)
                if key in already_tried:
                    continue
                else:
                    already_tried.add(key)
                    if self._matches(original_markup, item, already_tried):
                        return True
            else:
                return False
        
        # Beyond this point we might need to run the test twice: once against
        # the tag's name and once against its prefixed name.
        match = False
        
        if not match and isinstance(match_against, unicode):
            # Exact string match
            match = markup == match_against

        if not match and hasattr(match_against, 'search'):
            # Regexp match
            return match_against.search(markup)

        if (not match
            and isinstance(original_markup, Tag)
            and original_markup.prefix):
            # Try the whole thing again with the prefixed tag name.
            return self._matches(
                original_markup.prefix + ':' + original_markup.name, match_against
            )

        return match


class ResultSet(list):
    """A ResultSet is just a list that keeps track of the SoupStrainer
    that created it."""
    def __init__(self, source, result=()):
        super(ResultSet, self).__init__(result)
        self.source = source

    def __getattr__(self, key):
        raise AttributeError(
            "ResultSet object has no attribute '%s'. You're probably treating a list of items like a single item. Did you call find_all() when you meant to call find()?" % key
        )
