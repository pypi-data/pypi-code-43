"""Common functionality shared across the command line interface."""


from importlib import import_module

import click

from . import PtvPyError


class LazyImport:
    """Wrapper to delay importing a module until it is accessed.

    Accessing any attribute will trigger the import. To check whether the import was
    triggered use :meth:`~.is_imported`.
    This class can only import modules and does not support setting attributes on the
    imported module.
    This class can help decrease the start-up time for applications that don't always
    use all of their imports. Especially command line applications profit if unnecessary
    imports can be skipped.

    Parameters
    ----------
    name : str
        Specifies what module to import in absolute or relative terms. If the name is
        specified in relative terms, then the `package` argument must be set.
    package :
        Name of the package which is to act as the anchor for resolving the package
        `name`.

    Examples
    --------
    >>> from ptvpy._cli_utils import LazyImport
    >>> math = LazyImport("math")
    >>> math
    LazyImport(name='math')
    >>> math.sin
    <built-in function sin>
    >>> type(math)
    <class 'ptvpy._cli_utils.LazyImport'>
    """

    @classmethod
    def get(cls, importer, attribute):
        """Access attributes of a LazyImport without triggering the import.

        Parameters
        ----------
        importer : LazyImport
            The importer whose attribute should be accessed.
        attribute : str
            Name of the attribute to get.

        Returns
        -------
        value
            Value of the attribute.

        Examples
        --------
        >>> from ptvpy._cli_utils import LazyImport
        >>> math = LazyImport("math")
        >>> LazyImport.get(math, "__dict__")
        {'name': 'math', 'package': None}
        >>> math.sin
        <built-in function sin>
        """
        if not isinstance(importer, cls):
            raise TypeError(f"must be of type {cls}, was {type(importer)}")
        return object.__getattribute__(importer, attribute)

    @classmethod
    def is_imported(cls, importer):
        """Check whether the import was triggered.

        This inspection is a save and doesn't trigger the import.

        Parameters
        ----------
        importer : LazyImport
            The object to check.

        Returns
        -------
        flag : bool
            True if the import was triggered, else false.

        Examples
        --------
        >>> from ptvpy._cli_utils import LazyImport
        >>> math = LazyImport("math")
        >>> LazyImport.is_imported(math)
        False
        >>> math.__name__
        'math'
        >>> LazyImport.is_imported(math)
        True
        """
        if not isinstance(importer, cls):
            raise TypeError(f"must be of type {cls}, was {type(importer)}")
        return "module" in object.__getattribute__(importer, "__dict__")

    def __init__(self, name, package=None):
        if package is not None:
            package = str(package)
        object.__setattr__(self, "name", str(name))
        object.__setattr__(self, "package", package)

    def __getattribute__(self, item):
        try:
            module = object.__getattribute__(self, "module")
        except AttributeError:
            name = object.__getattribute__(self, "name")
            package = object.__getattribute__(self, "package")
            module = import_module(name, package)
            object.__setattr__(self, "module", module)
        return getattr(module, item)

    def __setattr__(self, key, value):
        raise AttributeError(
            "setting attributes on instances of LazyImport is not supported"
        )

    def __repr__(self):
        name = object.__getattribute__(self, "name")
        package = object.__getattribute__(self, "package")
        args = f"name={name!r}"
        if package is not None:
            args += f", package={package!r}"
        return f"{type(self).__name__}({args})"


functools = LazyImport("functools")
threading = LazyImport("threading")
time = LazyImport("time")
pd = LazyImport("pandas")
_profile = LazyImport(".._profile", package=__name__)


class CliTimer:
    """Context manager to track the time while performing an operation.

    Parameters
    ----------
    prefix : str
        A string to prefix the progress indicator with. The string ': ' is
        automatically appended.
    total : int, optional
        Total number of expected progressing steps. If given and :meth:`update` is
        called for each iteration, the timer will display the progress in addition to
        the elapsed time and will try to estimate the remaining time.
    animated : bool, optional
        If True, the progress indicator shows the current runtime otherwise a static
        message informs the user that the timer was started. If None, the indicator
        is animated if the used `stream` is interactive.

    Notes
    -----
    This class was losely inspired by  a class_ in the conda package.

    .. _class: https://github.com/conda/conda/blob/4.5.13/conda/common/io.py#L297-L364

    Examples
    --------
    >>> import time
    >>> from ptvpy._cli_utils import CliTimer
    >>> with CliTimer("sleeping"):
    ...     time.sleep(1)
    sleeping: ... 1.0 s | done
    >>> with CliTimer("iterating", total=20, animated=True) as timer:
    ...     for _ in range(20):
    ...         time.sleep(0.1)
    ...         timer.update()
    iterating: ... 20/20 (100.0%), 2.0 s (+ 0 s) | done
    """

    #: str: Message printed after the initial message to indicate that the timer is
    #: running. Only used if not animated.
    progress_message = "... "
    #: str: Message printed after the timer was stopped due to a KeyboardInterrupt.
    interrupt_message = "interrupted"
    #: str: Message printed after the timer was stopped due to an exception.
    fail_message = "failed"
    #: str: Message printed after the timer succeeded successfully.
    success_message = "done"

    @staticmethod
    def format_exact(seconds):
        """Format a time delta in a human readable format.

        Examples
        --------
        >>> from ptvpy._cli_utils import CliTimer
        >>> CliTimer.format_exact(0.5)
        '0.50 s'
        >>> CliTimer.format_exact(1276)
        '21 min 16 s'
        >>> CliTimer.format_exact(2 ** 14)
        '4 h 33 min 04 s'
        """
        if seconds < 1:
            return f"{seconds:.2f} s"
        if seconds < 60:
            return f"{seconds:.1f} s"
        # Show minute counter
        minutes, seconds = divmod(round(seconds), 60)
        if minutes < 60:
            return f"{minutes:d} min {seconds:02d} s"
        # Show hour counter
        hours, minutes = divmod(minutes, 60)
        return f"{hours:d} h {minutes:02d} min {seconds:02d} s"

    @staticmethod
    def format_rounded(seconds):
        """Round and format a time delta in a human readable format.

        Examples
        --------
        >>> from ptvpy._cli_utils import CliTimer
        >>> CliTimer.format_rounded(11)
        '11 s'
        >>> CliTimer.format_rounded(1276)
        '21 min'
        >>> CliTimer.format_rounded(2 ** 14)
        '4 h 30 min'
        """
        seconds = round(seconds)
        if seconds < 60:
            return f"{seconds:d} s"
        # Show minute counter
        minutes, seconds = divmod(seconds, 60)
        if minutes < 10:
            return f"{minutes:d} min {round(seconds, -1):02d} s"
        if minutes < 60:
            return f"{minutes:d} min"
        # Show hour counter
        hours, minutes = divmod(minutes, 60)
        return f"{hours} h {round(minutes, -1):02d} min"

    @staticmethod
    def _estimate_remaining(n, total, rate, update_delta):
        """Estimate remaining time for progress to complete.

        Parameters
        ----------
        n : int
            Current number of processed items.
        total : int
            Total expected number of processed items.
        rate : float
            Average number of items per second.
        update_delta : float
            Time difference between now and last call to :meth:`update`.

        Returns
        -------
        remaining : float
            The estimated remaining time. Limited to >= 0.
        """
        remaining_delta = (total - n) / rate - update_delta
        return max(remaining_delta, 0)

    def __init__(self, prefix, total=None, animated=None):
        self._stdout = click.get_text_stream("stdout")
        self._stderr = click.get_text_stream("stderr")

        #: str: See constructor.
        self.prefix = prefix + ": "
        #: bool: Whether the timer will be animated. Don't change once the timer was
        #: started.
        self.is_animated = self._stdout.isatty() if animated is None else bool(animated)
        #: Exception or None: Stores the exception, if one is raised during processing
        #: and will prompt the fail message.
        self.exception = None

        self._thread = threading.Thread(target=self._indicate_progress)
        self._stop_event = threading.Event()
        self._lock = threading.RLock()

        # Access with lock only
        self._total = total  # Expected number of progressed items
        self._n = 0  # Current number of progressed items
        self._start_time = None  # Time of call to :meth:`_start`
        self._update_time = None  # Time of last call to :meth:`update`
        self._stop_time = None  # Time of call to :meth:`_stop`
        self._rate = None  # Average number of items/second

    def __enter__(self):
        self._start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.exception = exc_val  # None if no exception was raised
        self._stop()

    def update(self, inc=1):
        """Increase progress counter.

        Will do nothing if `total` isn't specified in the constructor.

        Parameters
        ----------
        inc : int, optional
            Amount by which to increase the counter.
        """
        with self._lock:
            self._n += inc
            self._update_time = time.time()
            # Clear cached rate, will be calculated again just before printing
            self._rate = None

    def _start(self):
        """Start the timer."""
        if self._start_time is not None:
            raise RuntimeError("already started")
        self._stdout.write(self.prefix)
        self._stdout.flush()
        self._start_time = self._update_time = time.time()
        if self.is_animated:
            self._thread.start()
        else:
            self._stdout.write(self.progress_message)
            self._stdout.flush()

    def _stop(self):
        """Stop the timer."""
        with self._lock:
            if self._stop_time is not None:
                raise RuntimeError("already stopped")
            self._stop_time = time.time()

        if self.is_animated:
            self._stop_event.set()
            self._thread.join()
            # Make sure to leave current line properly formatted,
            # e.g. KeyboardInterrupt or other unexpected output
            self._stdout.write(f"\r{self.prefix}")

        if self.exception is not None:
            fg = "red"
            stream = self._stderr
            if isinstance(self.exception, KeyboardInterrupt):
                msg = self.interrupt_message
            else:
                msg = self.fail_message
        else:
            fg = "green"
            msg = self.success_message
            stream = self._stdout

        click.secho(f"{self._format_status()} | {msg}", file=stream, fg=fg)

    def _indicate_progress(self):
        """Animate progress.

        This is the target function of the thread animating the process in parallel.
        """
        width = 0
        while not self._stop_event.is_set():
            status = self._format_status()
            width = max(width, len(status) + 1)
            self._stdout.write(status.ljust(width))
            self._stdout.flush()
            time.sleep(0.1)
            self._stdout.write("\b" * width)
        self._stdout.flush()

    def _format_status(self):
        """Describe current status.

        Returns
        -------
        status : str
            A string describing the current status of the timer.
        """
        with self._lock:
            current_time = time.time()
            if self._stop_time:
                elapsed_delta = self._stop_time - self._start_time
            else:
                elapsed_delta = current_time - self._start_time
            elapsed_str = self.format_exact(elapsed_delta)

            if self.is_animated and self._total:
                # Show item count, percentage and elapsed time
                percent = self._n / self._total
                status = f"{self._n:d}/{self._total:d} ({percent:.1%}), {elapsed_str}"
                if self._n > 0:
                    # and estimate the remaining time of the progress
                    if self._rate is None:
                        self._rate = self._n / (self._update_time - self._start_time)
                    update_delta = current_time - self._update_time
                    remaining_delta = self._estimate_remaining(
                        self._n, self._total, self._rate, update_delta
                    )
                    remaining_str = self.format_rounded(remaining_delta)
                    status += f" (+ {remaining_str})"
                return status
            else:
                return elapsed_str


class DetectionError(PtvPyError):
    """Raised if automatic profile detection is not successful."""

    pass


class ValidationError(PtvPyError):
    """Raised if profile validation wasn't successful."""

    pass


class AddProfileDetection:
    """Add automatic profile detection and loading to click.Command.

    Calling this function returns a decorator that adds common tasks for profile
    management to click.Commands. It handles profile loading (or detection if
    "--profile" wasn't given) and passes a loaded profile into the decorated function
    via the keyword "profile".
    The decorated function will raise one of the following exceptions if the profile
    detection, loading or validation wasn't successful: :exc:`~.DetectionError`,
    :exc:`~.ValidationError` or :exc:`!FileNotFoundError`.

    Parameters
    ----------
    validation : bool, optional
        If false, the profile is not validated upon loading and the option
        "--no-validation" is not added. This means, that as long as only a single file
        was detected as a profile candidate, the decorated function will receive a
        :class:`~.Profile` object.
    remember : bool, optional
        Remember the detected/loaded profile. This allows to share a profile between
        different subcommands (e.g. chained subcommands) by sharing the initialized
        decorator. Only the first profile will be remembered and used from then on.
        Further attempts at explicitly loading a profile with the "--profile" option
        will print a warning.

    Returns
    -------
    decorator : function
        The new decorator to wrap a click.command.

    Examples
    --------
    >>> import click
    >>> @click.command()
    ... @AddProfileDetection()
    ... def print_profile(profile):
    ...     print(profile)
    >>> print_profile(["--help"], standalone_mode=False)
    Usage: ... [OPTIONS]
    <BLANKLINE>
    Options:
      --no-validation     Don't validate profile(s). Use this option with care as
                          an invalid profile can have unintended consequences.
      -p, --profile FILE  Use profile from the given file. If not given try to
                          autodetect in current directory. Enter "ptvpy profile
                          -h" for more information.
      --help              Show this message and exit.
    0

    Note how we added parenthesis "()" to the end of the function.
    """

    @staticmethod
    def detect_profile(pattern):
        """Detect and load a single profile matching a pattern.

        Parameters
        ----------
        pattern : str
            Pattern used to find one or more profile files.

        Returns
        -------
        profile : Profile
            A single profile.

        Raises
        ------
        DetectionError
            Raised if no or many profile files were found.
        """
        profiles = _profile.Profile.from_pattern(pattern)
        if len(profiles) == 0:
            raise DetectionError(
                message=f"no file matching '{pattern}'",
                hint="Explicitly specify a file to use with the option"
                " '--profile FILE' or see 'ptvpy profile create -h' for help on"
                " creating one.",
            )
        if len(profiles) > 1:
            candidates = "\n    " + "\n    ".join(str(p.path) for p in profiles)
            raise DetectionError(
                message=f"found more than one file matching '{pattern}'",
                hint="Specify which file to use with the '--profile FILE' option:"
                f"{candidates}",
            )
        # Successfully detected single profile
        assert len(profiles) == 1
        return profiles[0]

    def __init__(self, validation=True, remember=False):
        if not isinstance(validation, bool):
            raise TypeError(
                f"'validation' must be of type bool, was: {type(validation)}"
            )
        #: Stores the first loaded/detected profile if remembering is enabled
        #: (:class:`~.Profile` or None).
        self.profile = None
        self._validation = validation
        self._remember = remember

    def __call__(self, cmd):
        """Decorate `cmd`."""

        @functools.wraps(cmd)
        def wrapped_cmd(*args, **kwargs):
            if self.profile is not None:
                if kwargs["profile"]:
                    click.secho(
                        f"Warning: requested profile {kwargs['profile']!r} "
                        f"but already using '{self.profile.path}'",
                        fg="red",
                    )
                profile = self.profile
            else:
                if kwargs["profile"]:
                    profile = _profile.Profile(kwargs["profile"])
                else:
                    profile = self.detect_profile(_profile.Profile.DEFAULT_PATTERN)
                click.echo(f"Using profile: '{profile.path}'")

                # Only validate if decorator option AND command line option allow it
                validate = self._validation and not kwargs.get("no_validation")
                if validate and not profile.is_valid:
                    raise ValidationError(message=profile.report_validation())

            if self._remember:
                self.profile = profile
            kwargs["profile"] = profile
            kwargs.pop("no_validation", None)
            return cmd(*args, **kwargs)

        wrapped_cmd = self._add_options(wrapped_cmd)
        return wrapped_cmd

    def reset(self):
        """Delete remembered profile.

        Has no effect if the argument `remember` was False.
        """
        self.profile = None

    def _add_options(self, cmd):
        """Add "--profile" and "-no-validation" options to command."""
        cmd = click.option(
            "-p",
            "--profile",
            help="Use profile from the given file. If not given try to autodetect "
            'in current directory. Enter "ptvpy profile -h" for more information.',
            type=click.Path(dir_okay=False, exists=True),
        )(cmd)
        if self._validation:
            cmd = click.option(
                "--no-validation",
                is_flag=True,
                help="Don't validate profile(s). Use this option with care as an "
                "invalid profile can have unintended consequences.",
            )(cmd)
        return cmd


def print_summary(particles, show_all=False):
    """Print a summary describing the found particles.

    This function will try to summarize the results of the processing pipeline with a
    few statements and print a table for selected properties/columns in the data
    containing statistics such as the median, mean, standard deviation and range.

    Parameters
    ----------
    particles : pandas.DataFrame["frame", ...]
        The results of the processing pipeline. The column "frame" is required.
    show_all : bool, optional
        Per default not all measurements appear in the summarizing table. If this is
        true every column/measurement will be summarized.

    Examples
    --------
    >>> import pandas as pd
    >>> from ptvpy._cli_utils import print_summary
    >>> particles = pd.DataFrame({
    ...     "frame": [0, 1, 1, 2, 3],
    ...     "particle": [1, 1, 2, 2, 1],
    ...     "mass": [110, 123, 155, 170, 129],
    ...     "size": [5.4, 6.4, 10.1, 9.4, 5.8],
    ... })
    >>> print_summary(particles)
    <BLANKLINE>
    Summary:
    <BLANKLINE>
    5 particles in 4 frames (1.25 particles/frame)
    2 unique trajectories spanning on average 2.5 frames
    <BLANKLINE>
          median   mean    std  min   max
    mass     129  137.4   24.5  110   170
    size     6.4   7.42  2.171  5.4  10.1

    """
    click.echo("\nSummary:")
    if particles.size == 0:
        click.secho("Didn't find any particles.", fg="red")
        return

    # Summarize location step
    avg_per_frame = particles.groupby("frame").size().mean()
    unique_frames = particles["frame"].unique()
    click.echo(
        f"\n{particles.shape[0]:g} particles in {len(unique_frames):g} frames "
        f"({avg_per_frame:.4g} particles/frame)"
    )
    # Summarize linking step
    if "particle" in particles:
        unique_particles = particles["particle"].nunique()
        avg_traj_length = particles.groupby("particle").size().mean()
        click.echo(
            f"{unique_particles:g} unique trajectories spanning on average "
            f"{avg_traj_length:.4g} frames"
        )
    # Warn about frames without particles
    empty_frames = set(range(int(particles["frame"].max()))) - set(unique_frames)
    if empty_frames:
        empty_frames_str = str(sorted(empty_frames))[1:-1]
        msg = f"{len(empty_frames):g} empty frames: {empty_frames_str}"
        click.secho(click.wrap_text(msg), fg="red")

    # And create statistics table for selected measurements/columns
    summary = particles.describe(percentiles=[0.5])
    if not show_all:
        # Control order and which columns are shown
        show_columns = [
            "mass",
            "size",
            "pair_distance",
            "x",
            "y",
            "angle",
            "dx",
            "dy",
            "v",
        ]
        summary = summary[[c for c in show_columns if c in summary.columns]]
    # Flip table, rename and sort statistic labels
    summary = summary.transpose(copy=False)
    summary.rename(columns={"50%": "median"}, inplace=True)
    summary = summary[["median", "mean", "std", "min", "max"]]
    click.echo()
    with pd.option_context("display.float_format", " {:.4g}".format):
        click.echo(str(summary))
