import textwrap

from typing import List


def requestDocumentationToApiBlueprint(docs):
    queryParameters = []

    for method in docs.get("methods", {}).values():
        queryParameters += method.get(
            "requestParameters",
            {},
        ).get(
            "query",
            {},
        ).keys()

    queryParameterString = ",".join(sorted(set(queryParameters)))

    if queryParameters:
        queryParameterString = "{?" + queryParameterString + "}"

    s = f"""
# {docs.get("name", "Unnamed Route")} [{docs["path"]}{queryParameterString}]

{docs["description"]}
    """

    for method, data in docs["methods"].items():
        s += f"""\n## {data["name"]} [{method.upper()}]\n"""

        if data.get("description"):
            s += f"{data['description']}\n"

        parameters = data.get(
            "requestParameters",
            {},
        )

        displayableParameters = sorted(
            list(parameters.get(
                "url",
                {},
            ).items()) + list(parameters.get(
                "query",
                {},
            ).items())
        )

        bodyParameters = sorted(list(parameters.get(
            "body",
            {},
        ).items()))

        if displayableParameters:
            s += "\n+ Parameters\n"

            for name, parameter in displayableParameters:
                s += _parameterToMarkdown(
                    name=name,
                    parameter=parameter,
                )

        if bodyParameters:
            s += "\n Attributes\n"

            for name, parameter in bodyParameters:
                s += _parameterToMarkdown(
                    name=name,
                    parameter=parameter,
                )
        for example in data.get("examples", []):

            s += _testCaseToMarkdown(
                request=example["request"],
                response=example["response"],
                name="Unnamed",
            )

    return s


def _allowedTypesToString(allowedTypes: List) -> str:
    if len(allowedTypes) == 1:
        allowedTypesString = allowedTypes[0]
    elif allowedTypes:
        allowedTypesString = ",".join(allowedTypes)
    else:
        allowedTypesString = "any"
    return allowedTypesString


def _parameterToMarkdown(name: str, parameter: dict):
    s = ""
    allowedTypes = _allowedTypesToString(parameter.get("allowedTypes", []))

    optional = "optional" if parameter.get("optional") else "required"

    description = parameter.get("description") or ""

    default = parameter.get("default")

    s += f"\n\t+ {name} ({allowedTypes}, {optional}) - {description}\n"

    if default is not None:
        s += f"\t\t+ Default: ``{default}``\n"

    if parameter.get("allowedValues"):
        s += "\t\t+ Members\n"

        for value in parameter["allowedValues"]:
            s += f"\t\t\t+ `{value}`\n"

    return s


def _testCaseToMarkdown(request, response, name=""):
    contentType = request.headers.get("Content-Type", "application/json")

    s = f"+ Request {name} ({contentType})\n\n"
    if request.body:
        s += textwrap.indent(request.body, "\t") + "\n"

    contentType = request.headers.get("Content-Type", "application/json")
    s += f"+ Response {response.statusCode} ({contentType})\n\n"
    if response.body:
        s += textwrap.indent(response.body, "\t") + "\n"

    return s