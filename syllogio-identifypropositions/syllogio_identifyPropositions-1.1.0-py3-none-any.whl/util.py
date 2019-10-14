import operator


def getAllDescendantTokens(token):
    res = list(token.children)
    for child in token.children:
        res = operator.add(res, getAllDescendantTokens(child))
    return res


def clauseTokensToString(tokens):
    sortedTokens = sorted(tokens, key=lambda tt: tt.i)
    # Get rid of preceding punctuation or white space
    while sortedTokens[0].is_punct or sortedTokens[0].is_space:
        del sortedTokens[0]
    # Get rid of trailing punctuation
    while sortedTokens[-1].is_punct or sortedTokens[-1].is_space:
        del sortedTokens[-1]
    # Start with the first token's text
    res = sortedTokens[0].text
    remaining = sortedTokens[1:]

    for idx, token in enumerate(remaining):
        # concatenate punctuation
        if token.is_punct or remaining[idx - 1].text == "-":
            res = res + token.text
        # concatenate word tokens
        else:
            res = res + " " + token.text
    return res


# TODO: prevent issues from recursion when parsing large selections of text by using the
# trampoline pattern.
def parseClause(rootToken):
    props = []
    propTokens = [rootToken]
    for child in rootToken.children:
        # If the child is a verb or auxiliary verb and is related to the root in such a
        # way as to indicate a separate proposition, parse that proposition
        # independently.
        if (child.pos_ == "AUX" or child.pos_ == "VERB") and (
            child.dep_ == "conj"
            or child.dep_ == "advcl"
            or child.dep_ == "ccomp"
            or child.dep_ == "advcl"
        ):
            props = operator.add(props, parseClause(child))
        else:
            # Exclude coordinating conjunctions since they do not fit in the primary
            # text of either proposition.
            if child.dep_ != "cc" and child.dep_ != "conj":
                propTokens.append(child)

            propTokens = operator.add(propTokens, getAllDescendantTokens(child))
    props.append(clauseTokensToString(propTokens))
    return props
