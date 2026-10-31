# ShopSphere — Professional Full-Stack E-Commerce Platform

ShopSphere is an enterprise-grade, modern, full-stack e-commerce web platform engineered for portfolio demonstration and international client presentations. It features a robust Python/Django backend with Django REST Framework, atomic transactions, inventory concurrency locking, secure session-based authentication, and a responsive frontend with a minimalist international design system.

---

## 🌟 Key Architecture & Highlights

### 1. Backend Architecture (Django 5.1 & Django REST Framework)
- **Domain-Driven Modular Apps**: Clean separation of concerns across `accounts`, `products`, `cart`, `orders`, `payments`, `reviews`, `promotions`, and `wishlist`.
- **Database Concurrency & Integrity**:
  - `select_for_update()` inventory locking during checkout prevents overselling and race conditions under concurrent load.
  - Historical snapshots in `OrderItem` preserve the exact product name, SKU, and unit price paid at the time of purchase, ensuring accurate financial records even if product prices or details change later.
  - Strict database constraints (`CheckConstraint(price >= 0)`, `CheckConstraint(stock >= 0)`).
- **Cart Session Architecture**:
  - Unauthenticated guest visitors receive a secure session-based cart.
  - Seamless automatic cart merging upon customer registration or login, safely handling stock caps and deduplication while preserving session integrity across session rotation (`cycle_key`).
- **Flexible Dual Authentication**:
  - Custom `EmailOrUsernameBackend` allows users to sign in seamlessly with either their email or username.
  - Full CSRF protection and secure session cookies configured for Fetch API requests.
- **Dynamic Coupon & Promotion Engine**:
  - Percentage-based or fixed discounts with configurable minimum order thresholds, maximum discount caps, total usage limits, and per-user frequency limits.
- **Audited Review Moderation**:
  - Customer review system with verified-purchase eligibility verification directly queried from order records.
  - Duplicate review prevention per customer/product.
- **Business Operations Dashboard**:
  - Real-time revenue calculations strictly derived from completed/confirmed orders (never counting cancelled or unpaid orders).
  - Low-stock inventory monitoring and one-click CSV business sales report exports.

### 2. Frontend Design System (Bootstrap 5 & Vanilla ES6 Fetch)
- **International Minimalist Aesthetic**:
  - Deep navy typography (`#0f172a`), refined blue accents (`#2563eb`), crisp white surfaces, and subtle light-gray borders (`#e2e8f0`).
  - Restrained elevation shadows, generous whitespace, and typography using *Plus Jakarta Sans* and *Inter*.
- **Comprehensive Page Suites**:
  - **Homepage**: Configurable announcement bar, hero banner, featured categories, handpicked featured products, fresh arrivals, best sellers, promotional voucher banner, authentic reviews, and newsletter subscription.
  - **Shop Catalog**: Multi-attribute filtering (category, price range, stock availability), real-time search, sorting (price asc/desc, rating, bestseller, newest), URL query parameter syncing for bookmarking, and pagination.
  - **Product Detail**: Multi-angle image gallery with thumbnail switcher, stock level warnings, quantity selector, customer review ratings, review submission form, and related collection products.
  - **Shopping Cart**: Real-time quantity updates, free shipping progress bar ($100 threshold), promo coupon application, and backend-validated totals.
  - **Multi-Step Checkout**: Customer information, saved addresses selection, configurable shipping methods, test payment sandbox (Cash on Delivery & Stripe test mode), order review, and instant confirmation.
  - **Customer Portal**: Personal profile management, saved address book CRUD, password change, order history tracking with cancellation support, and persistent wishlist.
  - **Staff Operations Dashboard**: Real-time sales metrics, inventory restock alerts, order status transitions with audit notes, and CSV data export.

---

## 📁 Project Directory Structure

```
shopsphere/
├── backend/
│   ├── config/                 # Core settings, WSGI, ASGI, and URL routing
│   │   ├── __init__.py
│   │   ├── asgi.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── views.py
│   │   └── wsgi.py
│   ├── apps/
│   │   ├── accounts/           # User authentication, profile & address management
│   │   ├── products/           # Categories, products, gallery, and seed commands
│   │   ├── cart/               # Guest and authenticated cart operations
│   │   ├── orders/             # Checkout, order items, status tracking, & metrics
│   │   ├── payments/           # Stripe test mode & COD payment verification
│   │   ├── reviews/            # Verified customer ratings and reviews
│   │   ├── promotions/         # Coupons, newsletter, & announcement banners
│   │   └── wishlist/           # Customer saved item wishlist
│   ├── tests/                  # 37 Automated unit and integration tests
│   ├── media/                  # Uploaded and generated product media
│   ├── static/                 # Static assets for production collectstatic
│   ├── manage.py
│   ├── requirements.txt
│   ├── .env.example
│   └── .env
├── frontend/
│   ├── index.html              # Homepage
│   ├── assets/
│   │   ├── css/style.css       # ShopSphere design system stylesheet
│   │   └── js/
│   │       ├── api.js          # Centralized Fetch REST client
│   │       └── main.js         # Global toast, auth, cart, and search state
│   └── pages/
│       ├── shop.html           # Product catalog with filters & pagination
│       ├── product-detail.html # Gallery, review form, & related items
│       ├── cart.html           # Shopping cart & coupon discounts
│       ├── checkout.html       # 4-step secure checkout & confirmation
│       ├── login.html          # User login
│       ├── register.html       # User registration
│       ├── account.html        # Customer profile & address management
│       ├── orders.html         # Order history & status cancellation
│       ├── wishlist.html       # Customer wishlist
│       ├── admin.html          # Staff business operations dashboard
│       ├── about.html          # Brand story & technical architecture
│       └── contact.html        # Customer care inquiry & FAQs
├── README.md
└── .gitignore
```

---

## 🚀 Quickstart Guide (Local Development)

### 1. Prerequisites
- Python 3.10+ (tested with Python 3.12)
- Git

### 2. Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd shopsphere/backend
   ```
2. Create and activate a Python virtual environment:
   ```bash
   # Windows
   py -m venv venv
   .\venv\Scripts\activate

   # macOS / Linux
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install package dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure environment variables:
   ```bash
   # Copy example configuration
   cp .env.example .env
   ```
5. Apply database migrations:
   ```bash
   python manage.py migrate
   ```
6. Seed database with realistic sample categories, products, images, and coupons:
   ```bash
   python manage.py seed_sample_data
   ```
   *This command automatically populates 18 products across 6 categories with clean Pillow-generated images, active coupons (`WELCOME10`, `SAVE25`, `FREESHIP`), and a default superuser:*
   - **Admin Email:** `admin@shopsphere.com`
   - **Admin Password:** `adminpassword123`

7. Start the Django development server:
   ```bash
   python manage.py runserver 8000
   ```

### 3. Accessing the Application
- **Main Website (Full-Stack Single Port Preview):** Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.
- **REST API v1 Root:** [http://127.0.0.1:8000/api/v1/](http://127.0.0.1:8000/api/v1/)
- **Django Admin:** [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
- **Business Operations Dashboard:** [http://127.0.0.1:8000/pages/admin.html](http://127.0.0.1:8000/pages/admin.html)

---

## 🧪 Running Automated Tests

ShopSphere includes a comprehensive suite of 37 automated tests verifying critical application workflows:

```bash
cd shopsphere/backend
python manage.py test tests
```

### Test Coverage Summary:
- `test_accounts.py`: User registration, password matching, email/username login, logout, profile edits, address book isolation.
- `test_products.py`: Public vs inactive product visibility, category filtering, min/max price range, search by keyword, sorting (price asc/desc), staff creation permissions.
- `test_cart.py`: Anonymous session cart, stock validation during add-to-cart, quantity updates, item deletion, clearing cart, session-to-authenticated cart merging.
- `test_orders.py`: Multi-step checkout, atomic stock deduction, snapshot preservation in OrderItem, order ownership authorization, order cancellation and inventory restoration, admin net revenue calculations.
- `test_promotions.py`: Coupon validity, percentage vs fixed discounts, minimum order threshold validation, max discount capping, newsletter email format validation, announcement retrieval.
- `test_reviews.py`: 1–5 star rating validation, verified purchase badge derivation from order records, duplicate review prevention.
- `test_wishlist.py`: Unauthenticated access restrictions, wishlist item addition, duplicate prevention, move-to-cart workflow.

---

## 🛡️ Production Deployment Guide

### PostgreSQL Setup
1. Provision a PostgreSQL instance:
   ```sql
   CREATE DATABASE shopsphere_db;
   CREATE USER shopsphere_user WITH PASSWORD 'your_strong_password';
   ALTER ROLE shopsphere_user SET client_encoding TO 'utf8';
   ALTER ROLE shopsphere_user SET default_transaction_isolation TO 'read committed';
   ALTER ROLE shopsphere_user SET timezone TO 'UTC';
   GRANT ALL PRIVILEGES ON DATABASE shopsphere_db TO shopsphere_user;
   ```
2. In `backend/.env`, set:
   ```env
   DB_ENGINE=postgresql
   DB_NAME=shopsphere_db
   DB_USER=shopsphere_user
   DB_PASSWORD=your_strong_password
   DB_HOST=your-postgres-host
   DB_PORT=5432
   ```

### Production Security Settings
In production, update `backend/.env`:
```env
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=generate-a-strong-random-50-character-string
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### Static & Media Assets
Run the collection command:
```bash
python manage.py collectstatic --noinput
```
Configure your web server (Nginx / Caddy / Cloudflare / AWS S3) to serve:
- Static assets from `backend/staticfiles/`
- Media uploads from `backend/media/` or cloud storage bucket.

---

## 📄 License
MIT License.
