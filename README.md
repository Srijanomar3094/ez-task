# Ez-Task: File Sharing System

A Django-based file sharing application with role-based access control and email verification.

## Features

- **User Authentication**: Registration, login, logout with email verification
- **Role-Based Access**: Two user types (Ops, Client) with different permissions
- **File Management**: Upload, list, and secure download of files
- **File Type Validation**: Supports .pptx, .docx, .xlsx files only
- **Secure Downloads**: Encrypted download links with user validation

## Project Structure

```
ez-task/
├── ezshare/                 # Django project settings
│   ├── settings.py         # Main configuration
│   ├── urls.py            # Root URL patterns
│   └── wsgi.py            # WSGI configuration
├── user_auth/              # User authentication app
│   ├── models.py          # User and Role models
│   ├── views.py           # Auth views (register, login, verify)
│   ├── urls.py            # Auth URL patterns
│   └── tests.py           # Authentication tests
├── share/                  # File sharing app
│   ├── models.py          # File model
│   ├── views.py           # File operations views
│   ├── urls.py            # File sharing URL patterns
│   └── tests.py           # File sharing tests
├── requirements.txt        # Python dependencies
├── manage.py              # Django management script
└── .env                   # Environment variables
```

## Setup

### 1. Clone Repository
```bash
git clone https://github.com/Srijanomar3094/ez-task.git
cd ez-task
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate 
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
Create `.env` file:
```env
SECRET_KEY=your_django_secret_key
DEBUG=True
DB_NAME=ezshare
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=3306
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_gmail_app_password
```

### 5. Database Setup
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Run Server
```bash
python manage.py runserver
```

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/verify/` | Request/verify email code |
| POST | `/api/user_registration/` | Register user |
| POST | `/api/login_view/` | User login |
| GET | `/api/logout_view/` | User logout |

### File Operations
| Method | Endpoint | Description | Role Required |
|--------|----------|-------------|---------------|
| POST | `/api/upload/` | Upload file | Ops |
| GET | `/api/list/` | List files | Client |
| GET | `/api/download-file/<id>/` | Get download link | Client |
| GET | `/api/secure-download/<token>/` | Download file | Client |

## API Testing

For testing the APIs, import the Postman collection file `ez.postman_collection.json` into Postman. The collection includes pre-configured requests for all endpoints with example data and proper authentication setup.

## User Roles

### Ops Users
- Can upload files (.pptx, .docx, .xlsx)
- Cannot list or download files

### Client Users
- Can list all uploaded files
- Can download files via secure links
- Cannot upload files

## File Types Supported
- **PowerPoint**: .pptx
- **Word**: .docx  
- **Excel**: .xlsx

## Testing

### Run All Tests
```bash
python manage.py test
```

### Run Specific Test Suites
```bash
python manage.py test user_auth.tests
python manage.py test share.tests
```

## Dependencies

- **Django 4.2.7**: Web framework
- **mysqlclient 2.2.0**: MySQL database adapter
- **python-dotenv 1.0.0**: Environment variable management
- **cryptography 41.0.7**: Encryption for secure downloads
- **gunicorn 21.2.0**: WSGI server for production

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment instructions.

## License

MIT License 