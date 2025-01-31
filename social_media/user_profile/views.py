from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth.views import LoginView
from django.views.generic import ListView, DetailView, UpdateView
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.contrib.auth.forms import AuthenticationForm
from .models import UserProfile
from .forms import UserProfileForm, UserProfileEditForm, PostForm
from home.models import Post
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect

# Create your views here.

# --------------------------------------------------- Sign Up View


class SignUpView(View):
    def get(self, request):
        # Log out the user if already logged in
        if request.user.is_authenticated:
            logout(request)

        form = UserProfileForm()
        return render(request, 'user_profile/signup.html', {'form': form})

    def post(self, request):
        # Log out if user is still authenticated (double check)
        if request.user.is_authenticated:
            logout(request)

        form = UserProfileForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            # Redirect to home or dashboard after signup
            return redirect('dashboard')

        return render(request, 'user_profile/signup.html', {'form': form})


# --------------------------------------------------- Sign In View
class SignInView(LoginView):
    template_name = 'user_profile/signin.html'
    authentication_form = AuthenticationForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('dashboard')


# -------------------------------------------------------------- DASHBOARD -------------------------------------------------------------- #
class DashboardView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'user_profile/dashboard.html'
    context_object_name = 'posts'
    ordering = ['-created_at']
    login_url = 'signin'  # Specify your login URL name here

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add user profile information
        context['user'] = self.request.user
        context['profile_image'] = self.request.user.profile_image if hasattr(
            self.request.user, 'profile') else None
        # Add post creation form
        context['post_form'] = PostForm()
        return context

    def post(self, request, *args, **kwargs):
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()  # Save the tags
            return redirect('dashboard')
        else:
            return self.get(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
class DislikePostView(View):
    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        if request.user not in post.dislikers.all():
            post.dislikers.add(request.user)
            post.likers.remove(request.user)
        else:
            post.dislikers.remove(request.user)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@method_decorator(login_required, name='dispatch')
class LikePostView(View):
    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        if request.user not in post.likers.all():
            post.likers.add(request.user)
            post.dislikers.remove(request.user)
        else:
            post.likers.remove(request.user)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

# --------------------------------------------------- UserProfile


class UserProfileView(LoginRequiredMixin, DetailView):
    model = UserProfile
    template_name = 'user_profile/user_profile_page.html'
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        # Get the user profile based on the username passed in the URL
        username = self.kwargs.get('username')
        return get_object_or_404(UserProfile, username=username)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.get_object()

        # Check if the profile belongs to the authenticated user
        is_own_profile = self.request.user == profile
        context['is_own_profile'] = is_own_profile

        # Fetch posts related to the profile
        # Update 'author' if the field differs
        context['posts'] = Post.objects.filter(author=profile)

        # Sent and received requests
        context['sent_requests'] = self.request.user.sent_requests.all()
        context['received_requests'] = self.request.user.received_requests.all()

        return context

    # def post(self, request, *args, **kwargs):
    #     profile = self.get_object()

    #     # Handle sending a friend request
    #     if 'send_request' in request.POST:
    #         if profile != request.user and profile not in request.user.sent_requests.all():
    #             request.user.sent_requests.add(profile)
    #             return redirect('user_profile', username=profile.username)  # Redirect to the profile page

    #     return super().post(request, *args, **kwargs)


class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = UserProfileEditForm
    template_name = 'user_profile/edit_profile.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        # Redirect to the user's profile page
        return reverse('user_profile', kwargs={'username': self.request.user.username})

    def form_invalid(self, form):
        # Stay on the same page with the form errors
        return render(self.request, self.template_name, {'form': form})


@login_required
def send_friend_request(request, profile_id):
    if request.method == 'POST':
        user_to_follow = get_object_or_404(UserProfile, id=profile_id)
        request.user.sent_requests.add(user_to_follow)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


# --------------------------------------------------- Friend Request Handler
class FriendRequestHandlerView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        action = kwargs.get('action')
        user_id = kwargs.get('user_id')

        user_to_handle = get_object_or_404(UserProfile, id=user_id)

        if action == 'accept':
            self.accept_friend_request(request.user, user_to_handle)
        elif action == 'reject':
            self.reject_friend_request(request.user, user_to_handle)

        return redirect(reverse('user_profile', kwargs={'username': request.user.username}))

    def accept_friend_request(self, user, friend):
        user.following.add(friend)
        friend.following.add(user)
        user.received_requests.remove(friend)
        friend.sent_requests.remove(user)

    def reject_friend_request(self, user, friend):
        user.received_requests.remove(friend)
        friend.sent_requests.remove(user)
