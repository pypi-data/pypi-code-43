"""
RSS 2.0 implementations based on [this RSS 2.0 documentation](https://validator.w3.org/feed/docs/rss2.html).
"""

from typing import List, Optional

from markyp import IElement, PropertyDict
from markyp.formatters import format_properties, xml_escape


__all__ = ("Category", "Cloud", "Enclosure", "GUID", "Image", "Source", "Item", "Channel", "RSS")


class Category(IElement):
    """
    The category definition of an item.
    """

    __slots__ = ("value", "domain")

    def __init__(self, value: str, domain: Optional[str] = None) -> None:
        """
        Initialization.

        Arguments:
            value: Forward-slash-separated string that identifies a
                   hierarchic location in the indicated taxonomy.
            domain: A string that identifies a categorization taxonomy.
        """
        self.value: str = value
        """Forward-slash-separated string that identifies a hierarchic location in the indicated taxonomy."""

        self.domain: Optional[str] = domain
        """A string that identifies a categorization taxonomy."""

    def __str__(self) -> str:
        domain = f" domain=\"{self.domain}\"" if self.domain else ""
        return f"<category{domain}>{xml_escape(self.value)}</category>"


class Cloud(IElement):
    """
    `Channel` subelement that specifies a web service that supports the `rssCloud` interface.

    See this [page](https://validator.w3.org/feed/docs/rss2.html#ltcloudgtSubelementOfLtchannelgt)
    for the documentation this channel subelement.
    """

    __slots__ = ("domain", "port", "path", "register_procedure", "protocol")

    def __init__(self, domain: str, port: int, path: str, register_procedure: str, protocol: str) -> None:
        """
        Initialization.
        """
        self.domain: str = domain
        self.port: int = port
        self.path: str = path
        self.register_procedure: str = register_procedure
        self.protocol: str = protocol

    def __str__(self) -> str:
        properties: PropertyDict = {
            "domain": self.domain,
            "port": self.port,
            "path": self.path,
            "registerProcedure": self.register_procedure,
            "protocol": self.protocol
        }
        return f"<cloud {format_properties(properties)}/>"


class Enclosure(IElement):
    """
    Describes a media object that is attached to an item.
    """

    __slots__ = ("url", "length", "type")

    def __init__(self, url: str, length: int, type_: str) -> None:
        """
        Initialization.

        Arguments:
            url: The URL where the enclosure is located.
            length: The length of the enclosure in bytes.
            type_: The MIME type of the enclosure.
        """
        self.url: str = url
        """The URL where the enclosure is located."""

        self.length: int = length
        """The length of the enclosure in bytes."""

        self.type: str = type_
        """The MIME type of the enclosure."""

    def __str__(self) -> str:
        properties: PropertyDict = {
            "url": self.url,
            "length": self.length,
            "type": self.type
        }
        return f"<enclosure {format_properties(properties)}/>"


class GUID(IElement):
    """
    Globally unique identifier of an item.
    """

    __slots__ = ("is_perma_link", "value")

    def __init__(self, value: str, is_perma_link: bool = True) -> None:
        """
        Initialization.

        Arguments:
            value: The string that uniquely identifies an item.
            is_perma_link: Whether the GUID is a permanent link to the item.
        """
        self.value: str = value
        """The string that uniquely identifies an item."""

        self.is_perma_link: bool = is_perma_link
        """Whether the GUID is a permanent link to the item."""

    def __str__(self) -> str:
        is_perma_link: str = "true" if self.is_perma_link else "false"
        return f"<guid isPermaLink=\"{is_perma_link}\">{xml_escape(self.value)}</guid>"


class Image(IElement):
    """
    `Channel` subelement that specifies a GIF, JPEG or PNG image that can be displayed with the channel.
    """

    __slots__ = ("url", "title", "link")

    def __init__(self, title: Optional[str] = None, url: Optional[str] = None, link: Optional[str] = None) -> None:
        """
        Initialization.
        """
        self.url: Optional[str] = url
        """The URL of a GIF, JPEG or PNG image that represents the channel. """

        self.title: Optional[str] = title
        """A description of the image."""

        self.link: Optional[str] = link
        """The URL of the site, when the channel is rendered, the image is a link to the site."""

    def __str__(self) -> str:
        items = ["<image>"]
        if self.title is not None:
            items.append(f"<title>{xml_escape(self.title)}</title>")
        if self.url is not None:
            items.append(f"<url>{xml_escape(self.url)}</url>")
        if self.link is not None:
            items.append(f"<link>{xml_escape(self.link)}</link>")
        items.append("</image>")
        return "\n".join(items)


class Source(IElement):
    """
    The RSS channel an item originates from.
    """

    __slots__ = ("url", "value")

    def __init__(self, url: str, value: str) -> None:
        """
        Initialization.

        Arguments:
            url: The link to the XMLization of the source
            value: The name of the RSS channel an item originates from.
        """
        self.url: str = url
        """The link to the XMLization of the source"""

        self.value: str = value
        """The name of the RSS channel an item originates from."""

    def __str__(self) -> str:
        value: str = xml_escape(self.value) if self.value is not None else ""
        return f"<source url=\"{self.url}\">{xml_escape(value)}</source>"


class Item(IElement):
    """
    `Channel` subelement representing a single feed item.
    """

    __slots__ = (
        "title", "link", "description", "author", "_categories",
        "comments", "enclosure", "guid", "pub_date", "source"
    )

    def __init__(self,
                 title: str,
                 link: str,
                 description: Optional[str] = None,
                 *,
                 author: Optional[str] = None,
                 categories: Optional[List[Category]] = None,
                 comments: Optional[str] = None,
                 enclosure: Optional[Enclosure] = None,
                 guid: Optional[GUID] = None,
                 pub_date: Optional[str] = None,
                 source: Optional[Source] = None) -> None:
        """
        Initialization.

        Arguments:
            title: The title of the item.
            link: The URL of the item.
            description: The item synopsis.
            author: The email address of the author of the item.
            categories: The list of categories the item belongs to.
            comments: The list of categories the item belongs to.
            enclosure: Description of the media object that is attached to this item.
            guid: The globally unique identifier of the item.
            pub_date: The publication date of the item.
            source: The RSS channel the item originates from.
        """
        self.title: str = title
        """The title of the item."""

        self.link: str = link
        """The URL of the item."""

        self.description: Optional[str] = description
        """The item synopsis."""

        self.author: Optional[str] = author
        """The email address of the author of the item."""

        self._categories: List[Category] = categories or []
        """The list of categories the item belongs to."""

        self.comments: Optional[str] = comments
        """URL of a page for comments relating to the item."""

        self.enclosure: Optional[Enclosure] = enclosure
        """Description of the media object that is attached to this item."""

        self.guid: Optional[GUID] = guid
        """The globally unique identifier of the item."""

        self.pub_date: Optional[str] = pub_date
        """The publication date of the item."""

        self.source: Optional[Source] = source
        """The RSS channel the item originates from."""

    def __str__(self) -> str:
        items = [
            "<item>",
            f"<title>{xml_escape(self.title)}</title>",
            f"<link>{xml_escape(self.link)}</link>"
        ]

        if self.description is not None:
            items.append(f"<description>{xml_escape(self.description)}</description>")
        if self.author is not None:
            items.append(f"<author>{xml_escape(self.author)}</author>")
        if self.comments is not None:
            items.append(f"<comments>{xml_escape(self.comments)}</comments>")
        if self.enclosure is not None:
            items.append(str(self.enclosure))
        if self.guid is not None:
            items.append(str(self.guid))
        if self.pub_date is not None:
            items.append(f"<pubDate>{xml_escape(self.pub_date)}</pubDate>")
        if self.source is not None:
            items.append(str(self.source))

        items.extend((str(cat) for cat in self._categories))

        items.append("</item>")
        return "\n".join(items)

    def add_category(self, category: Category) -> "Item":
        """
        Adds the given `Category` to the item and returns the item
        itself to allow method chaining.

        Arguments:
            category: The `Category` to add to the item.

        Returns:
            The item itself, allowing method chaining.
        """
        self._categories.append(category)
        return self

    def add_categories(self, *categories: Category) -> "Item":
        """
        Takes any number of `Category` instances as positional arguments and
        adds them to the item.

        Returns:
            The item itself, allowing method chaining.
        """
        self._categories.extend(categories)
        return self

    def set_categories(self, *categories: Category) -> "Item":
        """
        Takes any number of `Category` instances as positional arguments and
        replaces the current categories of the item with the received ones.

        Returns:
            The item itself, allowing method chaining.
        """
        self._categories.clear()
        self._categories.extend(categories)
        return self


class Channel(IElement):
    """
    The `<channel></channel>` element.
    """

    __slots__ = (
        "title", "link", "description", "language", "copyright",
        "managing_editor", "web_master", "pub_date", "last_build_date",
        "generator", "docs", "cloud", "ttl", "image", "_categories", "_items"
    )

    def __init__(self,
                 title:str,
                 link: str,
                 description: str,
                 *,
                 language: Optional[str] = None,
                 copyright_: Optional[str] = None,
                 managing_editor: Optional[str] = None,
                 web_master: Optional[str] = None,
                 pub_date: Optional[str] = None,
                 last_build_date: Optional[str] = None,
                 generator: Optional[str] = "markyp_rss",
                 docs: Optional[str] = None,
                 cloud: Optional[Cloud] = None,
                 ttl: Optional[int] = None,
                 image: Optional[Image] = None,
                 categories: Optional[List[Category]] = None,
                 items: Optional[List[Item]] = None) -> None:
        """
        Initialization.

        Arguments:
            title: The name of the channel - mandatory property.
            link: The URL to the website corresponding to the channel - mandatory property.
            description: A short description of the channel - mandatory property.
            language: The language the channel is written in.
            copyright_: Copyright notice for content in the channel.
            managing_editor: Email address for person responsible for editorial content.
            web_master: Email address for person responsible for technical issues relating to channel.
            pub_date: The publication date for the content in the channel.
            last_build_date: The last time the content of the channel changed.
            generator: A string indicating the program used to generate the channel.
            docs: A URL that points to the documentation for the format used in the RSS file.
            cloud: Allows processes to register with a cloud to be notified of updates to the
                   channel, implementing a lightweight publish-subscribe protocol for RSS feeds.
            ttl: The number of minutes that indicates how long a channel can be cached before
                 refreshing from the source.
            image: A GIF, JPEG or PNG image that can be displayed with the channel.
            categories: The list of categories that the channel belongs to.
            items: The items in the channel.
        """
        # Mandatory properties.
        self.title: str = title
        """The name of the channel - mandatory property."""

        self.link: str = link
        """The URL to the website corresponding to the channel - mandatory property."""

        self.description: str = description
        """A short description of the channel - mandatory property."""

        # Optional properties.
        self.language: Optional[str] = language
        """The language the channel is written in."""

        self.copyright: Optional[str] = copyright_
        """Copyright notice for content in the channel."""

        self.managing_editor: Optional[str] = managing_editor
        """Email address for person responsible for editorial content."""

        self.web_master: Optional[str] = web_master
        """Email address for person responsible for technical issues relating to channel."""

        self.pub_date: Optional[str] = pub_date
        """The publication date for the content in the channel."""

        self.last_build_date: Optional[str] = last_build_date
        """The last time the content of the channel changed."""

        self.generator: Optional[str] = generator
        """A string indicating the program used to generate the channel."""

        self.docs: Optional[str] = docs
        """A URL that points to the documentation for the format used in the RSS file."""

        self.cloud: Optional[Cloud] = cloud
        """Allows processes to register with a cloud to be notified of updates to the channel,
        implementing a lightweight publish-subscribe protocol for RSS feeds."""

        self.ttl: Optional[int] = ttl
        """The number of minutes that indicates how long a channel can be cached before refreshing from the source."""

        self.image: Optional[Image] = image
        """A GIF, JPEG or PNG image that can be displayed with the channel."""

        # The skipHours and skipDays subelements are not supported yet.
        # The textInput subelement is not implemented, because it's not really in use.

        # Protected properties.
        self._categories: List[Category] = categories or []
        """The list of categories that the channel belongs to."""

        self._items: List[Item] = items or []
        """The items in the channel."""

    def __str__(self) -> str:
        items = [
            "<channel>",
            f"<title>{xml_escape(self.title)}</title>",
            f"<link>{xml_escape(self.link)}</link>",
            f"<description>{xml_escape(self.description)}</description>"
        ]

        if self.language is not None:
            items.append(f"<language>{xml_escape(self.language)}</language>")
        if self.copyright is not None:
            items.append(f"<copyright>{xml_escape(self.copyright)}</copyright>")
        if self.managing_editor is not None:
            items.append(f"<managingEditor>{xml_escape(self.managing_editor)}</managingEditor>")
        if self.web_master is not None:
            items.append(f"<webMaster>{xml_escape(self.web_master)}</webMaster>")
        if self.pub_date is not None:
            items.append(f"<pubDate>{xml_escape(self.pub_date)}</pubDate>")
        if self.last_build_date is not None:
            items.append(f"<lastBuildDate>{xml_escape(self.last_build_date)}</lastBuildDate>")
        if self.generator is not None:
            items.append(f"<generator>{xml_escape(self.generator)}</generator>")
        if self.docs is not None:
            items.append(f"<docs>{xml_escape(self.docs)}</docs>")
        if self.ttl is not None:
            items.append(f"<ttl>{str(self.ttl)}</ttl>")
        if self.cloud is not None:
            items.append(str(self.cloud))
        if self.image is not None:
            items.append(str(self.image))

        items.extend(str(cat) for cat in self._categories)
        items.extend((str(item) for item in self._items))

        items.append("</channel>")
        return "\n".join(items)

    def add_category(self, category: Category) -> "Channel":
        """
        Adds the given `Category` to the channel and returns the channel
        itself to allow method chaining.

        Arguments:
            category: The `Category` to add to the channel.

        Returns:
            The channel itself, allowing method chaining.
        """
        self._categories.append(category)
        return self

    def add_categories(self, *categories: Category) -> "Channel":
        """
        Takes any number of `Category` instances as positional arguments and
        adds them to the channel.

        Returns:
            The channel itself, allowing method chaining.
        """
        self._categories.extend(categories)
        return self

    def add_item(self, item: Item) -> "Channel":
        """
        Adds the given `Item` to the channel and returns the channel
        itself to allow method chaining.

        Arguments:
            item: The `Item` to add to the channel.

        Returns:
            The channel itself, allowing method chaining.
        """
        self._items.append(item)
        return self

    def add_items(self, *items: Item) -> "Channel":
        """
        Takes any number of `Item` instances as positional arguments and
        adds them to the channel.

        Returns:
            The channel itself, allowing method chaining.
        """
        self._items.extend(items)
        return self

    def set_categories(self, *categories: Category) -> "Channel":
        """
        Takes any number of `Category` instances as positional arguments and
        replaces the current categories of the channel with the received ones.

        Returns:
            The channel itself, allowing method chaining.
        """
        self._categories.clear()
        self._categories.extend(categories)
        return self

    def set_items(self, *items: Item) -> "Channel":
        """
        Takes any number of `Item` instances as positional arguments and
        replaces the current items of the channel with the received ones.

        Returns:
            The channel itself, allowing method chaining.
        """
        self._items.clear()
        self._items.extend(items)
        return self


class RSS(IElement):
    """
    The `<rss version="2.0">{channel}</rss>` element.
    """

    __slots__ = ("channel",)

    def __init__(self, channel: Channel) -> None:
        """
        Initialization.

        Arguments:
            channel: The channel element of the RSS 2.0 feed.
        """
        self.channel : Channel = channel
        """The channel element of the RSS 2.0 feed."""

    def __str__(self) -> str:
        return f"<rss version=\"2.0\">\n{str(self.channel)}\n</rss>"
