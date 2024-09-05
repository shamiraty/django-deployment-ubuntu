from django.contrib import admin
from .models import *
from import_export import resources
from import_export.admin import ImportExportModelAdmin

# Define a resource for the Product model
class ProductResource(resources.ModelResource):
    class Meta:
        model = Product
        fields = ('name', 'sku', 'category', 'supplier', 'purchase_price', 'selling_price', 'quantity_in_stock', 'expiry_date')
        import_id_fields = ('sku',)  # Use SKU as the unique identifier for imports

# Register ProductAdmin with import-export functionality
@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    resource_class = ProductResource
    list_display = ('name', 'sku', 'category', 'supplier', 'purchase_price', 'selling_price', 'quantity_in_stock', 'expiry_date')
    list_per_page = 10
    list_max_show_all = 10
    search_fields = ('name', 'sku__code', 'category__name', 'supplier')
    list_editable = ('selling_price', 'quantity_in_stock')
    list_select_related = ["sku", "category"]
     

@admin.register(Sale)
class SaleAdmin(ImportExportModelAdmin):
    list_display = ('product', 'quantity', 'sale_date', 'total_price', 'tax', 'total_with_tax', 'profit')
    list_per_page = 10
    date_hierarchy = 'sale_date'
    list_max_show_all = 10
    #autocomplete_fields = ['product']
    readonly_fields = ('sale_date',)
    list_select_related = ["product"]  # Assuming a ForeignKey relationship

@admin.register(InventoryLog)
class InventoryLogAdmin(admin.ModelAdmin):
    list_display = ('product', 'change_in_quantity', 'timestamp')
    list_per_page = 10
    date_hierarchy = 'timestamp'
    list_max_show_all = 10
    #autocomplete_fields = ['product']
    readonly_fields = ('timestamp',)
    list_select_related = ["product"]
    
    
@admin.register(Category)
class CategoryAdmin(ImportExportModelAdmin):
    list_per_page = 10
    list_max_show_all = 10

@admin.register(SKU)
class SKUAdmin(ImportExportModelAdmin):
    list_per_page = 10
    list_max_show_all = 10


