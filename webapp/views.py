from django.shortcuts import render,redirect
from django.views.generic import TemplateView,CreateView,ListView,UpdateView,DeleteView
from .forms import BlogForm, CommentForm
from .models import Blog, BlogComment
from django.template.loader import get_template
from django.urls import reverse_lazy
# Create your views here.

class DashBoard(CreateView):
    '''Creating the dasdboard for the blog '''
    def get(self,request):
        #fetching the blog form written in forms
        print("get")
        template_name = "blog_upload.html"
        form=BlogForm()
        context={
            'form':form,
            }
            #returning the form to display on page
        return render(request,template_name,context)
    def post(self,request):
        #posting the filled form
        template_name = "blog_upload.html"
        form=BlogForm(request.POST, request.FILES)
        if form.is_valid():# check if form is valid, if yes then it is saved
            print("valid")
            form.save()
            print("the saved")
            return redirect('/blog/all-blogs/')

        else:
            print(form.errors)
            print("invalid")
            context={
                'form':form, # retain the form and display the same page
                }
            return render(request,template_name,context)


class AllBlogView(ListView):
    model = Blog
    def get(self,request):
        template_name = "all_blog.html"
        blogs=Blog.objects.all() #returns all the blogs from blog models
        return render(request,template_name,{'blogs':blogs})

class SingleBlogView(CreateView):
    def get(self,request,title_slug):

        blog=Blog.objects.get(slug=title_slug)#returns the pk of particular blog
        template_name = "single_blog.html"
        form=CommentForm()
        comments=BlogComment.objects.filter(blog=blog) #combining all the comments of particular blog
        context={
            'form':form,
            'blog':blog,
            'comments':comments
            }
        return render(request,template_name,context)

    def post(self,request,title_slug):
        #
        blog=Blog.objects.get(slug=title_slug)
        template_name = "single_blog.html"
        form=CommentForm(request.POST)
        if form.is_valid():
            print("valid")
            first_name=form.cleaned_data['first_name']
            last_name=form.cleaned_data['last_name']
            email=form.cleaned_data['email_id']
            comment=form.cleaned_data['comment']
            comments,create=BlogComment.objects.get_or_create(blog=blog,first_name=first_name,
            last_name=last_name,email_id=email,comment=comment)
            comments=BlogComment.objects.filter(blog=blog)
            form=CommentForm()
            context={
                'form':form,
                'blog':blog,
                'comments':comments
                }
            return render(request,template_name,context)

        else:
            print(form.errors)
            print("invalid")
            comments=BlogComment.objects.filter(blog=blog)
            context={
                'form':form,
                'blog':blog,
                'comments':comments
                }
            return render(request,template_name,context)

class AllBlogChangeView(ListView):
    model = Blog
    def get(self,request):
        template_name = "edit_delete_blogs.html"
        blogs=Blog.objects.all() #returns all the blogs from blog models
        return render(request,template_name,{'blogs':blogs})

class BlogUpdateView(UpdateView):
    model = Blog
    fields=['main_title','single_line_body','content','date_of_publish','image','seo_title','seo_description','seo_keyword']
    template_name = 'blog_update.html'
    success_url = '/blog/edit_delete_blogs/'


class BlogDeleteView(DeleteView):
    model = Blog
    template_name = 'blog_delete.html'
    success_url = reverse_lazy('edit_delete_blogs')
