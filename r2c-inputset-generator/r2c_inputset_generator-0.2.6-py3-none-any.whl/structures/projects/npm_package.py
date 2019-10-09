from r2c_isg.structures.projects import Project


class NpmPackage(Project):
    def check_guarantees(self) -> None:
        """Guarantees a name or a url."""
        assert 'name' in self.uuids_ or 'url' in self.uuids_, \
            'Npm package guarantees not met; package name or ' \
            'url must be provided.'

    def get_name(self) -> str:
        """Returns the project's name."""
        if 'name' in self.uuids_:
            return self.uuids_['name']()

        # pull the name from the url
        return self.uuids_['url']().strip('/').split('/')[-1]

    def to_inputset(self, **kwargs) -> list:
        """Converts npm packages/versions to PackageVersion dict."""
        self.check_guarantees()

        if not self.versions:
            if kwargs.get('force', False):
                # return a package with a blank version string
                print(' ' * 9 + 'Warning: Package %s has no versions. '
                                'Forcing.' % self.get_name())

                return [{
                    'input_type': 'PackageVersion',
                    'package_name': self.get_name(),
                    'version': ''  # no versions; leave blank
                }]

            print(' ' * 9 + 'Warning: Project %s has no versions. '
                            'Ignoring.' % self.get_name())

        return[{
            'input_type': 'PackageVersion',
            'package_name': self.get_name(),
            **v.to_inputset()
        } for v in self.versions]
