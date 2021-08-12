from django import forms
from . models import Client,TicketIssue,Ticket,IssueTransaction


class ClientForm(forms.ModelForm):
    ''' form class to create an client '''
    name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control mb-30',
                                                        'placeholder':'CLIENT NAME'}))
    url = forms.URLField(widget=forms.URLInput(attrs={'class':'form-control mb-30',
                                                        'placeholder':'CLIENT URL'}))
    class Meta:
        model = Client
        fields = ['name','url']

class TicketForm(forms.Form):
	'''form class for create ticket'''
	subject = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control mb-30',
                                                        'placeholder':'Subject'}))
	ticket_details = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control mb-30',
                                                        'placeholder':'Issue Details'}))
