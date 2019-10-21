"""
The shared callback logic

expects to be called as part of a class with the properties:
* instance.should_whitelist
* instance.category
* instance.analyzer
* instance.white_lister
"""
from qai.issues.meta import get_meta_value


def _is_valid(instance):
    assert instance.should_whitelist is not None
    assert instance.category is not None
    assert instance.analyzer is not None


def qallback(instance, segment, metadata, language):
    """
    Helper libs won't memoize this for us, because
    "Arguments to memoized function must be hashable"
    so we need to build it ourselves... weakass Python can't hash class instances
    """
    _is_valid(instance)

    if language not in instance.supported_languages:
        print(
            f"Received language {language}, supported Languages: {instance.supported_languages}"
        )
        return []

    if instance.should_whitelist:
        # Should we have whitelisting on?
        # this is a per-service setting;
        # e.g. Passive voice => no whitelisting
        # Gender bias => whitelisting
        enabled, meta_value, sub_groups = get_meta_value(instance.category, metadata)
        if enabled:
            # enabled/disabled is a per-project setting
            # e.g. customers can configer this in a GUI

            try:
                # allow new analyze method that has access to everything
                issues = instance.analyzer.analyze_with_metadata(
                    segment,
                    language=language,
                    meta_value=meta_value,
                    sub_groups=sub_groups,
                )
            except AttributeError:
                issues = instance.analyzer.analyze(segment)
            issues = instance.white_lister(issues, meta_value, sub_groups)
        else:
            # Value is None means this service is disabled
            # for this client
            issues = []
    else:
        # no whitelisting, just get issues
        issues = instance.analyzer.analyze(segment)

    return issues
