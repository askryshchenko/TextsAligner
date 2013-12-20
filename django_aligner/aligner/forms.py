# -*- coding: utf-8 -*-
from django import forms

class FilesForm(forms.Form):

    source_file = forms.FileField(
        label='Select a source file'
    )
    target_file = forms.FileField(
        label='Select a target file'
    )
    book_name = forms.CharField( max_length = 40 )