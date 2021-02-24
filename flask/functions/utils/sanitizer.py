import logging
from flask_inputs.validators import JsonSchema
from flask_inputs import Inputs

schema_linear = {
    'type': 'object',
    'properties': {
        'query': {'type': 'string'},
        'start_date': {'type': 'string'},
        'end_date': {'type': 'string'},
        'trunc_by': {'type': 'string'}
    },
    'required': ['query'],
    'additionalProperties': False
}

class LinearRegressionInputs(Inputs):
    json = [JsonSchema(schema=schema_linear)]

