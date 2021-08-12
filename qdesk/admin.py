from django.contrib import admin
from . models import TicketIssue,Ticket,IssueTransaction,Client

admin.site.register(TicketIssue)
admin.site.register(Ticket)

admin.site.register(IssueTransaction)
admin.site.register(Client)



