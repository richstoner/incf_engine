#!/usr/bin/env python
"""Run FreeSurfer on a T1 image and capture all output as NIDM
"""
import os

import urllib
import urlparse
from StringIO import StringIO

from nipype.interfaces.base import CommandLine
CommandLine.set_default_terminal_output('allatonce')

from nipype import config
config.enable_provenance()

import rdflib

def run_bet(T1_image, workdir):
    """Run freesurfer, convert to nidm and extract stats
    """
    from nipype import fsl
    from nipype import Node
    from fs_dir_to_graph import to_graph
    from query_convert_fs_stats import get_collections, process_collection

    strip = Node(fsl.BET(), name='skullstripper')
    strip.inputs.in_file = T1_image
    strip.base_dir = workdir

    results = strip.run()
    provgraph = results.provenance
    return provgraph


from uuid import uuid1
import hashlib
from utils import hash_infile

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(prog='fs_dir_to_graph.py',
                                     description=__doc__)
    parser.add_argument('-i', '--in_graph', type=str, required=True,
                        help='Path to input graph turtle file')
    parser.add_argument('-e', '--endpoint', type=str,
                        help='SPARQL endpoint to use for update')
    parser.add_argument('-g', '--graph_iri', type=str,
                        help='Graph IRI to store the triples')
    parser.add_argument('-o', '--output_dir', type=str, required=True,
                        help='Output directory')

    args = parser.parse_args()

    rdfingraph = rdflib.Graph().parse(args.in_graph, format='turtle')

    """
    Parse the input graph to get subject id and a list of T1 files

    """
    t1_query = """
        PREFIX prov: <http://www.w3.org/ns/prov#>
        PREFIX nif: <http://neurolex.org/wiki/>
        PREFIX crypto: <http://www.w3.org/2000/10/swap/crypto#>
        select ?t1path ?sha where
        {?e a prov:Entity;
            a nif:nlx_inv_20090243;
            crypto:sha ?sha;
            prov:location ?t1path .
        }
    """
    t1_result = rdfingraph.query(t1_query)

    """
    Retrieve the file into wd
    """
    out_T1_files = []
    for idx, info in enumerate(t1_result.bindings):
        o = urlparse.urlparse(info['?t1path'])
        if o.scheme.startswith('file'):
            uri = 'file://' + o.path
        else:
            uri = info['?t1path']
        filename = os.path.join(args.work_dir,
                                'file_%d_' % idx + os.path.split(o.path)[-1])
        urllib.urlretrieve(uri, filename)
        if hash_infile(filename, crypto=hashlib.sha512) != str(info['?sha']):
            raise IOError("Hash of file doesn't match remote hash")
        out_T1_files.append(filename)


    """
    Run freesurfer and convert to rdf
    """
    subject_dir = os.path.abspath('subjects')
    if not os.path.exists(subject_dir):
        os.mkdir(subject_dir)
    provgraph, rdfgraph = run_freesurfer(subject_id,
                                         out_T1_files,
                                         subject_dir)

    # TODO: Need to reconcile rdfingraph and rdfgraph based on file hashes

    newgraph = rdflib.Graph().parse(StringIO(rdfgraph.serialize()))
    newgraph.serialize('outfile.ttl', format='turtle')

    context = {('@%s' % k): v for k, v in newgraph.namespaces()}
    newgraph.serialize('outfile.json', context=context, format='json-ld')