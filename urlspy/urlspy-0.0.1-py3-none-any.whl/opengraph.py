from ruia import Item, AttrField, TextField


OG_ATTRS = ['title', 'type', 'image', 'url', 'description']


class OpengraphItem(Item):
    target_item = TextField(css_select="head")
    title = AttrField(css_select=r'meta[property=og\:title]', attr='content')
    type = AttrField(css_select=r'meta[property=og\:type]', attr='content')
    image = AttrField(css_select=r'meta[property=og\:image]', attr='content')
    url = AttrField(css_select=r'meta[property=og\:url]', attr='content')
    description = AttrField(css_select=r'meta[property=og\:description]', attr='content')


async def extract_opengraph(html="", url=""):
    item = None

    async for item in OpengraphItem.get_items(html=html, url=url):
        break

    if not item:
        return {}

    return {key: getattr(item, key) or None for key in OG_ATTRS}
