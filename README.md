###Paso 1:
##Crear un entorno virtual
#código: python -m venv env
#Activar el entorno entrando a la carpeta y escribir  scripts\activate
###Paso 2:
##Entrar a la carpeta api
##Correr el archivo de requerimientos
# código: pip install -r requirements.txt
###Paso 3:
#Activar la base de datos
#Entrar y crear la base de datos (inventory)
###Paso 4:
##Correr migraciones
#código:python manage.py migrate
###Paso 5:
##Correr permisos
# código:python manage.py seeders
###Paso 6:
##Crear superusuario
# código: python manage.py createsuperuser
##Llenar los campos
###Paso 7: 
##Activar Servidor 
# código: python manage.py runserver
###Paso 8:
##Importar la collection en postman
###Paso 9:
##Iniciar Sesión con el superusuario o registrarse
##Utilizar el csrf_token que da al iniciar sesión junto al mensaje
###Paso 10: 




