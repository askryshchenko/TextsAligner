# -*- coding: utf-8 -*-

from nltk.corpus import wordnet
#from pymorphy2 import MorphAnalyzer
#from stardict import Dictionary

from nltk.tokenize import WhitespaceTokenizer
from nltk.tokenize import PunktSentenceTokenizer


def sentence_parser( input_str ):

    sentences_tokenize = PunktSentenceTokenizer()
    for sentence in sentences_tokenize.sentences_from_text( input_str ):
        if sentence.strip() != u'':
            yield sentence


def paragraph_parser( input_str ):
    for paragraph in input_str.split(u'\n'):
        if paragraph.strip() != u'':
            yield paragraph

def word_parser( input_str ):
    tokenizer = WhitespaceTokenizer()
    return tokenizer.tokenize( input_str )


def istitle(paragraph):
	#simbol_array = [u'.',u'!',u'?', u'',u'"', u'”',u'\'',u':',u'\n',u'-',u'\xa6']
	if  paragraph.strip().isupper() :
		return True
	else:
		return False



def chapter_parser( input_data ):
    chapter_str = ""
    for data in input_data:
        for paragraph in data.split('\n'):
            #print paragraph
            #print "#########"
            if istitle( paragraph ):
                if chapter_str != u'':
                    yield chapter_str
                chapter_str = paragraph
            else:
                chapter_str = chapter_str + u'\n' + paragraph
    if chapter_str != u'':
        yield chapter_str

def http_file_stream( http_file_handler ):
    for data in http_file_handler.chunks():
        yield data.decode( 'utf-8', 'ignore' )




