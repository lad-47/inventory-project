from home.models import SubscribedEmail,EmailBody,EmailTag,LoanDate
from django.shortcuts import render
from django.http import HttpResponseRedirect

def emails(request):
    if not request.user.is_staff:
        return render(request, 'home/notAdmin.html')
    subscribed_emails = SubscribedEmail.objects.all()
    subscribed=False
    for email in subscribed_emails:
        if request.user.email==email.email:
            subscribed=True
    body=EmailBody.objects.all()[0]
    tag=EmailTag.objects.all()[0]
    dates=[date for date in LoanDate.objects.all()]
    context = {
        'body':body.body,
        'tag':tag.tag,
        'dates':dates,
        'subscribed':subscribed
    }
    if request.method == 'POST':
        body_input = request.POST.get('body',None)
        tag_input = request.POST.get('tag',None)
        date_input = request.POST.get('date',None)
        if body_input!='' and body_input is not None:
            body.body=body_input
            body.save()
        if tag_input!='' and tag_input is not None:
            tag.tag=tag_input
            tag.save()
        if date_input!='' and date_input is not None:
            date = LoanDate(date=date_input)
            new = True
            for old_date in dates:
                if str(date.date)==str(old_date.date):
                    new = False
            if new:
                date.save()
        if subscribed and request.POST.get('subscribed', None)!='subscribed':
            print('start delete')
            email = SubscribedEmail.objects.get(email=request.user.email)
            print(request.user.email)
            print(email)
            email.delete()
            print('deleted')
            subscribed=False
        elif not subscribed and request.POST.get('subscribed', None)=='subscribed':
            print('add')
            email = SubscribedEmail(email=request.user.email)
            email.save()
            subscribed=True
        context['body']=body.body
        context['tag']=tag.tag
        context['dates']=[date for date in LoanDate.objects.all()]
        context['subscribed']=subscribed
        return render(request, 'manager/emails.html', context);

    else:
        return render(request, 'manager/emails.html', context);
    
def delete_loan_date(request, pk):
    date = LoanDate.objects.get(id=pk)
    date.delete()
    return HttpResponseRedirect('/manager/emails/')