from simplepagination.backends import Paginator
from aligner.align.files_aligner import load_matching_index


class HabrahabrPaginator(Paginator):
    def paginate(self, frame_size, number_of_pages, current_page,current_book):
        output = {}
        if current_page > 1:
            output['prev'] = current_page - 1
        if current_page < number_of_pages:
            output['next'] = current_page + 1
        if current_page + frame_size - 1 < number_of_pages:
            output['last'] = number_of_pages
        if current_page - frame_size + 1 > 1:
            output['first'] = 1
        if number_of_pages <= frame_size:
            output['pages'] = range(1, number_of_pages + 1)
        else:
            output['pages'] = range(max(current_page - frame_size + 1, 1), min(current_page + frame_size, number_of_pages + 1))

        output[ 'matching_list' ] = load_matching_index( current_book, current_page - 1 )
        return output