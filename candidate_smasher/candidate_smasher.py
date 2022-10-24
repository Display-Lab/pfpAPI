# !/usr/bin/env python3
# -*- coding: utf-8 -*-
""" CandidateSmasher Class
    Ported from ruby code at https://github.com/Display-Lab/candidate-smasher
    Date: 20220726
    By:
        Scientific Programming and Innovation (SPI)
        Academic IT
        H.I.T.S., Michigan Medicine
        University of Michigan
"""
import typing
import hashlib
import json
from rdflib import Graph


class CandidateSmasher():
    """CandidateSmasher
    """
    ID_PREFIX = "_:c"
    ABOUT_MEASURE_IRI = "http://example.com/slowmo#IsAboutMeasure"
    ABOUT_TEMPLATE_IRI = "http://example.com/slowmo#IsAboutTemplate"
    ANCESTOR_PERFORMER_IRI = "http://example.com/slowmo#AncestorPerformer"
    ANCESTOR_TEMPLATE_IRI = "http://example.com/slowmo#AncestorTemplate"
    HAS_CANDIDATE_IRI = "http://example.com/slowmo#HasCandidate"
    HAS_PERFORMER_IRI = "http://example.com/slowmo#IsAboutPerformer"
    REGARDING_COMPARATOR = "http://example.com/slowmo#RegardingComparator"
    REGARDING_MEASURE = "http://example.com/slowmo#RegardingMeasure"
    SPEK_IRI = "http://example.com/slowmo#spek"
    USES_ISR_IRI = "http://example.com/slowmo#IsAboutCausalPathway"
    CANDIDATE_IRI = "http://purl.obolibrary.org/obo/cpo_0000053"
    TEMPLATE_CLASS_IRI = "http://purl.obolibrary.org/obo/psdo_0000002"
    HAS_DISPOSITION_IRI = "http://purl.obolibrary.org/obo/RO_0000091"
    IS_ABOUT_IRI = "http://purl.obolibrary.org/obo/IAO_0000136"

    def __init__(self, input_string: str = "{}", templates_src:str = "{}"):
        try:
            self._spek_hsh = json.loads(input_string) 
            self._template_lib =json.loads(templates_src)  # is a dict
        except json.decoder.JSONDecodeError:

            self._spek_hsh = {}
         # is a list of dicts

    def load_ext_templates(self, templates_src: typing.Optional[str]) -> list:
        """ load from given filename
        """
        if templates_src is None:
            return []
        try:
            with open(templates_src, "r") as file_d:
                entire_file_dict = json.load(file_d)
        except json.decoder.JSONDecodeError:
            return []
        except FileNotFoundError:
            return []
        if '@graph' not in entire_file_dict:
            return []
        return entire_file_dict['@graph']

    def valid(self) -> bool:
        """ check all values of dict for True
        """
        checks = self.checks()
        for _, value in checks.items():
            if not value:
                return False
        return True

    def checks(self) -> dict:
        """ return a dict with three specific keys, where values are bool
            {
                "@type": bool,
                self.HAS_PERFORMER_IRI: bool,
                self.ABOUT_TEMPLATE_IRI: bool
            }
        """
        return {
            "@type": self.spek_hsh["@type"] == self.SPEK_IRI,
            self.HAS_PERFORMER_IRI: self.HAS_PERFORMER_IRI in self.spek_hsh,
            self.ABOUT_TEMPLATE_IRI: (len(self._template_lib) != 0) or (self.ABOUT_TEMPLATE_IRI in self.spek_hsh)
        }

    def list_missing(self) -> list:
        """ get the keys that are false from self.checks()
        """
        result = []
        checks = self.checks()
        for key, value in checks.items():
            if not value:
                result.append(key)
        return result

    def load_ext_templates_rdf(self, templates_src: str):
        """ RDFlib::Graph
        """
        if not templates_src:
            graph = Graph()
        else:
            graph = Graph()
            graph.parse(templates_src, format='n3')
        return graph

    @staticmethod
    def merge_external_templates(spec_templates: list, ext_templates: list):
        """ static method
            Go through the lists and merge the dicts from both lists that have the same '@id' value

            INPUT: list of dicts

            original Ruby code:

            def self.merge_external_templates(spec_templates, ext_templates)
             t_ids = spec_templates.map{|t| t['@id']}

             # For every template in spec, lookup from external and merge info.
             merged = spec_templates.map do |t|
               new_t = ext_templates.select{|e| e['@id'] == t['@id']}.first || {}

               new_t.merge(t) do |key, ext_val, spek_val|
                 if spek_val.is_a?(Array) || ext_val.is_a?(Array)
                   result = Array(spek_val) + Array(ext_val)
                   result.uniq
                 else
                   spek_val
                 end
               end
             end

             merged
           end

        For the Ruby merge, here is what it is doing:
        h1 = { "a" => 100, "b" => 200 }
        h2 = { "b" => 254, "c" => 300 }
        h1.merge(h2)   #=> {"a"=>100, "b"=>254, "c"=>300}
        h1.merge(h2){|key, oldval, newval| newval - oldval}
                       #=> {"a"=>100, "b"=>54,  "c"=>300}
        h1             #=> {"a"=>100, "b"=>200}


        EXAMPLE TEST DATA IN RUBY
            a = [{'@id' => '1', 'car' => 'ok' , '@type' => '5'}, {'@id' => '2', 'myitem' => 'test item'}]
            b = [{'@id' => '1', 'car2' => 'ok2' }]
            result = [
                {"@id"=>"1", "car2"=>"ok2", "car"=>"ok", '@type' => '5'},
                {"@id"=>"2", 'myitem' => 'test item'}
            ]

        NOTE: this code could be more performance efficent
        """
        # pylint: disable=too-many-locals
        def ids_are_same(template: dict, spec: dict):
            """ return True if id's exist and are the same
            """
            if ('@id' in spec) and ('@id' in template):
                if template['@id'] == spec['@id']:
                    return True
            return False

        def ext_merge(t: dict, itemkey, itemval) -> dict:
            """ merge this elem with dict t, but like the Ruby code

            The Ruby merge does the following:
                If the old value and new value are lists, then extend the new list and take the list(set())
                If the old value or new value is a list, then append to the new list and take the list(set())
                If neither is a list, the take the newval.

                Actually, it's not a set(), must preserve the order of old and new list(s).
                Cannot just "extend()" the list, because duplicates are not wanted.
            """
            result = {}
            if itemkey not in t:
                result[itemkey] = itemval
                return result
            oldval = t[itemkey]
            if isinstance(itemval, list):
                if isinstance(oldval, list):
                    result[itemkey] = oldval.copy()
                    for item in itemval:  # both are lists
                        if item not in result[itemkey]:
                            result[itemkey].append(item)
                else:
                    result[itemkey] = [oldval]  # new is list, old is value
                    for item in itemval:
                        if item not in result[itemkey]:
                            result[itemkey].append(item)  # new is list, old is value
            else:
                if isinstance(oldval, list):
                    result[itemkey] = oldval.copy()  # new is value, old is a list
                    result[itemkey].append(itemval)

                else:
                    result[itemkey] = [oldval]  # old and new are values, keep old value
            return result

        result = []
        spec_map = {}
        t_ids = []

        try:
            for elem in spec_templates:
                if '@id' not in elem:
                    # check for @id in each elem, break out if not found
                    # TODO could add some log message for a KeyError
                    raise KeyError

            # create a map of the values of all id's
            #
            # For example:
            #  this spec      [{'@id': '1', ...}, {'@id': '2', ...}, ...]
            #  becomes  ['1', '2', ...]
            #
            # PREREQ: all dict elems contain an item '@id'
            t_ids = [elem['@id'] for elem in spec_templates]

            # NOTE: The test test_generate_candidate_about_empty() shows that must check for '@id' key

            # create a spec map that maps the ids to the actual list elem
            #
            # For example:
            #  this spec      {'@id': '1', 'car': [1, 2, 3], '@type': '5', ...}
            #  becomes  {'1': {'@id': '1', 'car': [1, 2, 3], '@type': '5', ...}}
            #

            for elem in spec_templates:
                spec_map[elem['@id']] = elem

        except KeyError:
            # skip the above processing spec_map[]
            pass

        # do the merge of ext to spec
        merged_keys = []
        e_ids = []
        for item in ext_templates:
            if '@id' in item:
                ext_id = item['@id']
                if ext_id in t_ids:
                    e_ids.append(ext_id)
                    new_t = {}
                    for itemkey, itemval in item.items():
                        merged_elem = ext_merge(spec_map[ext_id], itemkey, itemval)
                        merged_keys.append(itemkey)
                        new_t.update(merged_elem)

                    # add in spec keys not added in above
                    for speckey, specval in spec_map[ext_id].items():
                        if speckey not in merged_keys:
                            new_t[speckey] = specval

                    result.append(new_t)

        # now, add in all of the elements in spec with ids that were not in ext
        for tid in t_ids:
            if tid not in e_ids:
                result.append(spec_map[tid])

        return result

    def templates_rdf_to_json(self, graph: Graph):
        """ convert rdf to json
        """
        result = graph.serialize(format='json-ld')
        result_json = json.loads(result)
        for elem in result_json:
            for keyelem, valueelem in elem.items():
                if isinstance(valueelem, list) and len(valueelem) == 1:
                    # this elem is a list with one element, convert it to the element itself
                    # NOTE: this is what I get from the Ruby code
                    elem[keyelem] = elem[keyelem][0]
        return result_json

    def split_by_disposition_attr(self, performer: dict, attr_uri: str) -> list:
        """ split by displosition
            Returns a list
        NOTE: this code could be more efficent
        """
        default_return_value = [performer]
        splits = []
        if self.HAS_DISPOSITION_IRI not in performer:
            return default_return_value
        dispositions = performer[self.HAS_DISPOSITION_IRI]  # list of dicts
        if dispositions is None:
            return default_return_value
        uniques = []
        for elem in dispositions:
            # error if key does not exist in elem
            if attr_uri not in elem:
                return default_return_value

            if elem[attr_uri] not in uniques:
                uniques.append(elem[attr_uri])

        for uniq in uniques:
            this_row = {}
            this_uniq_list = []
            for elem in dispositions:
                if elem[attr_uri] == uniq:
                    this_uniq_list.append(elem)
            this_row[self.HAS_DISPOSITION_IRI] = this_uniq_list
            splits.append(this_row)

        # print("--splits-------------", splits)
        return splits

    def split_by_measure(self, performer):
        """ split by self.REGARDING_MEASURE
        """
        return self.split_by_disposition_attr(performer, self.REGARDING_MEASURE)

    def split_by_comparator(self, performer):
        """ split by self.REGARDING_COMPARATOR
        """
        return self.split_by_disposition_attr(performer, self.REGARDING_COMPARATOR)

    @staticmethod
    def regarding_measure(split_performer: dict) -> str:
        """ return blank string or string in the dict arg
        """
        if CandidateSmasher.HAS_DISPOSITION_IRI not in split_performer:
            return ""
        dispositions = split_performer[CandidateSmasher.HAS_DISPOSITION_IRI]
        if not dispositions:
            return ""
        disp = dispositions[0]
        if CandidateSmasher.REGARDING_MEASURE not in disp:
            return ""
        if "@id" not in disp[CandidateSmasher.REGARDING_MEASURE]:
            return ""
        if disp[CandidateSmasher.REGARDING_MEASURE]["@id"] is None:
            return ""
        return disp[CandidateSmasher.REGARDING_MEASURE]["@id"]

    @staticmethod
    def regarding_comparator(split_performer):
        """ return elem
        """
        if CandidateSmasher.HAS_DISPOSITION_IRI not in split_performer:
            return ""
        dispositions = split_performer[CandidateSmasher.HAS_DISPOSITION_IRI]
        if not dispositions:
            return ""
        disp = dispositions[0]
        if CandidateSmasher.REGARDING_COMPARATOR not in disp:
            return ""
        if "@id" not in disp[CandidateSmasher.REGARDING_COMPARATOR]:
            return ""
        if disp[CandidateSmasher.REGARDING_COMPARATOR]["@id"] is None:
            return ""
        return disp[CandidateSmasher.REGARDING_COMPARATOR]["@id"]

    @staticmethod
    def make_candidate(template, performer):
        """ make candidate
        """
        t_id = None
        p_id = "_:p1"
        if "@id" in template:
            t_id = template["@id"]
        if "@id" in performer:
            p_id = performer["@id"]

        m_id = CandidateSmasher.regarding_measure(performer)
        c_id = CandidateSmasher.regarding_comparator(performer)
        candidate = {**template, **performer}

        def abouts_iao(candidate):
            """ set abouts from IAO if it is not None
            """
            abouts = None
            if 'IAO-IsAbout' in candidate:
                if candidate['IAO-IsAbout']:
                    # IAO exists and is not null
                    abouts = candidate['IAO-IsAbout'].copy()
                    del candidate['IAO-IsAbout']
            return abouts

        def abouts_iri(candidate):
            """ set abouts from IRI if it is not None
            """
            abouts = None
            if CandidateSmasher.IS_ABOUT_IRI in candidate:
                if candidate[CandidateSmasher.IS_ABOUT_IRI]:
                    # IRI exists and is not null
                    abouts = candidate[CandidateSmasher.IS_ABOUT_IRI].copy()
                    del candidate[CandidateSmasher.IS_ABOUT_IRI]
            return abouts

        def abouts_iao_or_iri(candidate):
            """ return abouts
                return true unless both are None
                i.e. return true if either exists and is not None or blank ""

                return false if both don't exist or if both are None or blank ""

                equivalent to the ruby code:
                    unless(candidate['IAO-IsAbout'].nil? && candidate[IS_ABOUT_IRI].nil?)
                        abouts = candidate['IAO-IsAbout'] || candidate[IS_ABOUT_IRI]
                        candidate.delete('IAO-IsAbout')
                        candidate.delete(IS_ABOUT_IRI)
                    end
            """
            # NOTE: sequence/position-dependent code, IAO comes before IRI
            abouts = abouts_iao(candidate)
            if not abouts:
                abouts = abouts_iri(candidate)
            return abouts

        abouts = abouts_iao_or_iri(candidate)
        if abouts:
            candidate[CandidateSmasher.HAS_DISPOSITION_IRI] = candidate[CandidateSmasher.HAS_DISPOSITION_IRI] + list(abouts)

        candidate["@type"] = CandidateSmasher.CANDIDATE_IRI
        # debug
        # tmp1 = f'{t_id or ""}{p_id or ""}{m_id or ""}{c_id or ""}'
        # tmp2 = tmp1.encode('utf-8')
        candidate["@id"] = CandidateSmasher.ID_PREFIX + hashlib.md5(f'{t_id or ""}{p_id or ""}{m_id or ""}{c_id or ""}'.encode('utf-8')).hexdigest()
        candidate[CandidateSmasher.ANCESTOR_PERFORMER_IRI] = "_:p1"
        candidate[CandidateSmasher.ANCESTOR_TEMPLATE_IRI] = t_id

        return candidate

    def generate_candidates(self) -> list:
        """ generate_candidates
        """
        def flatten1(list_in) -> list:
            """ flatten list by 1 level
            """
            return [item for sublist in list_in for item in sublist]

        # TODO
        if self.HAS_PERFORMER_IRI in self._spek_hsh:
            performers = self._spek_hsh[self.HAS_PERFORMER_IRI]
        else:
            performers = []

        # split by measure then by comparator
        p_map = list(map(self.split_by_measure, performers))
        pm_split = flatten1(p_map)
        pc_map = list(map(self.split_by_comparator, pm_split))
        pmc_split = flatten1(pc_map)

        if self.ABOUT_TEMPLATE_IRI in self._spek_hsh:
            spec_templates = self._spek_hsh[self.ABOUT_TEMPLATE_IRI]
        else:
            spec_templates = []

        templates = CandidateSmasher.merge_external_templates(spec_templates, self._template_lib)

        def map_for_pmc_split(p):
            """ first-level map on pmc_split
            """
            result = [CandidateSmasher.make_candidate(t, p) for t in templates]  # this is a map() on templates
            return result

        res_pmc = [map_for_pmc_split(s) for s in pmc_split]  # this is a map() on pmc_split

        # TODO need a recursive flatten function to flatten multiple (i.e. all) levels
        res = flatten1(res_pmc)
        return res

    def smash(self) -> str:
        """ smash!
        """
        candidates = self.generate_candidates()
        self._spek_hsh[self.HAS_CANDIDATE_IRI] = candidates
        return json.dumps(self._spek_hsh)

    @property
    def spek_hsh(self) -> dict:
        """the spek_hsh property
        """
        return self._spek_hsh

    @spek_hsh.setter
    def spek_hsh(self, value: dict):
        """spek_hsh setter
        """
        self._spek_hsh = value

    @property
    def template_lib(self) -> list:
        """the template_lib property
        """
        return self._template_lib

    @template_lib.setter
    def template_lib(self, value: list):
        """template_lib setter
        """
        self._template_lib = value
