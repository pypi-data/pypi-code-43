from qai.qonfigs import get_configs


class QRemoteConnection(object):
    def __init__(self, analyzer, category="", white_lister=None, config_file=None):
        self.configs = get_configs(config_file)

        # Only use name passed in as fallback
        try:
            self.category = self.configs["SERVICE_NAME"]
            print("Using SERVICE_NAME from config.json as category")
        except KeyError:
            self.category = category

        # this will crash if configs doesn't have SUPPORTED_LANGUAGES
        # that is intentional
        supported_languages = self.configs["SUPPORTED_LANGUAGES"]

        if isinstance(supported_languages, list):
            self.supported_languages = supported_languages
        elif isinstance(supported_languages, str):
            self.supported_languages = [supported_languages]
        else:
            raise TypeError(
                f"Config file {config_path} must have SUPPORTED_LANGUAGES as string or list of strings."
            )

        #  print(self.supported_languages)
        for lang in self.supported_languages:
            if lang.find("-") != -1:
                raise ValueError(
                    f"Language {lang} contains a '-', which is almost certainly an error. Correct values look like 'en'."
                )

        # Dependency Injection
        self.analyzer = analyzer
        if not hasattr(analyzer, "analyze"):
            raise ValueError('Analyzer instance must have "analyze" method.')

        if white_lister is not None:
            if not callable(white_lister):
                e = f"{white_lister.__name__} is not callable."
                raise TypeError(e)
            if not self.category:
                raise ValueError("Must specify a category to whitelist")
            self.should_whitelist = True
            self.white_lister = white_lister
        else:
            self.should_whitelist = False
        # end DI

    def get_future(self):
        raise NotImplementedError

    def connect(self):
        raise NotImplementedError
