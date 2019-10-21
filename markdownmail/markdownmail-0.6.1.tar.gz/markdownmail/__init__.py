import warnings

import envelopes
import markdown
import markdown.extensions.sane_lists

import markdownmail.styles


class MarkdownMail(envelopes.Envelope):
    def __init__(
        self,
        to_addr=None,
        from_addr=None,
        subject=None,
        content=None,
        css=markdownmail.styles.DEFAULT_STYLE,
    ):
        body_content = markdown.markdown(
            content,
            output_format="html4",
            extensions=[markdown.extensions.sane_lists.SaneListExtension()],
        )
        embed_css = '<style type="text/css">%(css)s</style>' % {"css": css}

        html = """<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>%(css)s</head>
<body><div id="content">%(body_content)s</div></body>
</html>""" % {
            "body_content": body_content,
            "css": embed_css,
        }
        super(MarkdownMail, self).__init__(
            to_addr, from_addr, subject, text_body=content, html_body=html
        )

    def send(self, smtp_server):
        if issubclass(smtp_server.__class__, NullServer):
            smtp_server.check(self)
        else:
            port = 25
            if ":" in smtp_server:
                smtp_server, port = smtp_server.split(":")
            super(MarkdownMail, self).send(host=smtp_server, port=int(port))


class NullServer(object):
    def check(self, markdownmail):
        pass

    def send(self, markdownmail):
        warnings.warn(
            "send() method is deprecated, use check() instead. Previous checks from send() are ignored currently.",
            DeprecationWarning,
        )
