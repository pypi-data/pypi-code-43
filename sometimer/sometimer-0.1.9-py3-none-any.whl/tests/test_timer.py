import logging
import unittest

from time import sleep
from datetime import timedelta

from sometimer.sometimer import timer
from sometimer.sometimer import Timer
from sometimer.sometimer import Checkpoint
from sometimer.sometimer import time_this_method


logger = logging.getLogger('Test Timer')


class TestTimerMethods(unittest.TestCase):

    def test_import(self):
        from sometimer.sometimer import timer
        self.assertEqual(type(timer), Timer)

    def test_call_doesnt_crash(self):
        timer.restart()
        for _ in range(10):
            actual = timer()
            sleep(0.05)
            logger.critical(actual)

    def test_singleton_property_for_class_creation(self):
        timer.restart()
        timer.new_checkpoint()
        timer.new_checkpoint(name='two')

        number_of_checkpoints = len(timer._checkpoints)
        _start_checkpoint = timer._start_checkpoint
        _current_checkpoint = timer._current_checkpoint

        _timer = Timer()

        self.assertEqual(3, len(_timer._checkpoints))
        self.assertEqual(number_of_checkpoints, len(_timer._checkpoints))
        self.assertEqual(_start_checkpoint, _timer._start_checkpoint)
        self.assertEqual(_current_checkpoint, _timer._current_checkpoint)
        self.assertTrue(_timer._start_checkpoint != _timer._current_checkpoint)
        self.assertTrue(_timer._start_checkpoint.duration() < timedelta(milliseconds=500))

    def test_restart(self):
        timer.new_checkpoint()
        timer.new_checkpoint(name='two')
        timer.new_checkpoint()
        sleep(1)
        timer.restart()
        self.assertTrue(len(timer._checkpoints) == 1)
        self.assertIsNotNone(timer._start_checkpoint)
        self.assertIsNone(timer._current_checkpoint)
        self.assertTrue(timer._start_checkpoint.duration() < timedelta(milliseconds=500))

    def test_one_checkpoint(self):
        timer.restart()
        _start_checkpoint_before = timer._start_checkpoint
        _current_checkpoint_before = timer._current_checkpoint
        number_of_checkpoints_before = len(timer._checkpoints)

        logger.critical(f'{self.test_one_checkpoint.__name__}\n')

        for _ in range(3):
            logger.critical(timer())
            sleep(0.1)

        checkpoint = timer.new_checkpoint(name='checkpoint_0')

        for _ in range(3):
            logger.critical(timer())
            sleep(0.1)

        _start_checkpoint_after = timer._start_checkpoint
        _current_checkpoint_after = timer._current_checkpoint
        number_of_checkpoints_after = len(timer._checkpoints)

        self.assertEqual(number_of_checkpoints_before, 1, f'expected 1, received {number_of_checkpoints_before} checkpoints')
        self.assertEqual(number_of_checkpoints_after, 2, f'expected 2, received {number_of_checkpoints_after} checkpoints')
        self.assertTrue(_start_checkpoint_before == _start_checkpoint_after, '_start_checkpoint changed')
        self.assertIsNone(_current_checkpoint_before, 'mismatch between first checkpoints')
        self.assertIsNotNone(_start_checkpoint_before, 'mismatch between first checkpoints')
        self.assertTrue(_start_checkpoint_after != _current_checkpoint_after, 'current checkpoint or start checkpoint changed unexpectedly')
        self.assertEqual(type(checkpoint), Checkpoint, '.new_checkpoint() does not return the Checkpoint')

    def test_many_checkpoints(self):
        pass

    def test_checkpoints_with_no_names(self):
        pass

    def test_string_representation(self):
        pass

    def test_summary(self):
        timer.restart()

        timer.new_checkpoint(name='checkpoint_0')
        sleep(0.3)
        timer.new_checkpoint(name='checkpoint_1')
        sleep(0.3)
        timer.new_checkpoint(name='victory lap')
        sleep(13)

        summary = timer.summary()
        logger.critical(f'{self.test_summary.__name__}\n')
        logger.critical(summary)

    def test_end_checkpoint(self):
        timer.restart()

        timer.new_checkpoint(name='checkpoint_0')
        timer.new_checkpoint(name='checkpoint_1')
        sleep(2)
        timer.end_checkpoint()
        sleep(2)
        final_time = timer.duration().total_seconds()
        self.assertTrue(final_time > 3, 'end_checkpoint affects timers endtime')

    #
    # DECORATOR
    #
    #
    #
    def test_decorator_one_checkpoint(self):
        timer.restart()
        _start_checkpoint_before = timer._start_checkpoint
        _current_checkpoint_before = timer._current_checkpoint
        number_of_checkpoints_before = len(timer._checkpoints)

        a_timed_function()

        _start_checkpoint_after = timer._start_checkpoint
        _current_checkpoint_after = timer._current_checkpoint
        number_of_checkpoints_after = len(timer._checkpoints)

        self.assertEqual(number_of_checkpoints_before, 1,
                         f'expected 1, received {number_of_checkpoints_before} checkpoints')
        self.assertEqual(number_of_checkpoints_after, 2,
                         f'expected 2, received {number_of_checkpoints_after} checkpoints')
        self.assertTrue(_start_checkpoint_before == _start_checkpoint_after, '_start_checkpoint changed')
        self.assertIsNotNone(_start_checkpoint_before, 'mismatch between first checkpoints')
        self.assertIsNone(_current_checkpoint_before, 'mismatch between first checkpoints')
        self.assertTrue(_start_checkpoint_after != _current_checkpoint_after,
                        'current checkpoint or start checkpoint changed unexpectedly')
        self.assertIsNone(_current_checkpoint_after, 'created checkpoint was not ended properly')

    def test_decorator_many_checkpoints(self):
        named_and_timed_function = 'user-specified-name'

        timer.restart()
        timer.new_checkpoint(name='checkpoint_0')
        a_timed_function()
        a_timed_function_with_name()
        timer.new_checkpoint(name='checkpoint_1')

        checkpoints = list(c for c in timer._checkpoints.values())

        self.assertEqual(len(timer._checkpoints), 5, 'incorrect amount of checkpoints created')
        self.assertEqual(checkpoints[2][0].name, 'a_timed_function', 'incorrectly named checkpoint when not passing a `name`')
        self.assertEqual(checkpoints[3][0].name, named_and_timed_function, 'incorrectly named checkpoiont when passing a `name`')

    def test_decorator_one_checkpoint_with_kwargs(self):
        timer.restart()
        _start_checkpoint_before = timer._start_checkpoint
        _current_checkpoint_before = timer._current_checkpoint
        number_of_checkpoints_before = len(timer._checkpoints)

        a_timed_function_with_kwargs()

        _start_checkpoint_after = timer._start_checkpoint
        _current_checkpoint_after = timer._current_checkpoint
        number_of_checkpoints_after = len(timer._checkpoints)

        self.assertEqual(number_of_checkpoints_before, 1,
                         f'expected 1, received {number_of_checkpoints_before} checkpoints')
        self.assertEqual(number_of_checkpoints_after, 2,
                         f'expected 2, received {number_of_checkpoints_after} checkpoints')
        self.assertTrue(_start_checkpoint_before == _start_checkpoint_after, '_start_checkpoint changed')
        self.assertIsNotNone(_start_checkpoint_before, 'mismatch between first checkpoints')
        self.assertIsNone(_current_checkpoint_before, 'mismatch between first checkpoints')
        self.assertTrue(_start_checkpoint_after != _current_checkpoint_after,
                        'current checkpoint or start checkpoint changed unexpectedly')
        self.assertEqual(_current_checkpoint_after, None, 'created checkpoint was not ended properly')

    def test_decorator_many_checkpoints_with_kwargs(self):
        timer.restart()
        timer.new_checkpoint(name='checkpoint_0')
        a_timed_function_with_kwargs()
        a_timed_function_with_name_and_kwargs()
        timer.new_checkpoint(name='checkpoint_1')

        checkpoints = list(c for c in timer._checkpoints.values())
        self.assertEqual(len(timer._checkpoints), 5, 'incorrect amount of checkpoints created')
        self.assertEqual('a_timed_function_with_kwargs', checkpoints[2][0].name, 'incorrectly named checkpoint when not passing a `name`')
        self.assertEqual('user-specified-name', checkpoints[3][0].name, 'incorrectly named checkpoiont when passing a `name`')

    def test_decorator_one_checkpoint_with_args(self):
        timer.restart()
        _start_checkpoint_before = timer._start_checkpoint
        _current_checkpoint_before = timer._current_checkpoint
        number_of_checkpoints_before = len(timer._checkpoints)

        a_timed_function_with_args(1, b=2)

        _start_checkpoint_after = timer._start_checkpoint
        _current_checkpoint_after = timer._current_checkpoint
        number_of_checkpoints_after = len(timer._checkpoints)

        self.assertEqual(number_of_checkpoints_before, 1,
                         f'expected 1, received {number_of_checkpoints_before} checkpoints')
        self.assertEqual(number_of_checkpoints_after, 2,
                         f'expected 2, received {number_of_checkpoints_after} checkpoints')
        self.assertTrue(_start_checkpoint_before == _start_checkpoint_after, '_start_checkpoint changed')
        self.assertIsNotNone(_start_checkpoint_before, 'mismatch between first checkpoints')
        self.assertIsNone(_current_checkpoint_before, 'mismatch between first checkpoints')
        self.assertTrue(_start_checkpoint_after != _current_checkpoint_after,
                        'current checkpoint or start checkpoint changed unexpectedly')
        self.assertEqual(_current_checkpoint_after, None, 'created checkpoint was not ended properly')

    def test_decorator_many_checkpoints_with_args(self):
        named_and_timed_function = 'user-specified-name'

        timer.restart()
        timer.new_checkpoint(name='checkpoint_0')
        a_timed_function_with_args(1, b=2)
        a_timed_function_with_name_and_args(1, b=2)
        timer.new_checkpoint(name='checkpoint_1')

        logger.critical(f'{self.test_decorator_many_checkpoints.__name__}:\n')
        logger.critical(timer.summary())

        for checkpoint in timer._checkpoints.values():
            logger.critical(f'{checkpoint[0].name}')

        checkpoints = list(c for c in timer._checkpoints.values())
        self.assertEqual(len(timer._checkpoints), 5, 'incorrect amount of checkpoints created')
        self.assertEqual(checkpoints[2][0].name, 'a_timed_function_with_args', 'incorrectly named checkpoint when not passing a `name`')
        self.assertEqual(checkpoints[3][0].name, named_and_timed_function, 'incorrectly named checkpoiont when passing a `name`')

    def test_multiple_count(self):
        timer.restart()
        timer.new_checkpoint('mercury')
        timer.new_checkpoint('venus')
        timer.new_checkpoint('tellus')
        timer.new_checkpoint('mars')
        timer.new_checkpoint('mercury')
        timer.new_checkpoint('mercury')
        timer.new_checkpoint('mars')
        logger.critical(timer.summary())

        cs = timer._checkpoints.summary()

        logger.critical(cs.keys())

        counts = [v['count'] for v in cs.values()]

        self.assertIn(1, counts)
        self.assertIn(2, counts)
        self.assertIn(3, counts)
        self.assertGreater(4, max(counts))

    def test_name_as_arg(self):
        try:
            @time_this_method('no kwarg, only arg')
            def arbitrary_method_name():
                pass
        except AttributeError as e:
            self.fail(f'unable to create method using `@time_this_method("no kwarg, only arg")`: {e}')


@time_this_method
def a_timed_function():
    sleep(0.1)
    return


@time_this_method(name='user-specified-name')
def a_timed_function_with_name():
    sleep(0.1)
    return


@time_this_method
def a_timed_function_with_kwargs(b=2):
    sleep(0.1)
    return


@time_this_method(name='user-specified-name')
def a_timed_function_with_name_and_kwargs(b=2):
    sleep(0.1)
    return


@time_this_method
def a_timed_function_with_args(a, b=2):
    sleep(0.1)
    return


@time_this_method(name='user-specified-name')
def a_timed_function_with_name_and_args(a, b=2):
    sleep(0.1)
    return


if __name__ == '__main__':
    unittest.main()
