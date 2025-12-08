from django.contrib import admin
from product_management_app.models import Shirt, ShirtCategory, ShirtImage, UserShirt, FavoriteShirt, ShirtSubCategory, Customizer, UserCustomizer, Pattern, Color, Font, Order, Invoice

# Register your models here.
admin.site.register(ShirtCategory)
admin.site.register(Shirt)
admin.site.register(ShirtImage)
admin.site.register(UserShirt)
admin.site.register(FavoriteShirt)
admin.site.register(ShirtSubCategory)
admin.site.register(Customizer)
admin.site.register(UserCustomizer)
admin.site.register(Pattern)
admin.site.register(Color)
admin.site.register(Font)
admin.site.register(Order)
admin.site.register(Invoice)