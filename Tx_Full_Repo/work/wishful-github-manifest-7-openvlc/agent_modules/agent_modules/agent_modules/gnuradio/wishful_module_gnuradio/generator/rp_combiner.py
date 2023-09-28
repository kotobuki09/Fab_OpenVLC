#!/usr/bin/env python3

import xml.etree.ElementTree as etree
import string
from ast import literal_eval as make_tuple
import filecmp
import logging
import os

'''
    Given a set of Gnuradio programs (described as GRC flowgraph) this program combines all
    those radio programs in a single meta radio program which allows very fast switching from
    one protocol to another.
'''

__author__ = "A. Zubow"
__copyright__ = "Copyright (c) 2016, Technische Universität Berlin"
__version__ = "0.1.0"
__email__ = "{zubow}@tkn.tu-berlin.de"


class RadioProgramCombiner():

    def __init__(self, gr_radio_programs_path):
        self.log = logging.getLogger('gnuradio_module.main')
        self.log.setLevel(logging.DEBUG)
        self.gr_radio_programs_path = gr_radio_programs_path
        self.radio_programs = {}
        self.usrp_source_fields = ['samp_rate', 'center_freq0', 'gain0']
        self.common_selector_id = None
        self.common_blocks_socket_pdu_id = None
        self.gen_grc_fname = 'meta_rp.grc'
        self.gen_proto_dict_fname = 'meta_rp_proto_dict.txt'
        self.gen_proto_fields_fname = 'meta_rp_fields.txt'


    def add_radio_program(self, proto_prefix, proto_grc_file_name):
        self.radio_programs[proto_prefix] = os.path.join(self.gr_radio_programs_path, proto_grc_file_name)


    def get_proto_idx(self, target_proto):
        for protocol_it, proto_prefix in enumerate(self.radio_programs):
            if target_proto == proto_prefix.replace('_', ''): #self.radio_programs[proto_prefix]:
                return protocol_it

        return None


    def generate(self):
        """ generate meta radio program """

        # create output document
        new_root = etree.Element("flow_graph")

        # open template
        self.log.info('Load base config ...')
        base_xfile = 'generator/gen_stub.grc'
        base_tree = etree.parse(base_xfile)

        # copy base blocks to new document
        for base_block in base_tree.getroot().findall('block'):
            new_root.append(base_block)

        self._update_selector_and_sink_socket(base_tree)

        self.log.debug('Copy all blocks/connections from radio program to meta radio program')

        old_uhd_usrp_source_id = []
        old_blocks_socket_pdu_id = []
        proto_trees = []
        proto_vars = []
        proto_usrp_src_dicts = []
        coord_y_offsets = (250, 500)

        for protocol_it, proto_prefix in enumerate(self.radio_programs):
            proto_xfile = self.radio_programs[proto_prefix]

            ptree = etree.parse(proto_xfile)
            proto_trees.append(ptree)
            proto_vars.append(self._rename_all_variables(proto_prefix, proto_trees[protocol_it], coord_y_offsets[protocol_it]))
            proto_usrp_src_dicts.append(self._copy_usrp_src_cfg(proto_trees[protocol_it].getroot(), proto_vars[protocol_it]))

            # do the rewiring: replace old usrp_source by selector
            for proto_block in proto_trees[protocol_it].getroot().findall('block'):
                block_key = proto_block.find('key')

                if block_key.text == 'uhd_usrp_source':
                    # skip uhd_usrp_source
                    for param in proto_block.findall("param"):
                        param_val = param.find("value")
                        param_key = param.find("key")
                        if param_key.text == 'id':
                            # replace by the new usrp_src
                            old_uhd_usrp_source_id.append(param_val.text)
                elif block_key.text == 'blocks_socket_pdu':
                    # skip uhd_usrp_source
                    for param in proto_block.findall("param"):
                        param_val = param.find("value")
                        param_key = param.find("key")
                        if param_key.text == 'id':
                            # replace by the new blocks_socket_pdu
                            old_blocks_socket_pdu_id.append(param_val.text)
                elif block_key.text == 'options':
                    found = False
                    # skip top block
                    for param in proto_block.findall("param"):
                        param_val = param.find("value")
                        param_key = param.find("key")
                        if param_key.text == 'id' and param_val.text == proto_prefix + 'top_block':
                            found = True
                    if not found:
                        new_root.append(proto_block)
                else:
                    new_root.append(proto_block)

        self.log.debug('Init session variable')

        # get selector ID
        for base_block in new_root.findall('block'):

            init_session_value = '[0'
            for field in self.usrp_source_fields:
                init_session_value = init_session_value + ',' + proto_usrp_src_dicts[0][field]
            init_session_value = init_session_value + ']'

            block_key = base_block.find('key')

            if block_key.text == 'variable':
                found = False
                for param in base_block.findall("param"):
                    param_val = param.find("value")
                    param_key = param.find("key")
                    if param_key.text == 'id' and param_val.text == 'session_var':
                        found = True

                if found:
                    for param in base_block.findall("param"):
                        param_val = param.find("value")
                        param_key = param.find("key")
                        if param_key.text == 'value':
                            param_val.text = init_session_value

        self.log.debug('Configure node connections ...')

        self.log.debug('... copy from template')
        for base_conn in base_tree.getroot().findall('connection'):
            new_root.append(base_conn)

        self.log.debug('... copy from each radio program & reconnect to selector/common sink')
        for protocol_it in range(self._get_num_protocols()):

            for proto_conn in proto_trees[protocol_it].getroot().findall('connection'):
                if proto_conn.find('source_block_id').text == old_uhd_usrp_source_id[protocol_it]:
                    proto_conn.find('source_block_id').text = self.common_selector_id
                    proto_conn.find('source_key').text = str(protocol_it)

                if proto_conn.find('sink_block_id').text == old_blocks_socket_pdu_id[protocol_it]:
                    proto_conn.find('sink_block_id').text = self.common_blocks_socket_pdu_id
                    # proto_conn.find('source_key').text = str(protocol_it)

                new_root.append(proto_conn)

        self.log.info('Serialize combined grc file')
        new_tree = etree.ElementTree(new_root)
        new_tree.write(os.path.join(self.gr_radio_programs_path, self.gen_grc_fname))
        #assert filecmp.cmp('../testdata/all.grc', '../testdata/_all.grc')

        fout = open(os.path.join(self.gr_radio_programs_path, self.gen_proto_dict_fname), 'w')
        fout.write(str(proto_usrp_src_dicts))
        fout.close()
        # assert filecmp.cmp('../testdata/proto_usrp_src_dicts.txt', '../testdata/_proto_usrp_src_dicts.txt')

        fout = open(os.path.join(self.gr_radio_programs_path, self.gen_proto_fields_fname), 'w')
        fout.write(str(self.usrp_source_fields))
        fout.close()
        #assert filecmp.cmp('../testdata/usrp_source_fields.txt', '../testdata/_usrp_source_fields.txt')

        return self.gen_grc_fname

    def _get_num_protocols(self):
        return len(self.radio_programs)


    def _update_selector_and_sink_socket(self, base_tree):

        num_protocols = self._get_num_protocols()

        # get selector ID
        for base_block in base_tree.getroot().findall('block'):
            block_key = base_block.find('key')

            if block_key.text == 'blks2_selector':
                for param in base_block.findall("param"):
                    param_val = param.find("value")
                    param_key = param.find("key")
                    if param_key.text == 'id':
                        self.common_selector_id = param_val.text
                    # set the number of required output ports
                    if param_key.text == 'num_outputs':
                        param_val.text = str(num_protocols)

            if block_key.text == 'blocks_socket_pdu':
                for param in base_block.findall("param"):
                    param_val = param.find("value")
                    param_key = param.find("key")
                    if param_key.text == 'id':
                        self.common_blocks_socket_pdu_id = param_val.text


    def _rename_all_variables(self, prefix, tree, coord_y_offset):
        root = tree.getroot()

        vars_dict = []
        self.log.info('Rename variables ...')

        for block in root.findall('block'):
            block_key = block.find('key')
            for param in block.findall("param"):
                param_key = param.find("key")
                param_val = param.find("value")
                if param_key.text == 'id':
                    old_id = param_val.text
                    new_id = prefix + param_val.text
                    # print('Replace %s by %s' % (old_id, new_id))
                    param_val.text = new_id
                    # replace references
                    self._rename_all_references(root, old_id, new_id)
                    vars_dict.append(new_id)
                if param_key.text == '_coordinate':
                    old_coord = make_tuple(param_val.text)
                    yc = old_coord[1] + coord_y_offset
                    xc = old_coord[0]
                    param_val.text = str((xc, yc))

        return vars_dict


    def _rename_all_references(self, root, old_id, new_id):
        # replace all reference in blocks
        for block in root.findall('block'):
            block_key = block.find('key')
            # print('block_key: %s' % block_key.text)
            for param in block.findall("param"):
                param_val = param.find("value")
                param_key = param.find("key")
                if param_key.text != 'id':
                    if param_val.text is not None:
                        param_val.text = param_val.text.replace(old_id, new_id)

        # replace all reference in connections
        for conn in root.findall('connection'):
            src_block_id = conn.find("source_block_id")
            if src_block_id.text is not None:
                src_block_id.text = src_block_id.text.replace(old_id, new_id)

            snk_block_id = conn.find("sink_block_id")
            if snk_block_id.text is not None:
                snk_block_id.text = snk_block_id.text.replace(old_id, new_id)


    def _copy_usrp_src_cfg(self, root, proto_vars):

        self.log.info('Copy old usrp_source config ...')

        usrp_src_dict = {}

        for block in root.findall('block'):
            block_key = block.find('key')

            if block_key.text == 'uhd_usrp_source':
                for param in block.findall("param"):
                    param_key = param.find("key")
                    param_val = param.find("value")

                    if param_key.text in self.usrp_source_fields:
                        if param_val.text in proto_vars:
                            # it is already a variable; nothing ...
                            # print('usrp_src: %s -> %s' % (param_key.text, param_val.text))
                            usrp_src_dict[param_key.text] = param_val.text

                        else:
                            # we have to create a variable ...
                            self.log.error('warning ... not yet implemented')
                            assert False

        return usrp_src_dict

if __name__ == '__main__':

    #gr_radio_programs_path = os.path.join(os.path.expanduser("~"), ".wishful", "radio")
    gr_radio_programs_path = "../testdata/"

    combiner = RadioProgramCombiner(gr_radio_programs_path)
    combiner.add_radio_program('one_', 't1.grc')
    combiner.add_radio_program('two_', 't2.grc')

    combiner.generate()