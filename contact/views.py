from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from django.conf import settings
from django.core.mail import send_mail
from .forms import ContactForm
from .models import ContactMessage

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        is_htmx = request.headers.get('HX-Request') == 'true' or request.headers.get('x-requested-with') == 'XMLHttpRequest'
        
        if form.is_valid():
            contact_msg = form.save(commit=False)
            contact_msg.ip_address = get_client_ip(request)
            contact_msg.save()

            # Dispatch notification email to site owner
            try:
                subject = f"[Portfolio Contact] {contact_msg.subject}"
                message_body = (
                    f"New contact inquiry submitted on your portfolio:\n\n"
                    f"Name: {contact_msg.name}\n"
                    f"Email: {contact_msg.email}\n"
                    f"IP Address: {contact_msg.ip_address}\n"
                    f"Subject: {contact_msg.subject}\n\n"
                    f"Message:\n{contact_msg.message}\n"
                )
                from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'ujval@dev.local')
                recipient = getattr(settings, 'CONTACT_NOTIFICATION_EMAIL', 'ujvalthakor14@gmail.com')
                send_mail(
                    subject=subject,
                    message=message_body,
                    from_email=from_email,
                    recipient_list=[recipient],
                    fail_silently=True,
                )
            except Exception:
                pass

            if is_htmx:
                return render(request, 'components/contact_success.html', {
                    'name': contact_msg.name,
                    'subject': contact_msg.subject,
                })
            
            messages.success(request, f"Thank you {contact_msg.name}! Your message has been routed to Ujval's inbox. Expect a response soon.")
            return redirect('core:home')
        else:
            if is_htmx:
                return render(request, 'components/contact_form.html', {
                    'contact_form': form,
                    'form_has_errors': True,
                })
            messages.error(request, "Please correct the errors in the contact form below.")
    else:
        form = ContactForm()

    return render(request, 'contact.html', {'contact_form': form})
