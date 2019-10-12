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
        queryParameters = "{?" + queryParameterString + "}"

    s = f"""
# {docs.get("name", "")} [{docs["path"]}{queryParameters}]

{docs["description"]}
    """

    for method, data in docs["methods"].items():
        s += f"""\n## {data["description"]} [{method.upper()}]\n"""

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
                allowedTypes = _allowedTypesToString(
                    parameter.get("allowedTypes", [])
                )

                optional = "optional" if parameter.get(
                    "optional"
                ) else "required"

                description = parameter.get("description")

                default = parameter.get("default")
                s += f"\n\t+ {name} ({allowedTypes}, {optional}) - {description}\n"
                if default is not None:
                    s += f"\t\t+ Default: `{default}`\n`"

        if bodyParameters:
            s += "\n Attributes\n"

            for name, parameter in bodyParameters:
                allowedTypes = _allowedTypesToString(
                    parameter.get("allowedTypes", [])
                )

                description = parameter.get("description")

                s += f"\t+ {name} ({allowedTypes}) - {description}\n"

    return s


def _allowedTypesToString(allowedTypes: List) -> str:
    if len(allowedTypes) == 1:
        allowedTypesString = allowedTypes[0]
    elif allowedTypes:
        allowedTypesString = ",".join(allowedTypes)
    else:
        allowedTypesString = "any"
    return allowedTypesString