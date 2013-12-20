# -*- coding: utf-8 -*-
import align
import distance_measures
from text_parser import paragraph_parser, word_parser,sentence_parser
from aligner.models import TextBlock

class sentence_data:
    def __init__(self, source, sent_id):
        self.data = source
        self.class_id = sent_id

class texts_data:
    def __init__(self, source, target):
        self.source = source
        self.target = target


def load_matching_index( book_pk, block_num ):


    block = TextBlock.objects.filter(book = book_pk)[block_num]



    if block.matching_list == []:

        sentence_source_word_list = []
        sentence_source_list  = []
        current_sentence = 0
        for paragraph in paragraph_parser( block.source_text_block ):
            current_paragraph = []
            for sentence in sentence_parser( paragraph ):
                current_paragraph.append( sentence_data( sentence, current_sentence  ) )
                sentence_source_word_list.append(  word_parser( sentence )  )
                current_sentence = current_sentence + 1
            sentence_source_list.append( current_paragraph )

        sentence_target_list  = []
        sentence_target_word_list = []
        current_sentence = 0
        for paragraph in paragraph_parser( block.target_text_block ):
            current_paragraph = []
            for sentence in sentence_parser( paragraph ):
                current_paragraph.append( sentence_data( sentence, current_sentence  ) )
                sentence_target_word_list.append(  word_parser( sentence )  )
                current_sentence = current_sentence + 1
            sentence_target_list.append( current_paragraph )



            #Alignment paragraph of texts
        alignment_sentence_list = source_target_texts_aligner( sentence_source_word_list, sentence_target_word_list)
        matching_list = []
        for block_ind in alignment_sentence_list:
            matching_list.append( list( block_ind ) )
        block.matching_list = matching_list
        block.save()



    return block.matching_list


def source_target_texts_aligner( source_list, target_list ):

    std = align.GaleChurchAligner(distance_measures.two_side_distance , 'original', 'index_tuples', print_flag=False)

    top_down_alignments = std.batch_align( [ source_list ], [ target_list ] )

    return top_down_alignments[ 0 ]


