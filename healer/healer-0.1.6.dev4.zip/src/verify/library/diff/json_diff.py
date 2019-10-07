import json

a = json.loads("""
{
    "errors": [
        {"error": "invalid", "field": "email"},
        {"error": "required", "field": "name"}
    ],
    "success": false
}
""")

b = json.loads("""
{
    "success": false,
    "errors": [
        {"error": "required", "field": "name"},
        {"error": "invalid", "field": "email"}
    ]
}
""")

print(sorted(a.items()))
print(sorted(b.items()))


def ordered(entry):
    if isinstance(entry, dict):
        return sorted((k, ordered(v)) for k, v in entry.items())
    elif isinstance(entry, list):
        return sorted(ordered(x) for x in entry)
    else:
        return entry


print(ordered(a))
print(ordered(b))

# assert sorted(a.items()) == sorted(b.items())

print(f"-----------------")

a, b = json.dumps(a, sort_keys=True), json.dumps(b, sort_keys=True)
print(a)
print(b)

