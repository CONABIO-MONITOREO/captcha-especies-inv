# captcha-especies-inv

## Descripción

Este repo tiene como proposito el desarrollo de una aplicación para el etiquedo simultaneo de especies invasoras en las imagenes de SIPECAM.

## Estado

Lo que se ha desarrollado hasta el momento son las siguientes características

1. La aplicación obtiene las imagenes del servidor de imagenes [http://cosmos-validacion-integridad-sipecam.conabio.gob.mx:777/], el cual disponibiliza las imagenes de las nuevas entregas en el servidor SIPECAM.
2. La aplicación descarga las imagenes y corta las detecciones guardandolas en el directorio local `/media/cropped_images/` para ser mostradas en la aplicaicón.
3. Las anotaciones se guardan en el core de Solr del cliente de anotación con colección SIPECAM.
4. Es posible parametrizar la especie de la que se va a etiquetar, el modelo `ParametrizedSpecies` es quién guarda y obtiene la especie.

## Base de datos

Se debe incluir un archivo `.env` en el que se especifiquen las credenciales de la base de datos

- DBHOST
- DBNAME
- DBPORT
- DBUSER
- DBPASS

## Dependencias 

La aplicación está desarrollada principalmente con dos herramientas

* Python >= 3.11
* PostgreSQL

Las dependencias de Python, como usualmente se hace están en el archivo `requirements.txt` y se pueden instalar con pip

```
    $> pip install -r requirements.txt
```

## Correr

La aplicación está desarrollada en Django. Antes de correr la aplicación deben correrse las migraciones usando el comando

```
    $> python manage.py migrate
```

Para correr en modo desarrollo hay que corrrer el siguiente comando

```
    $> python manage.py runserver
```

## APIs externas

* Esta aplicación depende del repositorio de gestión de usuarios que se desarrollo para el cliente de anotación [https://github.com/CONABIO-MONITOREO/annotation-client-users-management] y desplegada en [http://sipecamdata.conabio.gob.mx:888].
* La aplicación se conecta a la instancia de Solr del ambiente de desarrollo [http://sipecamdata.conabio.gob.mx:888] para obtener las rutas de las imagenes y hacer el guardado de las anotaciones.

## ToDo

Agregar a las variables de ambiente las URLs externas
- url_base_solr
- url_base_img
- url_user_management

