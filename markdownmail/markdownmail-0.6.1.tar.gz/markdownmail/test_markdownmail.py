import unittest
import mock

import markdownmail


class TestMarkdownMail(unittest.TestCase):
    def test(self):
        mail = markdownmail.MarkdownMail(
            from_addr=(u"from@example.com", u"From Example"),
            to_addr=(u"to@example.com", u"To Example"),
            subject=u"MarkdownMail demo",
            content=u"I'm a helicopter!",
        )

        self.assertEqual((u"from@example.com", u"From Example"), mail.from_addr)
        self.assertEqual([(u"to@example.com", u"To Example")], mail.to_addr)
        self.assertEqual(u"MarkdownMail demo", mail.to_mime_message()["subject"])

        txt_is_ok, html_is_ok = False, False
        for part in mail._parts:
            type_maj, type_min = part[0].split("/")
            if part[0] == "text/plain":
                self.assertEqual(u"I'm a helicopter!", part[1])
                txt_is_ok = True
            if part[0] == "text/html":
                self.assertIn(u"<html>", part[1])
                self.assertIn(u"<p>I'm a helicopter!</p>", part[1])
                html_is_ok = True
        if not txt_is_ok:
            self.fail("txt part not found")

        if not html_is_ok:
            self.fail("html part not found")

    def test_with_css(self):
        CSS = "font-family:Helvetica, Arial,sans-serif;text-align:left;color:#333333"
        mail = markdownmail.MarkdownMail(
            from_addr=(u"from@example.com", u"From Example"),
            to_addr=(u"to@example.com", u"To Example"),
            subject=u"SUBJECT",
            content=u"CONTENT",
            css=CSS,
        )

        for part in mail._parts:
            type_maj, type_min = part[0].split("/")
            if part[0] == "text/plain":
                self.assertNotIn(CSS, part[1])
            if part[0] == "text/html":
                EMBEDDED_CSS = '<style type="text/css">' + CSS + "</style>"
                self.assertIn(EMBEDDED_CSS, part[1])

    def test_force_count_for_ordered_list(self):
        mail = markdownmail.MarkdownMail(
            from_addr=(u"from@example.com", u"From Example"),
            to_addr=(u"to@example.com", u"To Example"),
            subject=u"SUBJECT",
            content="""
4. Apples
5. Oranges
6. Pears""",
        )

        for part in mail._parts:
            type_maj, type_min = part[0].split("/")
            if part[0] == "text/html":
                self.assertIn(
                    """<ol start="4">
<li>Apples</li>
<li>Oranges</li>
<li>Pears</li>
</ol>""",
                    part[1],
                )

    def test_html_is_version_4(self):
        mail = markdownmail.MarkdownMail(
            from_addr=(u"from@example.com", u"From Example"),
            to_addr=(u"to@example.com", u"To Example"),
            subject=u"SUBJECT",
            content="CONTENT",
        )

        for part in mail._parts:
            type_maj, type_min = part[0].split("/")
            if part[0] == "text/html":
                self.assertIn(
                    '<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">',
                    part[1],
                )

    def test_default_css(self):
        import markdownmail.styles

        mail = markdownmail.MarkdownMail(
            from_addr=(u"from@example.com", u"From Example"),
            to_addr=(u"to@example.com", u"To Example"),
            subject=u"SUBJECT",
            content=u"CONTENT",
        )

        for part in mail._parts:
            type_maj, type_min = part[0].split("/")
            if part[0] == "text/plain":
                self.assertNotIn(markdownmail.styles.DEFAULT_STYLE, part[1])
            if part[0] == "text/html":
                EMBEDDED_CSS = (
                    '<style type="text/css">'
                    + markdownmail.styles.DEFAULT_STYLE
                    + "</style>"
                )
                self.assertIn(EMBEDDED_CSS, part[1])

    def test_basic_css(self):
        import markdownmail.styles

        mail = markdownmail.MarkdownMail(
            from_addr=(u"from@example.com", u"From Example"),
            to_addr=(u"to@example.com", u"To Example"),
            subject=u"SUBJECT",
            content=u"CONTENT",
            css=markdownmail.styles.SIMPLE_STYLE,
        )

        for part in mail._parts:
            type_maj, type_min = part[0].split("/")
            if part[0] == "text/plain":
                self.assertNotIn(markdownmail.styles.DEFAULT_STYLE, part[1])
            if part[0] == "text/html":
                EMBEDDED_CSS = (
                    '<style type="text/css">'
                    + markdownmail.styles.SIMPLE_STYLE
                    + "</style>"
                )
                self.assertIn(EMBEDDED_CSS, part[1])


class TestSetSMTPServer(unittest.TestCase):
    def setUp(self):
        self.mail = markdownmail.MarkdownMail(
            from_addr=(u"from@example.com", u"From Example"),
            to_addr=(u"to@example.com", u"To Example"),
            subject=u"MarkdownMail demo",
            content=u"I'm a helicopter!",
        )

    @mock.patch("envelopes.Envelope.send")
    def test_server_is_localhost(self, envel_send):
        self.mail.send("localhost")

        envel_send.assert_called_once_with(host="localhost", port=25)

    @mock.patch("envelopes.Envelope.send")
    @mock.patch("markdownmail.NullServer.check")
    def test_NullServer_does_not_send_email(self, server_check, envel_send):
        self.mail.send(markdownmail.NullServer())

        self.assertFalse(envel_send.called)
        self.assertTrue(server_check.called)

    def test_CustomServer_provides_check_method_for_custom_behaviour(self):
        test_instance = self
        test_instance.custom_send_done = False

        class CustomServer(markdownmail.NullServer):
            def check(self, mail):
                test_instance.assertEqual(mail, test_instance.mail)
                test_instance.custom_send_done = True

        self.mail.send(CustomServer())

        if not test_instance.custom_send_done:
            self.fail("CustomServer.check() not called.")
