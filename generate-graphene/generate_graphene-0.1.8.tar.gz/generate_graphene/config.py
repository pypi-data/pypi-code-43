from graphql import GraphQLError

DEFAULT_FILTERS_FIELDS = ["id"]


class UserError(GraphQLError):
    pass
