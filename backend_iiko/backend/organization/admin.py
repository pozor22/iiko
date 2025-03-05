from django.contrib import admin

from .models import Organization, Chain, Restaurant


class AuthorsInline(admin.TabularInline):
    model = Organization.authors.through
    extra = 1


class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'get_authors')
    list_filter = ('authors',)
    search_fields = ('name',)
    ordering = ('id',)

    inlines = [AuthorsInline]

    filter_horizontal = ('authors',)

    def get_authors(self, obj):
        return ', '.join([author.username for author in obj.authors.all()])
    get_authors.short_description = 'Авторы'


class ChainAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'organization')
    list_filter = ('organization',)
    search_fields = ('name',)
    ordering = ('id',)


admin.site.register(Organization, OrganizationAdmin)
admin.site.register(Chain, ChainAdmin)
admin.site.register(Restaurant)
