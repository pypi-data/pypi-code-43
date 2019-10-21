from typing import List, Optional, Tuple

from qai.issues.issues import make_issue

try:
    from spacy.tokens.span import Span
except ModuleNotFoundError as e:
    print(
        "\n\nQAI v2.0.0 and above assume spaCy is installed, but do not list it as a requirement"
        "If you want to use SpacyFactor, please install spaCy >=2.1.0\n\n"
    )
    raise e


class SpacyFactor(object):
    def __init__(self, issue_type: str, description: Optional[str] = None):
        self.issue_type = issue_type
        if description:
            self.description = description

    @staticmethod
    def match_case(span_text, suggestions):
        """
        suggestions respect original casing
        ex. purchase -> buy (lower)
        ex. PURCHASE -> BUY (upper)
        ex. Purchase -> Buy (title)
        """

        try:
            if len(span_text.strip()):
                words = span_text.split(" ")
                if words[0].islower():
                    # todo: exclude I and capitalized proper nouns
                    suggestions = [s.lower() for s in suggestions]

                # len condition: exclude capitalization caused by "I"
                elif len(words[0]) > 1 and words[0].isupper():
                    suggestions = [s.upper() for s in suggestions]

                # title case - first letter check & conversion due to contractions
                elif len(words[0]) > 1 and words[0][0].isupper():
                    for i, s in enumerate(suggestions):
                        if len(s.strip()):
                            s_words = s.split(" ")
                            suggestions[i] = " ".join(
                                [s_words[0][0].upper() + s_words[0][1:]] + s_words[1:]
                            ).strip()
        except:
            suggestions_log = ",".join(suggestions)
            print(f"Case matching failed for span: {span_text} and {suggestions_log}")

        return suggestions

    def __call__(
        self, spacy_span: Span, meta_subcategory=None, describer=None, cased=True
    ):
        """
        convenient wrapper around make_issue if you are using spaCy

        usage example:

        ```python
        from spacy.tokens import Span
        from app.factor import SpacyFactor


        SOV = SpacyFactor(
            "subject_object_verb_spacing",
            "Keep the subject, verb, and object of a sentence close together to help the reader understand the sentence."
        )

        Span.set_extension("score", default=0)
        Span.set_extension("suggestions", default=[])

        doc = nlp("Holders of the Class A and Class B-1 certificates will be entitled to receive on each Payment Date, to the extent monies are available therefor (but not more than the Class A Certificate Balance or Class B-1 Certificate Balance then outstanding), a distribution.")
        score = analyze(doc)
        if score is not None:
            span = Span(doc, 0, len(doc))  # or whichever TOKENS are the issue (don't have to worry about character indexes)
            span._.score = score
            span._.suggestions = get_suggestions(doc)
            issues = SOV(span)
        ```
        """
        text, start, end = spacy_span.text, spacy_span.start_char, spacy_span.end_char
        score = spacy_span._.score if spacy_span.has_extension("score") else 0
        suggestions = (
            spacy_span._.suggestions if spacy_span.has_extension("suggestions") else []
        )

        if cased:
            suggestions = self.match_case(spacy_span.text, suggestions)

        if describer:
            description = describer(spacy_span)
        else:
            description = self.description

        if meta_subcategory:
            subcategory = meta_subcategory
        else:
            subcategory = ""

        return make_issue(
            text,
            start,
            end,
            issue_type=self.issue_type,
            score=score,
            description=description,
            suggestions=suggestions,
            subCategory=subcategory,
        )
