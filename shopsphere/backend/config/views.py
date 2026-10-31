import os
import mimetypes
from pathlib import Path
from django.conf import settings
from django.http import HttpResponse, Http404, FileResponse


def serve_frontend_root(request):
    """Serve frontend index.html for direct Django preview."""
    index_file = settings.BASE_DIR.parent / 'frontend' / 'index.html'
    if index_file.exists():
        with open(index_file, 'r', encoding='utf-8') as f:
            return HttpResponse(f.read(), content_type='text/html')
    return HttpResponse("<h1>PixelMart Backend API Running</h1><p>Visit /api/v1/ or /admin/</p>")


def serve_frontend_page(request, page_name):
    """Serve frontend HTML pages from frontend/pages/."""
    # If root/index/home is requested via /pages/
    if page_name in ['index.html', 'index', 'home.html', 'home']:
        return serve_frontend_root(request)
    if not page_name.endswith('.html'):
        page_name = f"{page_name}.html"
    page_file = settings.BASE_DIR.parent / 'frontend' / 'pages' / page_name
    if page_file.exists():
        with open(page_file, 'r', encoding='utf-8') as f:
            return HttpResponse(f.read(), content_type='text/html')
    raise Http404(f"Page '{page_name}' not found.")


def serve_frontend_asset(request, asset_path):
    """Serve static CSS, JS, and image assets from frontend/assets/."""
    asset_file = settings.BASE_DIR.parent / 'frontend' / 'assets' / asset_path
    if asset_file.exists() and asset_file.is_file():
        content_type, _ = mimetypes.guess_type(str(asset_file))
        return FileResponse(open(asset_file, 'rb'), content_type=content_type or 'application/octet-stream')
    raise Http404(f"Asset '{asset_path}' not found.")
