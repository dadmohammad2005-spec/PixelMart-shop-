# Shall Shop — Professional Full-Stack E-Commerce Platform
> **Discover More. Shop Better.**

Shall Shop is an enterprise-grade, modern, full-stack e-commerce web platform engineered for portfolio demonstration and international client presentations. It features a robust Python/Django backend with Django REST Framework, atomic transactions, inventory concurrency locking, secure session-based authentication, and a responsive frontend with a minimalist international design system combining clean white surfaces, deep obsidian black, and elegant royal purple accents.

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
  - Percentage-based or fixed discounts (`SHALL10`, `SHALL25`, `FREESHIP`) with configurable minimum order thresholds, maximum discount caps, total usage limits, and per-user frequency limits.
- **Audited Review Moderation**:
  - Customer review system with verified-purchase eligibility verification directly queried from order records.
  - Duplicate review prevention per customer/product.
- **Business Operations Dashboard**:
  - Real-time revenue calculations strictly derived from completed/confirmed orders (never counting cancelled or unpaid orders).
  - Low-stock inventory monitoring and one-click CSV business sales report exports.

### 2. Frontend Design System (Bootstrap 5 & Vanilla ES6 Fetch)
- **International Minimalist Aesthetic**:
  - Deep obsidian black typography (`#0b0f19`), elegant royal purple accents (`#7c3aed`, `#6d28d9`, `#8b5cf6`), crisp white surfaces, and subtle borders (`#e2e8f0`).
  - Restrained elevation shadows, hover micro-interactions, and typography using *Plus Jakarta Sans* and *Inter*.
- **Comprehensive Page Suites**:
  - **Homepage**: Announcement bar, hero banner with "Discover More. Shop Better.", Shop by Category (7 official verticals), Trending Products, Best Sellers, New Arrivals, Special Offers with copyable voucher codes, Recommended Products, authentic verified customer reviews, and newsletter subscription.
  - **Shop Catalog**: Multi-attribute filtering (category, price range, stock availability), real-time search, sorting (price asc/desc, rating, bestseller, newest), URL query parameter syncing for bookmarking, and pagination.
  - **Product Detail**: Multi-angle image gallery with thumbnail switcher, stock level warnings, quantity selector, customer review ratings, review submission form, and related collection products.
  - **Shopping Cart**: Real-time quantity updates, free shipping progress bar ($100 threshold), promo coupon application, and backend-validated totals.
  - **Multi-Step Checkout**: Customer information, saved addresses selection, configurable shipping methods, test payment sandbox (Cash on Delivery & Stripe test mode), order review, and instant confirmation.
  - **Customer Portal**: Personal profile management, saved address book CRUD, password change, order history tracking with cancellation support, and persistent wishlist.
  - **Staff Operations Hub**: Product CRUD with image URL/upload, category management, customer viewing, order status transitions with audit notes, coupon management, and CSV data export.

---

## 🛍️ Flagship Catalog & Departments

Shall Shop features 7 primary product verticals populated with high-resolution photography and realistic specifications:
1. **Electronics**: Apple iPhone 17 Pro, Samsung Galaxy S26 Ultra, MacBook Air 15" M3, Sony WH-1000XM5 Headphones, Wireless Mechanical Keyboard & Mouse
2. **Fashion & Clothing**: Men's Classic Oxford Shirt, Women's Cashmere Oversized Sweater
3. **Shoes & Sneakers**: Nike Air Max 270 Sneakers, Adidas Ultraboost Light Running Shoes
4. **Watches**: Premium Men's Chronograph Wristwatch, Smart Fitness Watch Ultra
5. **Bags & Accessories**: Women's Italian Leather Handbag, Premium Polarized Aviator Sunglasses
6. **Home & Living**: Minimalist Modern Desk Lamp, Artisanal Ceramic Coffee Pour-Over Set, French Pure Linen Throw Blanket
7. **Beauty & Personal Care**: Botanical Hydrating Facial Serum

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
│   │   ├── accounts/           # User authentication, profile, address & admin customer API
│   │   ├── products/           # Categories, products, image URLs, gallery & seed command
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
│   ├── index.html              # Shall Shop Homepage
│   ├── assets/
│   │   ├── css/style.css       # Shall Shop design system stylesheet (Purple & Obsidian)
│   │   └── js/
│   │       ├── api.js          # Centralized Fetch REST client
│   │       └── main.js         # Global toast, auth, cart, and search state
│   └── pages/
│       ├── shop.html           # Product catalog with filters & pagination
│       ├── product-detail.html # Gallery, review form, & related items
│       ├── cart.html           # Shopping cart & coupon discounts (SHALL10, SHALL25)
│       ├── checkout.html       # 4-step secure checkout & confirmation
│       ├── login.html          # User login
│       ├── register.html       # User registration
│       ├── account.html        # Customer profile & address management
│       ├── orders.html         # Order history & status cancellation
│       ├── wishlist.html       # Customer wishlist
│       ├── admin.html          # Staff operations hub (Product CRUD, categories, orders)
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
6. Seed database with Shall Shop flagship products, categories, reviews, and coupons:
   ```bash
   python manage.py seed_sample_data
   ```
   *This command populates all 17 flagship products across 7 categories with high-resolution photography, authentic reviews, active coupons (`SHALL10`, `SHALL25`, `FREESHIP`), and a default superuser:*
   - **Admin Email:** `admin@shopsphere.com` (or username `admin`)
   - **Admin Password:** `adminpassword123`

7. Start the Django development server:
   ```bash
   python manage.py runserver 8000
   ```

### 3. Accessing the Application
- **Main Website (Full-Stack Single Port Preview):** Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.
- **REST API v1 Root:** [http://127.0.0.1:8000/api/v1/](http://127.0.0.1:8000/api/v1/)
- **Django Admin:** [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
- **Operations Hub:** [http://127.0.0.1:8000/pages/admin.html](http://127.0.0.1:8000/pages/admin.html)

---

## 🧪 Running Automated Tests

Shall Shop includes a comprehensive suite of 37 automated tests verifying critical application workflows:

```bash
cd shopsphere/backend
python manage.py test tests
```

---

## 📄 License
This project is licensed under the MIT License — suitable for professional software engineering portfolios, commercial extensions, and client demonstrations.
