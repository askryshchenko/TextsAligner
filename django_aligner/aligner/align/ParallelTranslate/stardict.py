import gzip
import struct
from os import path
from itertools import takewhile
from collections import namedtuple, defaultdict


IndexEntry = namedtuple('IndexEntry', ('offset', 'size'))


DefinitionPartType = namedtuple('DefinitionPartType',
	('TEXT', 'HTML'))('m', 'h')
DefinitionPart = namedtuple('DefinitionPart', ('type', 'data'))


class Dictionary:

	def __init__(self, ifo_path):
		self.path = ifo_path
		self._config = self._load_dict_config(ifo_path)

		dict_root = path.splitext(ifo_path)[0]
		self._index = self._load_word_list(dict_root)

		try:
			self._definitions_file = gzip.open(dict_root + '.dict.dz', 'rb')
		except IOError:
			self._definitions_file = open(dict_root + '.dict', 'rb')

	def _load_dict_config(self, ifo_path):
		with open(ifo_path, encoding='utf-8') as config_file:
			
			config_file.readline()

			config = dict(line.rstrip().split('=', 1) for line in config_file)

		return config

	def _load_syn_list(self, dict_root):
		try:
			syn_list_file = open(dict_root + '.syn', 'rb')
		except IOError:
			return {}

		syn_index_map = defaultdict(list)

		with syn_list_file:
			syn_list = syn_list_file.read()

		i = 0

		while i < len(syn_list):
			j = i

			while syn_list[i] != 0x00:
				i += 1

			key = syn_list[j:i].decode('utf-8')
			original_word_index = struct.unpack('>I', syn_list[(i + 1):(i + 5)])[0]

			syn_index_map[original_word_index].append(key)

			i += 5

		return syn_index_map

	def _load_word_list(self, dict_root):
		try:
			index_file = open(dict_root + '.idx', 'rb')
		except IOError:
			index_file = gzip.open(dict_root + '.idx.gz', 'rb')

		with index_file:
			word_list = index_file.read()

		if self._config.get('idxoffsetbits', '32') == '64':
			meta_size = 12
			unpack_meta = struct.Struct('>QI').unpack
		else:
			meta_size = 8
			unpack_meta = struct.Struct('>II').unpack

		index = defaultdict(list)
		syn_index_map = self._load_syn_list(dict_root)

		i = n = 0

		while i < len(word_list):
			j = i

			while word_list[i] != 0x00:
				i += 1

			entry = IndexEntry(*unpack_meta(
				word_list[(i + 1):(i + 1 + meta_size)]))
			index[word_list[j:i].decode('utf-8')].append(entry)

			if n in syn_index_map:
				for key in syn_index_map[n]:
					index[key].append(entry)

			i += 1 + meta_size
			n += 1


		index.default_factory = None

		return index
	
	def _read_definition_part(self, part_type, definition_data):
		return bytearray(takewhile(lambda byte: byte != 0x00,
			definition_data)).decode('utf-8')

	def __len__(self):
		return len(self._index)

	def __iter__(self):
		return iter(self._index)

	def __getitem__(self, word):
		for entry in self._index[word]:
			self._definitions_file.seek(entry.offset)
			definition_data = \
				iter(self._definitions_file.read(entry.size))

			if 'sametypesequence' in self._config:
				for part_type in self._config['sametypesequence']:
					yield DefinitionPart(part_type,
						self._read_definition_part(part_type, definition_data))
			else:
				raise NotImplementedError

	def words(self):
		return self._index.keys()
