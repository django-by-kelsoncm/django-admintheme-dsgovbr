from django.contrib import admin
from dsgovbr.admin.import_export import DSGovBrModelAdmin
from .models import Categoria, Tag, Noticia, Comentario


class ComentarioInline(admin.TabularInline):
    model = Comentario
    extra = 1


@admin.register(Categoria)
class CategoriaAdmin(DSGovBrModelAdmin):
    icon = "fas fa-tags"
    list_display = ("nome", "slug")
    prepopulated_fields = {"slug": ("nome",)}


@admin.register(Tag)
class TagAdmin(DSGovBrModelAdmin):
    list_display = ("nome",)


@admin.register(Noticia)
class NoticiaAdmin(DSGovBrModelAdmin):
    icon = "fas fa-newspaper"
    list_display = ("titulo", "categoria", "status", "criado_em")
    list_filter = ("status", "categoria", "criado_em")
    search_fields = ("titulo", "conteudo")
    prepopulated_fields = {"slug": ("titulo",)}
    filter_horizontal = ("tags",)
    inlines = [ComentarioInline]
