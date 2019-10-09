import unittest
from todotxt.task import Task, Tasks

def returnTrue(obj):
    return True

def returnIdOne(obj):
    if obj.id == 1:
        return True
    return False

class TestStringMethods(unittest.TestCase):

    def setUp(self):
        pass

    def test_basic(self):
        l = Tasks()
        t = Task("2018-09-03 2018-08-01 test task @context +project due:2019-01-01")
        l.append(t)
        l.append(Task(str(t)))
        self.assertEqual(len(l), 2)
        self.assertRaises(ValueError, l.append, "test")

    def test_filter_one(self):
        l = Tasks()
        t = Task("2018-09-03 2018-08-01 test task @context +project due:2019-01-01")
        l.append(t)
        l.append(Task(str(t)))
        f = l.filter()
        self.assertEqual(len(f), 2)
 
    def test_filter_two(self):
        l = Tasks()
        t = Task("2018-09-03 2018-08-01 test task @context +project due:2019-01-01", 0)
        l.append(t)
        l.append(Task(str(t), 1))
        f = l.filter(id=1)
        self.assertEqual(len(f), 1)
 
    def test_filter_three(self):
        l = Tasks()
        t = Task("2018-09-03 2018-08-01 test task @context +project due:2019-01-01", 0)
        l.append(t)
        l.append(Task(str(t), 1))
        l.append(Task(str(t), 2))
        l.filter(id=2)[0].due = '2019-08-01'
        l.filter(id=2)[0].done = True
        l.filter(id=2)[0].created = '2018-01-01'
        l.filter(id=2)[0].completed = '2018-01-02'
        l.filter(id=2)[0].append('@test')       
        self.assertEqual(len(l.filter(due='2019-01-01')), 2)
        self.assertEqual(len(l.filter(due='2019-08-01')), 1)
        self.assertEqual(len(l.filter(due='2099-12-31')), 0)
        self.assertEqual(len(l.filter(due='2018-01-01..2019-02-01')), 2)
        self.assertEqual(len(l.filter(due='..2019-02-01')), 2)
        self.assertEqual(len(l.filter(due='2019-02-01..')), 1)
        self.assertEqual(len(l.filter(due='2019-02-01..2099-01-01')), 1)
        self.assertEqual(len(l.filter(done=False)), 2)
        self.assertEqual(len(l.filter(done=True)), 1)
        self.assertEqual(len(l.filter(created='2018-08-01')), 2)
        self.assertEqual(len(l.filter(created='2018-01-01')), 1)
        self.assertEqual(len(l.filter(created='2099-12-31')), 0)
        self.assertEqual(len(l.filter(created='2018-07-01..2020-01-01')), 2)
        self.assertEqual(len(l.filter(created='2018-07-01..')), 2)
        self.assertEqual(len(l.filter(created='..2018-07-01')), 1)
        self.assertEqual(len(l.filter(completed='2018-09-03')), 2)
        self.assertEqual(len(l.filter(completed='2018-01-02')), 1)
        self.assertEqual(len(l.filter(completed='2099-12-31')), 0)
        self.assertEqual(len(l.filter(completed='2018-09-01..2018-10-01')), 2)
        self.assertEqual(len(l.filter(completed='2018-09-01..')), 2)
        self.assertEqual(len(l.filter(completed='..2018-09-01')), 1)
        self.assertEqual(len(l.filter(txt='@test')), 1)
        self.assertEqual(len(l.filter(txt='test')), 3)
        self.assertEqual(len(l.filter(txt='tutu')), 0)
        self.assertEqual(len(l.filter(txt='@test test')), 1)
  
    def test_next_id(self):
        l = Tasks()
        self.assertEqual(l._next_id, 0)
        t = Task("2018-09-03 2018-08-01 test task @context +project due:2019-01-01")
        l.append(t)
        self.assertEqual(l._next_id, 1)
        l.append(Task(str(t), 1))
        self.assertEqual(l._next_id, 2)
        l.append(Task(str(t), 11))
        self.assertEqual(l._next_id, 12)
        l.append(Task(str(t), 9))
        self.assertEqual(l._next_id, 12)
    
    def test_get_id(self):
        l = Tasks()
        t = Task("2018-09-03 2018-08-01 test task @context +project due:2019-01-01")
        l.append(t)
        l.append(Task(str(t), 1))
        self.assertEqual(0, l.get_id(0).id)
        self.assertEqual(1, l.get_id(1).id)
        self.assertEqual(None, l.get_id(2))
        

         
if __name__ == '__main__':
    unittest.main()