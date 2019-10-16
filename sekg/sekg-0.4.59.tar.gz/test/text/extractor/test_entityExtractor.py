from unittest import TestCase

from sekg.text.extractor.domain_entity.entity_extractor import EntityExtractor


class TestEntityExtractor(TestCase):
    def test_extract_from_sentence(self):
        sent = """Specifically, workspaces are designed for cyclical workloads - such as training neural networks - as
            they allow for off-heap memory reuse (instead of continually allocating and deallocating memory on each iteration
            of the loop). """

        extractor = EntityExtractor()
        terms = extractor.extract_from_sentence(sent)
        for term in terms:
            print(term)

    def test_extract_code_element(self):
        sent = "public void addComponent(String label, Component comp)\n" + \
               "{\n" + \
               "JLabel l = newLabel(label, comp);\n" + \
               "l.setBorder(new EmptyBorder(0,0,0,12));\n" + \
               "addComponent(l,comp,GridBagConstraints.BOTH);\n" + \
               "} //}}\n"
        extractor = EntityExtractor()
        terms = extractor.extract_code_element(sent)
        for term in terms:
            print(term)
