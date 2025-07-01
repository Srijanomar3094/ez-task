from django.contrib.auth import login, authenticate, logout
from django.http import JsonResponse, HttpResponse
import json
from django.contrib.auth.models import User
from user_auth.models import Role
from .models import Verification
import re
from django.core.mail import send_mail
import random
import datetime
from django.conf import settings
from django.core.mail import EmailMessage, get_connection
from django.views.decorators.csrf import csrf_exempt

def user_registration(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        role = data.get('role')
        name = data.get('name')
        if not (email and password and role and name):
            return JsonResponse({'message': 'Invalid registration details.'}, status=400)
        if role not in ['Ops', 'Client']:
            return JsonResponse({'message': 'Invalid role.'}, status=400)
        if User.objects.filter(email=email).exists():
            return JsonResponse({'message': 'Email already exists.'}, status=400)
        verified = Verification.objects.filter(email=email, is_verified=True, is_expired=True).last()
        if not verified:
            return JsonResponse({'message': 'First verify your email.'}, status=400)
        if not re.match(
                r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$', password):
            return JsonResponse(
                {
                    'message': 'Invalid password. Password must contain at least one uppercase letter, one lowercase letter, '
                               'one special character, and be at least 8 characters long.'
                }, status=400)
        user = User.objects.create_user(
            username=email,
            password=password,
            email=email,
            first_name=name
        )
        Role.objects.create(user=user, role=role)
        return JsonResponse({'message': 'Registration successful!'}, status=200)
    return JsonResponse({"message": "Invalid request method."}, status=405)

def login_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        user = User.objects.filter(email=email).first()
        if user is not None and user.check_password(password):
            auth_user = authenticate(request, username=user.username, password=password)
            if auth_user is not None:
                login(request, auth_user)
                return JsonResponse({'message': 'Login successful'})
            else:
                return JsonResponse({'message': 'No user exists.'}, status=403)
        else:
            return JsonResponse({'message': 'Incorrect credentials'}, status=403)
    else:
        return JsonResponse({'message': 'Invalid method'}, status=405)

def logout_view(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            request.session.flush()
            logout(request)
            response = JsonResponse({'message': 'Logout successful.'})
            return response
        else:
            return JsonResponse({'message': 'User is not authenticated.'})
    else:
        return JsonResponse({'message': 'Request not valid'}, status=405)

def verify(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        code = data.get('code')
        randomcode = str(random.randint(1000, 9999))
        if email and not code:
            Verification.objects.create(
                code=randomcode,
                email=email
            )
            try:
                connection = get_connection(
                    host=settings.EMAIL_HOST,
                    port=settings.EMAIL_PORT,
                    username=settings.EMAIL_HOST_USER,
                    password=settings.EMAIL_HOST_PASSWORD,
                    use_tls=settings.EMAIL_USE_TLS
                )
                subject = 'Verification Code'
                message = f'Your verification code is: {randomcode}'
                email_msg = EmailMessage(
                    subject,
                    message,
                    settings.EMAIL_HOST_USER,
                    [email],
                    connection=connection
                )
                email_msg.send()
                return JsonResponse({"message": "Sent verification code to email."}, status=200)
            except Exception as e:
                return JsonResponse({"error": f"Failed to send email: {str(e)}"}, status=500)
        elif code and email:
            check = Verification.objects.filter(email=email, is_expired=False).last()
            if check:
                if str(code) == str(check.code):
                    start = check.created_at
                    now = datetime.datetime.now(start.tzinfo)
                    timediff = now - start
                    if timediff.seconds <= 120:
                        check.is_expired = True
                        check.is_verified = True
                        check.save()
                        return JsonResponse({"message": "Code verified"}, status=200)
                    else:
                        check.is_expired = True
                        check.save()
                        return JsonResponse({"message": "Expired code"}, status=400)
                else:
                    return JsonResponse({"message": "Code is not correct"}, status=400)
            else:
                return JsonResponse({"message": "Code does not exist"}, status=400)
        else:
            return JsonResponse({"message": "Send code"}, status=400)
    return JsonResponse({"message": "Invalid request method"}, status=405)
