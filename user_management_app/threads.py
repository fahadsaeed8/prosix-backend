from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from datetime import datetime


def send_password_reset_email(email, new_password):
    """Static method to send password reset email in a thread"""
    html_template = render_to_string('emails/forget_password.html', 
                                    {'email': email, 'password': new_password, 'year': datetime.now().year})
    
    text_template = strip_tags(html_template)
    
    # Getting Email ready
    from_email = f'"ProSix" <{settings.EMAIL_HOST_USER}>'

    email_msg = EmailMultiAlternatives(
        'Password Reset',
        text_template,
        from_email,
        [email],
    )
    email_msg.attach_alternative(html_template, "text/html")
    try:
        email_msg.send(fail_silently=False)
    except Exception as e:
        print('** Email sending error **', e)

def accept_reject_email(email, message, status):
    """Static method to send password reset email in a thread"""
    html_template = render_to_string('emails/accept_reject_user.html', 
                                    {'email': email, 'message': message, 'status':status, 'year': datetime.now().year})
    
    text_template = strip_tags(html_template)
    
    # Getting Email ready
    from_email = f'"ProSix" <{settings.EMAIL_HOST_USER}>'

    email_msg = EmailMultiAlternatives(
        'User Profile',
        text_template,
        from_email,
        [email],
    )
    email_msg.attach_alternative(html_template, "text/html")
    try:
        email_msg.send(fail_silently=False)
    except Exception as e:
        print('** Email sending error **', e)