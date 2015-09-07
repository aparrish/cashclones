import rdflib
from rdflib import URIRef
from rdflib.namespace import RDFS

from jinja2 import Template

import random
import urllib
import json
import time
import re

def get_random_class(g):
    return random.choice(list(g.subjects(RDFS.subClassOf, None)))

def get_label_string(g, thing):
    return g.preferredLabel(thing, lang="en")[0][1]

def get_property(subj, prop):
    query = """
    SELECT ?prop
    WHERE { <%s> %s ?prop }
    """ % (subj, prop)
    qstr = urllib.urlencode(
            {'query': query, 'output': 'json', 'default-graph-uri': 'http://dbpedia.org'})
    resp = urllib.urlopen("http://dbpedia.org/sparql?" + qstr)
    obj = json.loads(resp.read())
    if len(obj['results']['bindings']) > 0:
        return obj['results']['bindings'][0]['prop']['value']
    else:
        return None

def schema_convert(url, val):
    from dateutil.parser import parse
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep",
            "Oct", "Nov", "Dec"]
    if url == "http://www.w3.org/2001/XMLSchema#date":
        val = re.sub("\+.*$", "", val)
        dt = parse(val)
        retval = "%s %d, %d" % (months[dt.month-1], dt.day, dt.year)
    elif url == "http://www.w3.org/2001/XMLSchema#gYear":
        val = re.sub("\+.*$", "", val)
        dt = parse(val)
        retval = str(dt.year)
    elif url == "http://www.w3.org/2001/XMLSchema#gMonthDay":
        val = re.sub("\+.*$", "", val)
        dt = parse(val)
        retval = "%s %d" % (months[dt.month-1], dt.day)
    else:
        retval = val
    return retval

def get_random_property(subj):
    filter_terms = ["ID","id","Id","image","Image","gray","dorlands","wiki",
            "lat","long","color","info","Info","homepage","map","Map",
            "updated","Updated","logo","Logo","pushpin","label","Label",
            "photo","Photo"]
    query = """
    SELECT ?property ?propertyLabel ?propertyVal ?propertyValLabel
    WHERE {
      <%s> ?property ?propertyVal.
      ?property rdfs:label ?propertyLabel.
      FILTER(lang(?propertyLabel) = "en").
      OPTIONAL {
        ?propertyVal rdfs:label ?propertyValLabel.
        FILTER(lang(?propertyValLabel) = "en").
      }
      FILTER(regex(?property, "..")).
      FILTER(!regex(?property, "(%s)")).
      FILTER(?property != <http://dbpedia.org/ontology/wikiPageRevisionID>).
      FILTER(?property != <http://dbpedia.org/ontology/wikiPageID>).   
      FILTER(?property != <http://dbpedia.org/ontology/abstract>).
      FILTER(?property != <http://dbpedia.org/ontology/wikiPageExternalLink>).
      FILTER(?property != <http://dbpedia.org/ontology/filename>).
      FILTER(?property != <http://dbpedia.org/property/imageSize>).
      FILTER(?property != <http://dbpedia.org/property/imagesize>).
      FILTER(?property != <http://dbpedia.org/property/logoImage>).
      FILTER(?property != <http://dbpedia.org/property/webpage>).
      FILTER(?property != <http://dbpedia.org/property/name>).
      FILTER(?property != <http://dbpedia.org/property/image>).
      FILTER(?property != <http://dbpedia.org/ontology/thumbnail>).
      FILTER(?property != <http://dbpedia.org/property/graypage>).
      FILTER(?property != <http://dbpedia.org/ontology/grayPage>).
      FILTER(?property != <http://dbpedia.org/property/imageCaption>).
      FILTER(?property != <http://dbpedia.org/property/id>).
      FILTER(?property != <http://dbpedia.org/property/photo>).
      FILTER(?property != <http://dbpedia.org/property/caption>).
      FILTER(?property != <http://dbpedia.org/ontology/graySubject>).
      FILTER(?property != <http://dbpedia.org/property/graysubject>).
      FILTER(?property != <http://dbpedia.org/property/website>).
      FILTER(?property != <http://dbpedia.org/property/imageName>).
      FILTER(?property != <http://dbpedia.org/ontology/dorlandsSuffix>).
      FILTER(?property != <http://dbpedia.org/property/dorlandssuf>).
      FILTER(?property != <http://dbpedia.org/property/signature>).
      FILTER(?property != <http://dbpedia.org/ontology/viafId>).
      FILTER(?property != <http://dbpedia.org/property/pixels>).
      FILTER(?property != <http://dbpedia.org/property/mapCaption>).
      FILTER(?property != <http://dbpedia.org/property/picture>).
      FILTER(?property != <http://dbpedia.org/property/imageFlag>).
      FILTER(?property != <http://dbpedia.org/property/neurolexid>). 
      FILTER(?property != <http://dbpedia.org/property/gnd>).
      FILTER(?property != <http://dbpedia.org/ontology/dorlandsPrefix>).
      FILTER(?property != <http://dbpedia.org/property/dorlandspre>).
      FILTER(?property != <http://dbpedia.org/property/imageWidth>).
      FILTER(?property != <http://dbpedia.org/property/verifiedrevid>).
    }
    """ % (subj, '|'.join(filter_terms))
    qstr = urllib.urlencode({'query': query, 'output': 'json',
        'default-graph-uri': 'http://dbpedia.org'})
    resp = urllib.urlopen("http://dbpedia.org/sparql?" + qstr)
    obj = json.loads(resp.read())
    properties = dict()
    for prop in obj['results']['bindings']:
        purl = prop['property']['value']
        plabel = prop['propertyLabel']['value']
        if 'propertyValLabel' in prop:
            pval = prop['propertyValLabel']['value']
        else:
            pval = schema_convert(prop['propertyVal'].get('datatype', ''),
                    prop['propertyVal']['value'])
        if pval.startswith("List of"): continue
        if plabel not in properties:
            properties[(purl, plabel)] = set()
        properties[(purl, plabel)].add(pval)
    chosen = random.choice(properties.items())
    return {'url': chosen[0][0], 'label': chosen[0][1],
            'value': random.choice(list(chosen[1]))}

def get_random_neighboring_property(subj, prop):
    query = """
    SELECT DISTINCT ?t ?tlabel
    WHERE {
      <%s> <http://purl.org/dc/terms/subject> ?val.
      ?s ?prop ?val.
      ?s <%s> ?t.
      OPTIONAL {
        ?t rdfs:label ?tlabel.
        FILTER(lang(?tlabel) = "en").
      }
    }
    limit 1000""" % (subj, prop)
    qstr = urllib.urlencode({'query': query, 'output': 'json',
        'default-graph-uri': 'http://dbpedia.org'})
    resp = urllib.urlopen("http://dbpedia.org/sparql?" + qstr)
    obj = json.loads(resp.read())
    alternates = list()
    for prop in obj['results']['bindings']:
        if 'tlabel' in prop:
            if prop['tlabel']['value'].startswith("List of"): continue
            alternates.append(prop['tlabel']['value'])
        else:
            val = schema_convert(prop['t'].get('datatype', ''),
                    prop['t']['value'])
            alternates.append(val)
    return random.choice(alternates)

cache = {}
def get_subject_count(class_):
    if class_ in cache:
        return cache[class_]
    query = """
    SELECT count(*) WHERE {
    ?subject rdf:type <%s>.
    ?subject rdfs:label ?label.
    ?subject foaf:name ?name.
    FILTER(lang(?label) = "en").
    }
""" % class_
    qstr = urllib.urlencode({'query': query, 'output': 'json',
        'default-graph-uri': 'http://dbpedia.org'})
    resp = urllib.urlopen("http://dbpedia.org/sparql?" + qstr)
    obj = json.loads(resp.read())
    result = int(obj['results']['bindings'][0]['callret-0']['value'])
    cache[class_] = result
    return result

def get_random_subject(class_, count):
    query = """
    SELECT * WHERE {
    ?subject rdf:type <%s>.
    ?subject rdfs:label ?label.
    ?subject foaf:name ?name.
    FILTER(lang(?label) = "en").
    FILTER(!STRSTARTS(?label, "List of")).
    FILTER EXISTS {?subject foaf:depiction ?url}
    }
    offset %d
    limit 1""" % (class_, random.randrange(count))
    qstr = urllib.urlencode({'query': query, 'output': 'json',
        'default-graph-uri': 'http://dbpedia.org'})
    resp = urllib.urlopen("http://dbpedia.org/sparql?" + qstr)
    obj = json.loads(resp.read())
    info = dict([(k, v['value']) for k, v \
            in obj['results']['bindings'][0].iteritems() \
            if not(k.startswith("List of"))])
    return info 

def alternate_universe(subject, prop, real_prop_val, alt_prop_val):
    if prop.isupper(): prop = prop.lower()
    if re.search(r"^[a-zA-Z ]+[^s]$", subject):
        subj_prop = subject + "'s " + prop
    else:
        subj_prop = "the " + prop + " of " + subject
    if sum(map(len, [subj_prop, real_prop_val, alt_prop_val])) <= 47:
        tmpl_str = u"Everyone knows {{subj_prop}} is {{real_prop_val}}. What this book presupposes is\u2026 maybe it's {{alt_prop_val}}?"
    else:
        tmpl_str = u"Everyone knows {{subj_prop}} is {{real_prop_val}}. This book presupposes\u2026 maybe it's {{alt_prop_val}}?"
    tmpl = Template(tmpl_str)
    return tmpl.render(subj_prop=subj_prop, real_prop_val=real_prop_val,
            alt_prop_val=alt_prop_val)

def get_random_resource(g):
    while True:
        class_ = get_random_class(g)
        class_str = get_label_string(g, class_)
        count = get_subject_count(class_)
        if count > 0:
            try:
                return get_random_subject(class_, count)
            except IndexError as e:
                continue

def get_subj_from_wikilink(href):
    query = """
    SELECT * WHERE {
    ?subject rdfs:label ?label.
    ?subject foaf:isPrimaryTopicOf <%s>.
    FILTER(lang(?label) = "en").
    }
    """ % href
    qstr = urllib.urlencode({'query': query, 'output': 'json',
        'default-graph-uri': 'http://dbpedia.org'})
    resp = urllib.urlopen("http://dbpedia.org/sparql?" + qstr)
    obj = json.loads(resp.read())
    try:
        info = dict([(k, v['value']) for k, v \
                in obj['results']['bindings'][0].iteritems() \
                if not(k.startswith("List of"))])
    except IndexError:
        return None
    return info 

def generate(subj=None):
    g = rdflib.Graph()
    g.parse("dbpedia_3.9.owl")
    while True:
        if subj is None:
            subj = get_random_resource(g)
        try:
            prop_dict = get_random_property(subj['subject'])
            alt_prop = get_random_neighboring_property(subj['subject'],
                    prop_dict['url']).strip()
        except IndexError as e:
            continue
        real_prop = prop_dict['value'].strip()
        if real_prop.startswith('http') or alt_prop.startswith('http'):
            continue
        if real_prop.lower() == alt_prop.lower(): continue
        output = alternate_universe(subj['label'], prop_dict['label'],
                real_prop, alt_prop)
        output = output.replace("\n", "")
        if len(output) <= 115:
            return output + " " + get_property(subj['subject'],
                    'foaf:isPrimaryTopicOf')
        elif len(output) <= 140:
            return output

if __name__ == '__main__':
    pool = [s.strip() for s in open("pool.txt").readlines()]
    while True:
        if random.randrange(3) > 0:
            subj = get_subj_from_wikilink('http://en.wikipedia.org' + random.choice(pool))
            print generate(subj)
        else:
            print generate()
        time.sleep(1)

