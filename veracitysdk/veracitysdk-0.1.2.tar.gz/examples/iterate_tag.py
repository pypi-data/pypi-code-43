import os
import sys

from veracitysdk import Client, TagModel, TagType, paginated

def catch_err(err):
	if err:
		print(err.data)
		sys.exit()


# Create client
client = Client(
	key = os.environ["VERACITY_KEY"],
	secret = os.environ["VERACITY_SECRET"],
)


# Create tag
#tag, err = client.tags.create(
#	"share",
#	TagModel.Domain,
#	TagType.String
#)
#catch_err(err)

# Get tag
tag, err = client.tags.get("shu:share")
catch_err(err)
print(tag)

tag, err = tag.update("Test description")
catch_err(err)
print(tag)


# The paginated helper helps with pagination
# items, err = tag.search_by_value("8f4921ae", page=1)

items = paginated(tag.search_by_value, "8f4921ae")
for item in items:
	print(item)
