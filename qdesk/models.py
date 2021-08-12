from django.db import models
from django.contrib.auth.models import User
from . choices import PRIORITY_CHOICES, ISSUE_STATUS_CHOICES, TICKET_STATUS_CHOICES
from coreapp.models import Project

################## base #############
class Base(models.Model):
    '''
    A Base case mostly common for all the implementations
    '''
    name        = models.CharField(default="Unknown...", max_length=200,blank=True, null=True)
    description = models.TextField(default="some text...",blank=True, null=True)
    version     = models.PositiveIntegerField(blank=True, null=True)
    created     = models.DateTimeField('Created date', auto_now_add=True,
                                   auto_now=False,
                                   null=True, blank=True)
    updated     = models.DateTimeField('Updated date', auto_now_add=False,auto_now=True,null=True, blank=True)
    class Meta(object):
        abstract=True
        #unique_together = (("name", "version"),)
        ordering=('name',)

    def __str__(self):
        return self.name

#################### core code ##################

class Client(Base):
    '''class to create a client '''
    url = models.URLField()

    def __str__(self):
        return self.name



class TicketIssue(Base):
    '''class to handle the ticket issues'''
    client_image_1         = models.ImageField(null=True,blank=True)
    client_image_2         = models.ImageField(null=True,blank=True)
    client_image_3         = models.ImageField(null=True,blank=True)
    client_image_4         = models.ImageField(null=True,blank=True)
    solution_image_1       = models.ImageField(null=True,blank=True)
    solution_image_2       = models.ImageField(null=True,blank=True)
    solution_image_3       = models.ImageField(null=True,blank=True)
    solution_image_4       = models.ImageField(null=True,blank=True)
    whats_need_todo        = models.TextField()
    solution_description   = models.TextField(null=True,blank=True)
    
    def __str__(self):
        return self.whats_need_todo





class Ticket(Base):
    ''' class which will bind client with tickets'''
    ticket_id = models.CharField(max_length=20)
    issue     = models.ManyToManyField(TicketIssue)
    subject   = models.CharField(max_length=50)
    priority  = models.CharField( max_length=10,choices=PRIORITY_CHOICES,default='High')
    status    = models.CharField(max_length=20,choices=TICKET_STATUS_CHOICES,default='Open')
    customer  = models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    project   = models.ForeignKey(Project,on_delete=models.CASCADE,null=True)
    def __str__(self):
        return self.ticket_id


class IssueTransaction(Base):
    ''' class to track the issus update  from the backend'''
    from_value = models.CharField(max_length=50,null=True,blank=True)
    to_value   = models.CharField(max_length=50,null=True,blank=True)
    user       = models.ForeignKey(User,on_delete=models.CASCADE)
    issue      = models.ForeignKey(TicketIssue,on_delete=models.CASCADE)
    def __str__(self):
        return str(self.issue)+str(self.user)


class TicketTransaction(Base):
    ''' class to track the issus update  from the backend'''
    from_value = models.CharField(max_length=50,null=True,blank=True)
    to_value   = models.CharField(max_length=50,null=True,blank=True)
    user       = models.ForeignKey(User,on_delete=models.CASCADE)
    ticket      = models.ForeignKey(Ticket,on_delete=models.CASCADE)
    def __str__(self):
        return str(self.ticket)+str(self.user)
