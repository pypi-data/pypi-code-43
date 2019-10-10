"""
.. module:: models
   :synopsis: Core data structure models
"""
import abc
from bamboo_lib.logger import logger
from pathos.multiprocessing import ProcessPool
from bamboo_lib import helpers
from collections.abc import Iterable

STANDARD = 'standard'
ITERATOR = 'iterator'
ITERATOR_COLLECTOR = 'iterator-collector'
END_ITERATOR = 'enditerator'
END_ITERATOR_COLLECTOR = 'enditerator-collector'


class BasePipeline(object):
    """
    BasePipeline is the abstract base class that all pipelines must extend.

    .. note::

       You must override the methods of:
         * :func:`~BasePipeline.pipeline_id`.
         * :func:`~BasePipeline.name`
         * :func:`~BasePipeline.description`
         * :func:`~BasePipeline.website`
         * :func:`~BasePipeline.run`
    """

    __metaclass__ = abc.ABCMeta

    @staticmethod
    @abc.abstractmethod
    def validate_params(params):
        return True

    @staticmethod
    @abc.abstractmethod
    def pipeline_id():
        """
        :returns: `str` that uniquely identifies the pipeline.
        """
        raise NotImplementedError("Please implement the pipeline_id() method")

    @staticmethod
    @abc.abstractmethod
    def name():
        """
        :returns: `str` a human-readable name describing the pipeline.
        """
        raise NotImplementedError("Please implement the name() method")

    @staticmethod
    @abc.abstractmethod
    def description():
        """
        :returns: `str` description of the pipeline.
        """
        raise NotImplementedError("Please implement the description() method")

    @staticmethod
    @abc.abstractmethod
    def params():
        """
        :returns: `list` containing :class:`.Parameter` objects.
        """
        raise NotImplementedError("Please implement the params() method")

    @classmethod
    def parameter_list(cls):
        return cls.params()

    @staticmethod
    @abc.abstractmethod
    def website():
        raise NotImplementedError("Please implement the website() method")

    @staticmethod
    def run(params_dict, **kwargs):
        raise NotImplementedError("Please implement the run() method")

    @staticmethod
    def fill_in_default_params(params_obj_list, params_dict):
        """
        :param params_obj_list: `list` of all possible parameter objects.
        :param params_dict: `dict` of key-value pairs of input parameters.
        :returns: `dict` of parameter values with any missing keys added with their default values.
        """
        if not params_dict:
            params_dict = {}
        for param_obj in params_obj_list:
            if param_obj.name not in params_dict and hasattr(param_obj, "default_value"):
                params_dict[param_obj.name] = param_obj.default_value
        return params_dict


class LoopHelper(object):
    """The LoopHelper class is a helper class to facilitate creating loopable pipelines with the EasyPipeline.
    The `iter_step` parameter should return an iterable object and the `sub_steps` should be a list of steps that
    should be executed for each iteration through the `iter_step`.

    :param iter_step: A `PipelineStep` that returns an iterable.
    :param sub_steps: A list of `PipelineSteps` to be executed for each iteration of the `iter_step`.

    .. code-block:: python

        # Example usage inside an EasyPipeline
        # note that the `iter_step` will return an iterator
        # and the sub_steps will be excecuted for each item in the iterator of `iter_step`.
        @staticmethod
        def steps(params):
           get_data_step = GetDataStep()
           unzip_step = UnzipStep(pattern=r"\.csv$")
           xform_step = TransformStep1()
           return [get_data_step, LoopHelper(iter_step=unzip_step, sub_steps=[xform_step])]

    """
    def __init__(self, iter_step, sub_steps):
        self.iter_step = iter_step
        self.sub_steps = sub_steps


class EasyPipeline(BasePipeline):
    """
    EasyPipeline is a simple implementation of the BasePipeline class to reduce the boilerplate
    needed for setting up a new Bamboo pipeline.

    The only method strictly required is the steps static method. Each implementation of EasyPipeline should
    create a steps method that returns a list of `PipelineStep`. If your pipeline accepts parameters,
    you will also need to override the :func:`~EasyPipeline.parameter_list` static class method which returns
    a list of acceptable parameters for the pipeline.

    By default, EasyPipeline only supports linear pipelines (i.e. those without foreach loops). Though you may override the
    :func:`~EasyPipeline.run` method to customize this behavior if needed in the meantime.

    .. note::

       You must override the method:
         * :func:`~EasyPipeline.steps`.

    .. code-block:: python

        from bamboo_lib.models import Parameter, EasyPipeline, PipelineStep
        from bamboo_lib.steps import DownloadStep, LoadStep

        class MySimplePipeline(EasyPipeline):
            @staticmethod
            def parameter_list():
                return [Parameter("year", dtype=int)]

            @staticmethod
            def steps():
                dl_step = DownloadStep(connector="my-data", connector_path=__file__)
                xform_step = TransformStep()
                load_step = LoadStep()
                return [dl_step, xform_step, load_step]
    """
    @classmethod
    def name(cls):
        return cls.__name__

    @staticmethod
    def pipeline_id():
        return EasyPipeline.name()

    @staticmethod
    def parameter_list():
        """
        :returns: `list` of `Parameter` objects that define the possible inputs to the pipeline.
        """
        return []

    @staticmethod
    def description():
        return ""

    @staticmethod
    def website():
        return "N/A"

    @staticmethod
    @abc.abstractmethod
    def steps(params):
        """
        :param params: The original parameters passed into the pipeline.
        :returns: `list` of `PipelineStep` objects that define the steps to be executed for the pipeline.
        """
        raise NotImplementedError("Please make sure your subclass of EasyPipeline implements the steps() function")

    @classmethod
    def run(cls, params, **kwargs):
        params = BasePipeline.fill_in_default_params(cls.parameter_list(), params)
        pipeline = AdvancedPipelineExecutor(params, is_easy_pipeline=True)
        for step in cls.steps(params):
            if isinstance(step, ParallelizedStep):
                pipeline = pipeline.parallelized(step)
            elif isinstance(step, LoopHelper):
                pipeline = pipeline.foreach(step.iter_step)
                for my_step in step.sub_steps:
                    pipeline = pipeline.next(my_step)
                pipeline = pipeline.endeach()
            else:
                pipeline = pipeline.next(step)
        return pipeline.run_pipeline()


class Parameter(object):
    """
    A Parameter represents an input to a pipeline. In general, any value for a pipeline that
    should be user-configurable should be a parameter.

      :param name: is a `str` describing the parameter.
      :param dtype: is an `object` representing the type of the parameter (e.g. `int`, `str`).
      :param options: represents a `list` of values that are valid for the parameter.
      :param allow_multiple: is a `bool` whether in a user-interface users can select multiple values for this parameter.
      :param source: represents a `str`.
      :param default_value: A default value to set for the parameter.
      :param required: indicates if the parameter must be specified.
    """
    def __init__(self, name, dtype, options=None, allow_multiple=False, label="", source=None, default_value=None,
                 required=False):
        """

        """
        self.name = name
        self.dtype = dtype
        self.options = options
        self.allow_multiple = allow_multiple
        self.label = label
        self.source = source
        self.default_value = default_value
        self.required = required

    def parse_value(self, v):
        if self.dtype is str or not self.dtype:
            return v  # TODO expand OS environment variables / paths?
        if self.dtype is bool and not v:
            return True
        elif self.dtype is not bool and not v:
            raise ValueError("You must set a value for a non-bool parameter e.g. --{}=VALUE".format(self.name))
        if v in ["True", "true"]:
            return True
        elif v in ["False", "false"]:
            return False
        if v.isdecimal():
            try:
                return int(v)
            except ValueError:
                return float(v)
        return v

class LinearPipelineExecutor(object):
    def __init__(self, steps=None, params=None):
        self.steps = steps
        self.params = params

    def set_steps(self, steps):
        self.steps = steps

    # Run step, save output, move next
    def run_pipeline(self):
        prev_result = None
        # have pipeline catch then rethrow error
        logger.info("==== Pipeline run started...")
        for step in self.steps:
            logger.info("Starting step %s ....", str(step.__class__))
            result = step.run_step(prev_result, self.params)
            logger.info("Ending step %s ....", str(step.__class__))
            prev_result = result
        logger.info("==== Pipeline run completed!")


class GraphPipelineExecutor(object):
    def __init__(self, for_each=None, do_steps=None, params=None):
        self.for_each = for_each
        self.do_steps = do_steps
        self.params = params

    # Run step, save output, move next
    def run_pipeline(self):
        logger.info("==== Pipeline run started...")
        count = 1
        for chunk_result in self.for_each.run_step(None, self.params):
            logger.info("Starting pass {}".format(count))
            prev_result = chunk_result
            for step in self.do_steps:
                logger.info("Starting step %s ....", str(step.__class__))
                result = step.run_step(prev_result, self.params)
                logger.info("Ending step %s ....", str(step.__class__))
                prev_result = result
            count += 1
        logger.info("==== Pipeline run completed!")


class PipelineStep(object):
    """
    This class represents the basic unit of work in a pipeline. The outputs
    from steps are chained together, such that the output of step 1 is the input to step 2 and so on.

    Any keyword arguments passed to the `PipelineStep` constructor will be set as
    attributes in the object.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)

    def set_pipeline_results_ref(self, pipeline_results):
        self.pipeline_results = pipeline_results

    def get_pipeline_results_ref(self):
        return self.pipeline_results

    @abc.abstractmethod
    def run_step(self, prev_result, params):
        """
        :param prev_result: The output of the previous step in the pipeline.
        :param params: The original parameters passed into the pipeline.

        :returns: An `object` that is the result of the processing of this step.
        """


class ParallelizedStep(PipelineStep):
    """
    This class represents a special type of step that can be executed in parallel.

    :param num_processes: The number of parallel process workers to allow.
    """
    def __init__(self, num_processes=5, **kwargs):
        self.num_processes = num_processes
        super().__init__(**kwargs)

    def get_num_processes(self, params=None):
        """Returns the maximum number of process to be used by the multiprocessing pool"""
        return self.num_processes

    @abc.abstractmethod
    def parallel_param_list(self, params):
        """
        :param params: The global params `dict` for the pipeline.
        :returns: A list of dicts `dict` containing the list of parameters that should be passed to each step. These parameters will overwrite any global pipeline parameters with the same name.
        """


class Node(object):
    def __init__(self, step, is_iterator=False):
        self.step = step
        self.next = None
        self.prev = None
        self.children = None
        self.is_iterator = is_iterator
        self.iterator = None
        self.started = False


class EndNode(Node):
    def __init__(self):
        self.next = None
        self.prev = None
        self.is_iterator = False


class ComplexPipelineExecutor(object):
    def __init__(self, params=None):
        self.execution_plan = []
        self.params = params
        # self.pointer = None
        self.root = None
        self.pointer = None

    def insert(self, head, node_to_add):
        if not self.root and not head:
            self.root = node_to_add
        elif head.next:
            return self.insert(head.next, node_to_add)
        else:
            head.next = node_to_add
            node_to_add.prev = head
        self.pointer = node_to_add
        return node_to_add

    def next(self, step):
        node = Node(step)
        self.insert(self.root, node)
        return self

    def foreach(self, step):
        node = Node(step, is_iterator=True)
        self.insert(self.root, node)
        return self

    def endeach(self):
        node = EndNode()
        self.insert(self.root, node)
        return self

    def __str__(self):
        return str(self.execution_plan)

    def run_pipeline(self):
        return self.run_pipeline_helper(self.root, None, stack=[], history=[])

    def run_pipeline_helper(self, curr_node, prev_result, stack=None, history=None):
        if not curr_node:
            logger.debug("Done.")
            return prev_result
        elif curr_node.is_iterator and not curr_node.started:
            iterator = curr_node.step.run_step(prev_result, self.params)
            # print "ITERATOR CREATION", iterator
            stack.insert(0, [iterator, curr_node])
            curr_node.started = True
            return self.run_pipeline_helper(curr_node.next, next(iterator), stack=stack, history=history)
        elif curr_node.is_iterator and curr_node.started:
            try:
                # logger.debug("Refreshing iterator...")
                iterator, target_node = stack[0]
                # refresh children iterators
                hiterator, htarget_node = history.pop(0)
                hiterator = htarget_node.step.run_step(prev_result, self.params)
                stack.insert(0, [hiterator, htarget_node])
                return self.run_pipeline_helper(curr_node.next, next(hiterator), stack=stack, history=history)
            except StopIteration:
                raise Exception("TODO ... not yet implemented!")

        elif isinstance(curr_node, EndNode):

            iterator, target_node = stack[0]
            # logger.debug("Running ITERATOR" + str(iterator))
            try:
                return self.run_pipeline_helper(target_node.next, next(iterator), stack=stack, history=history)
            except StopIteration:
                old_node = stack.pop(0)
                history.insert(0, old_node)

                # logger.debug("ITERATOR EXHAUSTED " + str(iterator))
                if stack:
                    iterator, target_node = stack[0]
                    # if there's a parent iterator, go to that, otherwise
                    # continue on...
                return self.run_pipeline_helper(curr_node.next, prev_result, stack=stack, history=history)
        else:
            # simple movement
            prev_result = curr_node.step.run_step(prev_result, self.params)
            return self.run_pipeline_helper(curr_node.next, prev_result, stack=stack, history=history)


class AdvancedPipelineExecutor(BasePipeline):
    """AdvancedPipelineExecutor is the standard pipeline runner that most applications should utilize.

    Examples:
        Pipelines are passed dictionaries with key-value pairs for their parameters. Depending on the pipeline's `param` function,
        these raw values will then get parsed and validated into structured values. To assemble the pipeline,
        create a new AdvancedPipelineExecutor object passing in the raw dictionary. Using `next` you can specify the order in which
        the steps will run. Note that execution does not start until `run_pipeline` is called.

        For more information on creating steps, see :class:`.PipelineStep`.

        .. code-block:: python

           pipeline = AdvancedPipelineExecutor(raw_dict)
           pipeline = pipeline.next(extract_step).next(transform_step).next(load_step)
           pipeline.run_pipeline()
    """
    def __init__(self, params=None, is_easy_pipeline=False):
        self.execution_plan = []
        if not is_easy_pipeline:
            params = BasePipeline.fill_in_default_params(self.parameter_list(), params)
        self.params = params
        self.iterator_idx_stack = []
        self.saved_results = {}

    def next(self, step):
        self.execution_plan.append(["standard", step])
        return self

    def parallelized(self, step):
        self.execution_plan.append(["parallelized-step", step])
        return self

    def foreach(self, step):
        self.iterator_idx_stack.insert(0, len(self.execution_plan))
        self.execution_plan.append(["iterator", step])
        return self

    def endeach(self):
        if len(self.iterator_idx_stack) > 0:
            #  help iterators
            last_iterator_idx = self.iterator_idx_stack.pop(0)
            op, my_it_step = self.execution_plan[last_iterator_idx]
            setattr(my_it_step, "endpoint", len(self.execution_plan))
            # raise Exception(my_it_step.endpoint)
            self.execution_plan.append(["enditerator", last_iterator_idx])
        else:
            raise ValueError("Cannot have end iterator without matching start iterator")
        return self

    def next_endstate(self, start):
        for i in range(start, len(self.execution_plan)):
            if self.execution_plan[i][0] == 'enditerator':
                return i
        raise Exception("TODO!")

    @staticmethod
    def parameter_list():
        """
        :returns: `list` of `Parameter` objects that define the possible inputs to the pipeline.
        """
        return []

    def run_pipeline(self):
        pointer = 0
        prev_result = None
        it_stack = []
        it_stack_positions = []
        self.saved_results = {}
        while pointer < len(self.execution_plan):
            instruction, step = self.execution_plan[pointer]
            if isinstance(step, PipelineStep):
                step.set_pipeline_results_ref(self.saved_results)

            if instruction == STANDARD:
                # This is a simple step, so just run it and increment the pointer
                # raise Exception("TODO: jump past end of iterator")
                if isinstance(step, ParallelizedStep):
                    raise ValueError("Cannot run ParallelizedStep in serial mode")
                result = step.run_step(prev_result, self.params)
                if hasattr(step, "save_result_key"):
                    self.saved_results[step.save_result_key] = result
                prev_result = result
                pointer += 1
            elif instruction == "parallelized-step":
                # This is the start of a paralelized step, what we will want to do is,
                # run this step
                if not isinstance(step, ParallelizedStep):
                    raise ValueError("To execute in parallel, the step must be a ParallelizedStep")
                n = step.get_num_processes(self.params)
                parallel_params_list = step.parallel_param_list(self.params)
                if isinstance(parallel_params_list, dict):
                    check_types = [not isinstance(obj, Iterable) for obj in parallel_params_list.values()]
                    if any(check_types):
                        raise ValueError("All values of dictionary entries in parallel_param_list must be iterable.")
                    parallel_params_list = helpers.dict_product(parallel_params_list)
                prev_result = None
                with ProcessPool(nodes=n) as pool:
                    def wrapper_fn(my_params):
                        print(my_params)
                        return step.run_step(prev_result, {**self.params, **my_params})
                    prev_result = pool.map(wrapper_fn, parallel_params_list)
                    if hasattr(step, "save_result_key"):
                        self.saved_results[step.save_result_key] = prev_result
                pointer += 1
            elif instruction == ITERATOR:
                # This is the start of a loop, what we will want to do is,
                # run this step, and loop-over over steps
                result = step.run_step(prev_result, self.params)
                if hasattr(step, "save_result_key"):
                    self.saved_results[step.save_result_key] = result
                # it_stack.insert(0, enumerate(result))
                it_stack.insert(0, result)
                it_stack_positions.insert(0, pointer + 1)
                prev_result = next(result)  # sets up iterator so that it will be injected into prev_result of next step
                pointer += 1
            elif instruction == END_ITERATOR:
                try:
                    curr_iter = it_stack[0]
                    iter_result = next(curr_iter)
                    prev_result = iter_result
                    # move pointer back to start position
                    pointer = it_stack_positions[0]
                except StopIteration:
                    # prev_result = None
                    pointer += 1
                    it_stack.pop(0)
                    it_stack_positions.pop(0)
            else:
                raise ValueError("Invalid instruction!", instruction)
        return prev_result


class ResultWrapper(object):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
