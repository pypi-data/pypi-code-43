import unittest
from todotxt.util import validContext, validDate, validDone, validDue, validPriority, validProject, now, month, week, addday, validRepeat, addmonth, addyear

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

    def test_repeat(self):
        self.assertTrue(validRepeat('repeat:3d'))
        self.assertTrue(validRepeat('repeat:3m'))
        self.assertTrue(validRepeat('repeat:3y'))
        self.assertTrue(validRepeat('repeat:3w'))
        self.assertFalse(validRepeat('repeat:3a'))
        self.assertFalse(validRepeat('repeat:3'))

    def test_add_month(self):
        self.assertEqual(addmonth('2019-01-01',10),'2019-11-01')
        self.assertEqual(addmonth('2019-12-06',2),'2020-02-06')
        self.assertEqual(addmonth('2019-03-31',1),'2019-04-30')
 
    def test_add_year(self):
        self.assertEqual(addyear('2019-01-01',10),'2029-01-01')
        
if __name__ == '__main__':
    unittest.main()