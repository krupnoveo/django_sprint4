from django.utils import timezone
from blog.models import Post, Category, Comment
from django.contrib.auth import get_user_model
from .forms import CommentForm, PostForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .forms import EditUserForm
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.utils.timezone import now


User = get_user_model()


def index(request):
    posts = Post.objects.select_related('category', 'location',
                                        'author').annotate(
        comment_count=Count('comments')).filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=now()
    ).order_by('-pub_date')

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
    template = 'blog/index.html'
    return render(request, template, context)

def post_detail(request, post_id):
    post = get_object_or_404(
        Post.objects.select_related('category', 'author', 'location')
        .filter(Q(is_published=True, category__is_published=True,
                  pub_date__lte=now()) |
                Q(author=request.user)),
        pk=post_id
    )

    comments = Comment.objects.filter(post=post).select_related(
        'author').order_by('created_at')
    form = CommentForm()
    context = {'post': post, 'comments': comments, 'form': form}
    template = 'blog/detail.html'
    return render(request, template, context)

@login_required
def create_post(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('blog:profile', username=request.user.username)
    else:
        form = PostForm()

    context = {'form': form}
    template = 'blog/create.html'
    return render(request, template, context)

@login_required(login_url='login')
def edit_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if request.user != post.author:
        return redirect('blog:post_detail', post_id=post_id)

    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', post_id=post_id)
    else:
        form = PostForm(instance=post)

    context = {'form': form, 'post': post}
    template = 'blog/create.html'
    return render(request, template, context)

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if request.user != post.author:
        return redirect('blog:post_detail', post_id=post_id)

    if request.method == "POST":
        post.delete()
        return redirect('blog:profile', username=request.user.username)

    context = {'post': post}
    template = 'blog/delete_confirm.html'
    return render(request, template, context)

def category_posts(request, category_slug):
    template = 'blog/category.html'
    category = get_object_or_404(
        Category.objects.all().filter(is_published=True),
        slug=category_slug
    )
    post_list = get_relevant_posts(
        category.posts.filter(category=category)
    ).order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'category': category,
        'page_obj': page_obj,
    }
    return render(request, template, context)

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()

    return redirect('blog:post_detail', post_id=post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, post_id=post_id)

    if comment.author != request.user:
        raise PermissionDenied("У вас недостаточно прав!")

    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', post_id=post_id)
    else:
        form = CommentForm(instance=comment)

    context = {'comment': comment, 'form': form}
    template = 'blog/comment.html'
    return render(request, template, context)

@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, post_id=post_id)

    if comment.author != request.user:
        raise PermissionDenied("У вас недостаточно прав!")

    if request.method == "POST":
        comment.delete()
        return redirect('blog:post_detail', post_id=post_id)

    context = {'comment': comment}
    template = 'blog/comment.html'
    return render(request, template, context)


def get_relevant_posts(posts):
    return (
        posts.filter(
            is_published=True
        ).filter(
            pub_date__lte=timezone.now()
        ).filter(
            category__is_published=True
        )
    )


def profile(request, username):
    profile_user = get_object_or_404(User, username=username)

    filters = {'author_id': profile_user.id}
    if request.user.is_anonymous or request.user.id != profile_user.id:
        filters['is_published'] = True
        filters['pub_date__lte'] = now()

    posts = Post.objects.select_related('category', 'location',
                                        'author').annotate(
        comment_count=Count('comments')).filter(**filters).order_by(
        '-pub_date')

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'blog/profile.html',
                  {'page_obj': page_obj, 'profile': profile_user})

@login_required
def edit_profile(request):
    if request.method == "POST":
        form = EditUserForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('blog:profile', username=request.user.username)
    else:
        form = EditUserForm(instance=request.user)
    return render(request, 'blog/user.html', {'form': form})
