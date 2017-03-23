from django.core.management.base import BaseCommand
from home.models import LoanDate,EmailTag,EmailBody,Request
from django.utils.timezone import localtime, now
from django.core.mail import EmailMessage
from django.contrib.auth.models import User

localtime(now()).date()

class Command(BaseCommand):
    def handle(self, **options):
        date = localtime(now()).date()
        dates=[date for date in LoanDate.objects.all()]
        for loan_date in dates:
            if str(date)==str(loan_date.date):
                requests = Request.objects.filter(status='L')
                dict = {}
                for request in requests:
                    username = request.owner
                    user = User.objects.get(username=username)
                    email = user.email
                    if email in dict.keys():
                        dict[email].append(str(request.item_id)+" x"+str(request.quantity))
                    else:
                        dict[email]=[str(request.item_id)+" x"+str(request.quantity)]
                
                for email,items in dict.items():
                    message = EmailBody.objects.all()[0].body+"\n"
                    for item in items:
                        message+=item+"\n"
                    # ADD LIST OF LOANED ITEMS
                    tag=EmailTag.objects.all()[0].tag
                    email = EmailMessage(
                        tag+' Loan Reminder',
                        message,
                        'from@example.com',
                        [email]
                    )
                    email.send()
