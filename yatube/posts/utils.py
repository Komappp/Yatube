from django.core.paginator import Paginator
from yatube.settings import POSTS_COUNT


def my_paginator(request, posts):
    paginator = Paginator(posts, POSTS_COUNT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return page_obj
