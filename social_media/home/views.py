from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import DetailView
from django.db.models import Count
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse
from .models import Post, Tag, Comment  # Import your models
from .forms import CommentForm

from user_profile.models import UserProfile # Import your UserProfile model


class HomeView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('signup')  # Redirect to dashboard if logged in

        posts = Post.objects.filter(is_visible=True).order_by('-created_at')
        latest_posts = posts[:3]
        most_liked_post = Post.objects.filter(is_visible=True).annotate(like_count=Count('likers')).order_by('-like_count').first()
        most_trending_tag = Tag.objects.annotate(post_count=Count('posts')).order_by('-post_count').first()

        context = {
            'latest_posts': latest_posts,
            'most_liked_post': most_liked_post,
            'most_trending_tag': most_trending_tag,
            'title': 'HOME',
        }
        return render(request, 'home/home.html', context)
    



class PostDetailView(LoginRequiredMixin, DetailView):
    model = Post
    template_name = 'home/post_detail.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.filter(parent=None).order_by('-created_at')
        context['comment_form'] = CommentForm()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = CommentForm(request.POST)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.author = self.request.user
        comment.post = self.object
        parent_id = self.request.POST.get('parent_id')
        if parent_id:
            parent_comment = get_object_or_404(Comment, id=parent_id)
            comment.parent = parent_comment
        comment.save()
        messages.success(self.request, 'Your comment has been added successfully.')
        return redirect(reverse('post_detail', kwargs={'pk': self.object.pk}))

    def form_invalid(self, form):
        messages.error(self.request, 'There was an error with your comment. Please try again.')
        return self.render_to_response(self.get_context_data(comment_form=form))