__author__ = 'Nolan Nichols <nolan.nichols@gmail.com>'

import json

import rdflib


#TODO: handle both json-ld and turtle
def parse_payload(payload):
    """
    Parses the JSON-LD payload from a put request to the JobsList resource

    Returns submitted graph with added job parameters
    """
    graph_iri = get_graph_iri(payload)
    g = rdflib.ConjunctiveGraph(identifier=graph_iri)
    g.parse(data=payload, format='json-ld')
    return g


def submit_job(graph, context):
    """
    Submits jobs based on process type
    """
    job_ctx = {"status": "http://nidm.nidash.org/jobStatus",
               "percent": {"@id": "http://nidm.nidash.org/percentComplete",
                           "@type": "xsd:integer"}}
    context.update(job_ctx)
    status = rdflib.URIRef("http://nidm.nidash.org/jobStatus")
    percent = rdflib.URIRef("http://nidm.nidash.org/percentComplete")
    graph.add([graph.identifier, status, rdflib.Literal('submitted')])
    graph.add([graph.identifier, percent, rdflib.Literal(0)])
    job_json_ld = graph.serialize(format='json-ld', context=context)
    return job_json_ld


def get_graph_iri(json_ld):
    """Identify the non-bnode context of a graph"""
    g = rdflib.ConjunctiveGraph()
    g.parse(data=json_ld, format='json-ld')
    for context in g.contexts():
        if not isinstance(context.identifier, rdflib.BNode):
            graph_iri = str(context.identifier)
    return graph_iri
