from logging import getLogger

from openscm.scmdataframe import df_append

logger = getLogger(__name__)


class BaseSCM(object):
    """Base class which provides an interface to run various simple climate models when fitting

    Each concrete class must implement the `_run_single` method which runs the model.

    Parameters
    ----------
    kwargs : dict
        Initial configuration parameters for the scm. These values maybe used to perform heavy one-off computation.

    Attributes
    ----------
    name: str
        The name of the simple climate model
    """

    name = "base"

    def __init__(self, **kwargs):
        """
        """
        self.config_parameters = kwargs

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()

    def run(self, run_parameters, variables=None, iter_over_value=None):
        """Run the model

        Parameters
        ----------
        variables: list
            If not None, the list of variables which are requested from the model. The model must return at least these variables,
            but it free to return more

        kwargs :
            The parameters to run the model with.

            These parameters are joined with the ``config_parameters`` passed to the initialiser.

        Returns
        -------
        openscm.scmdataframe.ScmDataFrame
            An openScm DataFrame containing time series output

        """

        logger.debug(
            "running model {} with config: {}".format(self.name, run_parameters)
        )
        results = self._run_single(run_parameters, variables=variables)

        # Write the extra metadata to the results table
        if iter_over_value is not None:
            for k in iter_over_value:
                results[k] = iter_over_value[k]

        return results

    def run_multiple(self, runs, variables=None):
        """
        Perform multiple SCM runs

        This may be performed serially or in parallel depending on the SCM used

        Parameters
        ----------
        runs: list of tuples
            The runs to perform. Each run is described by a tuple of a dict containing the parameters to run and a dict which
            to overwrite the metadata from the run. i.e. ``{'scenario': 'RCP8.5'} would overwrite the 'scenario' metadata to be
            'RCP8.5' regardless of what the model outputs.
        variables: list of str
            Only return variables in this list
        Returns
        -------
        `openscm.scmdataframe.ScmDataFrame` containing the data from all runs. The ``run_id`` parameter can be used to differentiate
        the runs
        """
        res = [
            self.run(
                run_parameters, variables=variables, iter_over_value=iter_over_value
            )
            for run_parameters, iter_over_value in runs
        ]
        return df_append(res)

    def _run_single(self, parameters, variables=None):
        """
        Perform a single model run

        Parameters
        ----------
        parameters : dict
            A `dict` containing the run-specific configuration
        variables : list of str
            Only return variables in this list

        Returns
        -------
        `openscm.scmdataframe.ScmDataFrame` containing the data from the run

        """
        raise NotImplementedError

    def start(self):
        pass

    def cleanup(self):
        """
        Cleanup any created resources

        Automatically called when exiting a context manager
        """
        pass
