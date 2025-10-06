from django.contrib import admin
from product_management_app.models import Shirt, ShirtCategory, UserShirt, FavoriteShirt, ShirtSubCategory

# Register your models here.
admin.site.register(ShirtCategory)
admin.site.register(Shirt)
admin.site.register(UserShirt)
admin.site.register(FavoriteShirt)
admin.site.register(ShirtSubCategory)