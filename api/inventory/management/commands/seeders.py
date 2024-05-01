from django.core.management.base import BaseCommand
from django.contrib.auth.models import PermissionsMixin, Permission
from inventory.models import Role, Units

class Command(BaseCommand):
    help = 'Sembrar roles y unidades de medida en la base de datos'

    def handle(self, *args, **options):
        self.seed_roles()
        self.seed_units()   
        self.seed_admin_permissions()
        self.seed_employee_permissions()
        self.seed_client_permissions()

    def seed_roles(self):
        roles = [
            ('Administrador', 'Rol con permisos de administrador del sistema.'),
            ('Empleado', 'Rol para los empleados del sistema.'),
            ('Cliente', 'Rol para los clientes del sistema.'),
        ]
        for name, description in roles:
            Role.objects.get_or_create(name=name, description=description)

    def seed_units(self):
            units = [
                {'name': 'Gramo', 'description': 'Una unidad de masa utilizada comúnmente para medir ingredientes secos y líquidos en pequeñas cantidades.', 'abbreviation': 'g'},
                {'name': 'Kilogramo', 'description': 'Es una unidad de masa más grande que el gramo y se utiliza para medir ingredientes en cantidades más grandes.', 'abbreviation': 'kg'},
                {'name': 'Litro', 'description': 'Es una unidad de volumen que se utiliza para medir líquidos como agua, leche, aceite, etc.', 'abbreviation': 'L'},
                {'name': 'Mililitro', 'description': 'Es una unidad de volumen más pequeña que el litro y se utiliza comúnmente para medir líquidos en pequeñas cantidades.', 'abbreviation': 'ml'},
                {'name': 'Unidad', 'description': 'Una unidad genérica que puede referirse a cualquier artículo individual, ya sea sólido o líquido, sin una medida específica adjunta.', 'abbreviation': 'unidad'},
                {'name': 'Docena', 'description': 'Una docena se refiere a un grupo de doce unidades. Se utiliza comúnmente para contar artículos como huevos, panecillos, etc.', 'abbreviation': 'docena'},
            ]
            for unit_data in units:
                Units.objects.get_or_create(**unit_data)

    def seed_admin_permissions(self):
        admin_role = Role.objects.get(name='Administrador')

        all_permissions = Permission.objects.all()

        admin_role.permissions.add(*all_permissions)

    def seed_employee_permissions(self):
            employee_role = Role.objects.get(name='Empleado')

            permissions_codenames = [
                'add_user', 'view_user',
                'add_category', 'change_category', 'view_category',
                'add_units', 'change_units', 'view_units',
                'add_coin', 'change_coin', 'view_coin',
                'add_product', 'change_product', 'view_product',
                'add_inventory', 'change_inventory', 'view_inventory',
                'add_input', 'change_input', 'view_input',
                'add_output', 'change_output', 'view_output',
                'add_bill', 'change_bill', 'view_bill',
                'add_detail', 'change_detail', 'view_detail',
            ]

            permissions = Permission.objects.filter(codename__in=permissions_codenames)

            employee_role.permissions.add(*permissions)
    
    def seed_client_permissions(self):
            client_role = Role.objects.get(name='Cliente')

            permissions_codenames = ['view_product']

            permissions = Permission.objects.filter(codename__in=permissions_codenames)

            client_role.permissions.add(*permissions)