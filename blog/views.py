from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from django.urls import reverse_lazy
from .forms import PostForm, UserRegisterForm, CommentForm
from .models import UserProfile, Post, Comment, Like, CommentLike


# Create your views here.

class RegisterView(generic.CreateView):
    form_class = UserRegisterForm
    success_url = reverse_lazy('login')
    template_name = 'registration/register.html'


def profile_view(request, username):
    profile = get_object_or_404(UserProfile, user__username=username)
    posts = Post.objects.filter(user=profile)
    return render(request, 'blog/profile.html', {'profile': profile, 'posts': posts})

class CreatePostView(LoginRequiredMixin, generic.CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/posts_form.html'

    def form_valid(self, form):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        form.instance.user = profile
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('posts_detail', kwargs={'pk': self.object.pk})

class HomePageView(generic.ListView):
    model = Post
    template_name = 'home.html'
    context_object_name = 'home_posts'
    paginate_by = 10

class MyPostListView(LoginRequiredMixin, generic.ListView):
    model = Post
    context_object_name = 'my_posts'
    paginate_by = 10
    template_name = 'blog/post_list.html'

    def get_queryset(self):
        profile = UserProfile.objects.get(user=self.request.user)
        return Post.objects.filter(user=profile).order_by("-id")

class PostDetailView(generic.DetailView):
    model = Post
    context_object_name = 'post'
    template_name = 'blog/posts_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # All comments for this post
        context['comments'] = Comment.objects.filter(post=self.object)
        # Comment form (pass user to handle anonymous vs logged-in)
        context['form'] = CommentForm(user=self.request.user)

        if self.request.user.is_authenticated:
            profile = get_object_or_404(UserProfile, user=self.request.user)
            like_obj = Like.objects.filter(post=self.object, user=profile).first()
            context['user_liked'] = like_obj.is_liked if like_obj else False
            liked_comment_ids = CommentLike.objects.filter(comment__post=self.object, user=profile, is_liked=True).values_list('comment_id', flat=True)
            context['liked_comment_ids'] = list(liked_comment_ids)
        else:
            context['user_liked'] = False
            context['liked_comment_ids'] = []
        context['total_likes'] = Like.objects.filter(post=self.object, is_liked=True).count()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = CommentForm(request.POST, user=request.user)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = self.object
            if request.user.is_authenticated:
                comment.user = request.user.userprofile
                comment.name = request.user.get_full_name()
            else:
                comment.name = form.cleaned_data['name']
            comment.save()
            return redirect('posts_detail', pk=self.object.pk)
        context = self.get_context_data()
        context['form'] = form
        return self.render_to_response(context)

class PostUpdateView(LoginRequiredMixin, generic.UpdateView):
    login_url = "/login/"
    model = Post
    form_class = PostForm
    template_name = 'blog/posts_form.html'

    def get_success_url(self):
        return reverse_lazy('posts_detail', kwargs={'pk': self.object.pk})

    def dispatch(self, request, *args, **kwargs):
        post = self.get_object()
        if post.user.user != request.user:
            return HttpResponseForbidden()
        return super().dispatch(request, *args, **kwargs)

class PostDeleteView(LoginRequiredMixin, generic.DeleteView):
    login_url = "/login/"
    model = Post
    success_url = reverse_lazy('my_posts_list')

    def dispatch(self, request, *args, **kwargs):
        post = self.get_object()
        if post.user.user != request.user:
            return HttpResponseForbidden()
        return super().dispatch(request, *args, **kwargs)

@login_required(login_url='/login/')
def toggle_like(request, pk):
    post = get_object_or_404(Post, pk=pk)
    profile = request.user.userprofile
    # Check if a Like object already exists
    like_obj, created = Like.objects.get_or_create(user=profile, post=post)

    # Toggle like status
    like_obj.is_liked = not like_obj.is_liked
    like_obj.save()
    return redirect('posts_detail', pk=post.pk)

@login_required(login_url='/login/')
def toggle_comment_like(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    profile = request.user.userprofile
    like_obj, created = CommentLike.objects.get_or_create(user=profile, comment=comment)

    # Toggle like status
    like_obj.is_liked = not like_obj.is_liked
    like_obj.save()

    # redirect back to the post that this comment belongs to
    return redirect('posts_detail', pk=comment.post.pk)
