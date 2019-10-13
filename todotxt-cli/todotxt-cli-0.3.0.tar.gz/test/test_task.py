import unittest
from todotxt.task import Task

class TestStringMethods(unittest.TestCase):

    def setUp(self):
        pass

    def test_basic_one(self):
        t = Task("2018-09-03 2018-08-01 test task @context +project due:2019-01-01")
        self.assertEqual(t.due, '2019-01-01')
        self.assertEqual(t.projects, ['project',])
        self.assertEqual(t.contexts, ['context',])
        self.assertEqual(t.created, '2018-08-01')
        self.assertEqual(t.completed, '2018-09-03')
        self.assertEqual(t.txt, 'test task @context +project due:2019-01-01')

    def test_basic_two(self):
        t = Task("2018-08-01 test task @context +project due:2019-01-01")
        self.assertEqual(t.due, '2019-01-01')
        self.assertEqual(t.projects, ['project',])
        self.assertEqual(t.contexts, ['context',])
        self.assertEqual(t.created, '2018-08-01')
        self.assertEqual(t.completed, None)
        self.assertEqual(t.txt, 'test task @context +project due:2019-01-01')

    def test_basic_three(self):
        t = Task("test task @context +project due:2019-01-01")
        self.assertEqual(t.due, '2019-01-01')
        self.assertEqual(t.projects, ['project',])
        self.assertEqual(t.contexts, ['context',])
        self.assertEqual(t.created, None)
        self.assertEqual(t.completed, None)
        self.assertEqual(t.txt, 'test task @context +project due:2019-01-01')

    def test_basic_four(self):
        t = Task("test task +project due:2019-01-01")
        self.assertEqual(t.due, '2019-01-01')
        self.assertEqual(t.projects, ['project',])
        self.assertEqual(t.contexts, [])
        self.assertEqual(t.created, None)
        self.assertEqual(t.completed, None)
        self.assertEqual(t.txt, 'test task +project due:2019-01-01')

    def test_basic_five(self):
        t = Task("test task due:2019-01-01")
        self.assertEqual(t.due, '2019-01-01')
        self.assertEqual(t.projects, [])
        self.assertEqual(t.contexts, [])
        self.assertEqual(t.created, None)
        self.assertEqual(t.completed, None)
        self.assertEqual(t.txt, 'test task due:2019-01-01')

    def test_basic_six(self):
        t = Task("test task")
        self.assertEqual(t.due, None)
        self.assertEqual(t.projects, [])
        self.assertEqual(t.contexts, [])
        self.assertEqual(t.created, None)
        self.assertEqual(t.completed, None)
        self.assertEqual(t.txt, 'test task')

    def test_basic_seven(self):
        t = Task()
        self.assertEqual(t.due, None)
        self.assertEqual(t.projects, [])
        self.assertEqual(t.contexts, [])
        self.assertEqual(t.created, None)
        self.assertEqual(t.completed, None)
        self.assertEqual(t.txt, '')

    def test_append(self):
        t = Task("test task")
        t.append('fred')
        self.assertEqual(t.txt, 'test task fred')

    def test_remove_one(self):
        t = Task("one two three")
        t.remove('one')
        self.assertEqual(t.txt, 'two three')

    def test_remove_two(self):
        t = Task("one two three")
        t.remove('two')
        self.assertEqual(t.txt, 'one three')

    def test_remove_three(self):
        t = Task("one two three")
        t.remove('three')
        self.assertEqual(t.txt, 'one two')

    def test_remove_four(self):
        t = Task("one two three")
        t.remove('four')
        self.assertEqual(t.txt, 'one two three')

    def test_remove_thre(self):
        t = Task("one two three")
        t.remove('thre')
        self.assertEqual(t.txt, 'one two three')

    def test_projects(self):
        t = Task('my task')
        self.assertEqual(t.projects, [])
        t.append('+test')
        self.assertEqual(t.projects, ['test',])
        t.projects = ['tutu',]
        self.assertEqual(t.projects, ['tutu',])
        self.assertEqual(t.txt, 'my task +tutu')
        t.projects = ['tutu', 'tata']
        self.assertEqual(t.projects, ['tutu','tata'])
        self.assertEqual(t.txt, 'my task +tutu +tata')
        t.projects = ['tata', 'toto']
        self.assertEqual(t.projects, ['tata','toto'])
        self.assertEqual(t.txt, 'my task +tata +toto')

    def test_contexts(self):
        t = Task('my task')
        self.assertEqual(t.contexts, [])
        t.append('@test')
        self.assertEqual(t.contexts, ['test',])
        t.contexts = ['tutu',]
        self.assertEqual(t.contexts, ['tutu',])
        self.assertEqual(t.txt, 'my task @tutu')
        t.contexts = ['tutu', 'tata']
        self.assertEqual(t.contexts, ['tutu','tata'])
        self.assertEqual(t.txt, 'my task @tutu @tata')
        t.contexts = ['tata', 'toto']
        self.assertEqual(t.contexts, ['tata','toto'])
        self.assertEqual(t.txt, 'my task @tata @toto')

    def test_due(self):
        t = Task("test")
        t.due = "2019-01-01"
        self.assertEqual(t.due, '2019-01-01')
        self.assertEqual(t.txt, 'test due:2019-01-01')
        t.due = "2019-01-02"
        self.assertEqual(t.due, '2019-01-02')
        self.assertEqual(t.txt, 'test due:2019-01-02')
        t.due = None
        self.assertEqual(t.due, None)
        self.assertEqual(t.txt, 'test')

    def test_created(self):
        t = Task("test")
        t.created = "2019-01-01"
        self.assertEqual(t.created, '2019-01-01')
        t.created = "2019-01-02"
        self.assertEqual(t.created, '2019-01-02')

    def test_completed(self):
        t = Task("test")
        t.completed = "2019-01-01"
        self.assertEqual(t.completed, '2019-01-01')
        t.completed = "2019-01-02"
        self.assertEqual(t.completed, '2019-01-02')

    def test_priority(self):
        t = Task("(A) test")
        self.assertEqual(t.priority, 'A')
        t.priority = 'B'
        self.assertEqual(t.priority, 'B')
        t.priority = 'a'
        self.assertEqual(t.priority, 'B')

    def test_str(self):
        t = Task("")
        t.txt = "test"
        self.assertEqual(str(t), 'test')
        t.completed = "2018-01-02"
        self.assertEqual(str(t), 'test')
        t.created = '2018-01-01'
        self.assertEqual(str(t), '2018-01-02 2018-01-01 test')
        t.completed = None
        self.assertEqual(str(t), '2018-01-01 test')
        t.priority = 'B'
        self.assertEqual(str(t), '(B) 2018-01-01 test')
        t.done = True
        self.assertEqual(str(t), 'x (B) 2018-01-01 test')
        
    def test_copy(self):
        t = Task("2018-09-03 2018-08-01 test task @context +project due:2019-01-01")
        tt = Task(str(t))
        self.assertEqual(str(t), str(tt))
        self.assertTrue(t == tt)
        tt.due = "2019-01-02"
        self.assertFalse(t == tt)
         
    def test_sort(self):
        tone = Task("2018-09-03 2018-08-01 test task @context +project due:2019-01-02")
        ttwo = Task(str(tone))
        ttwo.due = "2019-01-03"
        tthree = Task(str(tone))
        tthree.due = "2019-01-01"
        l = [tone, ttwo, tthree]
        l.sort()
        self.assertEqual(l[0], tthree)
        tthree.due = '2019-01-04'
        l.sort()
        self.assertEqual(l[0], tone)
        tthree.due = tone.due
        tthree.created = '2017-01-01'
        l.sort()
        self.assertEqual(l[0], tthree)
        tfourth = Task("test")
        l.append(tfourth)
        l.sort()
        self.assertEqual(l[3], tfourth)
        ttwo.due = tone.due
        ttwo.priority = 'B'
        l=[tone, ttwo]
        l.sort()
        self.assertEqual(l[0], ttwo)
        tone.priority = 'A'
        l.sort()
        self.assertEqual(l[0], tone)

    def test_repeat(self):
        t = Task("test")
        self.assertEqual(t.repeat, None)
        t.repeat = "3d"
        self.assertEqual(t.repeat, '3d')
        self.assertEqual(t.txt, 'test repeat:3d')
        t.repeat = None
        self.assertEqual(t.repeat, None)
        self.assertEqual(t.txt, 'test')                
 
    def test_next_repeat(self):
        t = Task("test")
        self.assertEqual(t.next_repeat, None)
        t.repeat = "3d"
        t.due = "2019-01-01"
        self.assertEqual(t.next_repeat, '2019-01-04')
        t.repeat = "3w"
        self.assertEqual(t.next_repeat, '2019-01-22')
        t.repeat = "3m"
        self.assertEqual(t.next_repeat, '2019-04-01')
        t.repeat = "3y"
        self.assertEqual(t.next_repeat, '2022-01-01')
 
if __name__ == '__main__':
    unittest.main()