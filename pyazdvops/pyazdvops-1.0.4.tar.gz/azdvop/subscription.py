import requests, logging, json
from requests.auth import HTTPBasicAuth
from httpclient import HttpClient

logger = logging.getLogger(__name__)

meter_ids = {
  "express": "daf52501-330a-4a7a-a88a-cf85ed40988f",
  "hostedagent": "b40291f6-f450-429b-a21f-0bc6711787ac"
}

class Subscription():
  organization = ''
  client = None

  def __init__(self, pat, organization, redis = None):
    self.client = HttpClient(pat, redis)
    self.organization = organization

  def get_licenses(self):
    r = self.client.get('https://vsaex.dev.azure.com/{organization}/_apis/UserEntitlementSummary?select=accesslevels%2Clicenses'.format(organization=self.organization))
    return json.loads(r['payload'])['licenses']
  
  def find_license(self, match):
    licenses = self.get_licenses()
    return next((lic for lic in licenses if lic['accountLicenseType'] == match), None)
  
  def get_basic_license(self):
    basic = self.find_license('express')
    if basic is not None:
      return {
        'total': basic['total'],
        'available': basic['available'],
        'nextBillingDate': basic['nextBillingDate'],
        'totalPurchased': basic['total'] - basic['includedQuantity'],
        'assigned': basic['assigned'],
        '_original': basic
      }
    else:
      return {}

  def get_testplan_license(self):
    testplan = self.find_license('advanced')
    if testplan is not None:
      return {
        'total': testplan['total'],
        'available': testplan['available'],
        'assigned': testplan['assigned'],
        '_original': testplan
      }
    else:
      return {}
  
  def get_detailed_licenses(self):
    r = self.client.get('https://vscommerce.dev.azure.com/{organization}/_apis/OfferSubscription/OfferSubscription?nextBillingPeriod=false'.format(organization = self.organization))
    return json.loads(r['payload'])['value']

  def get_hosted_pipeline(self):
    pass

  def get_onprem_pipeline(self):
    pass

  def get_total_vum(self):
    pass

  def get_artifact_quota(self):
    licenses = self.get_detailed_licenses()
    quota = next(lic for lic in licenses if lic['offerMeter']['platformMeterId'] == '06ead2d2-3e67-49e5-8ca3-6ce21fd1d5a1')
    return {
      'quantity': quota['includedQuantity'],
      'unit': quota['offerMeter']['unit'],
      'resetDate': quota['resetDate'],
      '_original': quota
    }
