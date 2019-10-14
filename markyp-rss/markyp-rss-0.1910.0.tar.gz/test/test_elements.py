from markyp_rss.elements import Category,\
                                Cloud,\
                                Enclosure,\
                                GUID,\
                                Image,\
                                Source,\
                                Item,\
                                Channel,\
                                RSS

def test_Category():
    cat = Category("Testing")
    assert str(cat) == "<category>Testing</category>"

    cat.value = "Testing / Unit Testing"
    cat.domain = None
    assert str(cat) == "<category>Testing / Unit Testing</category>"

    cat.value = "Testing <&> Unit Testing"
    cat.domain = None
    assert str(cat) == "<category>Testing &lt;&amp;&gt; Unit Testing</category>"

    cat.value = "Testing / Unit Testing"
    cat.domain = ""
    assert str(cat) == "<category>Testing / Unit Testing</category>"

    cat.value = "Testing <&> Unit Testing"
    cat.domain = ""
    assert str(cat) == "<category>Testing &lt;&amp;&gt; Unit Testing</category>"

    cat.value = "Testing / Unit Testing"
    cat.domain = "some.custom.domain"
    assert str(cat) == "<category domain=\"some.custom.domain\">Testing / Unit Testing</category>"

    cat.value = "Testing <&> Unit Testing"
    cat.domain = "some.custom.domain"
    assert str(cat) == "<category domain=\"some.custom.domain\">Testing &lt;&amp;&gt; Unit Testing</category>"

def test_Cloud():
    cloud = Cloud("some.domain", 80, "/channel/example", "pingMe", "soap")
    assert cloud.markup == "<cloud domain=\"some.domain\" port=\"80\" path=\"/channel/example\" registerProcedure=\"pingMe\" protocol=\"soap\"/>"

def test_Enclosure():
    enclosure = Enclosure("https://some.pla/ce", 42, "image/jpeg")
    assert enclosure.markup == '<enclosure url="https://some.pla/ce" length="42" type="image/jpeg"/>'

def test_GUID():
    guid = GUID("FOO-BAR-BAZ", False)
    assert guid.markup == '<guid isPermaLink="false">FOO-BAR-BAZ</guid>'

    guid.value = "foo.bar/baz"
    guid.is_perma_link = True
    assert guid.markup == '<guid isPermaLink="true">foo.bar/baz</guid>'

def test_Image():
    image = Image("Image Title", "https://image.test/image.jpeg", "https://channel.link")
    assert image.markup == "<image>\n<title>Image Title</title>\n<url>https://image.test/image.jpeg</url>\n<link>https://channel.link</link>\n</image>"

    image = Image()
    image.title = "Image Title"
    image.url = "https://image.test/image.jpeg"
    image.link = "https://channel.link"
    assert image.markup == "<image>\n<title>Image Title</title>\n<url>https://image.test/image.jpeg</url>\n<link>https://channel.link</link>\n</image>"

    image = Image()
    image.title = "Image Title"
    image.url = "https://image.test/image.jpeg"
    image.link = None
    assert image.markup == "<image>\n<title>Image Title</title>\n<url>https://image.test/image.jpeg</url>\n</image>"

    image = Image()
    image.title = "Image Title"
    image.url = None
    image.link = None
    assert image.markup == "<image>\n<title>Image Title</title>\n</image>"

    image = Image()
    assert image.markup == "<image>\n</image>"

def test_Source():
    source = Source("https://feeds.rss/source-feed.rss", "Source Feed")
    assert source.markup == '<source url="https://feeds.rss/source-feed.rss">Source Feed</source>'

def test_Item():
    item = Item("News item", "link.to/news-item")
    assert item.markup == "\n".join((
        "<item>",
        "<title>News item</title>",
        "<link>link.to/news-item</link>",
        "</item>"
    ))

    item.description = "Item description"
    item.author = "Joe"
    item.comments = "https://place.to/comment-on-news"
    item.pub_date = "1999-05-26"
    assert item.markup == "\n".join((
        "<item>",
        "<title>News item</title>",
        "<link>link.to/news-item</link>",
        "<description>Item description</description>",
        "<author>Joe</author>",
        "<comments>https://place.to/comment-on-news</comments>",
        "<pubDate>1999-05-26</pubDate>",
        "</item>"
    ))

    item.enclosure = Enclosure("https://some.pla/ce", 42, "image/jpeg")
    item.guid = GUID("FOO-BAR-BAZ", False)
    item.source = Source("https://feeds.rss/source-feed.rss", "Source Feed")
    assert item.markup == "\n".join((
        "<item>",
        "<title>News item</title>",
        "<link>link.to/news-item</link>",
        "<description>Item description</description>",
        "<author>Joe</author>",
        "<comments>https://place.to/comment-on-news</comments>",
        '<enclosure url="https://some.pla/ce" length="42" type="image/jpeg"/>',
        '<guid isPermaLink="false">FOO-BAR-BAZ</guid>',
        "<pubDate>1999-05-26</pubDate>",
        '<source url="https://feeds.rss/source-feed.rss">Source Feed</source>',
        "</item>"
    ))

    assert item.add_categories() == item
    assert item.markup == "\n".join((
        "<item>",
        "<title>News item</title>",
        "<link>link.to/news-item</link>",
        "<description>Item description</description>",
        "<author>Joe</author>",
        "<comments>https://place.to/comment-on-news</comments>",
        '<enclosure url="https://some.pla/ce" length="42" type="image/jpeg"/>',
        '<guid isPermaLink="false">FOO-BAR-BAZ</guid>',
        "<pubDate>1999-05-26</pubDate>",
        '<source url="https://feeds.rss/source-feed.rss">Source Feed</source>',
        "</item>"
    ))

    assert item.set_categories() == item
    assert item.markup == "\n".join((
        "<item>",
        "<title>News item</title>",
        "<link>link.to/news-item</link>",
        "<description>Item description</description>",
        "<author>Joe</author>",
        "<comments>https://place.to/comment-on-news</comments>",
        '<enclosure url="https://some.pla/ce" length="42" type="image/jpeg"/>',
        '<guid isPermaLink="false">FOO-BAR-BAZ</guid>',
        "<pubDate>1999-05-26</pubDate>",
        '<source url="https://feeds.rss/source-feed.rss">Source Feed</source>',
        "</item>"
    ))

    assert item.add_category(Category("Testing")) == item
    assert item.markup == "\n".join((
        "<item>",
        "<title>News item</title>",
        "<link>link.to/news-item</link>",
        "<description>Item description</description>",
        "<author>Joe</author>",
        "<comments>https://place.to/comment-on-news</comments>",
        '<enclosure url="https://some.pla/ce" length="42" type="image/jpeg"/>',
        '<guid isPermaLink="false">FOO-BAR-BAZ</guid>',
        "<pubDate>1999-05-26</pubDate>",
        '<source url="https://feeds.rss/source-feed.rss">Source Feed</source>',
        "<category>Testing</category>",
        "</item>"
    ))

    assert item.add_categories(Category("Testing - 1"), Category("Testing - 2")) == item
    assert item.markup == "\n".join((
        "<item>",
        "<title>News item</title>",
        "<link>link.to/news-item</link>",
        "<description>Item description</description>",
        "<author>Joe</author>",
        "<comments>https://place.to/comment-on-news</comments>",
        '<enclosure url="https://some.pla/ce" length="42" type="image/jpeg"/>',
        '<guid isPermaLink="false">FOO-BAR-BAZ</guid>',
        "<pubDate>1999-05-26</pubDate>",
        '<source url="https://feeds.rss/source-feed.rss">Source Feed</source>',
        "<category>Testing</category>",
        "<category>Testing - 1</category>",
        "<category>Testing - 2</category>",
        "</item>"
    ))

    assert item.set_categories(Category("Testing - 1"), Category("Testing - 2")) == item
    assert item.markup == "\n".join((
        "<item>",
        "<title>News item</title>",
        "<link>link.to/news-item</link>",
        "<description>Item description</description>",
        "<author>Joe</author>",
        "<comments>https://place.to/comment-on-news</comments>",
        '<enclosure url="https://some.pla/ce" length="42" type="image/jpeg"/>',
        '<guid isPermaLink="false">FOO-BAR-BAZ</guid>',
        "<pubDate>1999-05-26</pubDate>",
        '<source url="https://feeds.rss/source-feed.rss">Source Feed</source>',
        "<category>Testing - 1</category>",
        "<category>Testing - 2</category>",
        "</item>"
    ))

    assert item.set_categories() == item
    assert item.markup == "\n".join((
        "<item>",
        "<title>News item</title>",
        "<link>link.to/news-item</link>",
        "<description>Item description</description>",
        "<author>Joe</author>",
        "<comments>https://place.to/comment-on-news</comments>",
        '<enclosure url="https://some.pla/ce" length="42" type="image/jpeg"/>',
        '<guid isPermaLink="false">FOO-BAR-BAZ</guid>',
        "<pubDate>1999-05-26</pubDate>",
        '<source url="https://feeds.rss/source-feed.rss">Source Feed</source>',
        "</item>"
    ))

def test_Channel():
    channel = Channel("RSS 2.0 Test Channel", "https://test.channel.rss/", "Test channel > description")
    assert channel.markup == "\n".join((
        "<channel>",
        "<title>RSS 2.0 Test Channel</title>",
        "<link>https://test.channel.rss/</link>",
        "<description>Test channel &gt; description</description>",
        "<generator>markyp_rss</generator>",
        "</channel>"
    ))

    channel.language = "eo"
    channel.copyright = "Copyright 2019, VP"
    channel.managing_editor = "joe@test.channel, Joe"
    channel.web_master = "webmaster@test.channel"
    channel.pub_date = "2008-05-21"
    channel.last_build_date = "2008-05-21"
    channel.generator = None
    channel.docs = "https://validator.w3.org/feed/docs/rss2.html"
    channel.ttl = 42

    assert channel.markup == "\n".join((
        "<channel>",
        "<title>RSS 2.0 Test Channel</title>",
        "<link>https://test.channel.rss/</link>",
        "<description>Test channel &gt; description</description>",
        "<language>eo</language>",
        "<copyright>Copyright 2019, VP</copyright>",
        "<managingEditor>joe@test.channel, Joe</managingEditor>",
        "<webMaster>webmaster@test.channel</webMaster>",
        "<pubDate>2008-05-21</pubDate>",
        "<lastBuildDate>2008-05-21</lastBuildDate>",
        "<docs>https://validator.w3.org/feed/docs/rss2.html</docs>",
        "<ttl>42</ttl>",
        "</channel>"
    ))

    channel.generator = "markyp_rss"
    channel.cloud = Cloud("some.domain", 80, "/channel/example", "pingMe", "soap")
    channel.image = Image("Image Title", "https://image.test/image.jpeg", "https://channel.link")
    assert channel.markup == "\n".join((
        "<channel>",
        "<title>RSS 2.0 Test Channel</title>",
        "<link>https://test.channel.rss/</link>",
        "<description>Test channel &gt; description</description>",
        "<language>eo</language>",
        "<copyright>Copyright 2019, VP</copyright>",
        "<managingEditor>joe@test.channel, Joe</managingEditor>",
        "<webMaster>webmaster@test.channel</webMaster>",
        "<pubDate>2008-05-21</pubDate>",
        "<lastBuildDate>2008-05-21</lastBuildDate>",
        "<generator>markyp_rss</generator>",
        "<docs>https://validator.w3.org/feed/docs/rss2.html</docs>",
        "<ttl>42</ttl>",
        '<cloud domain="some.domain" port="80" path="/channel/example" registerProcedure="pingMe" protocol="soap"/>',
        "<image>\n<title>Image Title</title>\n<url>https://image.test/image.jpeg</url>\n<link>https://channel.link</link>\n</image>",
        "</channel>"
    ))

    assert channel.add_category(Category("Testing")) == channel
    assert channel.add_item(Item("Testing", "testing.html")) == channel
    assert channel.markup == "\n".join((
        "<channel>",
        "<title>RSS 2.0 Test Channel</title>",
        "<link>https://test.channel.rss/</link>",
        "<description>Test channel &gt; description</description>",
        "<language>eo</language>",
        "<copyright>Copyright 2019, VP</copyright>",
        "<managingEditor>joe@test.channel, Joe</managingEditor>",
        "<webMaster>webmaster@test.channel</webMaster>",
        "<pubDate>2008-05-21</pubDate>",
        "<lastBuildDate>2008-05-21</lastBuildDate>",
        "<generator>markyp_rss</generator>",
        "<docs>https://validator.w3.org/feed/docs/rss2.html</docs>",
        "<ttl>42</ttl>",
        '<cloud domain="some.domain" port="80" path="/channel/example" registerProcedure="pingMe" protocol="soap"/>',
        "<image>\n<title>Image Title</title>\n<url>https://image.test/image.jpeg</url>\n<link>https://channel.link</link>\n</image>",
        "<category>Testing</category>",
        "<item>",
        "<title>Testing</title>",
        "<link>testing.html</link>",
        "</item>",
        "</channel>"
    ))

    assert channel.add_categories(Category("Testing - 1"), Category("Testing - 2")) == channel
    assert channel.add_items(Item("Testing - 1", "testing-1.html"), Item("Testing - 2", "testing-2.html"))
    assert channel.markup == "\n".join((
        "<channel>",
        "<title>RSS 2.0 Test Channel</title>",
        "<link>https://test.channel.rss/</link>",
        "<description>Test channel &gt; description</description>",
        "<language>eo</language>",
        "<copyright>Copyright 2019, VP</copyright>",
        "<managingEditor>joe@test.channel, Joe</managingEditor>",
        "<webMaster>webmaster@test.channel</webMaster>",
        "<pubDate>2008-05-21</pubDate>",
        "<lastBuildDate>2008-05-21</lastBuildDate>",
        "<generator>markyp_rss</generator>",
        "<docs>https://validator.w3.org/feed/docs/rss2.html</docs>",
        "<ttl>42</ttl>",
        '<cloud domain="some.domain" port="80" path="/channel/example" registerProcedure="pingMe" protocol="soap"/>',
        "<image>\n<title>Image Title</title>\n<url>https://image.test/image.jpeg</url>\n<link>https://channel.link</link>\n</image>",
        "<category>Testing</category>",
        "<category>Testing - 1</category>",
        "<category>Testing - 2</category>",
        "<item>",
        "<title>Testing</title>",
        "<link>testing.html</link>",
        "</item>",
        "<item>",
        "<title>Testing - 1</title>",
        "<link>testing-1.html</link>",
        "</item>",
        "<item>",
        "<title>Testing - 2</title>",
        "<link>testing-2.html</link>",
        "</item>",
        "</channel>"
    ))

    assert channel.set_categories(Category("Testing - 1"), Category("Testing - 2")) == channel
    assert channel.set_items(Item("Testing - 1", "testing-1.html"), Item("Testing - 2", "testing-2.html")) == channel
    assert channel.markup == "\n".join((
        "<channel>",
        "<title>RSS 2.0 Test Channel</title>",
        "<link>https://test.channel.rss/</link>",
        "<description>Test channel &gt; description</description>",
        "<language>eo</language>",
        "<copyright>Copyright 2019, VP</copyright>",
        "<managingEditor>joe@test.channel, Joe</managingEditor>",
        "<webMaster>webmaster@test.channel</webMaster>",
        "<pubDate>2008-05-21</pubDate>",
        "<lastBuildDate>2008-05-21</lastBuildDate>",
        "<generator>markyp_rss</generator>",
        "<docs>https://validator.w3.org/feed/docs/rss2.html</docs>",
        "<ttl>42</ttl>",
        '<cloud domain="some.domain" port="80" path="/channel/example" registerProcedure="pingMe" protocol="soap"/>',
        "<image>\n<title>Image Title</title>\n<url>https://image.test/image.jpeg</url>\n<link>https://channel.link</link>\n</image>",
        "<category>Testing - 1</category>",
        "<category>Testing - 2</category>",
        "<item>",
        "<title>Testing - 1</title>",
        "<link>testing-1.html</link>",
        "</item>",
        "<item>",
        "<title>Testing - 2</title>",
        "<link>testing-2.html</link>",
        "</item>",
        "</channel>"
    ))

    assert channel.set_categories() == channel
    assert channel.set_items() == channel
    assert channel.markup == "\n".join((
        "<channel>",
        "<title>RSS 2.0 Test Channel</title>",
        "<link>https://test.channel.rss/</link>",
        "<description>Test channel &gt; description</description>",
        "<language>eo</language>",
        "<copyright>Copyright 2019, VP</copyright>",
        "<managingEditor>joe@test.channel, Joe</managingEditor>",
        "<webMaster>webmaster@test.channel</webMaster>",
        "<pubDate>2008-05-21</pubDate>",
        "<lastBuildDate>2008-05-21</lastBuildDate>",
        "<generator>markyp_rss</generator>",
        "<docs>https://validator.w3.org/feed/docs/rss2.html</docs>",
        "<ttl>42</ttl>",
        '<cloud domain="some.domain" port="80" path="/channel/example" registerProcedure="pingMe" protocol="soap"/>',
        "<image>\n<title>Image Title</title>\n<url>https://image.test/image.jpeg</url>\n<link>https://channel.link</link>\n</image>",
        "</channel>"
    ))


def test_RSS():
    rss = RSS(Channel("RSS 2.0 Test Channel", "https://test.channel.rss/", "Test channel > description"))
    assert rss.markup == "\n".join((
        '<rss version="2.0">',
        "<channel>",
        "<title>RSS 2.0 Test Channel</title>",
        "<link>https://test.channel.rss/</link>",
        "<description>Test channel &gt; description</description>",
        "<generator>markyp_rss</generator>",
        "</channel>",
        "</rss>"
    ))
