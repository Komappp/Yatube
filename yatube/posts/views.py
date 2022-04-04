from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group, User, Follow
from .forms import PostForm, CommentForm
from .utils import my_paginator
from django.contrib.auth.decorators import login_required


def index(request):
    template = 'posts/index.html'
    posts = Post.objects.select_related('group')
    page_obj = my_paginator(request, posts)
    context = {
        'page_obj': page_obj
    }
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page_obj = my_paginator(request, posts)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    page_obj = my_paginator(request, posts)
    posts_count = author.posts.all().count()
    following = request.user.is_authenticated and (
        Follow.objects.filter(user=request.user, author=author).exists()
    )
    context = {
        'following': following,
        'posts_count': posts_count,
        'author': author,
        'page_obj': page_obj
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    form = CommentForm()
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all()
    count = post.author.posts.count()
    context = {
        'comments': comments,
        'form': form,
        'post': post,
        'count': count
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        form = form.save(commit=False)
        form.author = request.user
        form.save()
        return redirect('posts:profile', request.user.username)
    context = {
        'form': form
    }
    return render(request, 'posts/create.html', context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    is_edit = True
    context = {
        'post': post,
        'form': form,
        'is_edit': is_edit
    }
    return render(request, 'posts/create.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    posts = Post.objects.select_related('group').filter(
        author__following__user=request.user
    )
    page_obj = my_paginator(request, posts)
    context = {
        'page_obj': page_obj
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    follower = request.user
    author = User.objects.get(username=username)
    if request.user != author:
        follow, bool = Follow.objects.get_or_create(
            user=follower,
            author=author
        )
        follow.save()
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    Follow.objects.filter(
        user=request.user,
        author=User.objects.get(username=username)
    ).delete()
    return redirect('posts:profile', username)
