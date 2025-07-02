import os
from django.http import JsonResponse, FileResponse, HttpResponseForbidden, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.conf import settings
from django.contrib.auth.models import User
from user_auth.models import Role
from .models import File
from django.core.files.storage import default_storage
from django.urls import reverse
from cryptography.fernet import Fernet
import datetime


FERNET_KEY = os.environ.get('FERNET_KEY', Fernet.generate_key())
fernet = Fernet(FERNET_KEY)

def get_user_role(user):
    role_obj = Role.objects.filter(user=user).last()
    return role_obj.role if role_obj else None


@login_required
def upload_file(request):
    if request.method == 'POST':
        user = request.user
        if get_user_role(user) != 'Ops':
            return HttpResponseForbidden("Only Ops users can upload files.")

        file = request.FILES.get('file')
        if not file:
            return JsonResponse({'message': 'No file provided.'}, status=400)

        ext = os.path.splitext(file.name)[1].lower()
        if ext not in ['.pptx', '.docx', '.xlsx']:
            return JsonResponse({'message': 'Invalid file type.'}, status=400)

        saved_file = File.objects.create(
            owner=user,
            file_name=file,
            file_size_kb=file.size // 1024
        )
        return JsonResponse({'message': 'File uploaded successfully.', 'file_id': saved_file.id})

    return JsonResponse({'message': 'Invalid request method.'}, status=405)


@login_required
def list_files(request):
    user = request.user
    if get_user_role(user) != 'Client':
        return HttpResponseForbidden("Only Client users can list files.")

    files = File.objects.filter(status=True)
    file_list = [
        {
            'id': f.id,
            'file_name': os.path.basename(f.file_name.name),
            'file_size_kb': f.file_size_kb,
            'last_opened': f.last_opened
        }
        for f in files
    ]
    return JsonResponse({'files': file_list})


@login_required
def download_file(request, file_id):
    user = request.user
    if get_user_role(user) != 'Client':
        return HttpResponseForbidden("Only Client users can download files.")

    try:
        file_obj = File.objects.get(id=file_id, status=True)
    except File.DoesNotExist:
        return JsonResponse({'message': 'File not found.'}, status=404)

    
    token = fernet.encrypt(f"{user.id}:{file_obj.id}".encode()).decode()
    download_link = request.build_absolute_uri(
        reverse('secure_download', args=[token])
    )
    return JsonResponse({'download-link': download_link, 'message': 'success'})

@login_required
def secure_download(request, token):
    try:
        decrypted = fernet.decrypt(token.encode()).decode()
        user_id, file_id = decrypted.split(':')
        if int(user_id) != request.user.id:
            return HttpResponseForbidden("This link is not for you.")
        file_obj = File.objects.get(id=file_id, status=True)
    except Exception:
        return JsonResponse({'message': 'Invalid or expired link.'}, status=400)

    file_path = file_obj.file_name.path
    file_obj.last_opened = datetime.datetime.now()
    file_obj.save()
    response = FileResponse(open(file_path, 'rb'), as_attachment=True, filename=os.path.basename(file_path))
    return response