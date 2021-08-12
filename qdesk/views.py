from django.shortcuts import render, redirect
from . models import Ticket,Client,TicketIssue, IssueTransaction, TicketTransaction
from . forms import ClientForm,TicketForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView,CreateView,View,UpdateView,ListView
from coreapp.models import Project, ProjectUser,ProjectEndPoint,ProjectDashboard
import urllib.request
import urllib.parse
from django.core.mail import send_mail
from django.template import loader
import requests
from login.models import Customer
import base64
import urllib.request
import urllib.parse
from django.core.files.base import ContentFile
from django.contrib.auth.models import User,Group
import logging
logging.getLogger().setLevel(logging.INFO)


def sendSMS(numbers,message):
    '''function to send msg throught textlocal'''
    data =  urllib.parse.urlencode({'apikey': 'Op4a2F0vNEk-DhXQtjgkXkCCzU7BIDtvpftxRciz7X', 'numbers': numbers,
        'message' : message,'sender':'QDESKM', })
    data = data.encode('utf-8')
    request = urllib.request.Request("https://api.textlocal.in/send/?")
    f = urllib.request.urlopen(request, data)
    fr = f.read()
    return(fr)


class QDeskView(LoginRequiredMixin,View):
    login_url = '/login'
    def get(self,request):
        tickets = Ticket.objects.all().order_by('-id')
        client_form = ClientForm()
        clients = Client.objects.all()
        for i in  tickets:

            print("the display",i.pk)
        context = {'form':client_form,'tickets':tickets,'msg':'Client Added Successfully','clients':clients}
        return render(request,'qdesk.html',context)



class IssueDetailsView(LoginRequiredMixin,View):

    def get(self,request,pk):
        issue = TicketIssue.objects.get(pk=pk)
        issue_transactions = IssueTransaction.objects.filter(issue=issue)
        context = {'issue':issue,'issue_transaction':issue_transactions}
        return render(request,'qdesk_ticket_details.html',context)

    def post(self,request,pk,tpk):

        issue = TicketIssue.objects.get(pk=pk)
        ticket = Ticket.objects.get(pk=tpk)
        if issue.status == 'New':
            update =TicketIssue.objects.filter(pk=pk).update(status='Processing')
            issue_transaction = IssueTransaction.objects.create(issue=issue,user=request.user,from_value="New",to_value="Prosessing")
            html_message = loader.render_to_string(
            'transaction_email.html',
                {
                    'client':ticket.client.name,
                    'ticket_id':ticket.ticket_id,
                    'status':ticket.status,
                    'status_from':"New",
                    'status_to':"Prosessing",
                    'user':request.user,
                    'date':issue_transaction.created}
                )
        elif issue.status == 'Processing':
            update =TicketIssue.objects.filter(pk=pk).update(status='Solved')
            issue_transaction = IssueTransaction.objects.create(issue=issue,user=request.user,from_value="Processing",to_value="Solved")
            html_message = loader.render_to_string(
            'transaction_email.html',
                {
                    'client':ticket.client.name,
                    'ticket_id':ticket.ticket_id,
                    'status':ticket.status,
                    'status_from':"Prosessing",
                    'status_to':"Solved",
                    'user':request.user,
                    'date':issue_transaction.created}
                )

        elif issue.status == 'Solved':
            update =TicketIssue.objects.filter(pk=pk).update(status='Tested')
            issue_transaction = IssueTransaction.objects.create(issue=issue,user=request.user,from_value="Solved",to_value="Tested")
            html_message = loader.render_to_string(
            'transaction_email.html',
                {
                    'client':ticket.client.name,
                    'ticket_id':ticket.ticket_id,
                    'status':ticket.status,
                    'status_from':"Solved",
                    'status_to':"Tested",
                    'user':request.user,
                    'date':issue_transaction.created}
                )
        elif issue.status == 'Tested':
            update =TicketIssue.objects.filter(pk=pk).update(status='Completed')
            issue_transaction = IssueTransaction.objects.create(issue=issue,user=request.user,from_value="Tested",to_value="Completed")
            html_message = loader.render_to_string(
            'transaction_email.html',
                {
                    'client':ticket.client.name,
                    'ticket_id':ticket.ticket_id,
                    'status':ticket.status,
                    'status_from':"Tested",
                    'status_to':"Completed",
                    'user':request.user,
                    'date':issue_transaction.created}
                )
        number = ['8050796508','8951441252','6362017904','8217799741']
        for num in number:


            test=sendSMS('91'+num, "Hi, Status has been updated. Please login to Dashboard to know more details.")
        issue = TicketIssue.objects.get(pk=pk)
        issue_transactions = IssueTransaction.objects.filter(issue=issue)
        ticket = Ticket.objects.get(pk=tpk)




        sent = send_mail('Client Ticket Issue Status Changed | Brayn | QDESK',"New Ticket from "+ticket.client.name+"",'noreply@brayn.ai',['vatsa@quanscendence.com','shrikar@quanscendence.com','ranjitha@quanscendence.com','vijeth@quanscendence.com','vishwa@quanscendence.com'],fail_silently =False,html_message=html_message)

        issue_transaction = {}
        for issue in ticket.issue.all():
            issue_tr =IssueTransaction.objects.filter(issue=issue)
            issue_transaction[issue.pk] =  issue_tr
        context = {'ticket':ticket,'issue_transaction':issue_transaction}
        return render(request,'qdesk_ticket_details.html',context)

class AdminTicketDetailsView(LoginRequiredMixin,View):
    login_url="/login"
    def get(self,request,pk):
        ticket = Ticket.objects.get(pk=pk)
        issue_transaction = {}
        ticket_transaction=TicketTransaction.objects.filter(ticket=ticket)
        for issue in ticket.issue.all():
            issue_tr =IssueTransaction.objects.filter(issue=issue)
            issue_transaction[issue.pk] =  issue_tr
        context = {'ticket':ticket,'ticket_transaction':ticket_transaction,'issue_transaction':issue_transaction}
        print(context)
        return render(request,'admin_ticket_details.html',context)

class TicketDetailsView(LoginRequiredMixin,View):
    '''customer ticket details'''
    login_url="/login"
    def get(self,request,pk):
        ticket = Ticket.objects.get(pk=pk)
        project=ticket.project
        customer = Customer.objects.get(user=request.user)
        if Project.objects.filter(pk=project.pk,admin_user=request.user).exists():
            permission="Admin"
        elif ProjectUser.objects.filter(project=project,project_user=request.user).exists():
            user_group = User.objects.get(pk=request.user.pk)

            for g in user_group.groups.all():
                if g.name == str(project.pk)+"_Read":
                    permission="Read"
                elif g.name == str(project.pk)+"_Write":
                    permission="Write"
                elif g.name == str(project.pk)+"_Delete":
                    permission="Delete"
                elif g.name == str(project.pk)+"_Admin":
                    permission="Admin"
        else:
            pass
        ##print("the permission is",permission)
        if ProjectDashboard.objects.filter(project=project).exists():
            dashboard = ProjectDashboard.objects.filter(project=project)
        else:
            dashboard=None
        if ProjectEndPoint.objects.filter(project=project).exists():
            project_endpoints = ProjectEndPoint.objects.filter(project=project).order_by('name')
        else:
            project_endpoints=None

        context = {'ticket':ticket,
                    'dashboard':dashboard,
                    'permission':permission,
                    'project':project,
                    'customer':customer,
                    'project_endpoints':project_endpoints,}
        return render(request,'qdesk_ticket_details.html',context)



class ClientView(LoginRequiredMixin,View):
    '''class to create an client'''
    login_url = '/login'
    def get(self,request):
        pass

    def post(self,request):
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            tickets = Ticket.objects.filter(status='Open').order_by('-id')
            clients = Client.objects.all()
            client_form = ClientForm()
            context = {'form':client_form,'tickets':tickets,'msg':'Client Added Successfully','clients':clients}
            return render(request,'qdesk.html',context)
        else:
            tickets = Ticket.objects.filter(status='Open').order_by('-id')
            client_form = form
            clients = Client.objects.all()
            context = {'form':client_form,'tickets':tickets,'msg':'Invalid form','clients':clients}
            return render(request,'qdesk.html',context)



class TicketSolutionView(LoginRequiredMixin,View):
    '''class to update new solution images from backend'''
    login_url="/login"

    def post(self,request,pk,tpk):

        solution_description = request.POST.get('solution',None)
        status = request.POST.get('status',None)
        issue = TicketIssue.objects.get(pk=pk)
        ticket = Ticket.objects.get(pk=tpk) 
        if solution_description:
            update = TicketIssue.objects.filter(pk=issue.pk).update(solution_description=solution_description)
            issue_transaction = IssueTransaction.objects.create(issue=issue,from_value=issue.solution_description,to_value=solution_description,user=request.user)
        if status != ticket.issue :
            ticket = Ticket.objects.get(pk=tpk)
            update = Ticket.objects.filter(pk=tpk).update(status=status)
            ticket_trasaction = TicketTransaction.objects.create(from_value=ticket.status,to_value=status,user=request.user,ticket=ticket)
            logging.info("the data"+str(ticket_trasaction))
            html_message = loader.render_to_string(
                'ticket_transaction_email.html',
                    {
                        'project':ticket.project,
                        'ticket_id':ticket.ticket_id,
                        'status_from':ticket.status,
                        'status_to':status,
                        'user':request.user,
                        'date':ticket_trasaction.created,
                        'ticket':ticket
                        }
                    )
            logging.info("html message"+str(html_message))
            sent = send_mail('Client  Ticket  Status has Changed | Brayn | QDESK',"Ticket  "+ticket.ticket_id+"",'noreply@brayn.ai',['vatsa@quanscendence.com','shrikar@quanscendence.com','ranjitha@quanscendence.com','vijeth@quanscendence.com','vishwa@quanscendence.com'],fail_silently =False,html_message=html_message)
        ticket = Ticket.objects.get(pk=tpk)
        issue_transaction = {}
        ticket_transaction=TicketTransaction.objects.filter(ticket=ticket)
        for issue in ticket.issue.all():
            issue_tr =IssueTransaction.objects.filter(issue=issue)
            issue_transaction[issue.pk] =  issue_tr

        context = {'ticket':ticket,'ticket_transaction':ticket_transaction,'issue_transaction':issue_transaction}
        return render(request,'admin_ticket_details.html',context)


class TicketStatusChangeView(LoginRequiredMixin,View):
    ''' change the ticket priority '''
    def post(self,request,pk):
        status = request.POST['status']
        print("the choosen priority",priority)
        ticket = Ticket.objects.get(pk=pk)
        update = Ticket.objects.filter(pk=pk).update(status=status)
        tickets = Ticket.objects.filter(status='Open').order_by('-id')
        ticket = Ticket.objects.get(pk=pk)
        ticket_trasaction = TicketTransaction.objects.create(from_value=ticket.status,to_value=status,user=request.user,ticket=ticket)
        html_message = loader.render_to_string(
            'ticket_transaction_email.html',
                {
                    'project':ticket.proect,
                    'ticket_id':ticket.ticket_id,
                    'status_from ':ticket.status,
                    'status_to ':status,
                    'user':request.user,
                    'date':ticket_trasaction.created
                    }
                )
        sent = send_mail('Client  Ticket  Status has Changed | Brayn | QDESK',"Ticket  "+ticket.ticket_id+"",'noreply@brayn.ai',['vatsa@quanscendence.com','shrikar@quanscendence.com','ranjitha@quanscendence.com','vijeth@quanscendence.com','vishwa@quanscendence.com'],fail_silently =False,html_message=html_message)
        context = {'tickets':tickets,'msg':'Ticket Status Updated Successfully'}
        return redirect('/qdesk/')


class TicketCreateView(LoginRequiredMixin,View):
    '''class to create a ticket'''
    def post(slef,request,pk):
        project = Project.objects.get(pk=pk)
        form = TicketForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            details = form.cleaned_data['ticket_details']
            logging.info("files"+str(request.FILES))
            image_1 = request.FILES.get('image_1',None)
            image_2 = request.FILES.get('image_2',None)
            image_3 = request.FILES.get('image_3',None)
            if Ticket.objects.filter().exists():
                pk = Ticket.objects.latest('id')
                t_id = "QHD-"+str(pk.pk)
            else:
                t_id = "QHD-1"

            ticket_issue = TicketIssue.objects.create(whats_need_todo=details)
            ticket = Ticket.objects.create(ticket_id=t_id,subject=subject,project=project,customer=request.user)
            ticket.issue.add(ticket_issue)
            if image_1:
                ticket.client_image_1 = image_1
            if image_2:
                ticket.client_image_2 = image_2
            if image_3:
                ticket.client_image_3 = image_3

            ticket.save()

            html_message = loader.render_to_string(
            'qdesk_email.html',
                {
                    'project':ticket.project,
                    'ticket_id':ticket.ticket_id,
                    'status':ticket.status,
                    'priority':ticket.priority,
                    'ticket':ticket}
                )



            sent = send_mail('Client New Ticket | Brayn | QDESK',"New Ticket from "+str(ticket.project)+"",'noreply@brayn.ai',['vatsa@quanscendence.com','shrikar@quanscendence.com','ranjitha@quanscendence.com','vijeth@quanscendence.com','vishwa@quanscendence.com'],fail_silently =False,html_message=html_message)
            pk=str(project.pk)
            return redirect('/single-project-details/'+pk+'/')
