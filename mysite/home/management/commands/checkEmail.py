from django.core.management.base import BaseCommand
from home.models import LoanDate,EmailTag,EmailBody
from django.utils.timezone import localtime, now
from django.core.mail import EmailMessage

localtime(now()).date()

class Command(BaseCommand):
    def handle(self, **options):
        date = localtime(now()).date()
        dates=[date for date in LoanDate.objects.all()]
        for loan_date in dates:
            if str(date)==str(loan_date.date):
                # DO FOR ALL USERS WITH LOANS
                message = EmailBody.objects.all()[0].body
                # ADD LIST OF LOANED ITEMS
                tag=EmailTag.objects.all()[0].tag
                email = EmailMessage(
                    tag+' Loan Reminder',
                    message,
                    'from@example.com',
                    ['l.donaldson1995@yahoo.com']
                )
                email.send()
