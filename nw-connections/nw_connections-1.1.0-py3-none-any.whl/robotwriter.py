"""A python interface for rendering content through Robot Writer.
"""
import requests

class RobotWriter(object):
    """
    rw = RobotWriter("http://marple-robotwriter.herokuapp.com", "longandhard123")
    html = rw.render_by_name("test_basic")
    """
    def __init__(self, url, secret):
        self.url = url
        self.secret = secret

    def render_by_name(self, template_name, context, **kwargs):
        """Render a template that is internally avaiable for the robot writer.

        :param context (dict):
        :param template_name: name of template (the pug file)
        """
        template_params = {
            "type": "key",
            "key": template_name,
        }
        return self._render_html(context, template_params, **kwargs)

    def render_string(self, template_str, context, translations=[], **kwargs):
        """
        :param context (dict):
        :param template_str: template content as string (pug syntax)
        :param translations: translation files to be used
        """
        template_params = {
            "type": "string",
            "string": template_str,
        }
        return self._render_html(context, template_params,
                                 translations=translations,
                                 **kwargs)


    def _render_html(self, context, template_params, translations=None, lang="sv",
                     theme="newsworthy", regenerate_charts=False):
        """Calls the `/html` endpoint.

        :param context (dict): the data that the template will consume (called
            `lead` in the request)
        :param template_params (dict): passed to `template` in the request
        :param translations: a translation dictionary, or the name(s) of one
            or more build-in dicionaries.
        :param lang: Used to select writer templates, and for number formatting,
            currency symbols, etc.
        :param theme: used to style regenerate_charts
        :param regenerate_charts: force re-generation of charts if they already
            exist.
        :returns: html as string.
        """
        payload = {
            "lead": context,
            "template": template_params,
            "key": self.secret,
        }
        if translations is not None:
            payload["translations"] = translations

        url = "{base_url}/lead/html?language={lang}&theme={theme}"\
               .format(base_url=self.url, lang=lang, theme=theme)

        if regenerate_charts:
            url += u"&overwrite=1"

        headers= {
            "Accept-Version": "~3"
        }
        r = requests.post(url, json=payload, headers=headers)
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError:
            resp = r.json()
            raise RobotWriterError(str(resp["message"].encode("utf-8")))

        html = r.content.decode("utf-8")

        return html


class RobotWriterError(Exception):
    pass
