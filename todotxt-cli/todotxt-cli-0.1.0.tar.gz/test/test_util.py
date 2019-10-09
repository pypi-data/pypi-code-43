import unittest
from todotxt.util import validContext, validDate, validDone, validDue, validPriority, validProject, now, month, week, addday

class TestStringMethods(unittest.TestCase):

    def setUp(self):
        pass

    def test_project(self):
        self.assertTrue(validProject('+tutu'))
        self.assertFalse(validProject('+'))
        self.assertFalse(validProject('tutu'))
        self.assertFalse(validProject('@tutu'))
        self.assertFalse(validProject('+tutu titi'))

    def test_context(self):
        self.assertTrue(validContext('@tutu'))
        self.assertFalse(validContext('@'))
        self.assertFalse(validContext('tutu'))
        self.assertFalse(validContext('+tutu'))
        self.assertFalse(validContext('@tutu titi'))

    def test_done(self):
        self.assertTrue(validDone('x'))
        self.assertFalse(validDone(''))
        self.assertFalse(validDone('X'))
        self.assertFalse(validDone('tutu'))

    def test_priority(self):
        self.assertTrue(validPriority('A'))
        self.assertFalse(validPriority('a'))
        self.assertFalse(validPriority('AA'))
        self.assertFalse(validPriority('A B'))

    def test_date(self):
        self.assertTrue(validDate('2019-01-01'))
        self.assertFalse(validDate('2019/01/01'))
        self.assertFalse(validDate('01/01/2019'))
        self.assertFalse(validDate('19-01-01'))
        self.assertFalse(validDate('tutu'))
        self.assertFalse(validDate('2019-02-30'))

    def test_due(self):
        self.assertTrue(validDue('due:2019-01-01'))
        self.assertFalse(validDate('due:2019/01/01'))
        self.assertFalse(validDate('du:2019-01-01'))
        self.assertFalse(validDate('tutu'))

    def test_now(self):
        self.assertTrue(validDate(now()))

    def test_add(self):
        self.assertTrue(validDate(now()))

    def test_week(self):
        self.assertEqual(week('2019-10-01'),'2019-10-06')
        self.assertEqual(week('2019-10-06'),'2019-10-06')
        self.assertEqual(week('2019-09-30'),'2019-10-06')
        self.assertTrue(validDate(week()))

    def test_month(self):
        self.assertEqual(month('2019-10-01'),'2019-10-31')
        self.assertEqual(month('2019-10-06'),'2019-10-31')
        self.assertEqual(month('2019-09-30'),'2019-09-30')
        self.assertTrue(validDate(month()))

    def test_add_day(self):
        self.assertEqual(addday('2019-10-01',10),'2019-10-11')
        self.assertEqual(addday('2019-10-06',0),'2019-10-06')
        self.assertEqual(addday('2019-10-30', -1),'2019-10-29')
        self.assertEqual(addday(), now())

if __name__ == '__main__':
    unittest.main()