from unittest import TestCase, mock
from k9.helper import *
import io
import base64
import pprint
from datetime import datetime, timedelta

from k9.pretty_object import PrettyObject

po = PrettyObject()
pp = pprint.PrettyPrinter(indent=2, width=120)


class TestHelper(TestCase):

    ###########################################################################
    # Util
    ###########################################################################

    def test_last_word(self):
        self.assertEqual('my-pod', last_word('pods/my-pod'))

    @mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_view_yaml(self, mock_stdout):
        view_yaml(abs_path('../test/tomcat-deploy-dev.yml'))
        self.assertTrue('tomcat-dev' in mock_stdout.getvalue())

    def test_read_yaml(self):
        body = read_yaml(abs_path('../test/tomcat-deploy-dev.yml'))
        self.assertEqual('tomcat-dev', body['metadata']['name'])

    def test_age(self):
        now = datetime.now(timezone.utc)

        diff = timedelta(hours=14, minutes=4, seconds=22)
        then = now - diff
        self.assertEqual('14:04:22', get_age(then))

        diff = timedelta(hours=4, minutes=14, seconds=2)
        then = now - diff
        self.assertEqual('04:14:02', get_age(then))

        diff = timedelta(hours=23, minutes=14, seconds=2)
        then = now - diff
        self.assertEqual('23:14:02', get_age(then))

        diff = timedelta(days=1, hours=23, minutes=14, seconds=2)
        then = now - diff
        self.assertEqual('1d', get_age(then))

        diff = timedelta(days=25, hours=23, minutes=14, seconds=2)
        then = now - diff
        self.assertEqual('25d', get_age(then))

    def test_absolute_dir(self):
        result = abs_path('test')

        self.assertTrue(len(result) > 4)
        self.assertTrue('/' in result)
        self.assertEqual('test', last_word(result))


    ###########################################################################
    # Namespace
    ###########################################################################

    def test_list_namespaces(self):
        result = list_namespaces()
        self.assertTrue(len(result)>0)

    def test_default_namespace(self):
        with self.assertRaises(Exception) as e:
            self.get_default_namespace()
            self.assertTrue('You must call get_default_namespace()' in e)

        set_default_namespace("test")
        self.assertEqual("test", get_default_namespace())

    def test_create_namespace(self):
        try:
            ns = "namespace-unit-test"
            set_default_namespace(ns)

            create_namespace()
            self.assertTrue(namespace_exists())

            result = get_namespace()
            self.assertEqual(ns, result.metadata.name)

        finally:
            delete_namespace()
            self.assertFalse(namespace_exists())

    def test_delete_bogus_namespace(self):
        self.assertEqual(None, delete_namespace('bogus'))

    def test_get_bogus_namespace(self):
        with self.assertRaises(Exception) as e:
            self.set_default_namespace(None)
            self.get_default_namespace()
            self.assertTrue('You must call get_default_namespace()' in e)

    ###########################################################################
    # Pods
    ###########################################################################

    def test_list_pods(self):
        result = list_pods("kube-system")
        self.assertIsNotNone(result)
        self.assertTrue(len(result) > 0)

        set_default_namespace("default")
        result = list_pods()
        self.assertTrue(len(result) == 0)

    ###########################################################################
    # Secrets
    ###########################################################################

    def test_create_secret(self):
        try:
            set_default_namespace("default")

            secret_name = "tomcat-dev"
            secrets = {
                'ds-url': 'https://some/url',
                'password': 'My1SecretPassword',
                'username': 'postgres'
            }

            # Test create_secret()
            result = create_secret(secret_name, secrets)
            self.assertEqual(secret_name, result.metadata.name)

            # Test get_secret()
            result = get_secret(secret_name)
            self.assertEqual(secret_name, result.metadata.name)

            # Check secret values
            for key, value in result.data.items():
                self.assertEqual(secrets[key], base64.b64decode(value).decode('utf8'))

            # Test secret_exists()
            self.assertTrue(secret_exists(secret_name))

            # Test list_secret()
            result = list_secrets()

            secret_list = [
                s['name']
                for s in result
                if s['name'] == secret_name
            ]

            self.assertEqual(1, len(secret_list))
            self.assertEqual(secret_name, secret_list[0])

        finally:
            delete_secret(secret_name)

    def test_secret_exists(self):
        self.assertFalse(secret_exists('bogus-secret'))

    def test_delete_bogus_secret(self):
        set_default_namespace('default')
        self.assertEqual(None, delete_secret('bogus'))

    ###########################################################################
    # Deployments
    ###########################################################################

    def test_deployments(self):
        try:
            set_default_namespace("deployment-unit-test")
            if not namespace_exists("deployment-unit-test"):
                create_namespace()

            secret_name = "tomcat-dev"
            secrets = {
                'ds-url': 'https://some/url',
                'password': 'My1SecretPassword',
                'username': 'postgres'
            }

            # Test create_secret()
            create_secret(secret_name, secrets)

            deploy_name = 'tomcat-dev'
            body = read_yaml(abs_path('../test/tomcat-deploy-dev.yml'))
            create_deployment(body)
            self.assertTrue(deployment_exists(deploy_name))

            result = get_deployment(deploy_name)
            self.assertEqual(deploy_name, result.metadata.name)

            result = [
                d
                for d in list_deployments()
                if d['name'] == deploy_name
            ]
            self.assertEqual(1, len(result))
            self.assertFalse(deployment_exists('bogus'))

            # Update deployment
            update_deployment_image(deploy_name, 'tomcat', 'tomcat:8')

            # Confirm that deployment image has been updated.
            result = get_deployment(deploy_name)
            self.assertEqual(deploy_name, result.metadata.name)
            found = [
                container.image
                for container in result.spec.template.spec.containers
                if container.name == 'tomcat'
            ]
            self.assertEqual('tomcat:8', found[0])


            # Scale deployment
            spec = {
                'replicas': 3
            }
            scale_deployment(deploy_name, spec)
            result = get_deployment(deploy_name)
            self.assertEqual(deploy_name, result.metadata.name)
            self.assertEqual(3, result.spec.replicas)


        finally:

            delete_deployment(deploy_name)
            delete_secret(secret_name)
            delete_namespace()


    def test_delete_bogus_deployment(self):
        set_default_namespace('default')
        self.assertEqual(None, delete_deployment('bogus'))

    ###########################################################################
    # Services
    ###########################################################################
    def test_service(self):
        try:
            # Arrange
            set_default_namespace("service-unit-test")
            if not namespace_exists("service-unit-test"):
                create_namespace()

            secret_name = "tomcat-dev"
            secrets = {
                'ds-url': 'https://some/url',
                'password': 'My1SecretPassword',
                'username': 'postgres'
            }

            create_secret(secret_name, secrets)
            deploy_name = 'tomcat-dev'
            body = read_yaml(abs_path('../test/tomcat-deploy-dev.yml'))
            create_deployment(body)

            # Act
            svc_name = 'tomcat-svc-dev'
            body = read_yaml(abs_path('../test/tomcat-svc-dev.yml'))

            create_service(body)

            # Assert
            result = get_service(svc_name)
            self.assertEqual(svc_name, result.metadata.name)

            result = list_services()
            found = [
                svc['name']
                for svc in result
                if svc_name in svc['name']
            ]
            self.assertEqual(1, len(found))

        finally:
            if service_exists(svc_name):
                delete_service(svc_name)

            delete_deployment(deploy_name)

            delete_secret(secret_name)
            delete_namespace()

    def test_service_exists_fail(self):
        self.assertFalse(service_exists('bogus'))

    def test_delete_bogus_service(self):
        set_default_namespace('default')
        self.assertEqual(None, delete_service('bogus'))

    ###########################################################################
    # Ingress
    ###########################################################################
    def test_ingress(self):
        try:
            ##################
            # Arrange
            secret_name = "tomcat-dev"
            deploy_name = 'tomcat-dev'
            svc_name = 'tomcat-svc-dev'
            ing_name = 'tomcat-ing-dev'


            # create namespace
            set_default_namespace("ingress-unit-test")
            if not namespace_exists("ingress-unit-test"):
                create_namespace()

            # create secret
            secrets = {
                'ds-url': 'https://some/url',
                'password': 'My1SecretPassword',
                'username': 'postgres'
            }
            create_secret(secret_name, secrets)

            # create deployment
            body = read_yaml(abs_path('../test/tomcat-deploy-dev.yml'))
            create_deployment(body)

            # create service
            body = read_yaml(abs_path('../test/tomcat-svc-dev.yml'))
            create_service(body)

            ##################
            # Act

            # create ingress
            body = read_yaml(abs_path('../test/tomcat-ing-dev.yml'))
            result = create_ingress(body)
            self.assertEqual(ing_name, result.metadata.name)

            ##################
            # Assert

            # test get_ingress()
            result = get_ingress(ing_name)
            self.assertEqual(ing_name, result.metadata.name)

            # test ingress_exists()
            self.assertTrue(ingress_exists(ing_name))

            # test list_ingress()
            found = [
                ing['name']
                for ing in list_ingress()
                if ing['name'] == ing_name
            ]
            self.assertEqual(1, len(found))

        finally:
            delete_ingress(ing_name)
            delete_service(svc_name)
            delete_deployment(deploy_name)
            delete_secret(secret_name)
            delete_namespace()

    def test_ingress_exists_fail(self):
        self.assertFalse(ingress_exists('bogus'))

    def test_delete_bogus_ingress(self):
        set_default_namespace('default')
        self.assertEqual(None, delete_ingress('bogus'))

    ###########################################################################
    # Service Accounts
    ###########################################################################

    def test_service_accounts(self):
        try:
            ############
            # Arrange
            set_default_namespace('default')
            sa_name = "unit-test-tomcat-sa"

            ############
            # Act
            result = create_service_account(sa_name)

            ############
            # Assert

            self.assertEqual(sa_name, result.metadata.name)

            # test get_service_account()
            result = get_service_account(sa_name)
            self.assertEqual(sa_name, result.metadata.name)

            # test service_account_exists()
            self.assertTrue(service_account_exists(sa_name))

            # test_list_service_accounts()
            result = list_service_accounts()

            result = [
                sa['name']
                for sa in result
                if sa['name'] == sa_name
            ]
            self.assertEqual(1, len(result))

        finally:
            delete_service_account(sa_name)


    def test_service_account_exists_fail(self):
        set_default_namespace('default')
        self.assertFalse(service_account_exists('bogus'))
        self.assertTrue(service_account_exists('default'))

    def test_list_service_account_fail(self):
        self.assertEqual(0, len(list_service_accounts('bogus')))

    def test_delete_bogus_service_account(self):
        set_default_namespace('default')
        self.assertEqual(None, delete_service_account('bogus'))

    ###########################################################################
    # cron job
    ###########################################################################
    def test_cron_job(self):
        try:
            ###############
            # Arrange
            set_default_namespace('default')
            sa_name = 'xx-ecr-cron-sa'
            bind_name = 'xx-ecr-cron-sa-bind'
            secret_name = 'aws-info'
            cj_name = 'xx-ecr-login-cron'

            create_service_account(sa_name)
            self.assertTrue(service_account_exists(sa_name))

            role_name = 'ecr-login-role'
            role = {
                'apiVersion': 'rbac.authorization.k8s.io/v1',
                'kind': 'ClusterRole',
                'metadata': {'name': f'{role_name}'},
                'rules': [
                    {
                        'apiGroups': [''],
                        'resources': ["serviceaccounts"],
                        'verbs': ["get", "patch"]

                    },
                    {
                        'apiGroups': [''],
                        'resources': ['secrets'],
                        'verbs': ['create', 'delete']
                    }
                 ]
            }
            create_cluster_role(role)
            self.assertTrue(cluster_role_exists(role_name))

            create_cluster_role_binding(bind_name, role_name, sa_name)
            self.assertTrue(cluster_role_binding_exists(bind_name))

            secrets = {
                'ecr-url': 'https://some-url',
                'aws-account': 'bogus account value',
                'aws-region': 'us-east-1'
            }
            create_secret(secret_name, secrets)
            self.assertTrue(secret_exists(secret_name))

            ###############
            # Act
            body = read_yaml(abs_path('../test/ecr-login-cron.yml'))
            result = create_cron_job(body)

            ###############
            # Assert
            self.assertEqual(cj_name, result.metadata.name)
            self.assertTrue(cron_job_exists(cj_name))

            # test list_cron_jobs()
            found = [
                cj['name']
                for cj in list_cron_jobs()
                if cj['name'] == cj_name
            ]
            self.assertEqual(1, len(found))

            # test get_cron_job()
            result = get_cron_job(cj_name)
            self.assertEqual(cj_name, result.metadata.name)

        finally:
            delete_cron_job(cj_name)
            delete_secret(secret_name)
            delete_cluster_role_binding(bind_name)
            delete_cluster_role(role_name)
            delete_service_account(sa_name)


    def test_cron_job_exists_fail(self):
        self.assertFalse(cron_job_exists('bogus'))

    def test_delete_bogus_cron_job(self):
        set_default_namespace('default')
        self.assertEqual(None, delete_cron_job('bogus'))

    ###########################################################################
    # Roles
    ###########################################################################

    def test_role(self):
        try:
            set_default_namespace('default')

            ############
            # Arrange

            role_name = 'pod-reader-role'
            role = {
                'apiVersion': 'rbac.authorization.k8s.io/v1',
                'kind': 'Role',
                'metadata': {
                    'name': role_name,
                    'namespace': 'default'
                    },
            'rules': [
                    {
                        'apiGroups': [''],
                        'resources': ['pods'],
                        'verbs': ['get', 'watch', 'list']
                    }
                ]
            }

            ############
            # Act
            result = create_role(role)

            ############
            # Assert
            self.assertEqual(role_name, result.metadata.name)

            # test role_exists()
            self.assertTrue(role_exists(role_name))

            # test get_role()
            result = get_role(role_name)
            self.assertEqual(role_name, result.metadata.name)

            # test list_roles()
            found = [
                role
                for role in list_roles()
                if role['name'] == role_name
            ]
            self.assertEqual(1, len(found))

            # test delete_role()
            result = delete_role(role_name)
            self.assertEqual('Success', result.status)

            self.assertFalse(role_exists(role_name))

        finally:
            delete_role(role_name)

    def test_role_exists_fail(self):
        self.assertFalse(role_exists('bogus'))

    def test_role_binding(self):
        try:
            ############
            # Arrange
            set_default_namespace('default')

            sa_name = "xx-pod-reader-sa"
            role_name = "xx-pod-reader-role"
            binding_name = "xx-pod-reader-binding"

            # create the service account
            result = create_service_account(sa_name)
            sa_name = result.metadata.name

            # create role
            body = read_yaml(abs_path('../test/xx-pod-reader-role.yml'))
            result = create_role(body)

            ############
            # Act

            # create cluster role binding
            result = create_role_binding(binding_name, role_name, sa_name)

            ############
            # Assert
            self.assertEqual(binding_name, result.metadata.name)

            # test get_role_binding()
            result = get_role_binding(binding_name)

            # test role_binding_exists()
            self.assertTrue(role_binding_exists(binding_name))

        finally:
            delete_role_binding(binding_name)
            self.assertFalse(role_binding_exists(binding_name))

            delete_role(role_name)
            self.assertFalse(role_exists(role_name))

            delete_service_account(sa_name)
            self.assertFalse(service_account_exists(sa_name))

    def test_delete_bogus_role(self):
        self.assertEqual(None, delete_role('bogus'))

    def test_delete_bogus_role_binding(self):
        set_default_namespace('default')
        self.assertEqual(None, delete_role_binding('bogus'))

    ###########################################################################
    # Cluster Roles
    ###########################################################################

    def test_cluster_role(self):
        try:
            ############
            # Arrange

            role_name = 'ecr-login-role'
            role = {
                'apiVersion': 'rbac.authorization.k8s.io/v1',
                'kind': 'ClusterRole',
                'metadata': {'name': f'{role_name}'},
                'rules': [
                     {
                         'apiGroups': [''],
                         'resources': ['secrets'],
                         'verbs': ['create', 'delete']
                     },
                     {
                         'apiGroups': [''],
                         'resources': ['serviceaccounts'],
                         'verbs': ['get', 'patch']
                     }
                 ]
            }

            ############
            # Act
            result = create_cluster_role(role)

            ############
            # Assert
            self.assertEqual(role_name, result.metadata.name)

            # test cluster_role_exists()
            self.assertTrue(cluster_role_exists(role_name))

            # test list_cluster_roles()
            role_list = [
                role
                for role in list_cluster_roles()
                    if role['name'] == role_name
            ]
            self.assertEqual(role_name, role_list[0]['name'])

            # test delete_cluster_role()
            result = delete_cluster_role(role_name)
            self.assertEqual('Success', result.status)

            self.assertFalse(cluster_role_exists(role_name))

        finally:
            delete_cluster_role(role_name)

    def test_cluster_role_binding(self):
        try:
            ############
            # Arrange
            set_default_namespace('default')

            sa_name = "unit-test-tomcat-sa"
            cr_name = "unit-test-jenkins-access"
            cr_bind_name = "unit-test-jenkins-binding"

            # create the service account
            result = create_service_account(sa_name)
            sa_name = result.metadata.name

            # create cluster role
            body = read_yaml(abs_path('../test/unittest-jenkins-access.yml'))
            result = create_cluster_role(body)

            ############
            # Act

            # create cluster role binding
            result = create_cluster_role_binding(cr_bind_name, cr_name, sa_name)

            ############
            # Assert
            self.assertEqual(cr_bind_name, result.metadata.name)

            # test get_cluster_role_binding()
            result = get_cluster_role_binding(cr_bind_name)

            # test cluster_role_binding_exists()
            self.assertTrue(cluster_role_binding_exists(cr_bind_name))

        finally:
            delete_cluster_role_binding(cr_bind_name)
            self.assertFalse(cluster_role_binding_exists(cr_bind_name))

            delete_cluster_role(cr_name)
            self.assertFalse(cluster_role_exists(cr_name))

            delete_service_account(sa_name)
            self.assertFalse(service_account_exists(sa_name))

    def test_delete_bogus_cluster_role(self):
        self.assertEqual(None, delete_cluster_role('bogus'))

    def test_delete_bogus_cluster_role_binding(self):
        self.assertEqual(None, delete_cluster_role_binding('bogus'))
