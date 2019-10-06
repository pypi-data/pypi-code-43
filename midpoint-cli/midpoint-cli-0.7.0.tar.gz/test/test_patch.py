import unittest

from midpoint_cli.patch import patch_from_string


class PatchTest(unittest.TestCase):
    def test_simple_patch(self):
        xml = '''<role>
    <name>Organizational Unit</name>
    <description>Meta role for all organizational units.</description>

    <!-- Disabled for initial import
    <inducement>
    
    </inducement>
    -->
</role>'''

        self.assertTrue('<!--' in xml)
        self.assertTrue('-->' in xml)

        patch = '''
        <!--.*  => 
        -->     => 
        '''

        patched_xml = patch_from_string(xml, patch)

        self.assertFalse('<!--' in patched_xml)
        self.assertFalse('-->' in patched_xml)
