from tormor.main_script import script
import click
from click.testing import CliRunner
from click.exceptions import UsageError
from tormor.connections import Connection
from tormor.commands import BOOTSTRAP_SQL
import pytest

class TestScript():
    def setup(self):
        self.runner = CliRunner()
        self.conn = Connection('postgresql://localhost/tormordb')
        self.conn.execute("DROP TABLE IF EXISTS migration;")
        self.conn.execute("DROP TABLE IF EXISTS module;")
        self.conn.execute("DROP TABLE IF EXISTS customer;")
        self.conn.execute("DROP TABLE IF EXISTS employee;")
        self.conn.execute("DROP TABLE IF EXISTS product;")
        self.conn.execute(BOOTSTRAP_SQL)

    def teardown(self):
        self.conn.execute("DROP TABLE IF EXISTS migration;")
        self.conn.execute("DROP TABLE IF EXISTS module;")
        self.conn.execute("DROP TABLE IF EXISTS customer;")
        self.conn.execute("DROP TABLE IF EXISTS employee;")
        self.conn.execute("DROP TABLE IF EXISTS product;")
        self.conn.close()

    def test_script_to_invalid_command(self):
        result = self.runner.invoke(script, ['--xyz'])
        assert result.exit_code == click.UsageError.exit_code

    def test_script_to_migrate(self):
        self.runner.invoke(script, ['-h', 'localhost', '-d', 'tormordb', 'migrate', 'customer'])
        table_exists = self.conn.fetch("""
            SELECT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = 'public' AND tablename = 'customer');
        """)
        assert table_exists[0][0] == True
        customers = self.conn.fetch("""
            SELECT * FROM public.customer;
        """)
        actual_result = set(record.get("name") for record in customers)
        expected_result = {"Customer1", "Customer2", "Customer3", "Customer5"}
        assert actual_result == expected_result

    def test_script_to_migrate_multiple_module(self):
        self.runner.invoke(script, ['-h', 'localhost', '-d', 'tormordb', 'migrate', 'employee', 'customer'])
        customer_table_exists = self.conn.fetch("""
            SELECT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = 'public' AND tablename = 'customer');
        """)
        assert customer_table_exists[0][0] == True
        enployee_table_exists = self.conn.fetch("""
            SELECT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = 'public' AND tablename = 'employee');
        """)
        assert enployee_table_exists[0][0] == True

        customers = self.conn.fetch("""
            SELECT * FROM public.customer;
        """)
        actual_result = set(record.get("name") for record in customers)
        expected_result = {"Customer1", "Customer2", "Customer3", "Customer5"}
        assert actual_result == expected_result

        employees = self.conn.fetch("""
            SELECT * FROM public.employee;
        """)
        actual_result = set(record.get("name") for record in employees)
        expected_result = {"Employee1", "Employee2", "Employee3"}
        assert actual_result == expected_result

        migration = self.conn.fetch("""
            SELECT * FROM public.migration;
        """)
        assert migration[0][0] == 'customer'
        assert migration[0][1] == '01_customer.sql'

        assert migration[1][0] == 'employee'
        assert migration[1][1] == '01_employee.sql'

        assert migration[2][0] == 'customer'
        assert migration[2][1] == '03_customer.sql'

    def test_script_to_dry_migrate(self):
        self.conn.execute('''INSERT INTO module(name) VALUES ('customer')''')
        self.conn.execute('''INSERT INTO module(name) VALUES ('employee')''')
        self.conn.execute('''INSERT INTO module(name) VALUES ('product')''')
        self.conn.execute('''INSERT INTO module(name) VALUES ('department')''')
        result = self.runner.invoke(script, ['-h', 'localhost', '-d', 'tormordb', 'migrate', 'test_module', '--dry-run'])
        assert result.exit_code == 0
        assert self.conn.fetch('''SELECT * FROM migration''') == []

    def test_script_to_include(self):
        self.runner.invoke(script, ['-h', 'localhost', '-d', 'tormordb', 'include', 'tormor/tests/script_file.txt'])
        result = self.conn.fetch("SELECT name FROM module GROUP BY name ORDER BY name")
        actual_result = [x['name'] for x in result]
        assert ["customer", "employee", "product"] == actual_result

    def test_script_to_include_with_dry_migrate(self):
        self.runner.invoke(script, ['-h', 'localhost', '-d', 'tormordb', 'include', 'tormor/tests/script_file_dry.txt'])
        result = self.conn.fetch("SELECT name FROM module GROUP BY name ORDER BY name")
        actual_result = [x['name'] for x in result]
        assert [] == actual_result

    def test_script_to_include_without_file(self):
        result = self.runner.invoke(script, ['-h', 'localhost', '-d', 'tormordb', 'include'])
        assert result.exit_code == click.UsageError.exit_code

    def test_script_to_execute_sql(self):
        self.runner.invoke(script, ['-h', 'localhost', '-d', 'tormordb', 'sql', 'tormor/tests/Schema/customer/01_customer.sql'])
        result = self.conn.fetch("SELECT * FROM customer")
        actual_result = set(record.get("name") for record in result)
        expected_result = {"Customer1", "Customer2", "Customer3"}
        assert actual_result == expected_result

    def test_script_to_execute_sql_no_file(self):
        result = self.runner.invoke(script, ['-h', 'localhost', '-d', 'tormordb', 'sql'])
        assert result.exit_code == click.UsageError.exit_code
