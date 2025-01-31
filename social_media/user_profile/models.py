from django.db import models
from django.contrib.auth.models import AbstractUser

def image_path_generator(self, filename):
    return f"uploads/{self.username}_profile_image/{filename}"


# Create your models here.
class UserProfile(AbstractUser):
    bio = models.TextField(max_length=70, blank=True)
    profile_image = models.ImageField(upload_to=image_path_generator, default='images/def_prof_image.webp', blank=True, null=True)
    following = models.ManyToManyField('self', related_name='followers', symmetrical=False)
    sent_requests = models.ManyToManyField('self', related_name='received_requests', symmetrical=False)

    def accept_friend_request(self, friend):
        self.following.add(friend)
        friend.following.add(self)
        self.received_requests.remove(friend)
        friend.sent_requests.remove(self)

    def reject_friend_request(self, friend):
        self.received_requests.remove(friend)
        friend.sent_requests.remove(self)