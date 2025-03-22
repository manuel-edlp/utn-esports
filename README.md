## Liga Leyendas del Sur - UTN FRLP ESPORTS

### Descripción del Proyecto

Este proyecto, desarrollado con Django, es una plataforma web diseñada para gestionar las inscripciones al torneo, Liga Leyendas del Sur, un torneo de Esports organizado por la UTN FRLP. Permite a los participantes inscribirse al torneo y armar su equipo de competición. Y a los miembros coordinadores gestionar las inscripciones de los equipos.

### Tecnologías Utilizadas

* **Framework:** Django 5.1.2
* **Librerías:**
  * django-environ: Para gestionar las variables de entorno.
  * pillow: Para el procesamiento de imágenes.
  * filetype: Para analizar las imagenes y archivos comprimidos subidos

### Requisitos Previos

* **Python:** Asegúrate de tener instalado Python 3.x.
* **Virtualenv:** Recomendado para aislar las dependencias del proyecto.

### Instalación

1. **Clonar el repositorio:**

   ```bash
   git clone https://github.com/manuel-edlp/utn-esports
   ```

2. **Crear un entorno virtual:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # En Linux/macOS
   venv\Scripts\activate  # En Windows
   ```

3. **Instalar las dependencias:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar la base de datos:**
   * Crea una base de datos en tu sistema de gestión de bases de datos.
   * Configura las variables de entorno en un archivo `.env` dentro de la carpeta src(ejemplo):
   * Notas: En secret key elegir cualquier clave, y en la cadena de conexion de la bd poner la ip, puerto y hosts permitidos que vayas a usar.
  
    ```python
    # Ejemplo de archivo .env:
    
    SECRET_KEY=dw350344hfh5j4fk5kdksk324234dfsdf342976
    DEBUG=True
    DATABASE_NAME=
    DATABASE_USER=
    DATABASE_PASS=
    DATABASE_HOST=127.0.0.1
    DATABASE_PORT=3306
    ALLOWED_HOSTS=127.0.0.1,localhost
    EMAIL_ALIAS=
    EMAIL_USER=
    EMAIL_PASS=


    
    # El sistema usa sqlite en desarrollo y MariaDB en produccion
    # Para MariaDB se debe instalar
    #pip install mysql-connector-python

     DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': env('DATABASE_NAME'),
            'USER': env('DATABASE_USER'),
            'PASSWORD': env('DATABASE_PASS'),
            'HOST': env('DATABASE_HOST'),
            'PORT': env('DATABASE_PORT'),
            'OPTIONS': {
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
            },
        }
    }
    ```

5. **Ejecutar las migraciones:**
   
   Nota: asegurese de estar posicionado en la consola al mismo nivel del archivo manage.py siempre que ingrese un comando que haga uso de este (como los de a continuación).
   ```bash
   python manage.py migrate
   ```

7. **Iniciar el servidor de desarrollo:**

   ```bash
   python manage.py runserver
   ```

### Estructura del Proyecto

* **urls.py:** Define las URL del proyecto y redireccion a 'urls.py' de core.
* **core/urls.py:** Define las URL del proyecto, que necesitan al usuario autenticado.
* **core/urls_publics.py:** Define las URL del proyecto, que no necesitan de un usuario autenticado.
* **settings.py:** Configuraciones del proyecto.
* **wsgi.py:** Punto de entrada para servidores WSGI.
* **static/:** Archivos estáticos (CSS, JavaScript, imágenes).
* **templates/:** Plantillas Base HTML.
