# Rental Management System - API Documentation

## Base URL
```
http://127.0.0.1:8000/api/
```

## Authentication

The API uses Token-based authentication. Include the token in the Authorization header:

```
Authorization: Token <your-token-here>
```

### Obtain Token

**Endpoint:** `POST /api/token/`

**Request Body:**
```json
{
    "username": "user@example.com",
    "password": "yourpassword"
}
```

**Response:**
```json
{
    "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
}
```

---

## Accounts Module

### User Management

#### List Users
**Endpoint:** `GET /api/accounts/users/`

**Permissions:** Admin only

**Query Parameters:**
- `role` - Filter by role (tenant, owner, admin)
- `is_verified` - Filter by verification status (true, false)
- `search` - Search by email, first name, last name, phone number

**Response:**
```json
{
    "count": 50,
    "next": "http://127.0.0.1:8000/api/accounts/users/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "email": "tenant@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "phone_number": "+255712345678",
            "role": "tenant",
            "is_verified": true,
            "preferred_language": "en",
            "created_at": "2026-01-15T10:30:00Z",
            "updated_at": "2026-01-15T10:30:00Z"
        }
    ]
}
```

#### Create User
**Endpoint:** `POST /api/accounts/users/`

**Request Body:**
```json
{
    "email": "newuser@example.com",
    "password": "SecurePassword123!",
    "first_name": "Jane",
    "last_name": "Smith",
    "phone_number": "+255712345678",
    "role": "tenant",
    "preferred_language": "en"
}
```

**Response:** `201 Created`
```json
{
    "id": 2,
    "email": "newuser@example.com",
    "first_name": "Jane",
    "last_name": "Smith",
    "phone_number": "+255712345678",
    "role": "tenant",
    "is_verified": false,
    "preferred_language": "en",
    "created_at": "2026-01-30T14:20:00Z"
}
```

#### Get User Details
**Endpoint:** `GET /api/accounts/users/{id}/`

**Permissions:** Own profile or Admin

**Response:**
```json
{
    "id": 1,
    "email": "tenant@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+255712345678",
    "role": "tenant",
    "is_verified": true,
    "preferred_language": "en",
    "national_id": "19900101-12345-67890-01",
    "address": "123 Main St, Dar es Salaam",
    "created_at": "2026-01-15T10:30:00Z",
    "updated_at": "2026-01-15T10:30:00Z"
}
```

#### Update User
**Endpoint:** `PUT /api/accounts/users/{id}/` or `PATCH /api/accounts/users/{id}/`

**Permissions:** Own profile or Admin

**Request Body:**
```json
{
    "first_name": "John",
    "last_name": "Doe Updated",
    "phone_number": "+255712345679",
    "preferred_language": "sw"
}
```

**Response:** `200 OK`

#### Delete User
**Endpoint:** `DELETE /api/accounts/users/{id}/`

**Permissions:** Admin only

**Response:** `204 No Content`

### Tenant Management

#### List Tenants
**Endpoint:** `GET /api/accounts/tenants/`

**Permissions:** Owner (their tenants) or Admin

**Response:**
```json
{
    "count": 15,
    "results": [
        {
            "id": 1,
            "user": {
                "id": 5,
                "email": "tenant@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "phone_number": "+255712345678"
            },
            "emergency_contact_name": "Jane Doe",
            "emergency_contact_phone": "+255712345679",
            "current_lease": {
                "id": 10,
                "unit": "Apartment 3B",
                "start_date": "2026-01-01",
                "end_date": "2026-12-31"
            },
            "created_at": "2026-01-15T10:30:00Z"
        }
    ]
}
```

### Owner Management

#### List Owners
**Endpoint:** `GET /api/accounts/owners/`

**Permissions:** Admin

**Response:**
```json
{
    "count": 5,
    "results": [
        {
            "id": 1,
            "user": {
                "id": 2,
                "email": "owner@example.com",
                "first_name": "Mary",
                "last_name": "Johnson",
                "phone_number": "+255712345680"
            },
            "business_name": "Johnson Properties Ltd",
            "tax_id": "TIN-123456789",
            "properties_count": 5,
            "created_at": "2026-01-10T09:00:00Z"
        }
    ]
}
```

### Dashboards

#### Tenant Dashboard
**Endpoint:** `GET /api/accounts/dashboard/tenant/`

**Permissions:** Tenant only

**Response:**
```json
{
    "active_lease": {
        "id": 10,
        "unit": "Apartment 3B",
        "property": "Sunset Apartments",
        "rent_amount": "500000.00",
        "start_date": "2026-01-01",
        "end_date": "2026-12-31",
        "status": "active"
    },
    "recent_payments": [
        {
            "id": 50,
            "amount": "500000.00",
            "payment_date": "2026-01-05",
            "status": "completed",
            "payment_method": "mpesa"
        }
    ],
    "maintenance_requests": [
        {
            "id": 8,
            "title": "Leaking faucet",
            "status": "in_progress",
            "created_at": "2026-01-20T10:00:00Z"
        }
    ],
    "unread_notifications": 3
}
```

#### Owner Dashboard
**Endpoint:** `GET /api/accounts/dashboard/owner/`

**Permissions:** Owner only

**Response:**
```json
{
    "properties_count": 5,
    "total_units": 25,
    "occupied_units": 20,
    "occupancy_rate": 80.0,
    "active_leases": 20,
    "pending_payments": 3,
    "pending_maintenance": 5,
    "monthly_revenue": "10000000.00",
    "recent_payments": [...],
    "expiring_leases": [...]
}
```

#### Admin Dashboard
**Endpoint:** `GET /api/accounts/dashboard/admin/`

**Permissions:** Admin only

**Response:**
```json
{
    "total_users": 150,
    "total_tenants": 100,
    "total_owners": 20,
    "total_properties": 50,
    "total_units": 200,
    "occupied_units": 150,
    "active_leases": 150,
    "pending_verifications": 5,
    "pending_maintenance": 10,
    "recent_activities": [...]
}
```

---

## Localities Module

### List Locality Levels
**Endpoint:** `GET /api/localities/levels/`

**Response:**
```json
[
    {
        "id": 1,
        "name": "Region",
        "name_swahili": "Mkoa",
        "level": 1
    },
    {
        "id": 2,
        "name": "District",
        "name_swahili": "Wilaya",
        "level": 2
    }
]
```

### List Localities
**Endpoint:** `GET /api/localities/localities/`

**Query Parameters:**
- `parent` - Filter by parent locality ID
- `level` - Filter by level (1-4)
- `search` - Search by name

**Examples:**
```
GET /api/localities/localities/?level=1  # Get all regions
GET /api/localities/localities/?parent=5  # Get children of locality 5
```

**Response:**
```json
{
    "count": 26,
    "results": [
        {
            "id": 1,
            "name": "Dar es Salaam",
            "name_swahili": "Dar es Salaam",
            "level": {
                "id": 1,
                "name": "Region",
                "level": 1
            },
            "parent": null,
            "code": "DSM"
        }
    ]
}
```

---

## Properties Module

### Property Management

#### List Properties
**Endpoint:** `GET /api/properties/properties/`

**Query Parameters:**
- `owner` - Filter by owner ID
- `property_type` - apartment, house, commercial, office, warehouse
- `locality` - Filter by locality ID
- `min_price` - Minimum rent price
- `max_price` - Maximum rent price
- `bedrooms` - Number of bedrooms
- `bathrooms` - Number of bathrooms
- `is_available` - true/false
- `search` - Search by name, description

**Response:**
```json
{
    "count": 20,
    "results": [
        {
            "id": 1,
            "name": "Sunset Apartments",
            "name_swahili": "Nyumba za Sunset",
            "description": "Modern apartments in city center",
            "property_type": "apartment",
            "locality": {
                "id": 15,
                "name": "Kinondoni",
                "full_path": "Dar es Salaam > Kinondoni"
            },
            "address": "123 Morogoro Road",
            "owner": {
                "id": 2,
                "business_name": "Johnson Properties Ltd"
            },
            "images": [
                {
                    "id": 1,
                    "image": "/media/properties/sunset1.jpg",
                    "caption": "Front view",
                    "is_primary": true
                }
            ],
            "amenities": [
                {
                    "id": 1,
                    "name": "Swimming Pool",
                    "name_swahili": "Bwawa la Kuogelea"
                }
            ],
            "total_units": 10,
            "available_units": 3,
            "average_rating": 4.5,
            "created_at": "2026-01-10T09:00:00Z"
        }
    ]
}
```

#### Create Property
**Endpoint:** `POST /api/properties/properties/`

**Permissions:** Owner or Admin

**Request Body:**
```json
{
    "name": "Ocean View Apartments",
    "name_swahili": "Nyumba za Ocean View",
    "description": "Beautiful apartments with ocean view",
    "description_swahili": "Nyumba nzuri zenye mandhari ya bahari",
    "property_type": "apartment",
    "locality": 15,
    "address": "456 Beach Road",
    "latitude": -6.7924,
    "longitude": 39.2083
}
```

**Response:** `201 Created`

#### Get Property Details
**Endpoint:** `GET /api/properties/properties/{id}/`

**Response:**
```json
{
    "id": 1,
    "name": "Sunset Apartments",
    "description": "Modern apartments in city center",
    "property_type": "apartment",
    "locality": {...},
    "address": "123 Morogoro Road",
    "owner": {...},
    "images": [...],
    "amenities": [...],
    "units": [
        {
            "id": 1,
            "unit_number": "A101",
            "bedrooms": 2,
            "bathrooms": 1,
            "rent_amount": "500000.00",
            "is_available": true
        }
    ],
    "reviews": [...],
    "average_rating": 4.5
}
```

#### Get Available Properties
**Endpoint:** `GET /api/properties/properties/available/`

**Response:** List of properties with at least one available unit

#### Add Property Image
**Endpoint:** `POST /api/properties/properties/{id}/add_image/`

**Request:** `multipart/form-data`
```
image: <file>
caption: "Front view"
is_primary: true
```

**Response:** `201 Created`

#### Add Amenities
**Endpoint:** `POST /api/properties/properties/{id}/add_amenities/`

**Request Body:**
```json
{
    "amenities": [
        {
            "name": "Swimming Pool",
            "name_swahili": "Bwawa la Kuogelea"
        },
        {
            "name": "Parking",
            "name_swahili": "Maegesho ya Magari"
        }
    ]
}
```

### Rental Unit Management

#### List Rental Units
**Endpoint:** `GET /api/properties/units/`

**Query Parameters:**
- `property` - Filter by property ID
- `bedrooms` - Number of bedrooms
- `bathrooms` - Number of bathrooms
- `min_rent` - Minimum rent amount
- `max_rent` - Maximum rent amount
- `is_available` - true/false
- `furnished` - true/false

**Response:**
```json
{
    "count": 50,
    "results": [
        {
            "id": 1,
            "property": {
                "id": 1,
                "name": "Sunset Apartments"
            },
            "unit_number": "A101",
            "floor": 1,
            "bedrooms": 2,
            "bathrooms": 1,
            "square_meters": 85.5,
            "rent_amount": "500000.00",
            "deposit_amount": "500000.00",
            "is_furnished": true,
            "is_available": true,
            "description": "Spacious 2-bedroom apartment",
            "created_at": "2026-01-10T09:30:00Z"
        }
    ]
}
```

#### Get Available Units
**Endpoint:** `GET /api/properties/units/available/`

**Response:** List of available rental units

---

## Leases Module

### Lease Management

#### List Leases
**Endpoint:** `GET /api/leases/leases/`

**Query Parameters:**
- `tenant` - Filter by tenant ID
- `unit` - Filter by unit ID
- `property` - Filter by property ID
- `status` - draft, active, expired, terminated
- `start_date_after` - Filter leases starting after date
- `start_date_before` - Filter leases starting before date

**Permissions:** Tenant (own leases), Owner (their properties), Admin

**Response:**
```json
{
    "count": 30,
    "results": [
        {
            "id": 1,
            "tenant": {
                "id": 5,
                "user": {
                    "first_name": "John",
                    "last_name": "Doe",
                    "email": "tenant@example.com"
                }
            },
            "unit": {
                "id": 1,
                "unit_number": "A101",
                "property": {
                    "id": 1,
                    "name": "Sunset Apartments"
                }
            },
            "start_date": "2026-01-01",
            "end_date": "2026-12-31",
            "rent_amount": "500000.00",
            "deposit_amount": "500000.00",
            "payment_day": 5,
            "status": "active",
            "contract_file": "/media/contracts/lease_1.pdf",
            "created_at": "2025-12-20T14:00:00Z"
        }
    ]
}
```

#### Create Lease
**Endpoint:** `POST /api/leases/leases/`

**Permissions:** Owner or Admin

**Request Body:**
```json
{
    "tenant": 5,
    "unit": 1,
    "start_date": "2026-02-01",
    "end_date": "2027-01-31",
    "rent_amount": "500000.00",
    "deposit_amount": "500000.00",
    "payment_day": 5,
    "terms_conditions": "Standard lease terms...",
    "terms_conditions_swahili": "Masharti ya kawaida..."
}
```

**Response:** `201 Created`

#### Get Lease Details
**Endpoint:** `GET /api/leases/leases/{id}/`

**Response:**
```json
{
    "id": 1,
    "tenant": {...},
    "unit": {...},
    "start_date": "2026-01-01",
    "end_date": "2026-12-31",
    "rent_amount": "500000.00",
    "deposit_amount": "500000.00",
    "deposit_paid": true,
    "deposit_paid_date": "2025-12-28",
    "payment_day": 5,
    "status": "active",
    "terms_conditions": "...",
    "contract_file": "/media/contracts/lease_1.pdf",
    "created_at": "2025-12-20T14:00:00Z",
    "updated_at": "2026-01-01T10:00:00Z"
}
```

#### Activate Lease
**Endpoint:** `POST /api/leases/leases/{id}/activate/`

**Permissions:** Owner or Admin

**Response:**
```json
{
    "status": "activated",
    "message": "Lease activated successfully"
}
```

#### Terminate Lease
**Endpoint:** `POST /api/leases/leases/{id}/terminate/`

**Permissions:** Owner or Admin

**Request Body:**
```json
{
    "termination_date": "2026-06-30",
    "termination_reason": "Tenant relocating"
}
```

**Response:**
```json
{
    "status": "terminated",
    "message": "Lease terminated successfully"
}
```

#### Renew Lease
**Endpoint:** `POST /api/leases/leases/{id}/renew/`

**Permissions:** Owner or Admin

**Request Body:**
```json
{
    "new_end_date": "2027-12-31",
    "new_rent_amount": "550000.00"
}
```

**Response:**
```json
{
    "status": "renewed",
    "new_lease": {...},
    "message": "Lease renewed successfully"
}
```

#### Get Expiring Leases
**Endpoint:** `GET /api/leases/leases/expiring_soon/`

**Query Parameters:**
- `days` - Number of days ahead (default: 30)

**Response:** List of leases expiring within specified days

---

## Payments Module

### Payment Management

#### List Payments
**Endpoint:** `GET /api/payments/payments/`

**Query Parameters:**
- `tenant` - Filter by tenant ID
- `lease` - Filter by lease ID
- `status` - pending, completed, failed, cancelled
- `payment_method` - mpesa, bank_transfer, cash, cheque
- `payment_date_after` - Filter payments after date
- `payment_date_before` - Filter payments before date

**Permissions:** Tenant (own payments), Owner (their properties), Admin

**Response:**
```json
{
    "count": 100,
    "results": [
        {
            "id": 1,
            "lease": {
                "id": 1,
                "tenant": {...},
                "unit": {...}
            },
            "amount": "500000.00",
            "payment_date": "2026-01-05",
            "due_date": "2026-01-05",
            "payment_method": "mpesa",
            "status": "completed",
            "transaction_reference": "MPESA123456",
            "receipt_number": "RCP-2026-001",
            "late_fee": "0.00",
            "notes": "January rent payment",
            "created_at": "2026-01-05T09:00:00Z"
        }
    ]
}
```

#### Create Payment
**Endpoint:** `POST /api/payments/payments/`

**Permissions:** Tenant (own leases), Owner, Admin

**Request Body:**
```json
{
    "lease": 1,
    "amount": "500000.00",
    "payment_method": "mpesa",
    "transaction_reference": "MPESA123456",
    "notes": "February rent payment"
}
```

**Response:** `201 Created`

#### Verify Payment
**Endpoint:** `POST /api/payments/payments/{id}/verify/`

**Permissions:** Owner or Admin

**Request Body:**
```json
{
    "verified": true,
    "notes": "Payment verified via M-Pesa"
}
```

**Response:**
```json
{
    "status": "verified",
    "message": "Payment verified successfully"
}
```

#### Get Pending Payments
**Endpoint:** `GET /api/payments/payments/pending/`

**Response:** List of pending payments

#### Get Pending Verification Payments
**Endpoint:** `GET /api/payments/payments/pending_verification/`

**Permissions:** Owner or Admin

**Response:** List of payments awaiting verification

#### Get Overdue Payments
**Endpoint:** `GET /api/payments/payments/overdue/`

**Response:** List of overdue payments

---

## Maintenance Module

### Maintenance Request Management

#### List Maintenance Requests
**Endpoint:** `GET /api/maintenance/requests/`

**Query Parameters:**
- `tenant` - Filter by tenant ID
- `unit` - Filter by unit ID
- `property` - Filter by property ID
- `status` - pending, in_progress, completed, cancelled
- `priority` - low, medium, high, urgent
- `category` - plumbing, electrical, appliance, structural, other

**Permissions:** Tenant (own requests), Owner (their properties), Admin

**Response:**
```json
{
    "count": 25,
    "results": [
        {
            "id": 1,
            "tenant": {
                "id": 5,
                "user": {...}
            },
            "unit": {
                "id": 1,
                "unit_number": "A101",
                "property": {...}
            },
            "title": "Leaking faucet in kitchen",
            "title_swahili": "Bomba linavuja jikoni",
            "description": "Kitchen faucet is leaking water",
            "category": "plumbing",
            "priority": "medium",
            "status": "in_progress",
            "images": [
                {
                    "id": 1,
                    "image": "/media/maintenance/leak1.jpg",
                    "caption": "Kitchen faucet"
                }
            ],
            "assigned_to": "John the Plumber",
            "estimated_cost": "50000.00",
            "created_at": "2026-01-20T10:00:00Z",
            "updated_at": "2026-01-21T14:30:00Z"
        }
    ]
}
```

#### Create Maintenance Request
**Endpoint:** `POST /api/maintenance/requests/`

**Permissions:** Tenant (own units)

**Request Body:**
```json
{
    "unit": 1,
    "title": "Broken door lock",
    "title_swahili": "Kufuli ya mlango imevunjika",
    "description": "Cannot lock the front door",
    "category": "structural",
    "priority": "high"
}
```

**Response:** `201 Created`

#### Update Request Status
**Endpoint:** `POST /api/maintenance/requests/{id}/update_status/`

**Permissions:** Owner or Admin

**Request Body:**
```json
{
    "status": "in_progress",
    "assigned_to": "John the Plumber",
    "estimated_cost": "50000.00",
    "notes": "Plumber scheduled for tomorrow"
}
```

**Response:**
```json
{
    "status": "updated",
    "message": "Maintenance request updated successfully"
}
```

#### Add Image to Request
**Endpoint:** `POST /api/maintenance/requests/{id}/add_image/`

**Request:** `multipart/form-data`
```
image: <file>
caption: "Broken lock"
```

**Response:** `201 Created`

#### Get Urgent Requests
**Endpoint:** `GET /api/maintenance/requests/urgent/`

**Permissions:** Owner or Admin

**Response:** List of urgent maintenance requests

---

## Reviews Module

### Review Management

#### List Reviews
**Endpoint:** `GET /api/reviews/reviews/`

**Query Parameters:**
- `reviewer` - Filter by reviewer ID
- `reviewee` - Filter by reviewee ID
- `property` - Filter by property ID
- `review_type` - property, tenant
- `rating` - Filter by rating (1-5)

**Response:**
```json
{
    "count": 40,
    "results": [
        {
            "id": 1,
            "reviewer": {
                "id": 5,
                "user": {
                    "first_name": "John",
                    "last_name": "Doe"
                }
            },
            "property": {
                "id": 1,
                "name": "Sunset Apartments"
            },
            "review_type": "property",
            "rating": 5,
            "title": "Great place to live",
            "comment": "Very clean and well maintained",
            "response": "Thank you for your feedback!",
            "created_at": "2026-01-25T15:00:00Z"
        }
    ]
}
```

#### Create Review
**Endpoint:** `POST /api/reviews/reviews/`

**Permissions:** Tenant (can review properties), Owner (can review tenants)

**Request Body:**
```json
{
    "property": 1,
    "review_type": "property",
    "rating": 5,
    "title": "Excellent apartment",
    "title_swahili": "Nyumba nzuri sana",
    "comment": "Very comfortable and well located",
    "comment_swahili": "Starehe na mahali pazuri"
}
```

**Response:** `201 Created`

#### Respond to Review
**Endpoint:** `POST /api/reviews/reviews/{id}/respond/`

**Permissions:** Property owner or Admin

**Request Body:**
```json
{
    "response": "Thank you for your positive feedback!"
}
```

**Response:**
```json
{
    "status": "responded",
    "message": "Response added successfully"
}
```

---

## Notifications Module

### Notification Management

#### List Notifications
**Endpoint:** `GET /api/notifications/notifications/`

**Permissions:** Own notifications

**Query Parameters:**
- `notification_type` - rent_reminder, payment_received, lease_expiring, maintenance_update, review_received, general
- `is_read` - true/false

**Response:**
```json
{
    "count": 15,
    "results": [
        {
            "id": 1,
            "notification_type": "payment_received",
            "notification_type_display": "Payment Received",
            "title": "Payment Received",
            "message": "Your payment of TZS 500,000 has been received",
            "message_swahili": "Malipo yako ya TZS 500,000 yamepokelewa",
            "message_localized": "Your payment of TZS 500,000 has been received",
            "is_read": false,
            "action_url": "/payments/1",
            "created_at": "2026-01-30T10:00:00Z"
        }
    ]
}
```

#### Get Unread Notifications
**Endpoint:** `GET /api/notifications/notifications/unread/`

**Response:** List of unread notifications

#### Get Unread Count
**Endpoint:** `GET /api/notifications/notifications/unread_count/`

**Response:**
```json
{
    "unread_count": 5
}
```

#### Mark Notification as Read
**Endpoint:** `POST /api/notifications/notifications/{id}/mark_read/`

**Response:**
```json
{
    "status": "read",
    "message": "Notification marked as read"
}
```

#### Mark All Notifications as Read
**Endpoint:** `POST /api/notifications/notifications/mark_all_read/`

**Response:**
```json
{
    "status": "success",
    "message": "All notifications marked as read",
    "count": 5
}
```

---

## Error Responses

### Standard Error Format

All errors return a consistent format:

```json
{
    "error": "Error message here",
    "detail": "Detailed error description"
}
```

### HTTP Status Codes

- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `204 No Content` - Resource deleted successfully
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Permission denied
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

### Common Error Examples

#### Authentication Error
```json
{
    "detail": "Authentication credentials were not provided."
}
```

#### Permission Error
```json
{
    "detail": "You do not have permission to perform this action."
}
```

#### Validation Error
```json
{
    "email": ["This field is required."],
    "phone_number": ["Enter a valid phone number."]
}
```

#### Not Found Error
```json
{
    "detail": "Not found."
}
```

---

## Pagination

All list endpoints support pagination with the following parameters:

- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 20, max: 100)

**Example Request:**
```
GET /api/properties/properties/?page=2&page_size=50
```

**Response:**
```json
{
    "count": 150,
    "next": "http://127.0.0.1:8000/api/properties/properties/?page=3",
    "previous": "http://127.0.0.1:8000/api/properties/properties/?page=1",
    "results": [...]
}
```

---

## Filtering

Use query parameters to filter results:

**Examples:**
```
GET /api/properties/properties/?property_type=apartment&min_price=300000
GET /api/leases/leases/?status=active&tenant=5
GET /api/payments/payments/?status=pending&payment_method=mpesa
```

---

## Ordering

Use the `ordering` parameter to sort results:

**Examples:**
```
GET /api/properties/properties/?ordering=created_at
GET /api/properties/properties/?ordering=-rent_amount  # Descending
GET /api/payments/payments/?ordering=due_date
```

---

## Search

Use the `search` parameter for full-text search:

**Examples:**
```
GET /api/properties/properties/?search=apartment
GET /api/accounts/users/?search=john
GET /api/maintenance/requests/?search=plumbing
```

---

## Rate Limiting

To prevent abuse, API endpoints are rate-limited:

- **Authenticated users**: 1000 requests per hour
- **Anonymous users**: 100 requests per hour

When rate limit is exceeded, you'll receive a `429 Too Many Requests` response:

```json
{
    "detail": "Request was throttled. Expected available in 3600 seconds."
}
```

---

## Testing the API

### Using cURL

```bash
# Get token
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"user@example.com","password":"password"}'

# Use token
curl http://127.0.0.1:8000/api/properties/properties/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
```

### Using Python requests

```python
import requests

# Get token
response = requests.post('http://127.0.0.1:8000/api/token/', 
    json={'username': 'user@example.com', 'password': 'password'})
token = response.json()['token']

# Use token
headers = {'Authorization': f'Token {token}'}
response = requests.get('http://127.0.0.1:8000/api/properties/properties/', 
    headers=headers)
properties = response.json()
```

### Using Postman

1. Create a new request
2. Set Authorization → Type: API Key
3. Key: `Authorization`
4. Value: `Token <your-token>`
5. Add to: Header

---

## Webhooks

### M-Pesa Payment Callback

**Endpoint:** `POST /api/payments/mpesa-callback/`

The system receives M-Pesa payment callbacks at this endpoint. Configure this URL in your M-Pesa dashboard.

---

## Best Practices

1. **Always include authentication token** in requests
2. **Use appropriate HTTP methods** (GET, POST, PUT, PATCH, DELETE)
3. **Handle pagination** for list endpoints
4. **Use filters** to reduce response size
5. **Check error responses** and handle appropriately
6. **Respect rate limits** to avoid throttling
7. **Use HTTPS** in production
8. **Store tokens securely**, never in code
9. **Implement proper error handling** in your client
10. **Cache responses** when appropriate

---

## Support

For API issues or questions:
- Create an issue in the repository
- Contact: support@rentalmanagement.com
- Documentation: https://docs.rentalmanagement.com

---

**Last Updated:** January 30, 2026
**API Version:** 1.0
