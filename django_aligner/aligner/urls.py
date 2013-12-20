# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

urlpatterns = patterns('aligner.views',
    url(r'^upload_files/$', 'UploadFiles', name='upload_files'),
    url(r'^book_view/(?P<book_pk>\d+)$', 'book_view', name='book_view'),
    url(r'^book_list_view/$', 'book_list_view', name='book_list_view'),
    url(r'^$', 'UploadFiles', name='upload_files')

)