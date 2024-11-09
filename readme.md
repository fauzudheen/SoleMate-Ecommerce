# SoleMate: E-Commerce Platform for Shoes

A comprehensive e-commerce platform built with Django, specializing in footwear retail. The application provides a seamless shopping experience with secure payment processing and robust admin capabilities.

## Features

- User authentication and authorization
- Product catalog with variant management
- Shopping cart functionality
- Secure payment processing via Razorpay
- Order management system
- Email verification using SMTP
- Responsive design for all devices
- Admin dashboard for inventory management
- User profile management

## Technology Stack

- **Backend:** Django
- **Database:** PostgreSQL
- **Frontend:** HTML, CSS, JavaScript, Bootstrap
- **Payment Gateway:** Razorpay
- **Server:** AWS EC2, NGINX
- **Email:** SMTP

## Prerequisites

- Python 3.8+
- PostgreSQL
- pip
- virtualenv

## Local Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/fauzudheen/SoleMate-Ecommerce.git
   cd solemate
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   Create a `.env` file in the root directory:
   ```
   DEBUG=True
   SECRET_KEY=your_secret_key
   DATABASE_URL=postgresql://user:password@localhost:5432/solemate
   RAZORPAY_KEY_ID=your_razorpay_key
   RAZORPAY_KEY_SECRET=your_razorpay_secret
   EMAIL_HOST=your_smtp_host
   EMAIL_PORT=587
   EMAIL_HOST_USER=your_email
   EMAIL_HOST_PASSWORD=your_email_password
   ```

5. **Setup Database**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

## Project Structure
```
solemate/
├── AdminHome/            # Admin dashboard functionality
├── UserHome/             # User dashboard and main pages
├── admin_order/         # Order management for admins
├── admin_product_management/  # Product management
├── media/               # User-uploaded files
├── myproject/           # Project settings and configurations
├── static/              # Static files (CSS, JS, images)
├── user_order/         # User order management
├── user_product/       # Product display and management
├── user_profile/       # User profile management
├── vendor/             # Third-party packages
├── manage.py           # Django management script
└── requirements.txt    # Project dependencies
```

## Deployment

The application is deployed on AWS EC2 with NGINX. Here's a brief overview of the deployment process:

1. **Setup EC2 Instance**
   - Launch Ubuntu EC2 instance
   - Configure security groups
   - Setup SSH access

2. **Install Dependencies**
   ```bash
   sudo apt-get update
   sudo apt-get install python3-pip python3-venv postgresql nginx
   ```

3. **Configure PostgreSQL**
   ```bash
   sudo -u postgres createdb solemate
   sudo -u postgres createuser -P solemate_user
   ```

4. **Configure NGINX**
   ```nginx
   server {
       listen 80;
       server_name your_domain.com;
       
       location /static/ {
           root /path/to/your/project;
       }
       
       location /media/ {
           root /path/to/your/project;
       }
       
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

5. **Setup Gunicorn**
   ```bash
   gunicorn myproject.wsgi:application
   ```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Contact

Fauzudheen Abdul Hameed - fauzudheen2@gmail.com
Project Link: (https://solemate.site/)
