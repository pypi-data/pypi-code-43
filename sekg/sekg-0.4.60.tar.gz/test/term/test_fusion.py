from unittest import TestCase

from sekg.term.fusion import Fusion


class TestTerm(TestCase):

    def test_fusion(self):
        fusion_tool = Fusion()
        terms = {"annotated bind", "low bind", "binds", "ok", "low of bind", "string tc", "Fine", "good", "pretty"}
        synsets = fusion_tool.fuse_by_synonym(terms)
        print(synsets)


class TestFusion(TestCase):
    def test_checkT_synnym(self):
        fusion_tool = Fusion()
        terms = {"RETURN","rule","return","annotated binds","annotated bind", "low bind", "binds", "ok", "low of bind", "string tc", "Fine", "good", "pretty","mode","model"}


        synsets = fusion_tool.fuse_by_synonym(terms)
        print(synsets)
        for t in synsets:
            print(t)

    def test_checkT_synnym_for_time(self):
        fusion_tool = Fusion()

        terms =[]

        for t in range(0,1000):
            terms.append("hhh"+str(t))

        synsets = fusion_tool.fuse_by_synonym(terms)
        print(synsets)
        for t in synsets:
            print(t)