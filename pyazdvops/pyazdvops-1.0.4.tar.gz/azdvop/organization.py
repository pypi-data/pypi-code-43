import logging
from redishttp import HttpClient
from project import Project

logger = logging.getLogger(__name__)

class Organization():
  _client = HttpClient('')
  _organization = ''

  def __init__(self, pat, organization, redis_host = 'localhost', redis_port = 6379, redis_password = None, cache_expiry = 1):
    self._client = HttpClient(pat)
    self._organization = organization

  def query_organization(self, ids, organization = None):
    if organization == None:
      organization = self._organization
    return self._client.post('https://dev.azure.com/{organization}/_apis/Contribution/HierarchyQuery'.format(organization = organization), {
      'contributionIds': ids }, {
      'Accept': 'application/json;api-version=5.0-preview.1;excludeUrls=true;enumsAsNumbers=true;msDateFormat=true;noArrayWrap=true',
      'Content-Type': 'application/json'
    }, cache=True)
  
  def get_organizations(self):
    r = self.query_organization(['ms.vss-features.my-organizations-data-provider'])
    return r['dataProviders']['ms.vss-features.my-organizations-data-provider']['organizations']

  def get_organization(self, organization_name):
    r = self.query_organization(["ms.vss-admin-web.organization-admin-new-overview-component","ms.vss-admin-web.organization-admin-overview-data-provider"], organization_name)
    organization = r['dataProviders']['ms.vss-admin-web.organization-admin-overview-data-provider']
    organization['subscription_details'] = self._client.get('https://commerceprodwus21.vscommerce.visualstudio.com/_apis/Subscription/Subscription?providerNamespaceId=0&accountId={account_id}'.format(account_id=organization['id']))
    return organization

  def get_projects(self, organization_name):
    return self._client.get('https://dev.azure.com/{}/_apis/projects?api-version=6.0-preview.4'.format(organization_name))
