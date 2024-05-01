from django.core.management.base import BaseCommand
from inventory.models import Role, Units

class Command(BaseCommand):
    help = 'Sembrar roles y unidades de medida en la base de datos'

    def handle(self, *args, **options):
        self.seed_roles()
        self.seed_units()

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