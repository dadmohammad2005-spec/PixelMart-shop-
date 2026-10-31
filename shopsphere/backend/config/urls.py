from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve
from .views import serve_frontend_root, serve_frontend_page, serve_frontend_asset

urlpatterns = [
    path('admin/', admin.site.urls),

    # REST API Endpoints v1
    path('api/v1/accounts/', include('apps.accounts.urls')),
    path('api/v1/products/', include('apps.products.urls')),
    path('api/v1/cart/', include('apps.cart.urls')),
    path('api/v1/orders/', include('apps.orders.urls')),
    path('api/v1/payments/', include('apps.payments.urls')),
    path('api/v1/reviews/', include('apps.reviews.urls')),
    path('api/v1/promotions/', include('apps.promotions.urls')),
    path('api/v1/wishlist/', include('apps.wishlist.urls')),

    # Media files serving (works in both development and production)
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),

    # Frontend assets and page serving for seamless full-stack local preview
    re_path(r'^assets/(?P<asset_path>.*)$', serve_frontend_asset, name='frontend-asset'),
    path('index.html', serve_frontend_root, name='frontend-index-html'),
    path('index', serve_frontend_root, name='frontend-index'),
    path('home', serve_frontend_root, name='frontend-home-bare'),
    path('home/', serve_frontend_root, name='frontend-home-slash'),
    path('home.html', serve_frontend_root, name='frontend-home-html'),
    path('pages/index.html', serve_frontend_root, name='frontend-pages-index-html'),
    path('pages/home.html', serve_frontend_root, name='frontend-pages-home-html'),
    path('pages/<str:page_name>', serve_frontend_page, name='frontend-page'),
    path('', serve_frontend_root, name='frontend-home'),
]
