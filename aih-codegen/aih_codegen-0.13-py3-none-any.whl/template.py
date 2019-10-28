
template = {
    'schema': '''
const { gql } = require("apollo-server-lambda");

const typeDefs = gql`
type Mutation {
  {% for type in types %}
  create{{ type["name"] }}(input: Create{{ type["name"] }}Input!): {{ type["name"] }}
  update{{ type["name"] }}(id: ID!, input: Update{{ type["name"] }}Input!): {{ type["name"] }}
  delete{{ type["name"] }}(id: ID!): Boolean
  {% endfor %}
}

type Query {
  {% for type in types %}
  get{{ type["name"] }}(id: ID!): {{ type["name"] }}
  get{{ type["name"] }}s: [{{ type["name"] }}!]
  {% endfor %}
}

{% for type in types %}
input Create{{ type["name"] }}Input {
  {% for field in type["fields"] %}
  {{ field["name"] }}: {{ field["type"] }}{{ '!' if field["required"] else '' }}
  {% endfor %}
}

input Update{{ type["name"] }}Input {
  {% for field in type["fields"] %}
  {{ field["name"] }}: {{ field["type"] }}
  {% endfor %}
}

{% endfor %}

{% for type in types %}
type {{ type["name"] }} {
  id: ID!
  {% for field in type["fields"] %}
  {{ field["name"] }}: {{ field["type"] }}{{ '!' if field["required"] else '' }}
  {% endfor %}
}

{% endfor %}
`;

module.exports = typeDefs;
    ''',
    'resolver': '''
const db = require('./db');

const resolver = {
    Query: {
        {% for type in types %}
        get{{ type["name"] }}: (_, args) => {
            return db.getTable("{{ type["ref"] }}").getRecordById(args.id).then(data => {
                return data.Item
            }).catch(err => null);
        },
        get{{ type["name"] }}s: (_, args) => {
            return  db.getTable("{{ type["ref"] }}").getRecords({}).then(data => {
                return data.Items
            }).catch(err => null);
        },
        {% endfor %}
    },
    Mutation: {
        {% for type in types %}
        create{{ type["name"] }}: (_, args) => {
            return db.getTable("{{ type["ref"] }}")
            .insertRecord(args.input)
            .then(data => data)
            .catch(err => {
                throw err;
            })
        },
        delete{{ type["name"] }}: (_, args) => {
            return db.getTable("{{ type["ref"] }}")
                .deleteRecordById(args.id)
                .then(data => true)
                .catch(err => false);
        },
        update{{ type["name"] }}: (_, args) => {
            return db.getTable("{{ type["ref"] }}")
                .updateRecordById(args.id, args.input)
                .then(data => data.Attributes)
                .catch(err => null);
        },
        {% endfor %}
    }
}

module.exports = resolver;
    '''
}