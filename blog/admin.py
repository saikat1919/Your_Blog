from django.contrib import admin
from .models import Post, Category, Comment, Like, CommentLike, UserProfile

# Register your models here.

admin.site.register(Post)
admin.site.register(Category)
admin.site.register(Comment)
admin.site.register(Like)
admin.site.register(CommentLike)
admin.site.register(UserProfile)

