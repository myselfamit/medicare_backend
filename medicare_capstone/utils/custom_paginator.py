from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def paginate(object_list, page = 1, per_page = 10):
    # Check if Object is a List
    if type(object_list) == list:
        paginator = Paginator(object_list, per_page)
        total_pages = paginator.num_pages
        total_rows = paginator.count
        current_page = int(page) if page else 1

        try:
            object_list = paginator.page(page)

        except PageNotAnInteger:
            object_list = paginator.page(1)

        except EmptyPage:
            object_list = None

        if object_list:
            has_next = object_list.has_next()
            has_previous = object_list.has_previous()
            has_other_pages = object_list.has_other_pages()
            next_page_number = (
                object_list.next_page_number() if has_next else None
            )
            previous_page_number = (
                object_list.previous_page_number()
                    if has_previous else None
            )

            object_list = list(object_list)

        else:
            has_next = False
            has_previous = False
            has_other_pages = False
            next_page_number = None
            previous_page_number = None
            object_list = None

        data = {
            'current_page': current_page,
            'total_pages': total_pages,
            'total_rows': total_rows,
            'has_next': has_next,
            'has_previous': has_previous,
            'has_other_pages': has_other_pages,
            'next_page_number': next_page_number,
            'previous_page_number': previous_page_number,
            'results': object_list
        }

    else:
        data = object_list

    return data
