from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
import json
import os
from user_auth.models import Role
from .models import File
from cryptography.fernet import Fernet
from django.conf import settings


class FileSharingTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.upload_url = '/api/upload/'
        self.list_url = '/api/list/'
        self.download_url = '/api/download-file/'
        
        self.ops_user = User.objects.create_user(
            username='ops@example.com',
            email='ops@example.com',
            password='Test@1234'
        )
        Role.objects.create(user=self.ops_user, role='Ops')
        
        self.client_user = User.objects.create_user(
            username='client@example.com',
            email='client@example.com',
            password='Test@1234'
        )
        Role.objects.create(user=self.client_user, role='Client')
        
        self.test_file_content = b'This is a test file content'
        self.test_file = SimpleUploadedFile(
            'test.docx',
            self.test_file_content,
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )

    def test_upload_file_ops_user_success(self):
        """Test successful file upload by Ops user"""
        self.client.force_login(self.ops_user)
        
        response = self.client.post(
            self.upload_url,
            {'file': self.test_file},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('File uploaded successfully', response.json()['message'])
        
        file_obj = File.objects.first()
        self.assertIsNotNone(file_obj)
        self.assertEqual(file_obj.owner, self.ops_user)

    def test_upload_file_client_user_forbidden(self):
        """Test that Client users cannot upload files"""
        self.client.force_login(self.client_user)
        
        response = self.client.post(
            self.upload_url,
            {'file': self.test_file},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, 403)
        self.assertIn('Only Ops users can upload files', response.content.decode())

    def test_upload_file_invalid_type(self):
        """Test upload with invalid file type"""
        self.client.force_login(self.ops_user)
        
        invalid_file = SimpleUploadedFile(
            'test.txt',
            b'This is a text file',
            content_type='text/plain'
        )
        
        response = self.client.post(
            self.upload_url,
            {'file': invalid_file},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid file type', response.json()['message'])

    def test_list_files_client_user_success(self):
        """Test successful file listing by Client user"""
        self.client.force_login(self.client_user)
        
        file_obj = File.objects.create(
            owner=self.ops_user,
            file_name=self.test_file,
            file_size_kb=len(self.test_file_content) // 1024
        )
        
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('files', data)
        self.assertEqual(len(data['files']), 1)
        self.assertEqual(data['files'][0]['id'], file_obj.id)

    def test_list_files_ops_user_forbidden(self):
        """Test that Ops users cannot list files"""
        self.client.force_login(self.ops_user)
        
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, 403)
        self.assertIn('Only Client users can list files', response.content.decode())

    def test_download_file_client_user_success(self):
        """Test successful download link generation by Client user"""
        self.client.force_login(self.client_user)
        
        file_obj = File.objects.create(
            owner=self.ops_user,
            file_name=self.test_file,
            file_size_kb=len(self.test_file_content) // 1024
        )
        
        response = self.client.get(f'{self.download_url}{file_obj.id}/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('download-link', data)
        self.assertIn('success', data['message'])

    def test_download_file_ops_user_forbidden(self):
        """Test that Ops users cannot download files"""
        self.client.force_login(self.ops_user)
        
        file_obj = File.objects.create(
            owner=self.ops_user,
            file_name=self.test_file,
            file_size_kb=len(self.test_file_content) // 1024
        )
        
        response = self.client.get(f'{self.download_url}{file_obj.id}/')
        
        self.assertEqual(response.status_code, 403)
        self.assertIn('Only Client users can download files', response.content.decode())

    def test_secure_download_valid_token(self):
        """Test secure download with valid token"""
        self.client.force_login(self.client_user)
        
        file_obj = File.objects.create(
            owner=self.ops_user,
            file_name=self.test_file,
            file_size_kb=len(self.test_file_content) // 1024
        )
        
        from share.views import fernet
        token = fernet.encrypt(f"{self.client_user.id}:{file_obj.id}".encode()).decode()
        
        response = self.client.get(f'/api/secure-download/{token}/')
        
        self.assertEqual(response.status_code, 200)

    def test_secure_download_wrong_user(self):
        """Test secure download with token for different user"""
        self.client.force_login(self.client_user)
        
        file_obj = File.objects.create(
            owner=self.ops_user,
            file_name=self.test_file,
            file_size_kb=len(self.test_file_content) // 1024
        )
        
        from share.views import fernet
        token = fernet.encrypt(f"{self.ops_user.id}:{file_obj.id}".encode()).decode()
        
        response = self.client.get(f'/api/secure-download/{token}/')
        
        self.assertEqual(response.status_code, 403)
        self.assertIn('This link is not for you', response.content.decode())
