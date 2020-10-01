#!/usr/bin/env python3
#author: Harshvardhan J. Pandit 

'''Generates ReSpec documentation for DPV using RDF and SPARQL'''

# The vocabularies are modular

IMPORT_TTL_PATH = './vocab_rdf'
EXPORT_HTML_PATH = './docs'

from rdflib import Graph, Namespace
from rdflib import URIRef
from rdform import DataGraph, RDFS_Resource
import logging
# logging configuration for debugging to console
logging.basicConfig(
    level=logging.DEBUG, format='%(levelname)s - %(funcName)s :: %(lineno)d - %(message)s')
DEBUG = logging.debug

# UGLY UGLY globals
G = None
TEMPLATE_DATA = {}


def load_data(label, filepath):
    global G
    g = Graph()
    g.load(filepath, format='turtle')
    G = DataGraph()
    G.load(g)
    G.graph.ns = { k:v for k,v in G.graph.namespaces() }
    classes = G.get_instances_of('rdfs_Class')
    # for c in classes:
    #     print(c, c.__dict__['metadata'].keys())
    TEMPLATE_DATA[f'{label}_classes'] = classes
    TEMPLATE_DATA[f'{label}_properties'] = G.get_instances_of('rdf_Property')


def prefix_this(item):
    # DEBUG(f'item: {item} type: {type(item)}')
    if type(item) is RDFS_Resource:
        item = item.iri
    elif type(item) is URIRef:
        item = str(item)
    if type(item) is str and item.startswith('http'):
        iri = URIRef(item).n3(G.graph.namespace_manager)
    else:
        iri = item
    if iri.count('_') > 0:
        iri = iri.split('_', 1)[1]
    # DEBUG(f'prefixed {item} to: {iri}')
    return iri


def fragment_this(item):
    if '#' not in item:
        return item
    return item.split('#')[-1]


# LOAD DATA
load_data('core', f'{IMPORT_TTL_PATH}/base.ttl')
load_data('personaldata', f'{IMPORT_TTL_PATH}/personal_data_categories.ttl')
load_data('purpose', f'{IMPORT_TTL_PATH}/purposes.ttl')
load_data('processing', f'{IMPORT_TTL_PATH}/processing.ttl')
load_data('technical_organisational_measures', f'{IMPORT_TTL_PATH}/technical_organisational_measures.ttl')
load_data('entities', f'{IMPORT_TTL_PATH}/entities.ttl')
load_data('consent', f'{IMPORT_TTL_PATH}/consent.ttl')


# generate HTML
from jinja2 import FileSystemLoader, Environment
JINJA2_FILTERS = {
    'fragment_this': fragment_this,
    'prefix_this': prefix_this,
}

template_loader = FileSystemLoader(searchpath='./jinja2_resources')
template_env = Environment(
    loader=template_loader, 
    autoescape=True, trim_blocks=True, lstrip_blocks=True)
template_env.filters.update(JINJA2_FILTERS)
template = template_env.get_template('template_dpv.jinja2')
with open(f'{EXPORT_HTML_PATH}/index.html', 'w+') as fd:
    fd.write(template.render(**TEMPLATE_DATA))
DEBUG(f'wrote DPV spec at f{EXPORT_HTML_PATH}/index.html')

# dpv-gdpr

load_data('dpv_gdpr', f'{IMPORT_TTL_PATH}/dpv-gdpr.ttl')
template = template_env.get_template('template_dpv_gdpr.jinja2')
with open(f'{EXPORT_HTML_PATH}/dpv-gdpr.html', 'w+') as fd:
    fd.write(template.render(**TEMPLATE_DATA))
DEBUG(f'wrote DPV-GDPR spec at f{EXPORT_HTML_PATH}/dpv-gdpr.html')

DEBUG('--- END ---')