# -*- coding: utf-8 -*-

html = """
<!DOCTYPE html>
<html>
<head>
</head>
<body>
<strong>Welcome to Index page</strong>
</body>
</html>
""".strip()


def handler(event, context):
    return html
