from rest_framework import serializers
from .models import Category, Product, ProductImage


class ProductImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'image_url', 'alt_text']

    def get_image(self, obj):
        if obj.image_url:
            return obj.image_url
        if obj.image:
            return obj.image.url
        return ''


class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'image', 'is_featured', 'product_count']


class ProductListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_slug = serializers.CharField(source='category.slug', read_only=True)
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    is_on_sale = serializers.BooleanField(read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)
    in_stock = serializers.BooleanField(read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    review_count = serializers.IntegerField(read_only=True)
    main_image = serializers.SerializerMethodField()
    all_images = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'brand', 'name', 'slug', 'sku', 'category', 'category_name', 'category_slug',
            'specs', 'short_description', 'price', 'sale_price', 'current_price', 'is_on_sale',
            'discount_percentage', 'stock', 'in_stock', 'main_image', 'image_url', 'all_images', 'is_featured',
            'average_rating', 'review_count', 'created_at'
        ]

    def get_main_image(self, obj):
        if obj.image_url:
            return obj.image_url
        if obj.main_image:
            return obj.main_image.url
        return ''

    def get_all_images(self, obj):
        urls = []
        if obj.image_url:
            urls.append(obj.image_url)
        elif obj.main_image:
            urls.append(obj.main_image.url)
        for img in obj.images.all():
            u = img.image_url or (img.image.url if img.image else '')
            if u and u not in urls:
                urls.append(u)
        return urls


class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    all_images = serializers.SerializerMethodField()
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    is_on_sale = serializers.BooleanField(read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)
    in_stock = serializers.BooleanField(read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    review_count = serializers.IntegerField(read_only=True)
    main_image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'brand', 'name', 'slug', 'sku', 'category', 'specs', 'short_description',
            'description', 'price', 'sale_price', 'current_price', 'is_on_sale',
            'discount_percentage', 'stock', 'in_stock', 'main_image', 'image_url', 'images', 'all_images',
            'is_featured', 'average_rating', 'review_count', 'created_at', 'updated_at'
        ]

    def get_main_image(self, obj):
        if obj.image_url:
            return obj.image_url
        if obj.main_image:
            return obj.main_image.url
        return ''

    def get_all_images(self, obj):
        urls = []
        if obj.image_url:
            urls.append(obj.image_url)
        elif obj.main_image:
            urls.append(obj.main_image.url)
        for img in obj.images.all():
            u = img.image_url or (img.image.url if img.image else '')
            if u and u not in urls:
                urls.append(u)
        return urls


class ProductWriteSerializer(serializers.ModelSerializer):
    gallery_urls = serializers.ListField(
        child=serializers.URLField(),
        required=False,
        write_only=True
    )

    class Meta:
        model = Product
        fields = [
            'id', 'brand', 'name', 'slug', 'sku', 'category', 'specs', 'short_description',
            'description', 'price', 'sale_price', 'stock', 'main_image',
            'image_url', 'is_active', 'is_featured', 'gallery_urls'
        ]

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Price must be greater than or equal to 0.")
        return value

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("Stock cannot be negative.")
        return value

    def validate(self, attrs):
        price = attrs.get('price', getattr(self.instance, 'price', None))
        sale_price = attrs.get('sale_price', getattr(self.instance, 'sale_price', None))
        if sale_price is not None and price is not None and sale_price >= price:
            raise serializers.ValidationError({"sale_price": "Sale price must be strictly less than standard price."})
        return attrs

    def create(self, validated_data):
        gallery_urls = validated_data.pop('gallery_urls', [])
        product = super().create(validated_data)
        for idx, g_url in enumerate(gallery_urls):
            ProductImage.objects.create(
                product=product,
                image_url=g_url,
                alt_text=f"{product.name} - View {idx + 1}"
            )
        return product

    def update(self, instance, validated_data):
        gallery_urls = validated_data.pop('gallery_urls', None)
        product = super().update(instance, validated_data)
        if gallery_urls is not None:
            instance.images.all().delete()
            for idx, g_url in enumerate(gallery_urls):
                ProductImage.objects.create(
                    product=instance,
                    image_url=g_url,
                    alt_text=f"{instance.name} - View {idx + 1}"
                )
        return product
