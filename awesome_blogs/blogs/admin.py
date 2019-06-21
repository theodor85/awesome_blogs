from django.contrib import admin

from .models import Post


class PostAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'created_at', 'author')
    search_fields = ('title', )
    fields = (
        ('title', 'content', 'author')
    )
    #actions = (send_new_post_notifications, )

admin.site.register(Post, PostAdmin)
