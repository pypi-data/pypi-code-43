from django.utils.translation import gettext as _
from django.core.validators import URLValidator

from wagtail.core import blocks
from wagtail.images.blocks import ImageChooserBlock


TEXT_OVERLAY_DELTA = '20px'


class HeaderBlock(blocks.StructBlock):
    """A HTML header"""
    header_level = blocks.ChoiceBlock(
        choices=(
            ('h2', 'H2'),
            ('h3', 'H3'),
            ('h4', 'H4'),
            ('h5', 'H5'),
            ('h6', 'H6'),
        ),
        label=_('Header level'),
    )
    text = blocks.CharBlock(
        label=_('Text'),
    )

    class Meta:
        template = 'wagtailpress/blocks/header.html'
        icon = "title"


class ImageTextOverlayBlock(blocks.StructBlock):
    """An image with text overlay"""
    image = ImageChooserBlock(
        label=_('Image'),
    )
    text = blocks.CharBlock(
        label=_('Text'),
        max_length=200,
    )
    text_color = blocks.ChoiceBlock(
        choices=(
            ('black', _('Black')),
            ('white', _('White')),
            ('red', _('Red')),
            ('blue', _('Blue')),
            ('green', _('Green')),
        ),
        label=_('Text color')
    )
    text_position = blocks.ChoiceBlock(
        choices=(
            (
                'top: 50%; left: 50%; transform: translate(-50%, -50%);',
                _('Centered')
            ),
            (
                'top: {}; left: {};'.format(
                    TEXT_OVERLAY_DELTA,
                    TEXT_OVERLAY_DELTA,
                ),
                _('Top Left')
            ),
            (
                'top: {}; right: {};'.format(
                    TEXT_OVERLAY_DELTA,
                    TEXT_OVERLAY_DELTA,
                ),
                _('Top Right')
            ),
            (
                'bottom: {}; left: {};'.format(
                    TEXT_OVERLAY_DELTA,
                    TEXT_OVERLAY_DELTA,
                ),
                _('Bottom Left')
            ),
            (
                'bottom: {}; right: {};'.format(
                    TEXT_OVERLAY_DELTA,
                    TEXT_OVERLAY_DELTA,
                ),
                _('Bottom Right')
            ),
        )
    )

    class Meta:
        template = 'wagtailpress/blocks/image_text_overlay.html'
        icon = 'image'
        label = _('Image with text overlay')


class LinkBlock(blocks.StructBlock):
    """An URL with its description"""
    description = blocks.CharBlock(
        label=_('Description'),
    )
    url = blocks.URLBlock(
        label=_('URL'),
        validators=[
            URLValidator(
                [
                    'http',
                    'https',
                    'ftp',
                    'ftps',
                    'mailto',
                    'xmpp',
                    'tel',
                ]
            )
        ]
    )

    class Meta:
        template = 'wagtailpress/blocks/link.html'
        icon = 'site'
        label = _('Link')
