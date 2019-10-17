from yams.buildobjs import EntityType, RelationDefinition, String


class ObjectOfInterest(EntityType):
    name = String(required=True, unique=True)


class interested_in(RelationDefinition):
    subject = 'CWUser'
    object = 'ObjectOfInterest'


class nosy_list(RelationDefinition):
    subject = 'ObjectOfInterest'
    object = 'CWUser'
