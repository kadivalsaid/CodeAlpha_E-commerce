from __future__ import annotations

from django.conf import settings
from django.db import models
from django.db.models import F, Sum
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from django.db.models.query import QuerySet


class _ImageFileLike(Protocol):
    """
    Minimal protocol for Django's ImageFieldFile that we need for resizing.
    """

    @property
    def path(self) -> str: ...

    def __bool__(self) -> bool: ...


def _resize_image_in_place(image_field: _ImageFileLike, *, max_px: int = 1200) -> None:
    """
    Keep uploaded product images reasonably sized for the web.
    Resizes only when the image is larger than max_px on either side.
    """
    if not image_field:
        return
    try:
        from PIL import Image
    except Exception:
        return

    try:
        img = Image.open(image_field.path)
    except Exception:
        return

    width, height = img.size
    if width <= max_px and height <= max_px:
        return

    img.thumbnail((max_px, max_px))

    # Preserve original format when possible
    fmt = (img.format or "JPEG").upper()
    save_kwargs = {}
    if fmt in {"JPEG", "JPG"}:
        save_kwargs = {"quality": 85, "optimize": True, "progressive": True}

    try:
        img.save(image_field.path, format=fmt, **save_kwargs)
    except Exception:
        # As a fallback, just try saving without extra options.
        try:
            img.save(image_field.path)
        except Exception:
            return


class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        _resize_image_in_place(self.image, max_px=1200)


class Cart(models.Model):
    id: int
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart')
    updated_at = models.DateTimeField(auto_now=True)
    items: "QuerySet[CartItem]"

    def __str__(self) -> str:
        return f"Cart({self.user})"

    def total(self):
        result = (
            self.items.aggregate(
                total=Sum(F('quantity') * F('product__price'), output_field=models.DecimalField(max_digits=12, decimal_places=2))
            )['total']
            or 0
        )
        return result


class CartItem(models.Model):
    id: int
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('cart', 'product')

    def __str__(self) -> str:
        return f"{self.product} x{self.quantity}"

    def line_total(self):
        return self.quantity * self.product.price


class Order(models.Model):
    id: int
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    address = models.TextField()
    city = models.CharField(max_length=120)
    postal_code = models.CharField(max_length=30)
    paid = models.BooleanField(default=False)
    items: "QuerySet[OrderItem]"

    def __str__(self) -> str:
        return f"Order({self.id}) - {self.user}"

    def total(self):
        result = (
            self.items.aggregate(
                total=Sum(F('quantity') * F('price'), output_field=models.DecimalField(max_digits=12, decimal_places=2))
            )['total']
            or 0
        )
        return result


class OrderItem(models.Model):
    id: int
    order_id: int
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self) -> str:
        return f"OrderItem({self.order_id}) - {self.product}"
