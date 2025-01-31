from django.contrib import admin

# Register your models here.
from .models import Post, Comment, Tag

class PostAdmin(admin.ModelAdmin):
    readonly_fields = ('likers', 'dislikers')
    
admin.site.register(Post, PostAdmin)
admin.site.register(Comment)
admin.site.register(Tag)