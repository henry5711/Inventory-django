import django_filters
from .models import *

class UserFilter(django_filters.FilterSet):
    username = django_filters.CharFilter(lookup_expr='icontains')
    email = django_filters.CharFilter(lookup_expr='icontains')
    name = django_filters.CharFilter(lookup_expr='icontains')
    last_name = django_filters.CharFilter(lookup_expr='icontains')
    role_id = django_filters.NumberFilter(field_name='role__id') 
    document = django_filters.CharFilter(lookup_expr='icontains')
    address = django_filters.CharFilter(lookup_expr='icontains')
    phone_number = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
            model = User
            fields = [
                    'username', 
                    'email', 
                    'name', 
                    'last_name', 
                    'role_id',
                    'document', 
                    'address',
                    'phone_number', ]
            
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.filters:
            if 'icontains' in self.filters[field_name].lookup_expr:
                self.filters[field_name].lookup_expr = 'icontains' 
                self.filters[field_name].label = f'{self.filters[field_name].label} (similarity)'
        

class RoleFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')


    class Meta:
            model = Role
            fields = [ 
                    'name', 
                    'description',  ]
            
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.filters:
            if 'icontains' in self.filters[field_name].lookup_expr:
                self.filters[field_name].lookup_expr = 'icontains' 
                self.filters[field_name].label = f'{self.filters[field_name].label} (similarity)'        
        
class CategoryFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Category
        fields = [
            'name',
            'description',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.filters:
            if 'icontains' in self.filters[field_name].lookup_expr:
                self.filters[field_name].lookup_expr = 'icontains'
                self.filters[field_name].label = f'{self.filters[field_name].label} (similarity)'

class UnitFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    abbreviation = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Units
        fields = [
            'name',
            'description',
            'abbreviation',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.filters:
            if 'icontains' in self.filters[field_name].lookup_expr:
                self.filters[field_name].lookup_expr = 'icontains'
                self.filters[field_name].label = f'{self.filters[field_name].label} (similarity)'

class CoinFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    symbol = django_filters.CharFilter(lookup_expr='icontains')
    abbreviation = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Coin
        fields = [
            'name',
            'description',
            'symbol',
            'abbreviation',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.filters:
            if 'icontains' in self.filters[field_name].lookup_expr:
                self.filters[field_name].lookup_expr = 'icontains'
                self.filters[field_name].label = f'{self.filters[field_name].label} (similarity)'

class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    price = django_filters.NumberFilter()
    units = django_filters.CharFilter(field_name='units__name', lookup_expr='icontains')
    category = django_filters.CharFilter(field_name='category__name', lookup_expr='icontains')
    created_at = django_filters.DateFilter(field_name='created_at', lookup_expr='date')
    updated_at = django_filters.DateFilter(field_name='updated_at', lookup_expr='date')

    class Meta:
        model = Product
        fields = [
            'name',
            'description',
            'price',
            'units_id',
            'category_id',
            'created_at',
            'updated_at',
            'deleted_at',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.filters:
            if 'icontains' in self.filters[field_name].lookup_expr:
                self.filters[field_name].label = f'{self.filters[field_name].label} (similarity)'
    

class InventoryFilter(django_filters.FilterSet):
    quantity = django_filters.NumberFilter()
    created_at = django_filters.DateFilter(field_name='created_at', lookup_expr='date')
    updated_at = django_filters.DateFilter(field_name='updated_at', lookup_expr='date')

    class Meta:
        model = Inventory
        fields = [
            'product_id',
            'quantity',
            'created_at',
            'updated_at',
            'deleted_at',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.filters:
            if 'icontains' in self.filters[field_name].lookup_expr:
                self.filters[field_name].label = f'{self.filters[field_name].label} (similaridad)'

class InputFilter(django_filters.FilterSet):
    quantity = django_filters.NumberFilter()
    created_at = django_filters.DateFilter(field_name='created_at', lookup_expr='date')
    updated_at = django_filters.DateFilter(field_name='updated_at', lookup_expr='date')

    class Meta:
        model = Input
        fields = [
            'inventory_id',
            'quantity',
            'created_at',
            'updated_at',
            'deleted_at',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.filters:
            if 'icontains' in self.filters[field_name].lookup_expr:
                self.filters[field_name].label = f'{self.filters[field_name].label} (similaridad)'

class OutputFilter(django_filters.FilterSet):
    quantity = django_filters.NumberFilter()
    created_at = django_filters.DateFilter(field_name='created_at', lookup_expr='date')
    updated_at = django_filters.DateFilter(field_name='updated_at', lookup_expr='date')

    class Meta:
        model = Output
        fields = [
            'inventory_id',
            'quantity',
            'created_at',
            'updated_at',
            'deleted_at',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.filters:
            if 'icontains' in self.filters[field_name].lookup_expr:
                self.filters[field_name].label = f'{self.filters[field_name].label} (similaridad)'

class BillFilter(django_filters.FilterSet):
    id = django_filters.NumberFilter()
    date = django_filters.NumberFilter()
    total_price = django_filters.NumberFilter()
    created_at = django_filters.DateFilter(field_name='created_at', lookup_expr='date')
    updated_at = django_filters.DateFilter(field_name='updated_at', lookup_expr='date')

    class Meta:
        model = Bill
        fields = [
            'id',
            'date', 
            'user_id', 
            'total_price', 
            'created_at',
            'updated_at',
            'deleted_at',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.filters:
            if 'icontains' in self.filters[field_name].lookup_expr:
                self.filters[field_name].label = f'{self.filters[field_name].label} (similaridad)'

class DetailFilter(django_filters.FilterSet):
    quantity = django_filters.NumberFilter()
    price_unit = django_filters.NumberFilter()
    subtotal = django_filters.NumberFilter()
    created_at = django_filters.DateFilter(field_name='created_at', lookup_expr='date')
    updated_at = django_filters.DateFilter(field_name='updated_at', lookup_expr='date')

    class Meta:
        model = Detail
        fields = [
            'id',
            'inventory_id', 
            'bill_id',
            'quantity',  
            'price_unit',  
            'subtotal',  
            'created_at', 
            'updated_at', 
            'deleted_at'
            ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.filters:
            if 'icontains' in self.filters[field_name].lookup_expr:
                self.filters[field_name].label = f'{self.filters[field_name].label} (similaridad)'
