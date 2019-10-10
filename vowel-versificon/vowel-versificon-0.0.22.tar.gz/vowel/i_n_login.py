Ans="""

[
    {
        "id": "e1858e.76bf3a7",
        "type": "tab",
        "label": "Flow 1",
        "disabled": false,
        "info": ""
    },
    {
        "id": "14d4894b.0d7a0f",
        "type": "http in",
        "z": "e1858e.76bf3a7",
        "name": "",
        "url": "/test",
        "method": "get",
        "upload": false,
        "swaggerDoc": "",
        "x": 159.26666259765625,
        "y": 249.88333129882812,
        "wires": [
            [
                "d78fe440.1ae948"
            ]
        ]
    },
    {
        "id": "d78fe440.1ae948",
        "type": "template",
        "z": "e1858e.76bf3a7",
        "name": "",
        "field": "payload",
        "fieldType": "msg",
        "format": "html",
        "syntax": "mustache",
        "template": "<html>\n<body>\n    <center>\n        <form name=\"form1\">\n        <label><b>Username:</b></label>\n        <input type=\"text\" name=\"userid\" placeholder=\"Enter Username\" required><br><br>\n        <label><b>Password:</b></label>\n        <input type=\"Password\" name=\"pwd\" placeholder=\"Enter Password\" required><br><br>\n        <button type=\"submit\" onclick=\"return check(this.form)\">Login</button>\n        </form>\n    </center>\n<script>\nfunction check(form)\n{\n\nif(form1.userid.value == \"Om\" && form1.pwd.value == \"Om\")\n{\n    document.write(\"Successfully Logged in\");\n\treturn true;\n}\nelse\n{\n\talert(\"Error Password or Username\")\n\treturn false;\n}\n}\n</script>\n\n</body>    \n</html>",
        "output": "str",
        "x": 340.26666259765625,
        "y": 251.71664428710938,
        "wires": [
            [
                "8ecec26c.8d9b58"
            ]
        ]
    },
    {
        "id": "8ecec26c.8d9b58",
        "type": "http response",
        "z": "e1858e.76bf3a7",
        "name": "",
        "statusCode": "",
        "headers": {},
        "x": 559.2666015625,
        "y": 252.43331909179688,
        "wires": []
    }
]

"""