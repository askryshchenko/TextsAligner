# -*- coding: utf-8 -*-
from django.db import models
import ast

#custom model for python List

class ListField(models.TextField):
    __metaclass__ = models.SubfieldBase
    description = "Stores a python list"

    def __init__(self, *args, **kwargs):
        super(ListField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if not value:
            value = []

        if isinstance(value, list):
            return value

        return ast.literal_eval(value)

    def get_prep_value(self, value):
        if value is None:
            return value

        return unicode(value)

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_db_prep_value(value)



class AlignBook(models.Model):
    book_name = models.CharField( max_length = 40 )

class TextBlock(models.Model):
    book = models.ForeignKey(AlignBook)
    block_num = models.IntegerField()
    source_text_block = models.TextField()
    target_text_block = models.TextField()
    matching_list = ListField()
    class Meta:
        unique_together = ('book','block_num')


