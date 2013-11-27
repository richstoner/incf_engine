__author__ = 'Nolan Nichols <nolan.nichols@gmail.com>'


def parse_payload(payload):
    """
    Parses the JSON-LD payload from a job submission
    """
    data = json.loads(payload)
    expanded = json.dumps(jsonld.expand(data))
    g = rdflib.Graph(identifier=data['@id'])
    g.parse(data=expanded, format='json-ld')
    return g
