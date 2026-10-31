# PixelMart — Laptops, Mobile Phones & Tech Platform

**PixelMart** is a production-ready, full-stack e-commerce web platform specializing in verified laptops and mobile phones, featuring authentic Pakistani Rupee (PKR) pricing, responsive multi-image cards, real-time live search & brand filtering, dark theme toggle, slide-out cart drawer, and printable invoice/bill generation.

Branded for **PixelMart — Quetta, Balochistan** (Contact Hotline: `00816-23-736822`).

---

## 🌟 Key Features & Highlights

### 1. Catalog & Pakistani Rupee (PKR) Pricing
- **Laptops**: Popular brands including HP (e.g. HP EliteBook Core i7 5th Gen @ PKR 70,000, HP Envy x360, HP Omen 16), Dell (XPS 13, Latitude, G15), Lenovo ThinkPad (X1 Carbon, T14, Legion 5 Pro), and Sony.
- **Mobile Phones**: Major flagships and local market favorites including Apple iPhone (13, 14 Pro, 15 Pro Max, 16 Pro Max), Samsung Galaxy (S23, S24 Ultra, Z Fold 6, A55), Motorola Edge 50 Ultra, Nokia G42 5G, Vivo V30 Pro, and Oppo Reno 12 Pro.
- **Local Warranty & Specs**: Local specifications (RAM, SSD/Storage, Processor/Chipset, Battery health) and 1-Year Local Warranty badges.

### 2. Frontend UI / UX & Interactivity
- **Theme Engine**: Seamless toggle between **Light Mode** and **Dark Mode** with zero-flicker `<head>` scripts, smooth transitions, and persistent storage across sessions.
- **Real-Time Live Search & Brand Filters**: Instant filtering by laptop and mobile brands (Apple, HP, Dell, Lenovo, Samsung, Motorola, etc.) with real-time keystroke search.
- **Multi-Image Interactive Product Cards**: Hover arrow navigation to flip through multiple product angles directly from the catalog grid with counter badges.
- **Slide-Out Cart Drawer**: Fast side-drawer cart preview with animated counter badges, inline quantity steppers, and quick checkout.
- **Official Printable Bill / Invoice**: Formatted receipt with official store header, invoice number, itemized table in PKR, tax breakdown, barcode, and automated browser print dialog (`window.print()`).

### 3. Backend Architecture (Django 5.1 & Django REST Framework)
- **Modular Domain Apps**:
  - `accounts`: User authentication, profile management, shipping addresses.
  - `products`: Product catalog, brand categorization, specifications, multi-image gallery, and seed commands.
  - `cart`: Session-based guest carts with automatic merging upon authentication.
  - `orders`: Concurrency-safe atomic checkout (`select_for_update()`) preventing overselling, historical price snapshots, order tracking, and invoice generation.
  - `payments`: Cash on Delivery & Stripe test payment processing.
  - `reviews`: Verified purchase ratings and feedback.
  - `promotions`: Announcement bar, coupon validation engine, and newsletter subscriptions.
  - `wishlist`: Customer favorite product saves.
- **Static & Media Files**: WhiteNoise for high-efficiency static asset serving in production; media file serving for product imagery.
- **Automated Test Suite**: 37 comprehensive unit & integration tests covering authentication, cart, checkout concurrency, promotions, and reviews.

---

## 📁 Repository Structure

```
├── build.sh                  # Automated Render build script
├── Procfile                  # Production process command for Gunicorn
├── render.yaml               # Render Blueprint deployment definition
├── .gitignore
├── README.md
└── shopsphere/
    ├── backend/
    │   ├── manage.py
    │   ├── requirements.txt
    │   ├── build.sh
    │   ├── Procfile
    │   ├── config/           # Django settings, WSGI, ASGI, and URL routing
    │   ├── apps/             # Modular Django domain apps
    │   ├── media/            # Product photography & assets
    │   ├── static/           # Static files
    │   └── tests/            # Automated test suite (37 tests)
    └── frontend/
        ├── index.html        # Storefront homepage
        ├── assets/           # CSS, JS, and branding images
        └── pages/            # Shop catalog, cart, checkout, orders, admin, etc.
```

---

## 🚀 How to Run Locally

### 1. Clone the repository
```bash
git clone https://github.com/dadmohammad2005-spec/PixelMart-shop-.git
cd PixelMart-shop-
```

### 2. Set up Python virtual environment
```bash
cd shopsphere/backend
python -m venv venv

# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run database migrations & seed sample data
```bash
python manage.py migrate
python manage.py seed_sample_data
```

### 5. Run the development server
```bash
python manage.py runserver 8000
```
Open **http://127.0.0.1:8000/** in your browser.

---

## 🌐 How to Deploy on Render

Deploying PixelMart on [Render](https://render.com/) is straightforward.

### Method A: Automated Deployment via `render.yaml` (Recommended)

1. Sign in to your **[Render Dashboard](https://dashboard.render.com/)**.
2. Click **New +** in the top navigation and select **Blueprint**.
3. Connect your GitHub account and select the **`PixelMart-shop-`** repository.
4. Render will automatically detect [`render.yaml`](render.yaml) and configure:
   - **Service Name**: `pixelmart-store`
   - **Environment**: Python
   - **Build Command**: `./build.sh`
   - **Start Command**: `cd shopsphere/backend && gunicorn config.wsgi:application`
5. Click **Apply**. Render will run `build.sh` (install dependencies, run migrations, seed products, collect static files) and launch your live site.

---

### Method B: Manual Web Service Setup

If you prefer setting up the web service manually:

1. In Render Dashboard, click **New +** &rarr; **Web Service**.
2. Connect your GitHub repository **`PixelMart-shop-`**.
3. Fill in the following settings:
   - **Name**: `pixelmart-store` (or your preferred name)
   - **Language**: `Python 3`
   - **Branch**: `main`
   - **Root Directory**: *(Leave empty, or set to `.`)*
   - **Build Command**:
     ```bash
     ./build.sh
     ```
   - **Start Command**:
     ```bash
     cd shopsphere/backend && gunicorn config.wsgi:application
     ```
   *(Note: If you choose to set Root Directory to `shopsphere/backend`, use `./build.sh` as Build Command and `gunicorn config.wsgi:application` as Start Command).*

4. **Environment Variables** (under *Advanced*):
   | Key | Value | Notes |
   |---|---|---|
   | `PYTHON_VERSION` | `3.11.9` | Ensures modern Python runtime |
   | `DJANGO_DEBUG` | `False` | Production mode |
   | `DJANGO_SECRET_KEY` | *(Click "Generate" on Render)* | Cryptographic key |
   | `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1,.onrender.com` | Allows your Render domain |
   | `DATABASE_URL` | *(Optional)* | Connect Render PostgreSQL database string if using Postgres |

5. Click **Create Web Service**. Your app will build and go live at `https://<your-service-name>.onrender.com`!

---

## 🧪 Running Automated Tests

Run the full Django test suite (37 tests):
```bash
python manage.py test tests
```

---

## 📞 Store Contact Information
- **Brand**: PixelMart — Laptops, Mobile Phones & Tech Gadgets
- **Location**: Quetta, Balochistan, Pakistan
- **Hotline**: `00816-23-736822`
- **Email**: support@pixelmart.pk
