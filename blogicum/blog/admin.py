from django.contrib import admin
from django.template.defaultfilters import truncatechars
from blog.models import Post, Category, Location


def truncatetext(self):
    return truncatechars(self.text, 30)


truncatetext.short_description = 'Текст'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_published')
    list_editable = ('is_published',)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_published')
    list_editable = ('is_published',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        truncatetext,
        'pub_date',
        'author',
        'category',
        'is_published'
    )
    list_editable = (
        'category',
        'is_published'
    )
    search_fields = ('title',)
    list_filter = ('author', 'is_published')
    list_display_links = ('title',)

    list_per_page = 10
