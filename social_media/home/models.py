from django.db import models
from user_profile.models import UserProfile

def image_path_generator(instance, filename):
    return f"uploads/{instance.author.id}_posts_images/{filename}"

# Create your models here.
class Tag(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
    
class Post(models.Model):
    author = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    content = models.TextField()
    image = models.ImageField(upload_to=image_path_generator, default='images/default_post_image.webp', blank=True, null=True)
    tags = models.ManyToManyField(Tag, related_name='posts', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    likers = models.ManyToManyField(UserProfile, related_name='liked_posts')
    dislikers = models.ManyToManyField(UserProfile, related_name='disliked_posts')     
    is_visible = models.BooleanField(default=True)
    
    def __str__(self):
        return self.content[:20]
    
    def likers_count(self):
        return self.likers.count()

    def dislikers_count(self):
        return self.dislikers.count()
    
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    content = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.content[:20]
