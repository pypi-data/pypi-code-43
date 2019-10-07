from cnvrg.modules.base_module import CnvrgBase
import cnvrg.helpers.apis_helper as apis_helper
from cnvrg.modules.errors import CnvrgError
import cnvrg.helpers.export_library_helper as export_library_helper
from cnvrg.modules.project import Project
from cnvrg.helpers.param_build_helper import LIBRARY, PROJECT, parse_params
from cnvrg.helpers.url_builder_helper import url_join
from cnvrg.helpers.args_helper import args_to_string, validate_args
from cnvrg.modules.experiment import Experiment
from cnvrg.helpers.param_helper import wrap_string_to_list
import os
DEFAULT_WORKING_DIR = os.path.expanduser("~/cnvrg_libraries")

class Library(CnvrgBase):
    def __init__(self, library, project=None, working_dir=None, _info=None):
        owner, library = parse_params(library, LIBRARY)
        self.__working_dir = working_dir or DEFAULT_WORKING_DIR
        try:
            self.project = Project(project)
        except CnvrgError as e:
            self.project = None

        self.__library = library
        self.__owner = apis_helper.credentials.owner
        self.__info = _info
        self.__path = None
        self.__cloned = self.__lib_loaded()

    def __base_url(self):
        return url_join("users", self.__owner, "libraries", self.__library)

    @staticmethod
    def export(*paths):
        paths = [os.path.abspath(p) for p in paths]
        resp = export_library_helper.export_library(*paths)
        if resp.get("library"):
            lib_key = resp.get("library").get("key")
            return Library(lib_key)
        else:
            raise CnvrgError(resp.get("message"))

    @staticmethod
    def list():
        owner = apis_helper.credentials.owner
        lib_list = list(map(lambda x: Library(url_join(x.get('owner'), x.get("title")), _info=x), apis_helper.get(url_join("users", owner, "libraries")).get("libraries")))
        return {l.title(): l for l in lib_list}



    def info(self, force=False):
        """
        get info about this library
        :param force: to force api fetching
        :return: dict represent the library
        {clone_cmd: string,
        command: string,
        arguments: list of key: values(list),
        number_of_experiments: integer,
        description: string}
        """
        if self.__info and not force:
            return self.__info
        self.__info = self.__fetch_info()
        return self.info()


    def __fetch_info(self):
        try:
            resp = apis_helper.get(self.__base_url())
            return resp.get("library")
        except Exception as e:
            raise CnvrgError("Cant find library")



    def load(self):
        """
        load library to your local directory
        :param working_dir: path to clone the library to
        """
        info = self.info()
        lib_dir = self.__lib_path()
        os.makedirs(lib_dir, exist_ok=True)
        export_library_helper.load_library(info.get("package"), lib_dir)
        self.__path = lib_dir
        return lib_dir

    def __default_args(self):
        return {
            "project_dir": os.path.abspath(self.project.get_working_dir()),
            "output_dir": os.path.abspath(self.project.get_output_dir())
        }


    def arguments(self):
        return self.info().get("exp_arguments")

    def __mix_args(self, args=None, with_many=True, with_defaults=True):
        args = args or {}
        #exp arguments are key: values
        library_args = self.info().get("exp_arguments") or {}
        all_args = self.__default_args() if with_defaults else {}
        all_args = {
            **all_args,
            **library_args,
            **args
        }
        if not with_many: validate_args(all_args)
        return all_args


    def run(self, computes=None, compute=None, datasets=None, dataset=None, image=None, commit=None, title=None, local=True, sync_before=False, sync_after=False, **kwargs):
        ## support
        computes = computes or wrap_string_to_list(computes) or wrap_string_to_list(compute) or []
        datasets = datasets or wrap_string_to_list(datasets) or wrap_string_to_list(dataset) or []

        if "local" in computes or len(computes) == 0: return self.__run_local(title=title, sync_before=sync_before, sync_after=sync_after, **kwargs)
        if not self.project: raise CnvrgError("You should specify Project on the library constructor")
        args = self.__mix_args(kwargs, with_many=True, with_defaults=False)
        hyper_search_payload = self.project.run_task(cmd=self.info().get("command"), templates=computes, datasets=datasets, image=image, commit=commit, title=title, library=self.__library, arguments=args)


        return [Experiment(slug) for slug in hyper_search_payload.get("experiments")]



    def __run_local(self, title=None, sync_before=None, sync_after=None, **kwargs):
        if not self.project:
            raise CnvrgError("Cant run a library not in a project context, please cd into cnvrg project")
        if not self.__lib_loaded(): self.load()
        args = self.__mix_args(kwargs, with_many=False)

        ## prepare script.
        raw_script = "{cmd} {args}".format(cmd=self.info().get("command"), args=args_to_string(args))
        return [Experiment.run(raw_script, title=title, project=self.project, local=True, working_directory=self.__lib_path(), library=self.__library, sync_before=sync_before, sync_after=sync_after, **kwargs)]


    def __lib_loaded(self):
        return os.path.exists(os.path.join(self.__lib_path(), "library.yml"))


    def __lib_path(self):
        working_dir = self.__working_dir
        return os.path.join(working_dir, self.info().get("slug"))


    def __str__(self):
        return """{title}
        Description: {description}
        Arguments: {arguments}
        Command: {command}
        """.format(**{**self.info(), "arguments": args_to_string(self.info().get("arguments"))})

    def title(self):
        return url_join(self.info().get("owner"), self.info().get("title"))








