# Rental Management System

A comprehensive Django REST Framework application for managing rental properties, designed specifically for the Tanzanian market with bilingual support (English/Swahili) and M-Pesa payment integration.

## Features

### 🏠 Property Management
- Property listings with detailed information
- Multiple rental units per property
- Property images and amenities management
- Property availability tracking
- Location-based property search using Tanzania's administrative hierarchy

### 👥 User Management
- Multiple user roles: Tenants, Property Owners, Admins
- Document verification system
- User profiles with language preferences
- Authentication via Django REST Framework tokens

### 📝 Lease Management
- Digital lease agreements
- Lease activation, termination, and renewal
- Automatic lease status tracking
- Lease expiration notifications

### 💰 Payment Processing
- M-Pesa payment integration
- Payment verification and tracking
- Automatic rent payment generation
- Overdue payment monitoring
- Payment history and receipts

### 🔧 Maintenance Requests
- Tenant maintenance request submissions
- Request tracking and status updates
- Image attachments for maintenance issues
- Priority-based request handling

### ⭐ Review System
- Two-way reviews (tenants review properties, owners review tenants)
- Review responses
- Rating system

### 🔔 Notifications
- In-app notification system
- Email notifications
- Bilingual notification support
- Notification preferences

### 📍 Localities
- Complete Tanzania administrative hierarchy (Regions → Districts → Wards → Streets)
- Management commands for importing locality data

## Tech Stack

- **Backend Framework**: Django 6.0.1
- **API**: Django REST Framework 3.15.2
- **Database**: PostgreSQL
- **Authentication**: Token-based authentication
- **Filtering**: django-filter
- **CORS**: django-cors-headers
- **Environment**: python-decouple

## Project Structure

```
rental_management/
├── accounts/           # User authentication & profiles
├── localities/         # Location hierarchy (Tanzania)
├── properties/         # Property & rental unit management
├── leases/            # Lease agreement management
├── payments/          # Payment processing & M-Pesa
├── maintenance/       # Maintenance request handling
├── reviews/           # Review system
├── notifications/     # Notification service
├── rental_management/ # Project settings & configuration
├── manage.py
├── requirements.txt
└── README.md
```

## Installation

### Prerequisites

- Python 3.10+
- PostgreSQL 12+
- pip (Python package manager)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd rental_management
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   
   Create a `.env` file in the project root:
   ```env
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   
   # Database Configuration
   POSTGRES_DB=rental_management
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=your-password
   POSTGRES_HOST=127.0.0.1
   POSTGRES_PORT=5432
   
   # Email Configuration
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   DEFAULT_FROM_EMAIL=your-email@gmail.com
   
   # M-Pesa Configuration (for production)
   MPESA_CONSUMER_KEY=your-mpesa-consumer-key
   MPESA_CONSUMER_SECRET=your-mpesa-consumer-secret
   MPESA_SHORTCODE=your-shortcode
   MPESA_PASSKEY=your-passkey
   ```

5. **Create PostgreSQL database**
   ```bash
   createdb rental_management
   # Or using psql:
   psql -U postgres
   CREATE DATABASE rental_management;
   ```

6. **Run migrations**
   ```bash
   python manage.py migrate
   ```

7. **Import Tanzania localities data**
   ```bash
   python manage.py import_tanzania_localities
   ```

8. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```

9. **Run the development server**
   ```bash
   python manage.py runserver
   ```

The API will be available at `http://127.0.0.1:8000/`

## API Endpoints

### Authentication
- `POST /api/token/` - Obtain authentication token
- `POST /api/auth/login/` - Login
- `POST /api/auth/logout/` - Logout

### Accounts
- `GET /api/accounts/users/` - List users
- `POST /api/accounts/users/` - Create user
- `GET /api/accounts/users/{id}/` - User details
- `PUT /api/accounts/users/{id}/` - Update user
- `DELETE /api/accounts/users/{id}/` - Delete user
- `GET /api/accounts/tenants/` - List tenants
- `GET /api/accounts/owners/` - List property owners
- `GET /api/accounts/dashboard/tenant/` - Tenant dashboard
- `GET /api/accounts/dashboard/owner/` - Owner dashboard
- `GET /api/accounts/dashboard/admin/` - Admin dashboard

### Localities
- `GET /api/localities/levels/` - Locality levels
- `GET /api/localities/localities/` - List localities
- `GET /api/localities/localities/?parent={id}` - Child localities

### Properties
- `GET /api/properties/properties/` - List properties
- `POST /api/properties/properties/` - Create property
- `GET /api/properties/properties/{id}/` - Property details
- `PUT /api/properties/properties/{id}/` - Update property
- `DELETE /api/properties/properties/{id}/` - Delete property
- `GET /api/properties/properties/available/` - Available properties
- `POST /api/properties/properties/{id}/add_image/` - Add property image
- `GET /api/properties/units/` - List rental units
- `GET /api/properties/units/available/` - Available units

### Leases
- `GET /api/leases/leases/` - List leases
- `POST /api/leases/leases/` - Create lease
- `GET /api/leases/leases/{id}/` - Lease details
- `PUT /api/leases/leases/{id}/` - Update lease
- `POST /api/leases/leases/{id}/activate/` - Activate lease
- `POST /api/leases/leases/{id}/terminate/` - Terminate lease
- `POST /api/leases/leases/{id}/renew/` - Renew lease
- `GET /api/leases/leases/expiring_soon/` - Expiring leases

### Payments
- `GET /api/payments/payments/` - List payments
- `POST /api/payments/payments/` - Create payment
- `GET /api/payments/payments/{id}/` - Payment details
- `POST /api/payments/payments/{id}/verify/` - Verify payment
- `GET /api/payments/payments/pending/` - Pending payments
- `GET /api/payments/payments/overdue/` - Overdue payments

### Maintenance
- `GET /api/maintenance/requests/` - List maintenance requests
- `POST /api/maintenance/requests/` - Create request
- `GET /api/maintenance/requests/{id}/` - Request details
- `PUT /api/maintenance/requests/{id}/` - Update request
- `POST /api/maintenance/requests/{id}/update_status/` - Update status
- `POST /api/maintenance/requests/{id}/add_image/` - Add image
- `GET /api/maintenance/requests/urgent/` - Urgent requests

### Reviews
- `GET /api/reviews/reviews/` - List reviews
- `POST /api/reviews/reviews/` - Create review
- `GET /api/reviews/reviews/{id}/` - Review details
- `POST /api/reviews/reviews/{id}/respond/` - Respond to review

### Notifications
- `GET /api/notifications/notifications/` - List notifications
- `GET /api/notifications/notifications/unread/` - Unread notifications
- `GET /api/notifications/notifications/unread_count/` - Unread count
- `POST /api/notifications/notifications/{id}/mark_read/` - Mark as read
- `POST /api/notifications/notifications/mark_all_read/` - Mark all read

## Management Commands

### Generate Rent Payments
Automatically generates monthly rent payments for active leases:
```bash
python manage.py generate_rent_payments
```

### Check Lease Status
Updates lease statuses based on current date:
```bash
python manage.py check_lease_status
```

### Send Rent Reminders
Sends rent payment reminder notifications:
```bash
python manage.py send_rent_reminders
```

### Import Tanzania Localities
Imports Tanzania administrative data from CSV files:
```bash
python manage.py import_tanzania_localities
```

## Scheduled Tasks

For production, set up these commands to run periodically using cron or similar:

```cron
# Generate rent payments on the 1st of each month
0 0 1 * * python manage.py generate_rent_payments

# Check lease statuses daily
0 0 * * * python manage.py check_lease_status

# Send rent reminders on the 25th of each month
0 9 25 * * python manage.py send_rent_reminders
```

## Development

### Running Tests
```bash
python manage.py test
```

### Creating Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Accessing Admin Panel
Visit `http://127.0.0.1:8000/admin/` and login with your superuser credentials.

## API Documentation

The API uses Django REST Framework's browsable API. When `DEBUG=True`, you can navigate to any endpoint in your browser to see:
- Available HTTP methods
- Request/response formats
- Authentication requirements
- Query parameters

## Bilingual Support

The system supports both English and Swahili. Users can set their preferred language in their profile, and:
- Notifications will be sent in their preferred language
- API responses include localized fields where applicable
- Email notifications respect language preferences

## Security Considerations

For production deployment:

1. **Set `DEBUG=False`** in settings
2. **Use strong `SECRET_KEY`**
3. **Configure `ALLOWED_HOSTS`**
4. **Use HTTPS** for all communications
5. **Set up proper CORS** configuration
6. **Use environment variables** for sensitive data
7. **Enable Django security middleware**
8. **Set up proper database backups**
9. **Configure rate limiting** for API endpoints
10. **Use secure M-Pesa credentials**

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues, questions, or contributions, please open an issue in the repository.

## Roadmap

- [ ] Mobile app integration
- [ ] Real-time notifications via WebSockets
- [ ] Advanced analytics dashboard
- [ ] Automated rent collection via M-Pesa
- [ ] Multi-currency support
- [ ] Document e-signing
- [ ] Tenant screening system
- [ ] Property inspection scheduling

---

Built with ❤️ for the Tanzanian rental market
