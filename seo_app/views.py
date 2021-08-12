from django.shortcuts import render,redirect
from django.views.generic import TemplateView,CreateView,ListView,UpdateView,View
from .forms import SiteSeoForm
from .models import SiteSeo
from .choices import PageChoice

# Create your views here.
class Dashboard(CreateView):
    template_name = 'seo_dashboard.html'
    form_class = SiteSeoForm
    def get(self,request):
        form = SiteSeoForm()
        return render(request,'seo_dashboard.html',{'form':form })

    def post(self,request):
        template_name = 'seo_dashboard.html'
        print("inside the post")
        form = SiteSeoForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect('/seo/seo_updates/')

class SeoUpdateView(ListView):
    model = SiteSeo
    def get(self,request):
        template_name = "seo_update.html"
        SEO = SiteSeo.objects.all() #returns the seo updates
        print(SEO)
        return render(request,template_name,{'seo':SEO}) #key value pair and specify the key name in html page

    def post(self,request):
        template_name = "seo_update.html"
        SEO = SiteSeo.objects.all() #returns the seo updates
        if form.is_valid():
            form.save()
        return redirect('/seo/single_update/')



class SingleUpdateView(UpdateView):
    model = SiteSeo
    fields=['seo_title','seo_description','seo_keyword']
    template_name = 'single_update.html'
    success_url = '/seo/seo_updates/'
