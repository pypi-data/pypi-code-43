from typing import List, Optional



class InvalidTagNameException(Exception):
    pass


class AnnotatedTag:
    """
    Steven Yang, September 2019.
    This object understands raw tag names like "handgun-semi-slide-c1-1A".  Its greater
    purpose is bigger than this, as explained here.
    An AnnotatedTag contains all of the meta information associated with a ground truth
    bounding box, not including the box itself.  AnnotatedTag is a subcomponent of
    AnnotatedLabel, which owns both an AnnotatedTag and a BoundingBox.
    Historically, we've trained Cloud Factory to follow a strict naming scheme for raw
    tag names.  For as long as we rely on this tagging scheme, that raw tag name will remain
    critically important to our needs.  However, this object understands the individual elements
    associated with a raw tag name, which would enable us in the future to switch labeling
    interfaces.
    The load_from_raw_tag_name() function parses raw tags in a manner consistent with these
    examples:
    handgun-semi-slide-c1-1A -> class_name=handgun, tag0=semi, tag1=slide, orientation=1,
                                occlusion=1, recognizability=A
    handgun-c1 -> This is contrived, but would be parsed as class_name=handgun,
                  tag0=unknown, orientation=1, occlusion=None, recognizability=None
    In all known real cases, there is at least one tag, but this parser can recognize
    the lack of one to set tag0=unknown.  All tag_names are expected to contain
    the orientation (c1 or c2), and the absence of the occlusion/recognizability score
    is tolerated.
    Once a raw tag has been parsed into an AnnotatedTag object, the goal of
    all code external to this object is to not think about raw tag names, and focus on
    using the attributes instead.  This is quickly accomplished early in the process, where
    we convert the original format into a custom JSON format.
    """

    def __init__(
        self,
        raw_tag_name: str = "",
        class_name: str = "unknown",
        tags: Optional[List[str]] = None,
        occlusion: Optional[int] = None,
        recognizability: Optional[str] = None,
        orientation: int = 1
    ):
        """ Note: these member variable names are used by the dump() function as
            part of the process of generating JSON.  If other member variables are
            added in the future that you don't want in the JSON, you'll have to
            implement the dump() function rather than rely on what comes by
            default within JSONDumpable. """
        self.raw = raw_tag_name
        self.class_name = class_name
        self.tags = tags or []
        self.occlusion = occlusion
        self.recognizability = recognizability
        self.orientation = orientation

    @classmethod
    def load(cls, obj: dict) -> "AnnotatedTag":
        return cls(
            obj["raw"], obj["class_name"], obj["tags"], obj["occlusion"], obj["recognizability"],
            obj["orientation"]
        )

    @classmethod
    def load_from_raw_tag_name(cls, raw_tag_name: str) -> "AnnotatedTag":
        tag = cls()
        tag._parse_tag(raw_tag_name)
        return tag

    def _parse_tag(self, tag_name: str) -> None:

        if "--" in tag_name:
            raise InvalidTagNameException("Double dash '--' not permitted in tag_name: " + tag_name)

        self.raw = tag_name
        parts = tag_name.split('-')

        num_parts = len(parts)
        if num_parts < 2:
            raise InvalidTagNameException("Invalid tag name: " + tag_name)

        # the class name always comes first
        self.class_name = parts.pop(0)

        # approach, pop off the end until we get the orientation
        while len(parts) > 0:
            part = parts.pop()

            if self._parse_occlusion_and_recognizability(part):
                continue
            elif self._parse_orientation(part):
                break
            else:
                raise InvalidTagNameException("Invalid tag name: " + tag_name)

        # If here, we have a valid tag.  Any remaining parts are subtags
        self.tags = parts

        # if no subtags, set subtag0 to be "unknown"
        if len(parts) == 0:
            self.tags.append("unknown")

    def _parse_occlusion_and_recognizability(self, part: str) -> bool:

        if len(part) != 2:
            return False

        if part[0] in ["0", "1", "2", "3", "4"]:
            self.occlusion = int(part[0])
        else:
            return False

        if part[1] in ["A", "B", "C"]:
            self.recognizability = part[1]
        else:
            return False

        return True

    def _parse_orientation(self, part: str) -> bool:

        if len(part) != 2:
            return False

        if part[0] != "c":
            return False

        if part[1].isnumeric():
            self.orientation = int(part[1])
        else:
            return False

        return True


if __name__ == "__main__":

    def display_tag(tag_name: str) -> None:
        try:
            tag = AnnotatedTag.load_from_raw_tag_name(tag_name)
            print(tag)
        except Exception as e:
            print("Unexpected exception with tag named '{}': {}".format(tag_name, str(e)))

    display_tag("handgun-semi-slide-c1-1A")
    display_tag("handgun-c1")
    display_tag("sharp-steven-yang-fixed-c2-0C")
    display_tag("sharp-pocket-closed-c1-1A")

    def catch_exception_test(tag_name: str) -> None:
        try:
            AnnotatedTag.load_from_raw_tag_name(tag_name)
            print("failed to catch exception")
        except InvalidTagNameException:
            print("caught exception as expected")

    catch_exception_test("handgun--c1")
    catch_exception_test("handgun-semi-slide-d1-1A")
    catch_exception_test("handgun-semi-slide-c1-5A")
    catch_exception_test("handgun-semi-slide-c2-1D")
    catch_exception_test("handgun-semi-slide-c2-1a")
    catch_exception_test("handgun-semi-slide-1c-1A")
    catch_exception_test("handgun-semi-slide-C2-1A")