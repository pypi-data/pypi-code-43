# -*- coding: utf-8 -*-
"""SecretManager Class file."""

import base64

from bits.google.services.base import Base
# from googleapiclient.discovery import build
from google.auth.transport.requests import AuthorizedSession


class SecretManager(Base):
    """SecretManager class."""

    def __init__(self, credentials):
        """Initialize a class instance."""
        # self.sm = build('secretmanager', 'v1alpha', credentials=credentials)
        self.api_version = 'v1alpha'
        self.base_url = 'https://secretmanager.googleapis.com/%s' % (
            self.api_version,
        )
        self.credentials = credentials
        self.requests = AuthorizedSession(self.credentials)

    #
    # Secrets
    #
    def create_secret(self, project, secretId, regions=['us-central1']):
        """Create a secret."""
        url = '%s/projects/%s/secrets' % (self.base_url, project)
        params = {
            'secretId': secretId,
        }
        body = {
            'policy': {
                'replicaLocations': regions,
            }
        }
        self.requests.headers['Content-Type'] = 'application/json'
        self.requests.headers['X-Goog-User-Project'] = project
        return self.requests.post(url, json=body, params=params).json()

    def delete_secret(self, project, secretId):
        """Create a secret version."""
        url = '%s/projects/%s/secrets/%s' % (self.base_url, project, secretId)
        self.requests.headers['Content-Type'] = 'application/json'
        self.requests.headers['X-Goog-User-Project'] = project
        return self.requests.delete(url).json()

    def get_secrets(self, project):
        """List secrets in a project."""
        url = '%s/projects/%s/secrets' % (self.base_url, project)
        self.requests.headers['Content-Type'] = 'application/json'
        self.requests.headers['X-Goog-User-Project'] = project
        return self.requests.get(url).json().get('secrets', [])

    def update_secret(self, project, secretId, regions=['us-central1']):
        """Patch a secret to change the replica locations."""
        url = '%s/projects/%s/secrets/%s' % (self.base_url, project, secretId)
        params = {
            'updateMask': 'policy.replicaLocations',
        }
        body = {
            'policy': {
                'replicaLocations': regions,
            }
        }
        self.requests.headers['Content-Type'] = 'application/json'
        self.requests.headers['X-Goog-User-Project'] = project
        return self.requests.patch(url, json=body, params=params).json()

    #
    # Versions
    #
    def access_latest_version(self, project, secretId):
        """List latest version of a secret in a project."""
        url = '%s/projects/%s/secrets/%s/latest:access' % (
            self.base_url,
            project,
            secretId,
        )
        self.requests.headers['Content-Type'] = 'application/json'
        self.requests.headers['X-Goog-User-Project'] = project
        return self.requests.get(url).json()

    def access_version(self, project, secretId, versionId):
        """List latest version of a secret in a project."""
        url = '%s/projects/%s/secrets/%s/versions/%s' % (
            self.base_url,
            project,
            secretId,
            versionId
        )
        self.requests.headers['Content-Type'] = 'application/json'
        self.requests.headers['X-Goog-User-Project'] = project
        return self.requests.get(url).json()

    def create_version(self, project, secretId, text):
        """Create a secret version."""
        url = '%s/projects/%s/secrets/%s:setPayload' % (self.base_url, project, secretId)
        secret = base64.b64encode(text.encode('utf-8')).decode('utf-8')
        body = {
            'payload': {
                'data': secret,
            }
        }
        self.requests.headers['Content-Type'] = 'application/json'
        self.requests.headers['X-Goog-User-Project'] = project
        return self.requests.post(url, json=body).json()

    def destroy_version(self, project, secretId, versionId):
        """Create a secret version."""
        url = '%s/projects/%s/secrets/%s/versions/%s:destroy' % (
            self.base_url,
            project,
            secretId,
            versionId,
        )
        self.requests.headers['Content-Type'] = 'application/json'
        self.requests.headers['X-Goog-User-Project'] = project
        return self.requests.post(url).json()

    def disable_version(self, project, secretId, versionId):
        """Enable a version of a secret in a project."""
        self.update_version(project, secretId, versionId, 'DISABLED')

    def enable_version(self, project, secretId, versionId):
        """Enable a version of a secret in a project."""
        self.update_version(project, secretId, versionId, 'ENABLED')

    def update_version(self, project, secretId, versionId, state):
        """Enable a version of a secret in a project."""
        url = '%s/projects/%s/secrets/%s/versions/%s' % (
            self.base_url,
            project,
            secretId,
            versionId
        )
        params = {
            'updateMask': 'state',
        }
        body = {
            'state': state,
        }
        self.requests.headers['Content-Type'] = 'application/json'
        self.requests.headers['X-Goog-User-Project'] = project
        return self.requests.patch(url, json=body, params=params).json()

    def get_versions(self, project, secretId):
        """List versions of a secret in a project."""
        url = '%s/projects/%s/secrets/%s/versions' % (self.base_url, project, secretId)
        self.requests.headers['Content-Type'] = 'application/json'
        self.requests.headers['X-Goog-User-Project'] = project
        return self.requests.get(url).json().get('versions', [])
