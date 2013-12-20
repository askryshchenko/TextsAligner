# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.shortcuts import redirect
from django.template import RequestContext

from aligner.models import AlignBook
from aligner.models import TextBlock


from aligner.forms import FilesForm

from aligner.align.files_aligner import source_target_texts_aligner as texts_aligner
from aligner.align.text_parser import chapter_parser, http_file_stream

from annoying.decorators import render_to
from simplepagination import paginate
from aligner.align.text_parser import paragraph_parser, sentence_parser



class block_data:
    def __init__(self, source, target):
        self.source_data = source
        self.target_data = target

class sentence_data:
    def __init__(self, source, sent_id):
        self.data = source
        self.class_id = sent_id



@render_to( 'aligner/book_list.html' )
def book_list_view( request ):
    object_list = AlignBook.objects.all()
    return{ 'object_list' : object_list}


@render_to( 'aligner/book.html' )
@paginate( style='habrahabr', per_page=1 )
def book_view(request, book_pk):
    #book = AlignBook.objects.filter( book_name='Test11' )[0]
    blocks = TextBlock.objects.filter( book = book_pk )

    object_list = []

    for block in blocks:
            sentence_source_list = []
            current_sent = 0
            for paragraph in paragraph_parser( block.source_text_block ):
                current_paragraph = []
                for sentence in sentence_parser( paragraph ):
                    current_paragraph.append( sentence_data( sentence, "source_" + str( current_sent ) ) )
                    current_sent = current_sent + 1

                sentence_source_list.append( current_paragraph )

            sentence_target_list = []
            current_target_sent = 0
            for paragraph in paragraph_parser( block.target_text_block ):
                current_paragraph = []
                for sentence in sentence_parser( paragraph ):
                    current_paragraph.append( sentence_data( sentence, "target_" + str( current_target_sent ) ) )
                    current_target_sent = current_target_sent + 1
                sentence_target_list.append( current_paragraph )

            object_list.append( block_data( sentence_source_list, sentence_target_list ) )



    return { 'object_list' : object_list,  'current_book' : book_pk}


def UploadFiles(request):
    # Handle file upload
    if request.method == 'POST':
        form = FilesForm(request.POST, request.FILES)
        if form.is_valid():

            new_book = AlignBook( book_name = form.cleaned_data['book_name'] )
            new_book.save()

            chapter_source_list = []
            chapter_source_block_list = []
            for chapter in chapter_parser( http_file_stream( request.FILES['source_file'] ) ):
                chapter_source_list.append( chapter )
                chapter_source_block_list.append( list( paragraph_parser( chapter ) ) )

            chapter_target_list = []
            chapter_target_block_list = []
            for chapter in chapter_parser( http_file_stream( request.FILES['target_file'] ) ):
                chapter_target_list.append( chapter )
                chapter_target_block_list.append( list( paragraph_parser( chapter ) ) )

            #Alignment chapter of texts
            alignment_list = texts_aligner( chapter_source_block_list, chapter_target_block_list )

            current_block_num = 0

            for block in alignment_list:
                current_source_block = ""
                current_target_block = ""
                for source_chapter in block[0]:
                    current_source_block = current_source_block + chapter_source_list[ source_chapter ]

                for target_chapter in block[1]:
                    current_target_block = current_target_block +  chapter_target_list[ target_chapter ]

                new_block = TextBlock(
                    book = new_book,
                    block_num = current_block_num,
                    source_text_block = current_source_block,
                    target_text_block = current_target_block,
                    matching_list = []
                )
                new_block.save()
                current_block_num = current_block_num + 1

            return redirect('book_view', book_pk = new_book.pk )

    else:
        form = FilesForm() # A empty, unbound form


    # Render list page with the documents and the form
    return render_to_response(
        'aligner/upload_files.html',
        { 'form': form },
        context_instance=RequestContext(request)
    )
