from .command_auth import AuthCommand
from rockset.query import QueryStringSQLText


class SQLQuery(AuthCommand):
    def usage(self):
        return """
usage: rock sql --help
       rock sql
       rock sql <sql_statement> [<args>...]

Run a sql query and return results as documents.

arguments:
  <sql-statement>       sql query to run; will read from STDIN if == '-'

examples:

  # To enter into the rock SQL REPL
  $ rock sql

  # To run a simple SQL query
  $ rock sql 'SELECT * from my_collection LIMIT 10'

  # To supply SQL from STDIN, use "-"
  $ echo 'SELECT * from my_collection LIMIT 10' | rock sql -

        """

    def validate_args(self, pargs):
        allowed_args = ['flood']
        for arg in pargs['<args>']:
            if arg not in allowed_args:
                return False
        return True

    def go(self):
        if not self.sql_statement:
            try:
                from rockset_sqlcli.rscli.main import cli_main
            except (ImportError, FileNotFoundError) as e:
                raise ImportError(
                    'Python package rockset_sqlcli is not installed. '
                    'Please run `pip install rockset_sqlcli` and try again!'
                )
            return cli_main(
                api_server=self.api_server,
                api_key=self.api_key,
                workspace='commons'
            )
        elif self.sql_statement == '-':
            self.sql_statement = self.read_stdin('SQL query')
        q = QueryStringSQLText(self.sql_statement)

        # handle advanced args
        self.flood = 'flood' in self.args

        # lets do this
        cursor = self.client.sql(q=q, flood_all_leaves=self.flood)
        results = cursor.results()
        fields = cursor.fields() or []
        self.print_list(0, results, field_order=[f['name'] for f in fields])

        return 0
