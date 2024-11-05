from django.shortcuts import render

# Create your views here.
# django-braces: this allows to access some convenient Mixins to use CBV's
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import IntegrityError
from django.shortcuts import redirect

from django.views import generic
from django.http import Http404
 
from braces.views import SelectRelatedMixin

from . import models
from . import forms

from django.contrib.auth import get_user_model
User = get_user_model()              # when someone is logged into a session, i'm going to be able to use this User object as the current user and call things off of that.


class PostListView(SelectRelatedMixin,generic.ListView):
    model = models.Post
    select_related = ('user','group')   # The 'select_related' attribute  is set to a tuple of related field names ('user' and 'group'). This tells the mixin to use select_related to fetch the user and group related objects in the same query.
    

class UserPostListView(generic.ListView):
    model = models.Post
    template_name = "posts/user_post_list.html"

    def get_queryset(self):
        try:
            # Fetch the user object whose username matches the one in the URL
            self.post_user = User.objects.prefetch_related('posts').get(username__iexact=self.kwargs.get('username'))
        except User.DoesNotExist:
            raise Http404
        else: 
            # Return all posts associated with the fetched user
            return self.post_user.posts.all()
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post_user'] = self.post_user
        return context


class PostDetailView(SelectRelatedMixin, generic.DetailView):
    model = models.Post
    select_related = ('user','group')
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user__username__iexact=self.kwargs.get('username'))
    

class PostCreateView(LoginRequiredMixin,SelectRelatedMixin,generic.CreateView):
    fields = ['message','group']
    model = models.Post
    
    def form_valid(self, form):                          
        self.object = form.save(commit=False)
        self.object.user = self.request.user       # connecting the post to user itself
        try:
            self.object.save()
            return super().form_valid(form)
        except IntegrityError:
            messages.error(self.request, "You have already posted this message.")
            return redirect('posts:create')

class PostDeleteView(LoginRequiredMixin,SelectRelatedMixin,generic.DeleteView):
    model = models.Post
    select_related = ('user','group')
    success_url = reverse_lazy('posts:all')

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user_id = self.request.user.id)  # Filters the query set to include only posts created by the currently logged-in user. This ensures that users can only delete their own posts.

    def delete(self,*args,**kwargs):
        messages.success(self.request,'Post Deleted')
        return super().delete(*args,**kwargs)



    
# self.kwargs.get('username'): Retrieves the username parameter from the URL.
# get(username__iexact=self.kwargs.get('username')): Performs a case-insensitive exact match to find the user by their username.
# User.objects.prefetch_related('posts'): Fetches the user along with their posts in a single query to optimize performance.
   