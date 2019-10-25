import unittest

from collections import OrderedDict
from tempfile import NamedTemporaryFile

from pyats.log.utils import (banner, title, str_shortener, get_file_length,
    ReportingLogFile, FileRegion, )


class TestBanner(unittest.TestCase):

    def test_banner_simple(self):
        msg = "this is a banner"
        text = banner(msg)

        text = text.splitlines()

        self.assertEqual(len(text), 3)

        self.assertEqual(text[0], "+" +"-"*78+"+")
        self.assertEqual(text[1], "|" + msg.center(78) + "|")
        self.assertEqual(text[2], "+" +"-"*78+"+")

    def test_banner_multi_line(self):
        msg = "this is a banner\nthat is two lines\r\nand more"

        text = banner(msg)

        msg = msg.splitlines()

        text = text.splitlines()

        self.assertEqual(len(text), 5)

        self.assertEqual(text[0], "+" +"-"*78+"+")
        self.assertEqual(text[1], "|    " + msg[0].center(70) + "    |")
        self.assertEqual(text[2], "|    " + msg[1].center(70) + "    |")
        self.assertEqual(text[3], "|    " + msg[2].center(70) + "    |")
        self.assertEqual(text[4], "+" +"-"*78+"+")

    def test_banner_variable_length_multiple_line(self):
        msg = "this is a banner\nthat is two lines\r\nand more"

        text = banner(msg, 50)
        msg = msg.splitlines()
        text = text.splitlines()

        self.assertEqual(len(text), 5)

        self.assertEqual(text[0], "+" +"-"*48+"+")
        self.assertEqual(text[1], "|    " + msg[0].center(40) + "    |")
        self.assertEqual(text[2], "|    " + msg[1].center(40) + "    |")
        self.assertEqual(text[3], "|    " + msg[2].center(40) + "    |")
        self.assertEqual(text[4], "+" +"-"*48+"+")

    def test_really_long_banner(self):
        msg = "1" * 80

        text = banner(msg)

        text = text.splitlines()

        self.assertEqual(len(text), 4)

        self.assertEqual(text[0], "+" +"-"*78+"+")
        self.assertEqual(text[1], "|    " + "1" * 70 + "    |")
        self.assertEqual(text[2], "|    " + ("1" * 10).center(70) + "    |")
        self.assertEqual(text[3], "+" +"-"*78+"+")

    def test_custom_banner_wrap(self):
        msg = "1" * 80

        text = banner(msg, 50)
        text = text.splitlines()

        self.assertEqual(len(text), 4)

        self.assertEqual(text[0], "+" +"-"*48+"+")
        self.assertEqual(text[1], "|    " + "1" * 40 + "    |")
        self.assertEqual(text[2], "|    " + "1" * 40 + "    |")
        self.assertEqual(text[3], "+" +"-"*48+"+")

    def test_another_really_long_banner(self):
        msg = "1" * 68 + "2" * 30

        text = banner(msg)

        text = text.splitlines()

        self.assertEqual(len(text), 4)

        self.assertEqual(text[0], "+" +"-"*78+"+")
        self.assertEqual(text[1], "|    " + "1" * 68+"22    |")
        self.assertEqual(text[2], '|                         '+("2" * 28)+\
                                  '                         |')
        self.assertEqual(text[3], "+" +"-"*78+"+")

    def test_width_modification(self):
        msg = "this is a banner"
        text = banner(msg,width=20)

        text = text.splitlines()

        self.assertEqual(len(text), 4)

        self.assertEqual(text[0], "+" +"-"*18+"+")
        self.assertEqual(text[1],'|    this is a     |')
        self.assertEqual(text[2],'|      banner      |')
        self.assertEqual(text[3], "+" +"-"*18+"+")

    def test_padding_modification(self):
        msg = "this is a banner that is long but not that long for "\
              "padding testing zz z zz zzz"

        text = banner(msg,padding=6)
        text = text.splitlines()
        self.assertEqual(len(text), 4)

        self.assertEqual(text[0], "+" +"-"*78+"+")
        self.assertEqual(text[1], "|   this is a banner that is long but not "
                                  "that long for padding testing zz z   |")
        self.assertEqual(text[2], "|                                    zz "
                                  "zzz                                    |" )

        self.assertEqual(text[3], "+" +"-"*78+"+")

    def test_width_padding_modification(self):
        msg = "this is a banner"
        text = banner(msg,width=20,padding=6)

        text = text.splitlines()

        self.assertEqual(len(text), 4)

        self.assertEqual(text[0], "+" +"-"*18+"+")
        self.assertEqual(text[1],'|   this is a ba   |')
        self.assertEqual(text[2],'|       nner       |')
        self.assertEqual(text[3], "+" +"-"*18+"+")

    def test_width_h_margin_modification(self):
        msg = "this is a banner"
        text = banner(msg,width=20,h_margin='=')

        text = text.splitlines()

        self.assertEqual(len(text), 4)

        self.assertEqual(text[0], "+" +"="*18+"+")
        self.assertEqual(text[1],'|    this is a     |')
        self.assertEqual(text[2],'|      banner      |')
        self.assertEqual(text[3], "+" +"="*18+"+")

    def test_width_v_margin_modification(self):
        msg = "this is a banner"
        text = banner(msg,width=20,v_margin='l')

        text = text.splitlines()

        self.assertEqual(len(text), 4)

        self.assertEqual(text[0], "+" +"-"*18+"+")
        self.assertEqual(text[1],'l    this is a     l')
        self.assertEqual(text[2],'l      banner      l')
        self.assertEqual(text[3], "+" +"-"*18+"+")

    def test_width_v_margin_h_margin_modification(self):
        msg = "this is a banner"
        text = banner(msg,width=20,v_margin='l',h_margin='=')

        text = text.splitlines()

        self.assertEqual(len(text), 4)

        self.assertEqual(text[0], "+" +"="*18+"+")
        self.assertEqual(text[1],'l    this is a     l')
        self.assertEqual(text[2],'l      banner      l')
        self.assertEqual(text[3], "+" +"="*18+"+")

    def test_left_aligned_all_modifications(self):
        msg = "this is a left aligned banner"
        text = banner(msg,width=20,v_margin='l',h_margin='=',
                      align='left', padding =2)

        text = text.splitlines()

        self.assertEqual(len(text), 4)
        self.assertEqual(text[0], "+" +"="*18+"+")
        self.assertEqual(text[1],'l this is a left a l')
        self.assertEqual(text[2],'l ligned banner    l')
        self.assertEqual(text[3], "+" +"="*18+"+")

    def test_right_aligned_all_modifications(self):
        msg = "this is a right aligned banner"
        text = banner(msg,width=20,v_margin='l',h_margin='=',
                      align='right', padding =2)

        text = text.splitlines()

        self.assertEqual(len(text), 4)
        self.assertEqual(text[0], "+" +"="*18+"+")
        self.assertEqual(text[1],'l this is a right  l')
        self.assertEqual(text[2],'l   aligned banner l')
        self.assertEqual(text[3], "+" +"="*18+"+")

    def test_wrong_h_margin_int(self):
        msg = "this is a banner"
        with self.assertRaises(TypeError):
            banner(msg,h_margin=2)

    def test_wrong_h_margin_lenth(self):
        msg = "this is a banner"
        with self.assertRaises(ValueError):
            banner(msg,h_margin='22')

    def test_wrong_v_margin_int(self):
        msg = "this is a banner"
        with self.assertRaises(TypeError):
            banner(msg,v_margin=2)

    def test_wrong_v_margin_lenth(self):
        msg = "this is a banner"
        with self.assertRaises(ValueError):
            banner(msg,v_margin='22')

    def test_wrong_width_str(self):
        msg = "this is a banner"
        with self.assertRaises(TypeError):
            banner(msg,width='22')

    def test_wrong_padding_str(self):
        msg = "this is a banner"
        with self.assertRaises(TypeError):
            banner(msg,padding='22')

    def test_wrong_width_for_padding(self):
        msg = "this is a banner"
        with self.assertRaises(ValueError):
            banner(msg,width=5,padding=10)

class TestTitle(unittest.TestCase):

    def test_title_simple(self):
        msg = "this is a title"
        text = title(msg)

        text = text.splitlines()

        self.assertEqual(len(text), 1)
        self.assertEqual(text[0], "="*32 + msg + "="*33)

    def test_title_multi_line(self):
        msg = "this is a title\nthat is two lines\r\nand more"

        text = title(msg)

        msg = msg.splitlines()

        text = text.splitlines()

        self.assertEqual(len(text), 3)

        self.assertEqual(text[0], "="*32 + msg[0] + "="*33)
        self.assertEqual(text[1], "="*31 + msg[1] + "="*32)
        self.assertEqual(text[2], "="*36 + msg[2] + "="*36)

    def test_title_variable_length_multiple_line(self):
        msg = "this is a title\nthat is two lines\r\nand more"

        text = title(msg, 50)
        msg = msg.splitlines()
        text = text.splitlines()

        self.assertEqual(len(text), 3)

        self.assertEqual(text[0], "="*17 + msg[0] + "="*18)
        self.assertEqual(text[1], "="*16 + msg[1] + "="*17)
        self.assertEqual(text[2], "="*21 + msg[2] + "="*21)

    def test_really_long_title(self):
        msg = "1" * 80

        text = title(msg)

        text = text.splitlines()

        self.assertEqual(len(text), 2)

        self.assertEqual(text[0], "=" + "1" * 78 + "=")
        self.assertEqual(text[1], "="*39 + "1" * 2 + "="*39)

    def test_custom_title_wrap(self):
        msg = "1" * 80

        text = title(msg, 50)
        text = text.splitlines()

        self.assertEqual(len(text), 2)

        self.assertEqual(text[0], "=" + "1" * 48 + "=")
        self.assertEqual(text[1], "="*9 + "1" * 32 + "="*9)

    def test_another_really_long_title(self):
        msg = "1" * 68 + "2" * 30

        text = title(msg)

        text = text.splitlines()

        self.assertEqual(len(text), 2)

        self.assertEqual(text[0], "=" + "1" * 68 + '2' * 10 +"=")
        self.assertEqual(text[1], '='*30 + "2" * 20 + '='*30)

    def test_title_width_modification(self):
        msg = "this is a title"
        text = title(msg,width=21)

        text = text.splitlines()

        self.assertEqual(len(text), 1)

        self.assertEqual(text[0], "="*3 + 'this is a title' + "="*3)

    def test_title_padding_modification(self):
        msg = "this is a title that is long but not that long for "\
              "padding testing zz z zz zzz"

        text = title(msg,padding=8)
        text = text.splitlines()
        self.assertEqual(len(text), 2)

        self.assertEqual(text[0], "="*4 +\
                                  "this is a title that is long but not that "
                                  "long for padding testing zz z "\
                                  + "="*4)
        self.assertEqual(text[1], "="*37 + "zz zzz" + "="*37)

    def test_title_width_padding_modification(self):
        msg = "this is a title"
        text = title(msg,width=16,padding=6)

        text = text.splitlines()

        self.assertEqual(len(text), 2)

        self.assertEqual(text[0], "="*3 + "this is a " + "="*3)
        self.assertEqual(text[1], "="*5 + "title" + "="*6)

    def test_title_width_margin_modification(self):
        msg = "this is a title"
        text = title(msg,width=21,margin='-')

        text = text.splitlines()

        self.assertEqual(len(text), 1)

        self.assertEqual(text[0], "-"*3 + "this is a title" + "-"*3)

    def test_left_aligned(self):
        msg = "this is a left alinged title"
        text = title(msg,width=38,padding=2, align='left')

        text = text.splitlines()

        self.assertEqual(len(text), 1)

        self.assertEqual(text[0], "=" + "this is a left alinged title" + "="*9)

    def test_right_aligned(self):
        msg = "this is a right alinged title"
        text = title(msg,width=39,padding=2, align='right')

        text = text.splitlines()

        self.assertEqual(len(text), 1)

        self.assertEqual(text[0], "="*9 + "this is a right alinged title" + "=")

    def test_title_wrong_margin_int(self):
        msg = "this is a title"
        with self.assertRaises(TypeError):
            title(msg, margin=2)

    def test_title_wrong_margin_lenth(self):
        msg = "this is a title"
        with self.assertRaises(ValueError):
            title(msg, margin='22')

    def test_title_wrong_width_str(self):
        msg = "this is a title"
        with self.assertRaises(TypeError):
            title(msg, width='22')

    def test_title_wrong_padding_str(self):
        msg = "this is a title"
        with self.assertRaises(TypeError):
            title(msg, padding='22')

    def test_title_wrong_width_for_padding(self):
        msg = "this is a title"
        with self.assertRaises(ValueError):
            title(msg, width=5, padding=10)

class TestStrShortener(unittest.TestCase):
    def test_str_shortener_short_string_defaults(self):
        self.assertEqual(str_shortener("short_text"), "short_text")

    def test_str_shortener_long_string_defaults(self):
        self.assertEqual(str_shortener("a"*81), "a"*77 + "...")

    def test_str_shortener_limit(self):
        self.assertEqual(str_shortener("cut me here", 9), "cut me...")

    def test_str_shortener_subst(self):
        self.assertEqual(str_shortener("add numbers here:", 14, "123"),
                         "add numbers123")

    def test_str_shortener_shorter_limit_than_subst(self):
        self.assertEqual(str_shortener("abc", 1, "1234"), "abc")


class TestFileLength(unittest.TestCase):

    def test_get_unknown_file_length(self):
        self.assertEqual(get_file_length('/tmp/_unknown_file_name'), (0, 0))

    def test_get_empty_file_length(self):
        with NamedTemporaryFile(mode='w') as fil:
            self.assertEqual(get_file_length(fil.name), (0, 0))

    def test_get_file_length(self):
        with NamedTemporaryFile(mode='w') as fil:
            fil.write("First line\nSecond line\nThird line\n")
            fil.flush()
            self.assertEqual(get_file_length(fil.name), (34, 3))

class TestReportingLogFile(unittest.TestCase):

    def test_reporting_diff(self):
        with NamedTemporaryFile(mode='w') as fil:
            fil.write("First line\nSecond line\nThird line\n")
            snapshot1 = ReportingLogFile(fil)
            fil.write("Fourth line\nFifth line\n")
            snapshot2 = ReportingLogFile(fil)
            expected_region = FileRegion(
                begin_bytes = 34,
                size_bytes = 23,
                begin_lines = 3,
                size_lines = 2,
            )
            actual_region = snapshot2-snapshot1
            self.assertEqual(actual_region, expected_region)
            expected_summary = OrderedDict(
                name = snapshot1.basename,
                begin = actual_region.begin_bytes,
                size = actual_region.size_bytes,
                begin_lines = actual_region.begin_lines,
                size_lines = actual_region.size_lines)
            self.assertEqual(
                snapshot1.get_summary(actual_region), expected_summary)

    def test_reporting_diff_bad_type(self):
        with NamedTemporaryFile(mode='w') as fil1:
            fil1.write("File1 content")
            snapshot1 = ReportingLogFile(fil1)
            with self.assertRaisesRegex(TypeError,
                    'Cannot subtract a log file with type.*str'):
                snapshot1 - 'badsnapshot'

    def test_reporting_diff_not_same_file(self):
        with NamedTemporaryFile(mode='w') as fil1:
            fil1.write("File1 content")
            snapshot1 = ReportingLogFile(fil1)
            with NamedTemporaryFile(mode='w') as fil2:
                fil2.write("File2 content")
                snapshot2 = ReportingLogFile(fil2)

                with self.assertRaisesRegex(ValueError,
                        'Comparisons only supported on the same file\.'):
                    actual_region = snapshot2-snapshot1


if __name__ == '__main__': # pragma: no cover
    unittest.main()
