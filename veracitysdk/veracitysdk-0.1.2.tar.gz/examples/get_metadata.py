import os
import sys

from veracitysdk import Client, MetadataType

def catch_err(err):
	if err:
		print(err.data)
		sys.exit()


# Create client
client = Client(
	key = os.environ["VERACITY_KEY"],
	secret = os.environ["VERACITY_SECRET"],
)

# Perform a search
results, err = client.domains.search("thedailybeast.com")
catch_err(err)
print(results)

# Searches return a bare domain with minimal information
# Resolving will get the full domain object
# But isn't strictly necessary as the pk is all you need
# for child methods
domain, err = results[0].resolve()
catch_err(err)
print(domain)

whois, err = domain.metadata.get(MetadataType.Whois)
catch_err(err)
print(whois)

header_bidding, err = domain.metadata.get(MetadataType.HeaderBidding)
catch_err(err)
print(header_bidding)
