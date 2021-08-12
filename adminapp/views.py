from django.shortcuts import render,redirect
from adminapp.forms import ConversionInputs, ProjectPricingForm,TaxForm, SingleProjectPricing,ApiRequestForm
from coreapp.models import Project,ProjectUser,ProjectDashboard,ProjectPricing,DefaultProjectPricing,ProjectInvoice,Tax,ProjectUser,EndpointMlApi
from login.models import Customer
from django.views.generic import TemplateView,CreateView,View,UpdateView,ListView
from django.contrib.auth.mixins import LoginRequiredMixin
import csv
import pandas as pd
from django.contrib.auth.models import User,Group
import os
from actstream.models import Action
from django.contrib.auth.models import User
from django.http import JsonResponse
from actstream.models import actor_stream
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
# Create your views here.
'''Start of class to display all the projects '''
class AdminDashboard(LoginRequiredMixin,TemplateView):
    login_url = '/admin-login/'
    redirect_field_name = 'redirect_to'
    template_name='admin_dashboard.html'
    def get(self,request):
        '''get method to display all the projects'''
        template_name = 'admin_dashboard.html'
        projects = Project.objects.all()

        customers = Customer.objects.all()
        context ={
            'projects':projects,
            'customers':customers
        }
        return render(request,template_name,context)
'''End of class to display all the projects '''

''' Start of class to display and receive conversion inputs form'''
class ConversionTable(LoginRequiredMixin,TemplateView):
    login_url = '/admin-login/'
    redirect_field_name = 'redirect_to'
    template_name='admin_dashboard.html'
    def get(self,request):
        '''get method to display the conversion input form'''
        template_name = "conversion_input.html"
        conversion_inputs = ConversionInputs()
        context={
            'conversion_inputs':conversion_inputs
            }
        return render(request,template_name,context)

    def post(self,request):
        '''post method to receive the conversion input and append it to csv file'''
        template_name = "conversion_input.html"
        conversion_inputs = ConversionInputs(request.POST)
        if conversion_inputs.is_valid():
            print("valid")
            character = conversion_inputs.cleaned_data["character"]
            function = conversion_inputs.cleaned_data["function"]
            header = ['Character','Function']
            file_exists = os.path.isfile('Conversion_Table.csv')
            with open('Conversion_Table.csv', 'a', newline ='') as file:
                writer = csv.writer(file, delimiter=',')
                if not file_exists:
                    writer.writerow(i for i in header)
                    writer.writerow([character] + [function])
                else:
                    writer.writerow([character] + [function])
            # with open('Conversion_Table.csv', 'a') as f:
            #     writer = csv.writer(f)
            #     writer.writerow([character] + [function])
            return redirect('/administrator/admin-dashboard/')
        else:
            context={
                  'conversion_inputs':conversion_inputs
            }
            return render(request,template_name,context)
'''End of class to display and receive conversion inputs form'''


'''Start of class to display each project details'''
class SingleProjectDetails(LoginRequiredMixin,TemplateView):
    login_url = '/admin-login/'
    redirect_field_name = 'redirect_to'
    template_name='admin_dashboard.html'
    def get(self,request,pk):
        template_name='single_project_details.html'
        project = Project.objects.get(pk=pk)
        user = project.admin_user
        customer=Customer.objects.get(user=user)
        print(customer)
        account_type=customer.type
        if account_type == "Individual":
            try:
                print("inside individual dashboard try")
                dashboards = ProjectDashboard.objects.filter(project=project)
                print(dashboards)
                context={
                   'project':project,
                   'dashboards':dashboards,
                   'account_type':account_type
                   }
            except Exception as e:
                print(type(e))
                context={
                    'project':project,
                    'account_type':account_type
                }
        elif account_type == 'Company':
            try:
                print("inside project user try")
                project_users = ProjectUser.objects.filter(project=project)
                print(project_users)
                context={
                    'project':project,
                    'project_users':project_users,
                    'account_type':account_type
                    }
                try:
                    print("inside company dashboard try")
                    dashboards = ProjectDashboard.objects.filter(project=project)
                    context={
                       'project':project,
                       'dashboards':dashboards,
                       'account_type':account_type,
                       'project_users':project_users,
                       }
                except:
                    context={
                       'project':project,
                       'account_type':account_type,
                       'project_users':project_users,
                       }
            except:
                try:
                    dashboards = ProjectDashboard.objects.filter(project=project)
                    context={
                       'project':project,
                       'dashboards':dashboards,
                       'account_type':account_type
                       }
                except:
                    context={
                        'project':project,
                        'account_type':account_type
                        }
        return render(request,template_name,context)
'''End of class to display each project details'''

'''Start of class to display the conversion table'''
class ConversionTableView(View):
    def get(self,request):
        template_name='conversion table.html'
        file=pd.read_csv("Conversion_Table.csv")
        html=file.to_html()
        context={
            'html':html
        }
        return render(request,template_name,context)

class AllActions(View):
    def get(self,request):
        template_name = 'dashboard/all_actions.html'
        actions =Action.objects.all()
        # actor_actions = actor_stream(request.user)
        # actions_verb = Action.objects.filter(verb='Viewed dashboard')
        context={
        'actions':actions,

        }
        return render(request,template_name,context)



def all_projects(request):
    print("inside function")
    project=Project.objects.all()
    projects=[]

    for p in project:
        title=p.name
        project_pk=p.pk


        project_id=p.type.project_id
        user=User.objects.get(username=p.admin_user)
        name= user.first_name + " " + user.last_name
        customer=Customer.objects.get(user=user)
        current_site = get_current_site(request)
        site_name = current_site.name
        domain = current_site.domain
        if domain.startswith('127.0.'):
            domain = 'https://'+domain
        else:
            domain = 'https://'+domain
        try:
            # print("inside try")
            project_user=ProjectUser.objects.filter(project=p)
            # print(project_user)
            if project_user:
                # print("Inside if ")
                for p in project_user:
                    admin_count=1
                    user_count=0
                    if p.permission == "Read" or "Write":
                        user_count=user_count+1
                        # print(user_count)
                    elif p.permission == "Admin":
                        admin_count = admin_count+1
                        # print(admin_count)
                    # print("After try")
                    pk= str(project_pk)
                    a_url ='<a href="https://www.brayn.ai/go-to/'
                    end_a ='/project/">Go To</a>'

                    # print("the project pk ",pk)
                    # print("the project pid ",project_id)

                    data={
                        'title':title,
                        'project_id':project_id,
                        'admin_user':user.username,
                        'url':a_url+pk+end_a,
                        'name':name,
                        'contact_no':customer.contact_no,
                        'user_count':user_count,
                        'admin_count':admin_count,

                    }
            else:
                pk= str(project_pk)
                a_url ='<a href="https://www.brayn.ai/go-to/'
                end_a ='/project/">Go To</a>'

                # print("the project pk ",pk)
                # print("the project pid ",project_id)


                data={
                    'title':title,
                    'project_id':project_id,
                    'admin_user':user.username,
                    'url':a_url+pk+end_a,
                    'name':name,
                    'contact_no':customer.contact_no,
                    'admin_count':1,
                    'user_count':0,

                    }

        except:
            # print("inside except")
            pk= str(project_pk)
            a_url ='<a href="https://www.brayn.ai/go-to/'
            end_a ='/project/">Go To</a>'


            # print("the project pk ",pk)
            # print("the project pid ",project_id)






            data={
                'title':title,
                'project_id':project_id,
                'admin_user':user.username,
                'url':a_url+pk+end_a,
                'name':name,
                'contact_no':customer.contact_no,

                }
        projects.append(data)
        # print(projects)
    data={
    'projects':projects
    }

    return JsonResponse(data,safe=False)

def all_invoice(request):
    print("inside function")
    invoices = ProjectInvoice.objects.all().order_by('-id')
    invoice_list=[]


    for inv in invoices:
        inv_id=inv.invoice_id
        project=inv.monthly_cost.project.name
        dog = str(inv.created.date())
        from_to = str(inv.from_date.date())+' to '+str(inv.to_date.date())
        status_val = inv.status
        if status_val == 'Paid':
            status = '<span style="color:green;">'+status_val+'</span>'
        elif status_val == 'Unpaid':
            status = '<span style="color:red;">'+status_val+'</span>'
        data={
        'inv_id':inv_id,
        'project':project,
        'dog':dog,
        'from_to':from_to,
        'status':status
        }

        invoice_list.append(data)
    data={
    'invoice_list':invoice_list
    }

    return JsonResponse(data,safe=False)

class ProjectPricingView(View):
    '''clas  to manage the project pricing'''
    def get(self,request):
        template_name='project_pricing.html'
        all_project_pricing = ProjectPricing.objects.all()

        if DefaultProjectPricing.objects.filter().exists():
            project_pricing = DefaultProjectPricing.objects.all().order_by('-id')[0]
            form = ProjectPricingForm(initial={'user':project_pricing.user,'end_point':project_pricing.end_point,'iqs':project_pricing.iqs,'disk_space':project_pricing.disk_space,'free_tire':project_pricing.free_tire,'monthly_maintenance':project_pricing.monthly_maintenance})
        else:
            form = ProjectPricingForm()
            project_pricing = None
        project_form = SingleProjectPricing()
        project_invoice = ProjectInvoice.objects.all().order_by('-id')
        print("the invoice is ",project_invoice)
        return render(request,template_name,{'form':form,'project_form':project_form,'all_project_pricing':all_project_pricing,'project_pricing':project_pricing,'project_invoice':project_invoice})

    def post(self,request):
        template_name='project_pricing.html'
        form = ProjectPricingForm(request.POST)
        all_project_pricing = ProjectPricing.objects.all()
        if form.is_valid():
            user       = form.cleaned_data['user']
            end_point  = form.cleaned_data['end_point']
            disk_space = form.cleaned_data['disk_space']
            iqs        = form.cleaned_data['iqs']
            free_tire  = form.cleaned_data['free_tire']
            monthly_maintenance  = form.cleaned_data['monthly_maintenance']
            if DefaultProjectPricing.objects.filter().exists():
                print("exists")

                project_pricing = DefaultProjectPricing.objects.all().order_by('-id')[0]
                update = DefaultProjectPricing.objects.filter(pk=project_pricing.pk).update(user=user,end_point=end_point,disk_space=disk_space,iqs=iqs,monthly_maintenance=monthly_maintenance,free_tire=free_tire)
                project_pricing = DefaultProjectPricing.objects.get(pk=project_pricing.pk)
            else:
                project_pricing,created =DefaultProjectPricing.objects.get_or_create(user=user,end_point=end_point,disk_space=disk_space,iqs=iqs,monthly_maintenance=monthly_maintenance,free_tire=free_tire)
            form = ProjectPricingForm(initial={'user':project_pricing.user,'end_point':project_pricing.end_point,'iqs':project_pricing.iqs,'disk_space':project_pricing.disk_space,'monthly_maintenance':project_pricing.monthly_maintenance,'free_tire':project_pricing.free_tire})
            project_invoice = ProjectInvoice.objects.all().order_by('-id')
            return render(request,template_name,{'form':form,'all_project_pricing':all_project_pricing,'project_invoice':project_invoice,'project_pricing':project_pricing})

        else:
            print("form errors",form.errors)
            project_pricing = None
            project_invoice = ProjectInvoice.objects.all().order_by('-id')
            return render(request,template_name,{'form':form,'all_project_pricing':all_project_pricing,'project_invoice':project_invoice,'project_pricing':project_pricing})

class SingleProjectPricingCreate(View):
    def post(self,request):
        form = SingleProjectPricing(request.POST)
        if form.is_valid():
            user       = form.cleaned_data['user']
            end_point  = form.cleaned_data['end_point']
            disk_space = form.cleaned_data['disk_space']
            iqs        = form.cleaned_data['iqs']
            free_tire  = form.cleaned_data['free_tire']
            project    = form.cleaned_data['project']
            custom_cost = form.cleaned_data['custom_cost']
            monthly_maintenance = form.cleaned_data['monthly_maintenance']

            if ProjectPricing.objects.filter(project=project).exists():
                update = ProjectPricing.objects.filter(project=project).update(user=user,end_point=end_point,disk_space=disk_space,iqs=iqs,free_tire=free_tire,custom_supprt=custom_cost,monthly_maintenance=monthly_maintenance)
            else:
                project_pricing = ProjectPricing.objects.create(project=project,user=user,end_point=end_point,disk_space=disk_space,iqs=iqs,free_tire=free_tire,custom_supprt=custom_cost,monthly_maintenance=monthly_maintenance)
            return redirect('/administrator/project-pricing/')


class ProjectPricingDelete(View):
    def post(self,request,pk):
        project_pricing = ProjectPricing.objects.get(pk=pk)
        delete = ProjectPricing.objects.filter(pk=pk).delete()
        pk = str(project_pricing.project)
        return redirect('/administrator/project-pricing/')


class ProjectInvoiceView(View):
    '''view to dispaly and change the invoice status '''
    def get(self,request):
        template_name='project_pricing.html'

        if ProjectInvoice.objects.filter().exists():
            print("exists")
            project_invoice = ProjectInvoice.objects.all().order_by('-id')
        else:

            project_invoice = None
        return render(request,template_name,{'project_invoice':project_invoice})

    def post(self,request):
        template_name='project_pricing.html'
        status = request.POST.get('status',None)
        invoice_id = request.POST.get('inv_id',None)
        if status:
            print("the changed status is",status)
            update = ProjectInvoice.objects.filter(invoice_id=invoice_id).update(status=status)
            invoice = ProjectInvoice.objects.get(invoice_id=invoice_id)
            return redirect('/administrator/project-pricing/')








class TaxView(View):
    '''clas  to manage the tax'''
    def get(self,request):
        template_name='tax.html'

        if Tax.objects.filter().exists():
            print("exists")
            tax = Tax.objects.all().order_by('-id')[0]
            form = TaxForm(initial={'name':tax.name, 'tax_percentage':tax.tax_percentage,'tax_no':tax.tax_no,'tax_representation':tax.tax_representation})
        else:
            form = TaxForm()
            tax = None

        return render(request,template_name,{'form':form,'tax':tax})

    def post(self,request):
        template_name='tax.html'
        form = TaxForm(request.POST)
        if form.is_valid():
            name       = form.cleaned_data['name']
            tax_percentage  = form.cleaned_data['tax_percentage']
            tax_no = form.cleaned_data['tax_no']
            tax_representation = form.cleaned_data['tax_representation']
            if Tax.objects.filter().exists():

                tax = Tax.objects.all().order_by('-id')[0]
                update = Tax.objects.filter(pk=tax.pk).update(name=name, tax_percentage=tax_percentage,tax_no=tax_no,tax_representation=tax_representation)
                tax = Tax.objects.get(pk=tax.pk)
            else:
                tax,created =Tax.objects.get_or_create(name=name, tax_percentage=tax_percentage,tax_no=tax_no,tax_representation=tax_representation)
            form = TaxForm(initial={'name':tax.name, 'tax_percentage':tax.tax_percentage,'tax_no':tax.tax_no,'tax_representation':tax.tax_representation})

            return render(request,template_name,{'form':form,'tax':tax})

        else:
            tax = None
            return render(request,template_name,{'form':form,'tax':tax})






def all_users(request):
    customers= Customer.objects.all().order_by('-id')
    customer_count= Customer.objects.all().count()
    customers_list = []
    for customer in customers:
        email = customer.user.email
        contact_no = customer.contact_no
        first_name = customer.user.first_name
        last_name = customer.user.last_name
        type = customer.type
        company_name = customer.company_name
        dog = str(customer.created.date())
        data ={
        'email':email,
        'contact_no':contact_no,
        'first_name':first_name,
        'last_name':last_name,
        'type':type,
        'company_name':company_name,
        'dog':dog,

        }
        customers_list.append(data)
    data={'customers_list':customers_list,'customer_count':customer_count}
    return JsonResponse(data,safe=False)



class CustomerDashboard(View):
    def get(self,request):
        template_name ='customer_dashboard.html'
        return render(request,template_name)


class MachineLearningView(View):
    def get(self,request):
        template_name='machine_learning.html'
        ml_requests = EndpointMlApi.objects.all().order_by('-id')
        context = {'ml_requests':ml_requests}

        return render(request,template_name,context)

class SingleMachineLearning(LoginRequiredMixin,View):
    def get(self,request,pk):
        ml_request = EndpointMlApi.objects.get(pk=pk)
        form = ApiRequestForm(initial={'status':ml_request.status,'api':ml_request.api,'token':ml_request.token})
        context={'ml_request':ml_request,'form':form}
        return render(request,'api_request_process.html',context)
    def post(self,request,pk):
        form = ApiRequestForm(request.POST)
        ml_request = EndpointMlApi.objects.get(pk=pk)
        if form.is_valid():
            status = form.cleaned_data['status']
            api = form.cleaned_data['api']
            token = form.cleaned_data['token']
            print("the token",token,api)
            if status == "PROCESSED":
                if api and token:
                    api_request = EndpointMlApi.objects.filter(pk=pk).update(status=status,api=api,token=token)
                    ml_request = EndpointMlApi.objects.get(pk=pk)
                    print("the token",ml_request.token,ml_request.api)
                    body = f"Hi {ml_request.user.first_name},\n \n Your request for API has been processed. Please find the below API details \n \n API URL: {ml_request.api} \n TOKEN: {ml_request.token} \n \n Thank you, \n Team Brayn "
                    send_mail(
                    'Brayn | New API Request | Approved',
                    body,
                    'noreply@brayn.ai',
                    [ml_request.user.email],
                     fail_silently=False,
                    )
                    return redirect('/administrator/machine-learning/')
                else:
                    context={'ml_request':ml_request,'form':form,'msg':''}
                    return render(request,'api_request_process.html',context)
            elif status == 'CANCELLED':
                api_request = EndpointMlApi.objects.filter(pk=pk).update(status=status)
                body = f"Hi {ml_request.user.first_name},\n \n Your request for API has been cancelled. Please contact Qdesk for further support. \n \n Thank you, \n Team Brayn "
                send_mail(
                    'Brayn | New API Request | Cancelled',
                    body,
                    'noreply@brayn.ai',
                    [ml_request.user.email],
                     fail_silently=False,
                )
                return redirect('/administrator/machine-learning/')
        else:
            context={'ml_request':ml_request,'form':form}
            return render(request,'api_request_process.html',context)
















