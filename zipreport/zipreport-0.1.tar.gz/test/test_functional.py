import unittest
from zipreport import Document, Part, Element, FormattedText, Renderer, Margins, SummaryDescriptor, BorderStyle

class TestFunctional(unittest.TestCase):
    def test_something(self):
        content_part = Part(
            elements=[Element(x=0.,
                              y=0.,
                              width=72.,
                              height=18.,
                              content=FormattedText("N:$name", font_family='Futura', font_size=9.)),

                      Element(x=96.,
                              y=0,
                              width=72.*4.,
                              height=4.*72.,
                              can_shrink=True,
                              content=FormattedText("$comment", font_family='Futura', font_size=9.)),
                      Element(x=72. * 6, y=0., width=36, height=18,
                              content=FormattedText("$rn", font_family='Futura', font_size=9.,
                                                    alignment='r'))],
            minimum_height=72.,
            bottom_spacing=12.,
            bottom_border=BorderStyle(width=0.5, color=(.3,.3,.3))
        )

        header_band = Part(
            bottom_border=BorderStyle(color=(.0,.0,1.), width=3., dash=((5., 2.), 0.)),
            background_color=(.9, .9, .9),
            elements=[Element(x=0., y=0., width=144. , height=22.,
                              content=FormattedText("REPORT", font_family='Futura', font_size=12.))],
        )

        footer_part = Part(
            elements=[Element(x=5.* 72., y=0., width=72. * 1.5, height=18,
                              content=FormattedText("Page $page_number", font_family='Futura', font_size=9., alignment='r'))],
        )

        mode_header_part = Part(
            background_color=(1.,1.,.8),
            elements=[Element(x=0., y=0., width=400., height=14.,
                              content=FormattedText(">>> Mode $new_value >>>", font_size=9., font_family='Futura'))],
        )

        mode_footer_part = Part(
            elements=[Element(x=0., y=0., width=7. * 72., height=14.,
                              content=FormattedText("<<< End Mode $old_value <<< ", font_size=9., font_family='Futura'))],
        )
        summarize_by_mode = SummaryDescriptor(key='mode',
                                              leading_header=mode_header_part,
                                                  trailing_header=mode_footer_part)

        document = Document(content_part=content_part, summary_descriptors=[summarize_by_mode],
                            page_header=header_band, page_footer=footer_part)

        renderer = Renderer(
            document=document,
            media_height=11.0 * 72.,
            media_width=8.5 * 72.,
            page_margins=Margins(left=72. * .75, right=72. * .75, top=72., bottom=72. * .5)
        )

        content = [
            dict(name='Test 1', comment="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod "
                                        "tempor incididunt ut labore et dolore magna aliqua.", mode='a', rn='1213'),
            dict(name='Test 2', comment="Nascetur ridiculus mus mauris vitae ultricies.", mode='a', rn='99'),
            dict(name='Test 3', comment="Morbi tempus iaculis urna id volutpat "
                                                                            "lacus laoreet non. Ac odio tempor orci "
                                                                            "dapibus. Curabitur gravida arcu ac "
                                                                            "tortor. Amet dictum sit amet justo.",
                 mode='a', rn='2'),

            dict(name='Test 4', comment="Morbi tempus iaculis urna id volutpat lacus laoreet non. Ac odio tempor orci "
                                        "dapibus. Curabitur gravida arcu ac tortor. Amet dictum sit amet justo.  "
                                        "Morbi tempus iaculis urna id volutpat lacus laoreet non. Ac odio tempor orci "
                                        "dapibus. Curabitur gravida arcu ac tortor. Amet dictum sit amet justo.  ",
                 mode='b', rn='145'),
            dict(name='Test 5', comment="Massa tincidunt nunc pulvinar sapien et. In fermentum et sollicitudin ac.",
                 mode='b', rn='9990'),
            dict(name='Test 6', comment="Arcu vitae elementum curabitur vitae nunc sed velit dignissim. Porta lorem "
                                        "mollis aliquam ut porttitor.",
                 mode='b', rn='2'),
            dict(name='Test 7', comment="Porta nibh venenatis cras sed felis eget velit aliquet sagittis. Tristique "
                                        "sollicitudin nibh sit amet commodo.",
                 mode='b', rn='0184023'),

            dict(name='Test 8', comment="Anteger vitae justo eget magna.",
                 mode='c'),
            dict(name='Test 9', comment="Ultricies integer quis auctor elit sed vulputate mi.",
                 mode='c'),
            dict(name='Test 10', comment="Amet est placerat in egestas erat imperdiet sed euismod.",
                 mode='c'),
            dict(name='Test 11', comment="Scelerisque fermentum dui faucibus in ornare quam viverra orci sagittis.",
                 mode='c'),

            dict(name='Test 12', comment="Pretium nibh ipsum consequat nisl vel pretium lectus quam id.",
                 mode='d'),
            dict(name='Test 13', comment="Sit amet volutpat consequat mauris nunc congue nisi vitae suscipit. Eget "
                                         "gravida cum sociis natoque penatibus. Sed viverra tellus in hac habitasse "
                                         "platea. Euismod elementum nisi quis eleifend quam adipiscing vitae proin "
                                         "sagittis. Dignissim diam quis enim lobortis.",
                 mode='d')
        ]

        renderer.render(content=content, out_filename='test.pdf')


if __name__ == '__main__':
    unittest.main()
