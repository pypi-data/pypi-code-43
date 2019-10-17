import logging
from redishttp import HttpClient

logger = logging.getLogger(__name__)

license_map = {
  'basic': 'ms.vss-vstsuser',
  'testplan': 'ms.vss-testmanager-web',
  'hostedagent': 'ms.build-release-hosted-pipelines',
  'selfhostedagent': 'ms.build-release-private-pipelines',
  'artifacts': 'ms.artifacts'
}

class AzDevOps:
  _organization = ''
  _client = HttpClient('')

  def __init__(self, pat, organization):
    omitted = pat[:5]
    for i in range(len(pat) - 5):
      omitted = omitted + '*'
    logger.debug('Initializing with pat {omitted}'.format(omitted = omitted))
    self._organization = organization
    self._client = HttpClient(pat)
  
  def set_redis(self, host, port, password = None, cache_expiry = 1):
    self._client.set_redis(host, port, password, cache_expiry)

  def query_organization(self, ids, organization = None):
    if organization == None:
      organization = self._organization
    return self._client.post('https://dev.azure.com/{organization}/_apis/Contribution/HierarchyQuery'.format(organization = self._organization), {
      'contributionIds': ids }, {
      'Accept': 'application/json;api-version=5.0-preview.1;excludeUrls=true;enumsAsNumbers=true;msDateFormat=true;noArrayWrap=true',
      'Content-Type': 'application/json'
    })
  
  def get_organization(self, organization_name):
    r = self.query_organization(["ms.vss-admin-web.organization-admin-new-overview-component","ms.vss-admin-web.organization-admin-overview-data-provider"], organization_name)
    organization = r['dataProviders']['ms.vss-admin-web.organization-admin-overview-data-provider']

    organization['subscription_details'] = self._client.get('https://commerceprodwus21.vscommerce.visualstudio.com/_apis/Subscription/Subscription?providerNamespaceId=0&accountId={account_id}'.format(account_id=organization['id']))
    return organization
  
  def find_users(self, organization_name, query):
    results = self._client.post('https://dev.azure.com/{organization_name}/_apis/IdentityPicker/Identities'.format(organization_name = organization_name), {
        "query": query,
        "identityTypes":["user","group"],
        "operationScopes":["ims","source"],
        "properties":[
          "DisplayName",
          "IsMru",
          "ScopeName",
          "SamAccountName",
          "Active",
          "SubjectDescriptor",
          "Department",
          "JobTitle",
          "Mail",
          "MailNickname",
          "PhysicalDeliveryOfficeName",
          "SignInAddress",
          "Surname",
          "Guest",
          "TelephoneNumber",
          "Description"],
        "filterByAncestorEntityIds":[],
        "filterByEntityIds":[],
        "options":{
          "MinResults":40,
          "MaxResults":40
        }
      }, {
        'Accept': 'application/json;api-version=6.0-preview.1;excludeUrls=true',
        'Content-Type': 'application/json'
      })
    if len(results['results']) > 0:
      return results['results'][0]['identities']
    else:
      return []

  def get_organizations(self):
    r = self.query_organization(['ms.vss-features.my-organizations-data-provider'])
    return r['dataProviders']['ms.vss-features.my-organizations-data-provider']['organizations']

  def get_licenses(self, organization):
    r = self._client.get('https://vsaex.dev.azure.com/{organization}/_apis/UserEntitlementSummary?select=accesslevels%2Clicenses'.format(organization=organization))
    return r['licenses']
  
  def get_projects(self, organization_name):
    r = self._client.get('https://dev.azure.com/{organization}/_apis/projects?api-version=6.0-preview.4'.format(organization=organization_name))
    return r['value']
  
  def get_project_teams(self, organization_name, project_id):
    r = self._client.get('https://dev.azure.com/{organization}/_apis/projects/{project_id}/teams?api-version=6.0-preview.3'.format(organization = organization_name, project_id = project_id))
    return r['value']

  def get_project_team(self, organization_name, project_id, team_id):
    team = self._client.get('https://dev.azure.com/{organization}/_apis/projects/{projectId}/teams/{teamId}?api-version=6.0-preview.3'.format(organization = organization_name, projectId = project_id, teamId = team_id))
    team['members'] = []
    members = self._client.get('https://dev.azure.com/{organization}/{project_id}/_api/_identity/ReadGroupMembers?__v=5&scope={team_id}&readMembers=true&scopedMembershipQuery=1'.format(organization = organization_name, project_id = project_id, team_id = team_id))['identities']
    team['members'] = [member for member in members if member['IdentityType'] == 'user']
    return team

  def get_memberships(self, organization):
    return self._client.get('https://vsaex.dev.azure.com/{organization}/_apis/userentitlements?api-version=5.1-preview.2&top=1000&skip=0'.format(organization=organization))['members']
  
  def get_membership(self, organization, member_id):
    return self._client.get('https://vsaex.dev.azure.com/{organization}/_apis/userentitlements/{member_id}?api-version=5.1-preview.2'.format(member_id=member_id, organization=organization))

  def get_membership_details(self, organization):
    members = self.get_memberships(organization)
    for member in members:
      member = self.get_membership(organization, member['id'])
    return members
  
  def set_stakeholder(self, organization, member_id):
    self._client.patch('https://vsaex.dev.azure.com/{organization}/_apis/UserEntitlements/{member_id}'.format(member_id = member_id, organization = organization), [{
      'from': '',
      'op': 2,
      'path': '/accessLevel',
      'value': {
        'accountLicenseType': 5,
        'licensingSource': 1
      }
    }], {
      'Accept': 'application/json;api-version=5.1-preview.2;excludeUrls=true',
      'Content-Type': 'application/json-patch+json'
    })

  def set_basic(self, organization, member_id):
    self._client.patch('https://vsaex.dev.azure.com/{organization}/_apis/UserEntitlements/{member_id}'.format(member_id = member_id, organization = organization), [{
      'from': '',
      'op': 2,
      'path': '/accessLevel',
      'value': {
        'accountLicenseType': 2,
        'licensingSource': 1
      }
    }], {
      'Accept': 'application/json;api-version=5.1-preview.2;excludeUrls=true',
      'Content-Type': 'application/json-patch+json'
    })

  def set_testplan(self, organization, member_id):
    self._client.patch('https://vsaex.dev.azure.com/{organization}/_apis/UserEntitlements/{member_id}'.format(member_id = member_id, organization = organization), [{
      'from': '',
      'op': 2,
      'path': '/accessLevel',
      'value': {
        'accountLicenseType': 4,
        'licensingSource': 1
      }
    }], {
      'Accept': 'application/json;api-version=5.1-preview.2;excludeUrls=true',
      'Content-Type': 'application/json-patch+json'
    })

  def update_license(self, organization, quantity, licence_type):
    if licence_type not in license_map:
      raise Exception('License type is invalid. Use following: {}'.format(license_map))
    organization = self.get_organization(organization)
    self._client.post('https://commerceprodwus21.vscommerce.visualstudio.com/_apis/OfferSubscription/OfferSubscription?billingTarget={organizationId}&skipSubscriptionValidation=true'.format(organizationId=organization['id']), {
      "azureSubscriptionId": organization['subscription_details']['subscriptionId'],
      "committedQuantity": str(quantity),
      "offerMeter": {
        "galleryId": license_map[licence_type]
      },
      "renewalGroup": 'null'
    }, {
      'Accept': 'application/json;api-version=5.1-preview.1;excludeUrls=true;enumsAsNumbers=true;msDateFormat=true;noArrayWrap=true',
      'Content-Type': 'application/json'
    }, cache=True)

  def update_basic_license(self, organization, quantity):
    self.update_license(organization, quantity, 'basic')
  
  def update_testplan_license(self, organization, quantity):
    self.update_license(organization, quantity, 'testplan')
  
  def update_hosted_agent(self, organization, hosted_agent_count):
    self.update_license(organization, hosted_agent_count, 'hostedagent')

  def update_selfhosted_agent(self, organization, selfhosted_agent_count):
    self.update_license(organization, selfhosted_agent_count, 'selfhostedagent')

  def update_artifact_quota(self, organization, quota):
    self.update_license(organization, quota, 'artifacts')

  def get_all_builds(self, organization, project, start_date, end_date):
    return self._client.get('https://dev.azure.com/{organization}/{project}/_apis/build/builds?api-version=5.1&minTime={start_date}&maxTime={end_date}'
      .format(organization = organization, project = project, start_date = start_date.strftime('%Y-%m-%d'), end_date = end_date.strftime('%Y-%m-%d')))['value']
