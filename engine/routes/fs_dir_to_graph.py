#!/usr/bin/env python
"""Upload a FreeSurfer directory structure as RDF to a SPARQL triplestore
"""

# standard library
from datetime import datetime as dt
import hashlib
import os
import pwd
from socket import getfqdn
import uuid

from utils import (prov, foaf, dcterms, fs, nidm, niiri, obo, nif, crypto,
                   hash_infile, get_id)

# map FreeSurfer filename parts
fs_file_map = [('T1', [nif["nlx_inv_20090243"]]),  # 3d T1 weighted scan
               ('lh', [(nidm["AnatomicalAnnotation"], obo["UBERON_0002812"])]),  # left cerebral hemisphere
               ('rh', [(nidm["AnatomicalAnnotation"], obo["UBERON_0002813"])]),  # right cerebral hemisphere
               ('BA.', [(nidm["AnatomicalAnnotation"], obo["UBERON_0013529"])]),  # Brodmann area
               ('BA1.', [(nidm["AnatomicalAnnotation"], obo["UBERON_0006099"])]),  # Brodmann area 1
               ('BA2.', [(nidm["AnatomicalAnnotation"], obo["UBERON_0013533"])]),  # Brodmann area 2
               ('BA3a.', [(nidm["AnatomicalAnnotation"], obo["UBERON_0006100"]),  # Brodmann area 3a
                          (nidm["AnatomicalAnnotation"], obo["FMA_74532"])]),  # anterior
               ('BA3b.', [(nidm["AnatomicalAnnotation"], obo["UBERON_0006100"]),  # Brodmann area 3b
                          (nidm["AnatomicalAnnotation"], obo["FMA_74533"])]),  # posterior
               ('BA44.', [(nidm["AnatomicalAnnotation"], obo["UBERON_0006481"])]),  # Brodmann area 44
               ('BA45.', [(nidm["AnatomicalAnnotation"], obo["UBERON_0006482"])]),  # Brodmann area 45
               ('BA4a.', [(nidm["AnatomicalAnnotation"], obo["UBERON_0013535"]),  # Brodmann area 4a
                          (nidm["AnatomicalAnnotation"], obo["FMA_74532"])]),  # anterior
               ('BA4p.', [(nidm["AnatomicalAnnotation"], obo["UBERON_0013535"]),  # Brodmann area 4p
                          (nidm["AnatomicalAnnotation"], obo["FMA_74533"])]),  # posterior
               ('BA6.', [(nidm["AnatomicalAnnotation"], obo["UBERON_0006472"])]),  # Brodmann area 6
               ('V1.', [(nidm["AnatomicalAnnotation"], obo["UBERON_0002436"])]),
               ('V2.', [(nidm["AnatomicalAnnotation"], obo["UBERON_0006473"])]),
               ('MT', [(nidm["AnatomicalAnnotation"], fs["MT_area"])]),
               ('entorhinal', [(nidm["AnatomicalAnnotation"], obo["UBERON_0002728"])]),
               ('exvivo', [(nidm["AnnotationSource"], fs["exvivo"])]),
               ('label', [(fs["FileType"], fs["label_file"])]),
               ('annot', [(fs["FileType"], fs["annotation_file"])]),
               ('cortex', [(nidm["AnatomicalAnnotation"], obo["UBERON_0000956"])]),
               ('.stats', [(fs["FileType"], fs["statistic_file"])]),
               ('aparc.annot', [(nidm["AtlasName"], fs["default_parcellation"])]),
               ('aparc.a2009s', [(nidm["AtlasName"], fs["a2009s_parcellation"])]),
               ('.ctab', [(fs["FileType"], fs["color_table"])])
               ]

# files or directories that should be ignored
ignore_list = ['bak', 'src', 'tmp', 'trash', 'touch']


def create_entity(graph, fs_subject_id, filepath, hostname):
    """ Create a PROV entity for a file in a FreeSurfer directory
    """
    # identify FreeSurfer terms based on directory and file names
    _, filename = os.path.split(filepath)
    relpath = filepath.split(fs_subject_id)[1].lstrip(os.path.sep)
    fstypes = relpath.split('/')[:-1]
    additional_types = relpath.split('/')[-1].split('.')

    file_md5_hash = hash_infile(filepath, crypto=hashlib.md5)
    file_sha512_hash = hash_infile(filepath, crypto=hashlib.sha512)
    if file_md5_hash is None:
        print('Empty file: %s' % filepath)

    #url = "file://%s%s" % (hostname, filepath)
    url = filepath
    url_get = prov.URIRef("http://localhost/file?file=%s" % filepath)
    url_get = prov.URIRef("file://%s" % filepath)
    obj_attr = [(prov.PROV["label"], filename),
                (fs["relative_path"], "%s" % relpath),
                (prov.PROV["location"], url_get),
                (crypto["md5"], "%s" % file_md5_hash),
                (crypto["sha"], "%s" % file_sha512_hash)
                ]

    for key in fstypes:
        obj_attr.append((nidm["tag"], key))
    for key in additional_types:
        obj_attr.append((nidm["tag"], key))

    for key, uris in fs_file_map:
        if key in filename:
            if key.rstrip('.').lstrip('.') not in fstypes + additional_types:
                obj_attr.append((nidm["tag"], key.rstrip('.').lstrip('.')))
            for uri in uris:
                if isinstance(uri, tuple):
                    obj_attr.append((uri[0], uri[1]))
                else:
                    obj_attr.append((prov.PROV["type"], uri))
    id = get_id()
    return graph.entity(id, obj_attr)


def encode_fs_directory(g, basedir, subject_id, hostname=None,
                        n_items=100000):
    """ Convert a FreeSurfer directory to a PROV graph
    """
    # directory collection/catalog
    collection_hash = get_id()
    fsdir_collection = g.collection(collection_hash)
    fsdir_collection.add_extra_attributes({prov.PROV['type']: fs['subject_directory'],
                                           fs['subject_id']: subject_id})
    directory_id = g.entity(get_id())
    if hostname == None:
        hostname = getfqdn()
    url = "file://%s%s" % (hostname, os.path.abspath(basedir))
    directory_id.add_extra_attributes({prov.PROV['location']: prov.URIRef(url)})
    g.wasDerivedFrom(fsdir_collection, directory_id)

    a0 = g.activity(get_id(), startTime=dt.isoformat(dt.utcnow()))
    user_agent = g.agent(get_id(),
                         {prov.PROV["type"]: prov.PROV["Person"],
                          prov.PROV["label"]: pwd.getpwuid(os.geteuid()).pw_name,
                          foaf["name"]: pwd.getpwuid(os.geteuid()).pw_name})
    g.wasAssociatedWith(a0, user_agent, None, None,
                        {prov.PROV["Role"]: nidm["LoggedInUser"]})
    g.wasGeneratedBy(fsdir_collection, a0)

    i = 0
    for dirpath, dirnames, filenames in os.walk(os.path.realpath(basedir)):
        for filename in sorted(filenames):
            if filename.startswith('.'):
                continue
            i += 1
            if i > n_items:
                break
            file2encode = os.path.realpath(os.path.join(dirpath, filename))
            if not os.path.isfile(file2encode):
                print "%s not a file" % file2encode
                continue
            ignore_key_found = False
            for key in ignore_list:
                if key in file2encode:
                    ignore_key_found = True
                    continue
            if ignore_key_found:
                continue
            try:
                entity = create_entity(g, subject_id, file2encode, hostname)
                g.hadMember(fsdir_collection, entity.get_identifier())
            except IOError, e:
                print e
    return g


def to_graph(subject_specific_dir):
    # location of FreeSurfer $SUBJECTS_DIR
    basedir = os.path.abspath(subject_specific_dir)
    subject_id = basedir.rstrip(os.path.sep).split(os.path.sep)[-1]

    # location of the ProvToolBox commandline conversion utility
    graph = prov.ProvBundle(identifier=get_id())
    graph.add_namespace(foaf)
    graph.add_namespace(dcterms)
    graph.add_namespace(fs)
    graph.add_namespace(nidm)
    graph.add_namespace(niiri)
    graph.add_namespace(obo)
    graph.add_namespace(nif)
    graph.add_namespace(crypto)

    graph = encode_fs_directory(graph, basedir, subject_id)
    return graph

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(prog='fs_dir_to_graph.py',
                                     description=__doc__)
    parser.add_argument('-s', '--subject_dir', type=str, required=True,
                        help='Path to subject directory to upload')
    parser.add_argument('-p', '--project_id', type=str, required=True,
                        help='Project tag to use for the subject directory.')
    parser.add_argument('-e', '--endpoint', type=str,
                        help='SPARQL endpoint to use for update')
    parser.add_argument('-g', '--graph_iri', type=str,
                        help='Graph IRI to store the triples')
    parser.add_argument('-o', '--output_dir', type=str,
                        help='Output directory')
    parser.add_argument('-n', '--hostname', type=str,
                        help='Hostname for file url')

    args = parser.parse_args()
    if args.output_dir is None:
        args.output_dir = os.getcwd()

    graph = to_graph(args.subject_dir, args.project_id, args.output_dir,
                     args.hostname)
