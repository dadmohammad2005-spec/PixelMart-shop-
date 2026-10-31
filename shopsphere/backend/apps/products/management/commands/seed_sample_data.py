import os
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from django.utils import timezone
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

from apps.products.models import Category, Product, ProductImage
from apps.promotions.models import Coupon, Announcement
from apps.reviews.models import Review

User = get_user_model()


class Command(BaseCommand):
    help = 'Populates PixelMart (Quetta, Balochistan) with authentic laptops, mobile phones, PKR pricing, and reviews.'

    def handle(self, *args, **options):
        self.stdout.write("Initializing PixelMart (Quetta, Balochistan) catalog...")

        # 1. Admin Superuser
        admin_user = User.objects.filter(username='admin').first()
        if not admin_user:
            admin_user = User.objects.create(
                username='admin',
                email='admin@pixelmart.pk',
                first_name='PixelMart',
                last_name='Manager',
                is_staff=True,
                is_superuser=True
            )
            admin_user.set_password('adminpassword123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS("Created Admin: admin@pixelmart.pk / adminpassword123"))
        else:
            admin_user.email = 'admin@pixelmart.pk'
            admin_user.first_name = 'PixelMart'
            admin_user.last_name = 'Manager'
            admin_user.set_password('adminpassword123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS("Updated Admin: admin@pixelmart.pk / adminpassword123"))

        # 2. Customers for reviews
        customers_data = [
            {'username': 'tariq_quetta', 'email': 'tariq.kakar@gmail.com', 'first': 'Tariq', 'last': 'Kakar'},
            {'username': 'bilal_tech', 'email': 'bilal.baloch@yahoo.com', 'first': 'Bilal', 'last': 'Baloch'},
            {'username': 'farhan_dev', 'email': 'farhan.ali@gmail.com', 'first': 'Farhan', 'last': 'Ali'},
            {'username': 'zainab_pk', 'email': 'zainab.khan@hotmail.com', 'first': 'Zainab', 'last': 'Khan'},
            {'username': 'asad_uet', 'email': 'asad.engineer@gmail.com', 'first': 'Asadullah', 'last': 'Mengal'}
        ]
        customer_objs = []
        for c in customers_data:
            u = User.objects.filter(email=c['email']).first() or User.objects.filter(username=c['username']).first()
            if not u:
                u = User.objects.create(
                    email=c['email'],
                    username=c['username'],
                    first_name=c['first'],
                    last_name=c['last']
                )
            else:
                u.email = c['email']
                u.first_name = c['first']
                u.last_name = c['last']
            u.set_password('customerpass123')
            u.save()
            customer_objs.append(u)

        # 3. Clean and Populate Categories
        categories_data = [
            {
                'name': 'Laptops',
                'slug': 'laptops',
                'description': 'High-performance business, workstation, and gaming laptops from HP, Dell, Lenovo, Apple, Sony, and Asus with certified local warranty.',
                'is_featured': True
            },
            {
                'name': 'Mobile Phones',
                'slug': 'mobile-phones',
                'description': 'Official PTA approved smartphones from Apple iPhone, Samsung Galaxy, Motorola, Nokia, Vivo, and Oppo with warranty.',
                'is_featured': True
            },
            {
                'name': 'Gadgets & Accessories',
                'slug': 'gadgets-accessories',
                'description': 'Active noise cancelling headphones, smartwatches, GaN fast chargers, laptop backpacks, and power banks.',
                'is_featured': True
            }
        ]

        cat_map = {}
        for c in categories_data:
            cat_obj, _ = Category.objects.update_or_create(
                slug=c['slug'],
                defaults={
                    'name': c['name'],
                    'description': c['description'],
                    'is_featured': c['is_featured'],
                    'is_active': True
                }
            )
            cat_map[c['slug']] = cat_obj

        # 4. Comprehensive Product Catalog in PKR
        products_data = [
            # ----------------------------------------------------
            # LAPTOPS
            # ----------------------------------------------------
            {
                'category_slug': 'laptops',
                'brand': 'HP',
                'name': 'HP EliteBook 840 G2 Core i7 5th Gen',
                'sku': 'PM-LAP-HP-840G2',
                'specs': 'Intel Core i7 5th Gen • 8GB RAM • 256GB SSD • 14" HD Anti-Glare',
                'short_description': 'Durable magnesium-aluminum business ultrabook featuring Intel Core i7 5th Generation processor, 8GB DDR3L RAM, and 256GB SSD.',
                'description': 'The HP EliteBook 840 G2 is a dependable corporate workhorse built to withstand rigorous daily use. Equipped with a powerful Intel Core i7 5th Gen CPU, fast 256GB solid-state drive, backlit spill-resistant keyboard, fingerprint reader, and multiple USB 3.0 ports. Ideal for software development, office productivity, and university students in Quetta looking for exceptional value.',
                'price': Decimal('78000.00'),
                'sale_price': Decimal('70000.00'),
                'stock': 18,
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1544731612-de292439cc4b?w=800&auto=format&fit=crop&q=80',
                'gallery_images': [
                    'https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=800&auto=format&fit=crop&q=80',
                    'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=800&auto=format&fit=crop&q=80'
                ]
            },
            {
                'category_slug': 'laptops',
                'brand': 'HP',
                'name': 'HP EliteBook 840 G5 Core i5 8th Gen',
                'sku': 'PM-LAP-HP-840G5',
                'specs': 'Intel Core i5 8th Gen Quad-Core • 16GB DDR4 • 512GB NVMe SSD • 14" FHD IPS',
                'short_description': 'Sleek silver aluminum ultrabook with Bang & Olufsen premium audio, 8th Gen Quad-Core processor, and 512GB high-speed NVMe.',
                'description': 'Engineered for modern mobile professionals. The HP EliteBook 840 G5 features an ultra-slim aluminum precision-cut chassis, 14-inch Full HD anti-glare display, ambient light sensor, Privacy Camera shutter, and USB Type-C Thunderbolt 3 connectivity. 16GB DDR4 RAM guarantees effortless multitasking.',
                'price': Decimal('95000.00'),
                'sale_price': Decimal('89999.00'),
                'stock': 14,
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=800&auto=format&fit=crop&q=80',
                'gallery_images': [
                    'https://images.unsplash.com/photo-1544731612-de292439cc4b?w=800&auto=format&fit=crop&q=80',
                    'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=800&auto=format&fit=crop&q=80'
                ]
            },
            {
                'category_slug': 'laptops',
                'brand': 'Dell',
                'name': 'Dell Latitude 7490 Core i7 8th Gen',
                'sku': 'PM-LAP-DEL-7490',
                'specs': 'Intel Core i7 8th Gen • 16GB DDR4 • 512GB SSD • 14" FHD Carbon Fiber',
                'short_description': 'Enterprise flagship laptop featuring carbon-fiber reinforced structure, Core i7 8th Gen, and all-day battery efficiency.',
                'description': 'Dell Latitude 7490 delivers top-tier reliability for demanding executives and field engineers. Built with premium materials including woven carbon fiber, magnesium alloy chassis, crisp 1080p anti-glare screen, trackstick navigation, and comprehensive ports (HDMI, USB-C, LAN, SD). Tested and certified by PixelMart technicians.',
                'price': Decimal('110000.00'),
                'sale_price': Decimal('104500.00'),
                'stock': 12,
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=800&auto=format&fit=crop&q=80',
                'gallery_images': [
                    'https://images.unsplash.com/photo-1541807084-5c52b6b3adef?w=800&auto=format&fit=crop&q=80',
                    'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=800&auto=format&fit=crop&q=80'
                ]
            },
            {
                'category_slug': 'laptops',
                'brand': 'Dell',
                'name': 'Dell XPS 15 9500 4K UHD Touch',
                'sku': 'PM-LAP-DEL-XPS15',
                'specs': 'Intel Core i7 10th Gen • 16GB RAM • 512GB NVMe • GTX 1650 Ti 4GB • 4K InfinityEdge',
                'short_description': 'Architectural masterpiece with 4K touch display, CNC aluminum chassis, carbon fiber palm rest, and dedicated Nvidia GPU.',
                'description': 'The Dell XPS 15 9500 sets the gold standard for creative creators, video editors, and power users. Boasting a breathtaking 16:10 4K UHD+ touch screen with 100% Adobe RGB coverage, Quad-speaker sound with Waves Nx 3D audio, and dedicated Nvidia GeForce GTX 1650 Ti graphics.',
                'price': Decimal('240000.00'),
                'sale_price': Decimal('228000.00'),
                'stock': 7,
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1541807084-5c52b6b3adef?w=800&auto=format&fit=crop&q=80',
                'gallery_images': [
                    'https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=800&auto=format&fit=crop&q=80',
                    'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=800&auto=format&fit=crop&q=80'
                ]
            },
            {
                'category_slug': 'laptops',
                'brand': 'Lenovo',
                'name': 'Lenovo ThinkPad T480 Dual-Battery Edition',
                'sku': 'PM-LAP-LEN-T480',
                'specs': 'Intel Core i5 8th Gen Quad-Core • 16GB RAM • 256GB SSD • Power Bridge Dual Battery',
                'short_description': 'Legendary ThinkPad ergonomics with military-spec durability, spill-proof keyboard, and swappable dual batteries.',
                'description': 'Renowned worldwide by programmers and sysadmins. The ThinkPad T480 features Lenovo\'s class-leading tactile keyboard, TrackPoint navigation nub, dual hot-swappable batteries enabling over 14 hours of run time, and rugged MIL-STD-810G certification resistant to dust, shocks, and extreme temperatures.',
                'price': Decimal('85000.00'),
                'sale_price': Decimal('79999.00'),
                'stock': 16,
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=800&auto=format&fit=crop&q=80',
                'gallery_images': [
                    'https://images.unsplash.com/photo-1544731612-de292439cc4b?w=800&auto=format&fit=crop&q=80',
                    'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=800&auto=format&fit=crop&q=80'
                ]
            },
            {
                'category_slug': 'laptops',
                'brand': 'Lenovo',
                'name': 'Lenovo ThinkPad X1 Carbon Gen 9',
                'sku': 'PM-LAP-LEN-X1C9',
                'specs': 'Intel Core i7 11th Gen Evo • 16GB LPDDR4x • 512GB PCIe Gen4 • 1.13kg Carbon Fiber',
                'short_description': 'Ultra-lightweight executive flagship with 16:10 display, Dolby Atmos soundbar, and 16-hour endurance.',
                'description': 'The pinnacle of business ultrabooks. Built with aerospace-grade carbon fiber and magnesium alloy, weighing a featherlight 1.13 kg. Features a 14-inch 16:10 WUXGA anti-glare display, dual-fan cooling system, quad 360-degree far-field microphones, and Intel Iris Xe graphics.',
                'price': Decimal('215000.00'),
                'sale_price': None,
                'stock': 8,
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=800&auto=format&fit=crop&q=80',
                'gallery_images': [
                    'https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=800&auto=format&fit=crop&q=80'
                ]
            },
            {
                'category_slug': 'laptops',
                'brand': 'Sony',
                'name': 'Sony VAIO SX14 4K Ultra-Light',
                'sku': 'PM-LAP-SNY-SX14',
                'specs': 'Intel Core i7 10th Gen • 16GB RAM • 512GB PCIe SSD • 14" 4K UHD • 1.05kg',
                'short_description': 'Japanese engineering excellence with gorgeous 4K display, UD carbon chassis, and comprehensive full-sized ports.',
                'description': 'Crafted in Japan with uncompromising attention to detail. The Sony VAIO SX14 weighs only 1.05 kg while packing a breathtaking 4K Ultra HD IPS display, tilted hinge design for ergonomic typing, full-sized HDMI, VGA, LAN, and USB-C ports without needing cumbersome dongles.',
                'price': Decimal('165000.00'),
                'sale_price': Decimal('155000.00'),
                'stock': 6,
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1544731612-de292439cc4b?w=800&auto=format&fit=crop&q=80',
                'gallery_images': [
                    'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=800&auto=format&fit=crop&q=80'
                ]
            },
            {
                'category_slug': 'laptops',
                'brand': 'Apple',
                'name': 'Apple MacBook Air M1 (Retina 13.3")',
                'sku': 'PM-LAP-APP-AIRM1',
                'specs': 'Apple M1 Chip 8-Core • 8GB Unified Memory • 256GB SSD • 18h Battery',
                'short_description': 'Revolutionary fanless Apple Silicon performance with whisper-quiet operation and all-day battery life.',
                'description': 'The most popular laptop in the world. Powered by the groundbreaking Apple M1 chip with 8-core CPU and 7-core GPU. Delivers up to 3.5x faster performance while operating completely silently with zero fan noise. Features True Tone Retina display, Magic Keyboard with Touch ID, and machined aluminum body.',
                'price': Decimal('210000.00'),
                'sale_price': Decimal('199000.00'),
                'stock': 15,
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=800&auto=format&fit=crop&q=80',
                'gallery_images': [
                    'https://images.unsplash.com/photo-1611186871348-b1ce696e52c9?w=800&auto=format&fit=crop&q=80',
                    'https://images.unsplash.com/photo-1541807084-5c52b6b3adef?w=800&auto=format&fit=crop&q=80'
                ]
            },
            {
                'category_slug': 'laptops',
                'brand': 'Apple',
                'name': 'Apple MacBook Pro 14" M2 Pro',
                'sku': 'PM-LAP-APP-MBP14',
                'specs': 'Apple M2 Pro 10-Core • 16GB Unified RAM • 512GB SSD • Liquid Retina XDR 120Hz',
                'short_description': 'Professional studio powerhouse with 120Hz ProMotion XDR display, MagSafe 3, HDMI, and studio-grade mics.',
                'description': 'Designed for pro developers, 3D animators, and music producers. The MacBook Pro 14 packs the blazingly fast M2 Pro chip with 16-core GPU, 1,000,000:1 contrast ratio Liquid Retina XDR mini-LED display with 1600 nits peak brightness, 6-speaker spatial audio system, and MagSafe fast charging.',
                'price': Decimal('480000.00'),
                'sale_price': None,
                'stock': 5,
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1611186871348-b1ce696e52c9?w=800&auto=format&fit=crop&q=80',
                'gallery_images': [
                    'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=800&auto=format&fit=crop&q=80'
                ]
            },
            {
                'category_slug': 'laptops',
                'brand': 'Asus',
                'name': 'Asus ROG Strix G16 Gaming Laptop',
                'sku': 'PM-LAP-ASU-ROG16',
                'specs': 'Intel Core i7 13th Gen • 16GB DDR5 • RTX 4060 8GB • 512GB Gen4 SSD • 165Hz ROG Nebula',
                'short_description': 'Extreme AAA gaming performance with Conductonaut Extreme liquid metal cooling and Aura Sync RGB.',
                'description': 'Dominate competitive esports and modern AAA blockbusters. Powered by a 13th Gen Intel Core i7-13650HX processor paired with Nvidia GeForce RTX 4060 8GB GDDR6 with MUX Switch and Advanced Optimus. Features ROG Intelligent Cooling with 3 fans and full-surround heatsink.',
                'price': Decimal('390000.00'),
                'sale_price': Decimal('375000.00'),
                'stock': 6,
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=800&auto=format&fit=crop&q=80',
                'gallery_images': [
                    'https://images.unsplash.com/photo-1544731612-de292439cc4b?w=800&auto=format&fit=crop&q=80'
                ]
            },

            # ----------------------------------------------------
            # MOBILE PHONES
            # ----------------------------------------------------
            {
                'category_slug': 'mobile-phones',
                'brand': 'Apple',
                'name': 'Apple iPhone 15 Pro Max 256GB',
                'sku': 'PM-MOB-APP-IP15PM',
                'specs': 'A17 Pro 3nm • Grade 5 Titanium • 48MP 5x Zoom • USB-C 3.0 • Official PTA Approved',
                'short_description': 'Flagship aerospace-grade titanium design with A17 Pro chip, Action button, and 5x optical telephoto lens.',
                'description': 'The ultimate smartphone experience. Forged in titanium with a textured matte-glass back, Ceramic Shield front, and custom Action button. Powered by the industry-first 3nm A17 Pro processor supporting console-quality ray-tracing gaming. Official PTA approved with physical SIM + eSIM dual capability.',
                'price': Decimal('445000.00'),
                'sale_price': Decimal('429000.00'),
                'stock': 12,
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=800&auto=format&fit=crop&q=80',
                'gallery_images': [
                    'https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=800&auto=format&fit=crop&q=80',
                    'https://images.unsplash.com/photo-1510557880182-3d4d3cba35a5?w=800&auto=format&fit=crop&q=80',
                    'https://images.unsplash.com/photo-1565849904461-04a58ad377e0?w=800&auto=format&fit=crop&q=80'
                ]
            },
            {
                'category_slug': 'mobile-phones',
                'brand': 'Apple',
                'name': 'Apple iPhone 14 Pro 128GB',
                'sku': 'PM-MOB-APP-IP14P',
                'specs': 'A16 Bionic • Dynamic Island • 48MP Pro Camera • Always-On OLED • Official PTA Approved',
                'short_description': 'Deep Purple flagship with innovative Dynamic Island, 48MP primary sensor with sensor-shift OIS, and crash detection.',
                'description': 'A magical way to interact with iPhone. Features the Dynamic Island bubbling up music, sports scores, and calls. Powered by the A16 Bionic chip, pro-level cinematic mode in 4K HDR at 24 fps, Action mode for smooth handheld video, and all-day battery life.',
                'price': Decimal('330000.00'),
                'sale_price': None,
                'stock': 9,
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=800&auto=format&fit=crop&q=80',
                'gallery_images': [
                    'https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=800&auto=format&fit=crop&q=80'
                ]
            },
            {
                'category_slug': 'mobile-phones',
                'brand': 'Apple',
                'name': 'Apple iPhone 13 128GB (PTA Approved)',
                'sku': 'PM-MOB-APP-IP13',
                'specs': 'A15 Bionic • Dual 12MP Camera • Super Retina XDR OLED • Ceramic Shield',
                'short_description': 'Exceptional balance of speed, battery life, and cinematic camera capabilities in Midnight Blue.',
                'description': 'The best value iPhone in the market today. Boasts diagonal dual camera system with sensor-shift optical image stabilization, ultra-bright Super Retina XDR display, lightning-fast A15 Bionic processor, and IP68 water resistance. Fully PTA registered with lifetime tax cleared.',
                'price': Decimal('225000.00'),
                'sale_price': Decimal('215000.00'),
                'stock': 16,
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1510557880182-3d4d3cba35a5?w=800&auto=format&fit=crop&q=80',
                'gallery_images': [
                    'https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=800&auto=format&fit=crop&q=80'
                ]
            },
            {
                'category_slug': 'mobile-phones',
                'brand': 'Apple',
                'name': 'Apple iPhone 11 128GB (Factory Unlocked)',
                'sku': 'PM-MOB-APP-IP11',
                'specs': 'A13 Bionic • 6.1" Liquid Retina • Dual 12MP Ultra-Wide • PTA Approved',
                'short_description': 'Reliable everyday iPhone featuring Night mode photography, 4K selfie video, and proven longevity.',
                'description': 'An affordable entry point into the Apple ecosystem. Features a 6.1-inch Liquid Retina HD display, dual 12MP ultra-wide cameras with Night mode, Face ID authentication, and all-day battery life. Guaranteed authentic with original box and accessories.',
                'price': Decimal('115000.00'),
                'sale_price': None,
                'stock': 20,
                'is_featured': False,
                'image_url': 'https://images.unsplash.com/photo-1565849904461-04a58ad377e0?w=800&auto=format&fit=crop&q=80',
                'gallery_images': [
                    'https://images.unsplash.com/photo-1510557880182-3d4d3cba35a5?w=800&auto=format&fit=crop&q=80'
                ]
            },
            {
                'category_slug': 'mobile-phones',
                'brand': 'Samsung',
                'name': 'Samsung Galaxy S24 Ultra 5G 512GB',
                'sku': 'PM-MOB-SAM-S24U',
                'specs': 'Snapdragon 8 Gen 3 • Titanium Frame • Built-in S-Pen • 200MP Quad Tele • Official PTA',
                'short_description': 'Titanium powerhouse with Galaxy AI live translation, Corning Gorilla Armor anti-reflective glass, and 100x Space Zoom.',
                'description': 'The ultimate Android smartphone. Equipped with Galaxy AI features including Circle to Search, Live Call Translation, and Note Assist. Features a flat 6.8-inch QHD+ 120Hz Dynamic AMOLED 2X display with 2600 nits brightness, embedded S-Pen stylus, and titanium armor frame.',
                'price': Decimal('410000.00'),
                'sale_price': Decimal('395000.00'),
                'stock': 10,
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=800&auto=format&fit=crop&q=80',
                'gallery_images': [
                    'https://images.unsplash.com/photo-1580910051074-3eb694886505?w=800&auto=format&fit=crop&q=80',
                    'https://images.unsplash.com/photo-1585060544812-6b45742d762f?w=800&auto=format&fit=crop&q=80'
                ]
            },
            {
                'category_slug': 'mobile-phones',
                'brand': 'Samsung',
                'name': 'Samsung Galaxy S23 FE 5G 256GB',
                'sku': 'PM-MOB-SAM-S23FE',
                'specs': '8GB RAM • 256GB Storage • 50MP OIS Camera • 120Hz Dynamic AMOLED • PTA Approved',
                'short_description': 'Fan Edition flagship with pro-grade cameras, vapor chamber cooling, and 4 years of OS upgrades.',
                'description': 'Brings premium flagship capabilities to an accessible price tag. Features a vivid 6.4-inch FHD+ 120Hz display with Vision Booster, 50MP triple-camera system with nightography, IP68 water and dust resistance, and 4500mAh battery with 25W fast charging.',
                'price': Decimal('165000.00'),
                'sale_price': None,
                'stock': 14,
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1580910051074-3eb694886505?w=800&auto=format&fit=crop&q=80',
                'gallery_images': [
                    'https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=800&auto=format&fit=crop&q=80'
                ]
            },
            {
                'category_slug': 'mobile-phones',
                'brand': 'Samsung',
                'name': 'Samsung Galaxy A55 5G 8GB/256GB',
                'sku': 'PM-MOB-SAM-A55',
                'specs': '8GB RAM • 256GB Storage • Metal Frame • Gorilla Glass Victus+ • Official Warranty',
                'short_description': 'Metal-frame mid-ranger with Knox Vault security, 50MP OIS camera, and 5000mAh 2-day battery life.',
                'description': 'Elevated design with an authentic metal frame and 3D glass back. Powered by the Exynos 1480 processor with AMD Xclipse 530 GPU. Certified with Samsung Knox Vault hardware security, IP67 water immersion rating, and micro-SD card expansion up to 1TB.',
                'price': Decimal('135000.00'),
                'sale_price': Decimal('129000.00'),
                'stock': 18,
                'is_featured': False,
                'image_url': 'https://images.unsplash.com/photo-1585060544812-6b45742d762f?w=800&auto=format&fit=crop&q=80',
                'gallery_images': [
                    'https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=800&auto=format&fit=crop&q=80'
                ]
            },
            {
                'category_slug': 'mobile-phones',
                'brand': 'Motorola',
                'name': 'Motorola Edge 40 Neo 5G 12GB/256GB',
                'sku': 'PM-MOB-MOT-E40N',
                'specs': '12GB RAM • 256GB • 144Hz Endless Edge pOLED • 68W TurboPower • IP68 Waterproof',
                'short_description': 'Ultra-thin curved design curated by Pantone, IP68 water resistance, and fluid 144Hz 10-bit display.',
                'description': 'Stunning design that stands out from the crowd. Features a dual-curved 6.55-inch 144Hz pOLED HDR10+ display, MediaTek Dimensity 7030 5G chipset, 50MP Ultra Pixel camera with optical image stabilization, Dolby Atmos stereo sound, and 68W fast charger included in the box.',
                'price': Decimal('92000.00'),
                'sale_price': Decimal('88000.00'),
                'stock': 12,
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=800&auto=format&fit=crop&q=80',
                'gallery_images': [
                    'https://images.unsplash.com/photo-1580910051074-3eb694886505?w=800&auto=format&fit=crop&q=80'
                ]
            },
            {
                'category_slug': 'mobile-phones',
                'brand': 'Motorola',
                'name': 'Motorola Moto G84 5G 12GB/256GB',
                'sku': 'PM-MOB-MOT-G84',
                'specs': '12GB RAM • 256GB • Viva Magenta Vegan Leather • 50MP OIS • 5000mAh Battery',
                'short_description': 'Premium vegan leather back in Pantone Color of the Year with 12GB RAM and bright 120Hz pOLED panel.',
                'description': 'Remarkable style and substance. Features a soft vegan leather finish, 6.5-inch 120Hz pOLED display with billion-color depth, 50MP OIS camera that shoots clean low-light shots, Snapdragon 5G connectivity, and a 3.5mm headphone jack for audio purists.',
                'price': Decimal('68000.00'),
                'sale_price': None,
                'stock': 15,
                'is_featured': False,
                'image_url': 'https://images.unsplash.com/photo-1565849904461-04a58ad377e0?w=800&auto=format&fit=crop&q=80',
                'gallery_images': [
                    'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=800&auto=format&fit=crop&q=80'
                ]
            },
            {
                'category_slug': 'mobile-phones',
                'brand': 'Nokia',
                'name': 'Nokia G42 5G (QuickFix Repairable)',
                'sku': 'PM-MOB-NOK-G42',
                'specs': '6GB+5GB Virtual RAM • 128GB • 50MP AI Triple • 3-Day Battery • Snapdragon 480+',
                'short_description': 'Self-repairable 5G smartphone with 3-day battery life, 50MP AI camera, and clean stock Android.',
                'description': 'Built to last. The Nokia G42 5G is designed with QuickFix repairability allowing easy replacement of damaged screens or degraded batteries at home. Features 50MP AI camera with OZO 3D audio recording, guaranteed 2 years of Android OS upgrades, and durable recycled rear casing.',
                'price': Decimal('48000.00'),
                'sale_price': Decimal('44999.00'),
                'stock': 22,
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=800&auto=format&fit=crop&q=80',
                'gallery_images': [
                    'https://images.unsplash.com/photo-1565849904461-04a58ad377e0?w=800&auto=format&fit=crop&q=80'
                ]
            },
            {
                'category_slug': 'mobile-phones',
                'brand': 'Nokia',
                'name': 'Nokia C32 (Toughened Glass Back)',
                'sku': 'PM-MOB-NOK-C32',
                'specs': '4GB RAM • 64GB Storage • 50MP Camera • Toughened Glass Back • 5000mAh Battery',
                'short_description': 'Budget champion with luxury glass finish, 50MP night-mode camera, and 3-day battery longevity.',
                'description': 'A luxury look at an entry-level price. Features an elegant toughened glass back panel, 50MP main camera with advanced imaging algorithms for crisp daytime and night photos, side-mounted fingerprint sensor, and clean Android 13 without bloatware.',
                'price': Decimal('28000.00'),
                'sale_price': None,
                'stock': 25,
                'is_featured': False,
                'image_url': 'https://images.unsplash.com/photo-1565849904461-04a58ad377e0?w=800&auto=format&fit=crop&q=80',
                'gallery_images': [
                    'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=800&auto=format&fit=crop&q=80'
                ]
            },
            {
                'category_slug': 'mobile-phones',
                'brand': 'Vivo',
                'name': 'Vivo V30 5G 12GB/256GB',
                'sku': 'PM-MOB-VIV-V30',
                'specs': '12GB RAM • 256GB Storage • 50MP Studio Aura Light OIS • 80W FlashCharge • Snapdragon 7 Gen 3',
                'short_description': 'Studio-grade portrait photography phone with intelligent Aura Light ring, 3D curved 1.5K AMOLED, and 80W fast charging.',
                'description': 'Redefines portrait photography with its enlarged Studio Aura Light that intelligently adjusts color temperature based on ambient lighting. Features a 6.78-inch 120Hz 1.5K 3D curved AMOLED screen, ultra-slim 7.45mm body, 5000mAh battery, and Snapdragon 7 Gen 3 performance.',
                'price': Decimal('129000.00'),
                'sale_price': Decimal('124000.00'),
                'stock': 14,
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1580910051074-3eb694886505?w=800&auto=format&fit=crop&q=80',
                'gallery_images': [
                    'https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=800&auto=format&fit=crop&q=80'
                ]
            },
            {
                'category_slug': 'mobile-phones',
                'brand': 'Vivo',
                'name': 'Vivo Y27s 8GB/128GB',
                'sku': 'PM-MOB-VIV-Y27S',
                'specs': '8GB+8GB Extended RAM • 128GB • 44W FlashCharge • 50MP Dual Camera • Snapdragon 680',
                'short_description': 'Practical everyday smartphone with 44W rapid charging, IP54 splash resistance, and crystalline matte finish.',
                'description': 'Features a smooth 90Hz sunlight display, 50MP primary sensor, 44W fast charging capable of reaching 70% in 35 minutes, side fingerprint scanner, and NFC support. Tested and guaranteed by PixelMart.',
                'price': Decimal('46000.00'),
                'sale_price': None,
                'stock': 20,
                'is_featured': False,
                'image_url': 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=800&auto=format&fit=crop&q=80',
                'gallery_images': [
                    'https://images.unsplash.com/photo-1580910051074-3eb694886505?w=800&auto=format&fit=crop&q=80'
                ]
            },
            {
                'category_slug': 'mobile-phones',
                'brand': 'Oppo',
                'name': 'Oppo Reno 11 5G 12GB/256GB',
                'sku': 'PM-MOB-OPP-R11',
                'specs': '12GB RAM • 256GB • 32MP Telephoto Portrait • 67W SUPERVOOC • 120Hz 3D Curved Screen',
                'short_description': 'The portrait expert with dedicated Sony 32MP 2x optical telephoto lens and flagship 67W SUPERVOOC charging.',
                'description': 'Capture studio portraits with creamy natural bokeh. Features a Sony IMX709 32MP telephoto portrait camera, 6.7-inch 120Hz borderless 3D curved OLED display with HDR10+, MediaTek Dimensity 7050 5G processor, and 67W flash charging that tops up in under 45 minutes.',
                'price': Decimal('124000.00'),
                'sale_price': Decimal('118000.00'),
                'stock': 12,
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1580910051074-3eb694886505?w=800&auto=format&fit=crop&q=80',
                'gallery_images': [
                    'https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=800&auto=format&fit=crop&q=80'
                ]
            },
            {
                'category_slug': 'mobile-phones',
                'brand': 'Oppo',
                'name': 'Oppo A78 8GB/256GB',
                'sku': 'PM-MOB-OPP-A78',
                'specs': '8GB RAM • 256GB Storage • 67W SUPERVOOC • 90Hz FHD+ AMOLED • Dual Stereo Speakers',
                'short_description': 'Fast-charging everyday star with 67W flash charge, vibrant AMOLED panel, and retro slim squared frame.',
                'description': 'Features a diamond matrix back design, 6.43-inch FHD+ 90Hz AMOLED display with in-display fingerprint reader, 50MP primary AI camera, dual stereo speakers with 200% Ultra Volume mode, and 5000mAh battery.',
                'price': Decimal('58000.00'),
                'sale_price': None,
                'stock': 18,
                'is_featured': False,
                'image_url': 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=800&auto=format&fit=crop&q=80',
                'gallery_images': [
                    'https://images.unsplash.com/photo-1565849904461-04a58ad377e0?w=800&auto=format&fit=crop&q=80'
                ]
            },

            # ----------------------------------------------------
            # GADGETS & ACCESSORIES
            # ----------------------------------------------------
            {
                'category_slug': 'gadgets-accessories',
                'brand': 'Sony',
                'name': 'Sony WH-1000XM5 Wireless Headphones',
                'sku': 'PM-GAD-SNY-WH1000',
                'specs': 'Industry-Leading Active Noise Cancelling • 30h Battery • 8-Mic Array • LDAC Hi-Res Audio',
                'short_description': 'Top-rated noise cancelling wireless headphones with 8 microphones, Auto NC Optimizer, and speak-to-chat.',
                'description': 'The benchmark in personal audio tranquility. Features two processors controlling eight microphones for unprecedented noise cancellation. Integrated V1 processor unlocks the full potential of Sony\'s HD Noise Cancelling Processor QN1. Soft fit leather design with 30-hour battery life.',
                'price': Decimal('85000.00'),
                'sale_price': Decimal('79999.00'),
                'stock': 15,
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&auto=format&fit=crop&q=80',
                'gallery_images': [
                    'https://images.unsplash.com/photo-1484704849700-f032a568e944?w=800&auto=format&fit=crop&q=80'
                ]
            },
            {
                'category_slug': 'gadgets-accessories',
                'brand': 'Apple',
                'name': 'Apple AirPods Pro (2nd Gen with USB-C)',
                'sku': 'PM-GAD-APP-APP2',
                'specs': 'Apple H2 Chip • 2x Active Noise Cancellation • Adaptive Audio • MagSafe USB-C Case',
                'short_description': 'Pro earbuds with up to 2x more active noise cancellation, transparency mode, and precision finding.',
                'description': 'Experience next-level audio fidelity with the Apple H2 chip. Adaptive Audio dynamically blends Transparency and Active Noise Cancellation to match your surroundings. Features personalized Spatial Audio with dynamic head tracking, touch swipe volume controls, and IP54 dust and sweat resistance.',
                'price': Decimal('65000.00'),
                'sale_price': None,
                'stock': 20,
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1600294037681-c80b4cb5b434?w=800&auto=format&fit=crop&q=80',
                'gallery_images': [
                    'https://images.unsplash.com/photo-1572569511254-d8f925fe2cbb?w=800&auto=format&fit=crop&q=80'
                ]
            },
            {
                'category_slug': 'gadgets-accessories',
                'brand': 'Samsung',
                'name': 'Samsung Galaxy Watch 6 Classic 47mm LTE',
                'sku': 'PM-GAD-SAM-W6C',
                'specs': 'Physical Rotating Bezel • Sapphire Crystal • Body Composition ECG • Standalone LTE',
                'short_description': 'Classic stainless steel smartwatch with rotating click bezel, advanced sleep coaching, and heart monitoring.',
                'description': 'Timeless horology meets smart fitness tracking. Features a 1.5-inch Super AMOLED always-on display protected by Sapphire Crystal glass, Samsung BioActive sensor monitoring ECG and blood pressure, LTE connectivity for calls without your phone, and 5 ATM water resistance.',
                'price': Decimal('78000.00'),
                'sale_price': Decimal('72000.00'),
                'stock': 12,
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=800&auto=format&fit=crop&q=80',
                'gallery_images': [
                    'https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?w=800&auto=format&fit=crop&q=80'
                ]
            },
            {
                'category_slug': 'gadgets-accessories',
                'brand': 'Anker',
                'name': 'Anker Prime 67W GaN Fast Wall Charger',
                'sku': 'PM-GAD-ANK-67W',
                'specs': '67W Max Output • 2x USB-C + 1x USB-A • GaNPrime Architecture • ActiveShield 2.0',
                'short_description': 'Compact multi-device GaN wall charger capable of fast-charging laptops, iPhones, and Galaxy devices simultaneously.',
                'description': 'Say goodbye to bulky brick chargers. Powered by Anker GaNPrime technology with dynamic power distribution. Fast charges an iPhone 15 Pro to 50% in 25 minutes or a MacBook Air M1 at full speed. ActiveShield 2.0 monitors temperature over 3 million times per day for ultimate safety.',
                'price': Decimal('14500.00'),
                'sale_price': None,
                'stock': 35,
                'is_featured': False,
                'image_url': 'https://images.unsplash.com/photo-1583863788434-e58a36330cf0?w=800&auto=format&fit=crop&q=80',
                'gallery_images': [
                    'https://images.unsplash.com/photo-1585338107529-13afc5f02586?w=800&auto=format&fit=crop&q=80'
                ]
            },
            {
                'category_slug': 'gadgets-accessories',
                'brand': 'Baseus',
                'name': 'Baseus Blade 20000mAh 100W Laptop Power Bank',
                'sku': 'PM-GAD-BAS-100W',
                'specs': '20000mAh Capacity • 100W Dual-Way USB-C • 18mm Ultra-Thin • Digital LED Power Meter',
                'short_description': 'Ultra-thin laptop power bank with 100W Power Delivery, 4 ports, and digital real-time wattage display.',
                'description': 'Designed specifically for laptops and high-draw devices. Weighs only 490g with an 18mm ultra-slim profile that slides right into your laptop sleeve. Supports PD 3.0, QC 4.0, and SCP protocols. Digital screen displays remaining battery percentage, charging wattage, and time remaining.',
                'price': Decimal('18500.00'),
                'sale_price': Decimal('16900.00'),
                'stock': 28,
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1609091839311-d5365f9ff1c5?w=800&auto=format&fit=crop&q=80',
                'gallery_images': [
                    'https://images.unsplash.com/photo-1583863788434-e58a36330cf0?w=800&auto=format&fit=crop&q=80'
                ]
            },
            {
                'category_slug': 'gadgets-accessories',
                'brand': 'Dell',
                'name': 'Dell Pro 15.6" Executive Laptop Backpack',
                'sku': 'PM-GAD-DEL-BAG',
                'specs': 'Fits 15.6" Laptops • Water-Resistant Eco-Friendly • EVA Foam Protection • Trolley Pass',
                'short_description': 'Weather-resistant executive backpack with dedicated padded laptop compartment and reflective accents.',
                'description': 'Keep your laptop, tablet, and everyday essentials safely protected on your daily commute through Quetta. Features shock-absorbing EVA foam cushioning, water-resistant exterior coating made from recycled car windshields, ergonomic breathable shoulder straps, and dedicated cable routing for on-the-go charging.',
                'price': Decimal('9500.00'),
                'sale_price': None,
                'stock': 40,
                'is_featured': False,
                'image_url': 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=800&auto=format&fit=crop&q=80',
                'gallery_images': [
                    'https://images.unsplash.com/photo-1622560480605-d83c853bc5c3?w=800&auto=format&fit=crop&q=80'
                ]
            }
        ]

        # Deactivate previous products and create/update PixelMart products
        Product.objects.all().delete()
        created_products = []

        for p_data in products_data:
            cat = cat_map[p_data['category_slug']]
            gallery_urls = p_data.pop('gallery_images', [])
            cat_slug = p_data.pop('category_slug')

            prod = Product.objects.create(
                category=cat,
                brand=p_data['brand'],
                name=p_data['name'],
                sku=p_data['sku'],
                specs=p_data.get('specs', ''),
                short_description=p_data['short_description'],
                description=p_data['description'],
                price=p_data['price'],
                sale_price=p_data['sale_price'],
                stock=p_data['stock'],
                image_url=p_data['image_url'],
                is_active=True,
                is_featured=p_data['is_featured']
            )

            for idx, g_url in enumerate(gallery_urls):
                ProductImage.objects.create(
                    product=prod,
                    image_url=g_url,
                    alt_text=f"{prod.name} angle {idx + 1}"
                )

            created_products.append(prod)

        self.stdout.write(self.style.SUCCESS(f"Populated {len(created_products)} authentic PixelMart products with PKR pricing."))

        # 5. Customer Reviews for Pakistani Tech Community
        Review.objects.all().delete()
        reviews_data = [
            {
                'product_sku': 'PM-LAP-HP-840G2',
                'user': customer_objs[0],
                'rating': 5,
                'title': 'Best Core i7 5th Gen laptop in Quetta under 70k!',
                'comment': 'Purchased the HP 840 G2 Core i7 from PixelMart showroom. Excellent condition, battery backup easily 3.5 hours, and 256GB SSD is lightning fast. Genuine shop and transparent testing!',
                'is_verified': True
            },
            {
                'product_sku': 'PM-LAP-LEN-T480',
                'user': customer_objs[1],
                'rating': 5,
                'title': 'ThinkPad T480 dual battery is incredible for load-shedding',
                'comment': 'Dual battery keeps my work running for 10+ hours without interruption. Keyboard typing feel is unmatched. PixelMart delivered with original charger and warranty receipt.',
                'is_verified': True
            },
            {
                'product_sku': 'PM-MOB-APP-IP15PM',
                'user': customer_objs[2],
                'rating': 5,
                'title': 'Original Box Packed & PTA Tax Verified on DIRBS!',
                'comment': 'Checked IMEI on PTA DIRBS portal before paying COD. 100% genuine physical dual SIM model. The natural titanium finish is stunning. Thank you PixelMart team!',
                'is_verified': True
            },
            {
                'product_sku': 'PM-MOB-SAM-S24U',
                'user': customer_objs[3],
                'rating': 5,
                'title': 'S24 Ultra camera and AI translation is a game changer',
                'comment': 'Upgraded from Note 20 Ultra. The flat anti-reflective screen and 100x zoom are mindblowing. Delivered next day across Quetta in sealed packing.',
                'is_verified': True
            },
            {
                'product_sku': 'PM-GAD-SNY-WH1000',
                'user': customer_objs[4],
                'rating': 5,
                'title': 'Original Sony noise cancellation headphones',
                'comment': 'The active noise cancelling completely blocks street noise and generator hum. Crystal clear audio calls and LDAC Bluetooth quality.',
                'is_verified': True
            }
        ]

        for r in reviews_data:
            try:
                prod = Product.objects.get(sku=r['product_sku'])
                Review.objects.create(
                    product=prod,
                    user=r['user'],
                    rating=r['rating'],
                    title=r['title'],
                    comment=r['comment'],
                    is_verified_purchase=r['is_verified'],
                    is_approved=True
                )
            except Product.DoesNotExist:
                pass

        # 6. Promotions & Coupons in PKR
        Coupon.objects.all().delete()
        Coupon.objects.create(
            code='PIXEL10',
            discount_type='PERCENTAGE',
            discount_value=Decimal('10.00'),
            min_order_amount=Decimal('50000.00'),
            usage_limit=500,
            is_active=True
        )
        Coupon.objects.create(
            code='QUETTA5',
            discount_type='FIXED',
            discount_value=Decimal('5000.00'),
            min_order_amount=Decimal('80000.00'),
            usage_limit=200,
            is_active=True
        )

        # 7. Announcement Bar
        Announcement.objects.all().delete()
        Announcement.objects.create(
            message='✨ Welcome to PixelMart Quetta! Pakistan\'s premier hub for Laptops, Mobile Phones & Gadgets. Cash on Delivery & Free Delivery on orders over PKR 100,000! Contact: 00816-23-736822',
            is_active=True,
            link_url='/pages/shop.html'
        )

        self.stdout.write(self.style.SUCCESS("PixelMart sample dataset loaded successfully!"))
