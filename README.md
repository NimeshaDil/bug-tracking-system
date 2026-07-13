# Bug Tracking System

This Bug Tracking System is built with Python Flask and PostgreSQL, designed to streamline issue management. It features a role-based access control system that defines specific workflows for Admins, Developers, and Testers to ensure secure and organized collaboration. Users can efficiently track bugs through their entire lifecycle with integrated tools for file attachments, priority settings, and detailed commenting. Additionally, the system provides visual insights into project health via an interactive dashboard that monitors bug status distribution and recent team activity.

## Features

### Authentication
- Login / Logout
- Forgot Password with reset token
- Change Password
- Session-based authentication

### User Roles & Permissions
- **Admin**: Full access to all bugs, user management
- **Developer**: Can create, edit, assign bugs and update status
- **Tester**: Can create bugs and view (read-only)

### Bug Management
- Create, Read, Update, Delete bugs
- Assign bugs to team members
- Change bug status (Open → In Progress → Closed)
- Set priority (Low, Medium, High, Critical)
- Add comments to bugs
- Track reporter and assignee

### Search & Filters
- Full-text search by title and description
- Filter by status
- Filter by assignee
- Filter by priority
- Sort by creation date
- Pagination (20 bugs per page)

### File Uploads
- Upload screenshots (PNG, JPG, GIF)
- Upload logs (TXT, LOG)
- Upload documents (PDF, DOCX)
- Max file size: 25MB per file
- Download and delete attachments

### Dashboard
- Open bugs count
- Closed bugs count
- In-progress bugs count
- Bugs by status chart (pie/doughnut)
- Bugs by priority chart (bar)
- Recent bugs activity feed

## Tech Stack

### Backend
- **Framework**: Flask 3.0.3
- **Database ORM**: Flask-SQLAlchemy
- **Database**: PostgreSQL
- **Authentication**: Flask-Login, Werkzeug
- **Forms**: WTForms
- **Validation**: email-validator

### Frontend
- **Markup**: HTML5 with Jinja2 templates
- **Styling**: CSS3 (Responsive design)
- **JavaScript**: Vanilla JS with Fetch API
- **Charts**: Chart.js 4.4.0

### Infrastructure
- **Containerization**: Docker
- **Orchestration**: Docker Compose
- **Web Server**: Gunicorn
- **Reverse Proxy**: Can use Nginx

## Prerequisites

- Docker
- Docker Compose

## Installation & Setup

### Local Development (Docker Compose)

1. Clone the repository and navigate to the bug-tracker directory:
```bash
cd apps/bug-tracker
```

2. Copy the environment file:
```bash
cp .env.example .env
```

3. Build and start the application:
```bash
docker-compose up -d --build 
```

4. Access the application:
- Frontend: http://localhost:5000
- Backend API: http://localhost:5000/api
- Database: localhost:5432

## Default Credentials

Login with these credentials:

| Email | Password | Role |
|-------|----------|------|
| admin@example.com | password123 | Admin |
| dev@example.com | password123 | Developer |
| tester@example.com | password123 | Tester |

## Project Structure

```
bug-tracker/
├── app/
│   ├── models.py           # Database models
│   ├── utils.py            # Utility functions and decorators
│   ├── __init__.py         # App factory
│   ├── routes/
│   │   ├── auth.py         # Authentication routes
│   │   ├── bugs.py         # Bug management routes
│   │   ├── dashboard.py    # Dashboard and statistics
│   │   └── users.py        # User management (admin)
│   ├── templates/          # Jinja2 templates
│   ├── static/             # CSS and JS files
│   └── uploads/            # Uploaded files
├── config.py               # Configuration
├── wsgi.py                 # WSGI entry point
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker image definition
├── docker-compose.yml      # Docker Compose configuration
├── .env.example            # Environment variables template
└── README.md               # This file
```

## Database Schema

### Users Table
- id (Primary Key)
- username (Unique)
- email (Unique)
- password_hash
- role (admin/developer/tester)
- is_active
- reset_token (for password reset)
- reset_token_expiry
- created_at, updated_at

### Bugs Table
- id (Primary Key)
- title
- description
- status (open/in_progress/closed)
- priority (low/medium/high/critical)
- reporter_id (FK -> Users)
- assignee_id (FK -> Users)
- created_at, updated_at, closed_at

### Comments Table
- id (Primary Key)
- bug_id (FK -> Bugs)
- user_id (FK -> Users)
- body
- created_at

### Attachments Table
- id (Primary Key)
- bug_id (FK -> Bugs)
- filename
- stored_filename (unique storage name)
- file_type
- file_size
- uploaded_by (FK -> Users)
- created_at

## API Endpoints

### Authentication
- `POST /auth/login` - Login
- `GET /auth/logout` - Logout
- `GET /auth/forgot-password` - Request password reset
- `POST /auth/reset-password` - Reset password with token
- `GET/POST /auth/change-password` - Change password

### Bugs
- `GET /bugs/` - List bugs (with filters and pagination)
- `GET /bugs/<id>` - Get bug detail
- `GET /bugs/create` - Create bug form
- `POST /bugs/create` - Create bug
- `GET /bugs/<id>/edit` - Edit bug form
- `POST /bugs/<id>/edit` - Update bug
- `POST /bugs/<id>/delete` - Delete bug
- `POST /bugs/<id>/assign` - Assign bug
- `POST /bugs/<id>/status` - Change status
- `POST /bugs/<id>/comment` - Add comment
- `POST /bugs/<id>/upload` - Upload attachment
- `POST /bugs/attachment/<id>/delete` - Delete attachment

### Dashboard
- `GET /dashboard/` - Dashboard page
- `GET /dashboard/stats` - Dashboard statistics (JSON)

### Users (Admin Only)
- `GET /users/` - List users
- `GET /users/create` - Create user form
- `POST /users/create` - Create user
- `GET /users/<id>/edit` - Edit user form
- `POST /users/<id>/edit` - Update user
- `POST /users/<id>/delete` - Delete user

## Environment Variables

```
FLASK_ENV=development                          # development, production, testing
FLASK_APP=wsgi.py
SECRET_KEY=your-secret-key-here                # Change in production!
DATABASE_URL=postgresql://user:pass@host:port/db
UPLOAD_FOLDER=app/uploads
```

## Security Features

- CSRF protection with Flask-WTF
- SQL injection prevention via SQLAlchemy ORM
- XSS prevention with template escaping
- Password hashing with Werkzeug (PBKDF2)
- Password reset tokens with expiration
- File upload validation (type, size)
- Role-based access control
- Session cookie security flags
- Non-root Docker user
- Environment-based secrets

## Performance Considerations

- Database indexes on frequently queried columns (status, assignee, created_at)
- Pagination to limit query results
- CSS and JS minification in production
- Nginx gzip compression (when used as reverse proxy)
- Connection pooling
- Dashboard statistics caching (optional)

## Troubleshooting

### Database Connection Error
```
Ensure PostgreSQL is running and credentials in .env are correct:
DATABASE_URL=postgresql://buguser:bugpass@db:5432/bugtracker
```

### Port Already in Use
```bash
# Change ports in docker-compose.yml
# Or kill existing processes:
lsof -i :5000  # Find process on port 5000
kill -9 <PID>  # Kill the process
```

### Permissions Error with Uploads
```
Ensure app/uploads directory exists with proper permissions:
mkdir -p app/uploads
chmod 755 app/uploads
```

## File Upload Limits

- Allowed file types: png, jpg, jpeg, gif, txt, log, pdf, docx
- Max file size: 25MB
- Max attachments per bug: Unlimited (limited by 25MB per file)

## Testing

To test the application:

1. Use default credentials to login
2. Create bugs from the dashboard
3. Assign bugs to team members
4. Test file uploads
5. Test search and filters
6. Test role permissions

## Deployment

For production deployment:

1. Update `.env` with production values
2. Set `FLASK_ENV=production`
3. Generate a strong `SECRET_KEY`
4. Use HTTPS by setting `SESSION_COOKIE_SECURE=True`
5. Configure proper database backups
6. Set up proper logging
7. Use environment secrets management

Example production deployment with nginx:

```yaml
# In docker-compose.yml, add nginx service
nginx:
  image: nginx:alpine
  ports:
    - "80:80"
    - "443:443"
  volumes:
    - ./nginx.conf:/etc/nginx/nginx.conf
  depends_on:
    - web
```

## License

MIT License

## Support

For issues and questions, please open an issue in the repository.

## Author

Nimesha Dilshan
