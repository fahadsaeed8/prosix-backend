from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class ShirtCategory(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
class ShirtSubCategory(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
class Shirt(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(ShirtCategory, related_name='shirts_category', on_delete=models.CASCADE) 
    sub_category = models.ForeignKey(ShirtSubCategory, related_name='shirts_subcategory', on_delete=models.SET_NULL, null=True, blank=True) 

    svg_file = models.FileField(upload_to='shirts/svg/', blank=True, null=True)
    white_base_file = models.FileField(upload_to='shirts/white_base/', blank=True, null=True)
    black_base_file = models.FileField(upload_to='shirts/black_base/', blank=True, null=True)

    front_base = models.FileField(upload_to='shirts/Shirt_images/', blank=True, null=True)
    front_child1 = models.FileField(upload_to='shirts/Shirt_images/', blank=True, null=True)
    front_child2 = models.FileField(upload_to='shirts/Shirt_images/', blank=True, null=True)
    front_child3 = models.FileField(upload_to='shirts/Shirt_images/', blank=True, null=True)

    back_base = models.FileField(upload_to='shirts/Shirt_images/', blank=True, null=True)
    back_child1 = models.FileField(upload_to='shirts/Shirt_images/', blank=True, null=True)
    back_child2 = models.FileField(upload_to='shirts/Shirt_images/', blank=True, null=True)
    back_child3 = models.FileField(upload_to='shirts/Shirt_images/', blank=True, null=True)

    left_base = models.FileField(upload_to='shirts/Shirt_images/', blank=True, null=True)
    left_child1 = models.FileField(upload_to='shirts/Shirt_images/', blank=True, null=True)
    left_child2 = models.FileField(upload_to='shirts/Shirt_images/', blank=True, null=True)
    left_child3 = models.FileField(upload_to='shirts/Shirt_images/', blank=True, null=True)
    
    right_base = models.FileField(upload_to='shirts/Shirt_images/', blank=True, null=True)
    right_child1 = models.FileField(upload_to='shirts/Shirt_images/', blank=True, null=True)
    right_child2 = models.FileField(upload_to='shirts/Shirt_images/', blank=True, null=True)
    right_child3 = models.FileField(upload_to='shirts/Shirt_images/', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class UserShirt(models.Model):
    user = models.ForeignKey(User, related_name='usershirts_user', on_delete=models.CASCADE)
    shirt = models.ForeignKey(Shirt, related_name='usershirts_shirt', on_delete=models.CASCADE)
    colors = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.shirt.name}"
    
class FavoriteShirt(models.Model):
    user = models.ForeignKey(User, related_name='favoriteshirt_user', on_delete=models.CASCADE)
    shirt = models.ForeignKey(Shirt, related_name='favoriteshirt_shirt', on_delete=models.CASCADE, null=True, blank=True)
    user_shirt = models.ForeignKey(UserShirt, related_name='favoriteshirt_user_shirt', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.user_shirt:
            return f"{self.user.username} - User Shirt-{self.user_shirt.id}"
        elif self.shirt:
            return f"{self.user.username} - {self.shirt.name}"
        else:
            return f"{self.user.username} - No shirt selected"