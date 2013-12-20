
from nltk.corpus import wordnet
from pymorphy2 import MorphAnalyzer
from stardict import Dictionary
import nltk
import re
import munkres


"""
Path to Dictionary: 'Dict/ER-LingvoUniversal.ifo'

"""

class word_info:
    def __init__( self, word, sentence_num, n_word, translate_list ) :
        self.word = word
        self.sentence_num = sentence_num
        self.normal_form = n_word
        self.translate_list = translate_list


class sentence_info:
    def __init__( self, sentence, sentence_words) :
        self.sentence = sentence
        self.sentence_words = sentence_words





class Parallel_Translate:
    def __init__(self, input_ru, input_en):

        self.morph_ru = MorphAnalyzer()

        self.sentences_ru = self.Pars_sentences( input_ru )
        wordPattern_ru = re.compile( "((?:[а-яА-ЯёЁ]+[-']?)*[а-яА-яёЁ]+)" )
        self.sentences_list_ru = self.Create_Word_List( wordPattern_ru, self.sentences_ru,
                                                   self.Normalize_ru, self.Translate_ru )
        self.word_list_ru = []

        self.sentences_en = self.Pars_sentences( input_en )
        self.dict_en_ru = Dictionary('Dict/ER-LingvoUniversal.ifo')
        wordPattern_en = re.compile("((?:[a-zA-Z]+[-']?)*[a-zA-Z]+)")
        self.sentences_list_en = self.Create_Word_List( wordPattern_en, self.sentences_en,
                                                   self.Normalize_en, self.Translate_en )
        self.word_list_en = []
        self.Graph = self.Create_Graph()

        munkres_algorithm = munkres.Munkres()
        #self.word_matching = munkres_algorithm.compute( self.Graph )




# Input file? read text and split to sentences
    def Pars_sentences(self,file_name ) :
        sentences_list = []

        with open(file_name, 'rU') as input_file:
            file_str = input_file.read()
            sentences_tokenize = nltk.tokenize.PunktSentenceTokenizer()
            for sentence in sentences_tokenize.sentences_from_text( file_str ):
                sentences_list.append(  sentence )

        return sentences_list



    def Create_Word_List(self, wordPattern, sentences, Normalize, Translate ):
        word_list = []
        sentence_num = 0
        sent_list = []
        for sentence in sentences:
            sentence_word_list = []
            for word in wordPattern.findall( sentence ):
                word = word.strip()
                word = word.lower()
                n_word = Normalize( word )
                translate_list = Translate( n_word )
                w_info = word_info( word, sentence_num, n_word, translate_list )
                word_list.append( w_info )
                sentence_word_list.append(w_info)
            sent_list.append( sentence_info( sentence, sentence_word_list ) )
            sentence_num= sentence_num + 1
        return sent_list



    def Translate_ru( self, n_word ):
        return []

    def Translate_en( self, n_word ):

        self.re_for_entry = re.compile("<dtrn>(.*?)</dtrn>")

        valueWord = []
        try:
            for normal_word in n_word:
                for entry in self.dict_en_ru[ normal_word ]:
                    result_pars = self.ParsEntry( entry.data )
                    valueWord = valueWord + result_pars
        except KeyError:
            pass
        return valueWord

    def ParsEntry( self, entry_data  ) :
        l = entry_data.split( "<abr><i><c><co>" )
        result_first_step = []
        for data in l:
            result_first_step = result_first_step + self.re_for_entry.findall(data)
        result_second_step = []
        for data in result_first_step:
            temp = data.split("<")
            if temp[0] != "":
                result_second_step.append(temp[0])
        result = []
        for data in result_second_step:
            for data_prom in data.split(","):
                result = result + data_prom.split(";")
        for i in range( len( result ) ):
            result[i] = result[i].strip()
        return result


    def Normalize_ru( self, word ):
        n_word = self.morph_ru.normal_forms( word )
        if n_word:
            return n_word[0]
        else:
            return []

    def Normalize_en( self, word ):
        n_word = wordnet.morphy( word )
        if n_word:
            return [ n_word ]
        else:
            return []

    def Create_Graph(self):
        graph_matrix = [ [ 0 for i in range( len( self.sentences_list_ru ) ) ]
                            for j in range( len( self.sentences_list_en ) ) ]
        koef = abs( len( self.sentences_list_en ) - len( self.sentences_list_ru ) )
        sentence_num = 0
        for sentence in self.sentences_list_en:

            sentence_left_num = sentence_num
            sentence_right_num = sentence_num +1

            while (sentence_left_num >= 0) and (sentence_num - sentence_left_num <= koef):

                sum_eq_words = 0
                for w_info in sentence.sentence_words:

                    for translate_word in w_info.translate_list:

                        for w_info_ru in self.sentences_list_ru[sentence_left_num]:

                            for w_normal in w_info_ru.normal_form:

                                if w_normal == translate_word:
                                    sum_eq_words = sum_eq_words + 1

                graph_matrix[sentence_num][sentence_left_num] = -( sum_eq_words - sentence_num + sentence_left_num )

            while (sentence_right_num < len( self.sentences_list_ru ) ) and ( sentence_right_num - sentence_num <= koef):

                sum_eq_words = 0
                for w_info in sentence.sentence_words:

                    for translate_word in w_info.translate_list:

                        for w_info_ru in self.sentences_list_ru[sentence_right_num]:

                            for w_normal in w_info_ru.normal_form:

                                if w_normal == translate_word:
                                    sum_eq_words = sum_eq_words + 1

                graph_matrix[sentence_num][sentence_right_num] = -( sum_eq_words - sentence_num + sentence_left_num )

        return graph_matrix
