<h1>
Análisis de un conjunto de datos usando diagramas relacionales y de entidad-relación, base de datos PostreSQL y Python
</h1>

<h1> 
Tabla de contenidos
</h1>

- [Conjunto de datos](#conjunto-de-datos)
  - [Variables](#variables)
  - [Diagramas](#diagramas)
    - [Entidad-Relación](#entidad-relación)
    - [Relacional](#relacional)
    - [Relacional normalizado](#relacional-normalizado)
  - [Inserción y manipulación de datos](#inserción-y-manipulación-de-datos)
- [Estructura del directorio](#estructura-del-directorio)
- [Ejecución](#ejecución)
  - [En host](#en-host)
    - [Requisitos](#requisitos)
    - [Preparación](#preparación)
    - [Configuración](#configuración)
    - [Pasos finales](#pasos-finales)
  - [En contenedor](#en-contenedor)
    - [Requisitos](#requisitos-1)
    - [Pasos](#pasos)

# Conjunto de datos 

Nos presentan un esquema general demográfico de una persona y cuántos colombianos emigrantes pertenecen a esta desde el año 2016 hasta el año 2022 de manera anónima[^1]. 

## Variables

En nuestro análisis acordamos los siguientes datos como variables de interés:

<div align="center">

|       Variable       | Descripción                                                                |
| :------------------: | :------------------------------------------------------------------------- |
|         Edad         | Edad actual dada en años.                                                  |
|   Especialización    | Carrera que desempeña.                                                     |
| Área de conocimiento | Campo en el cual pertenece la especialización.                             |
|   Nivel académico    | El nivel educativo alcanzado.                                              |
|  País de residencia  | País actual en el que vive.                                                |
| Oficina de registro  | Lugar en el cual llevó a cabo su registro <br> consular.                   |
|        Género        | Género en el cual está catalogado; <br> masculino, femenino o desconocido. |
|       Estatura       | Altura en centímetros.                                                     |
| Cantidad de personas | La cantidad de personas que coinciden <br> con la descripción demográfica. |

</div>

## Diagramas

### Entidad-Relación

<div align="center">

![Diagrama entidad-relación](/assets/images/ER.svg)

</div>

### Relacional

<div align="center">

![Diagrama relacional](/assets/images/R.svg)

</div>

### Relacional normalizado

<div align="center">

![Diagrama relacional normalizado](/assets/images/3FN.svg)

</div>

## Inserción y manipulación de datos

nos llevó a tener gran cantidad de identificadores no pertenecientes al conjunto de datos (lo cual implica hacerlo manualmente) que, sumado a la dimensión de los datos presentes en el [archivo CSV](/data/colombianos_registrados_exterior.csv.zip), consideramos más pertinente usar inserciones con Python usando hashmaps (diccionarios) y colas en lugar de usar el lector nativo que ofrece PostgreSQL ([copy](https://www.postgresql.org/docs/current/sql-copy.html)).

A su vez, consideramos idóneo comprimir el [archivo CSV](/data/colombianos_registrados_exterior.csv.zip) para optimizar el espacio ocupado en el repositorio.

# Estructura del directorio

En la carpeta [entregas](/entregas/) se tienen las entregas realizadas del proyecto en .pdf.

La carpeta [assets](/assets/) contiene todas las imágenes, archivos relacionados al diseño de la base datos (.sql, .csv) y los estilos o scripts que usará la página generada por Dash[^2].

La carpeta [src](/src) tiene todo nuestro código realizado en python. 

En esta última está la carpeta [modules](/src/modules/), la cual hace referencia a, como indica su nombre, los módulos de Python. Dado un lenguaje (por el momento CSV, SQL y HTML), el archivo [executors.py](/src/modules/executors.py) ejecuta las sentencias del lenguaje (si dispone de estas); el archivo [parsers.py](/src/modules/parsers.py) convierte los parámetros dados a una sentencia válida para el lenguaje; el archivo [readers.py](/src/modules/readers.py) lee un archivo con el formato del lenguaje y obtiene de este sentencias válidas en Python; el archivo [objects.py](/src/modules/objects.py) crea simulaciones de objetos propios del lenguaje, como lo serían las tablas tanto SQL como HTML; el archivo [utils.py](/src/modules/utils.py) que contiene funciones generales para todos los archivos, como inicializar las tablas propuestas en el archivo [objects.py](/src/modules/objects.py) o descomprimir archivos; el archivo [views.py] contiene todas las gráficas usadas en Dash[^2], dividos por análisis.

En el archivo [app.py](/src/app.py) está toda la aplicación Dash[^2] y en el archivo [cli_app.py](/src/cli_app.py) toda la aplicación desarrollada en el terminal de comandos, permitiendo la inserción de datos como la visualización de las tablas.

# Ejecución

Diseñamos dos maneras de poder hacerlo. Una es mediante la preparación total del sistema host; la otra es mediante el uso de un contenedor que aisle sólo lo necesario.

## En host

### Requisitos

- [`python3.10`](https://www.python.org/downloads/release/python-3100/)
- [`postgres`](https://www.postgresql.org/download/)
- [`psql`](https://www.postgresql.org/docs/current/app-psql.html)
- [`perl`](https://www.perl.org/get.html)

### Preparación

- Unix-Like

```bash
python3.10 -m venv env
source ./env/bin/activate
pip install -r src/requeriments.txt

user="postgres"
file="./assets/colombianos_registrados_exterior.sql"
psql -U $user -d $user -f $file

port="127.0.0.1"
file="./.env"
for host in "dash_host" "pg_host"
do
    perl -i -pe "s/(?<=${host}\s=\s)\S+/\"${port}\"/g" $file
done
```

- Windows
  
Aún no hemos implementado un script para este sistema operativo. Debes asegurarte de ejecutar el archivo [colombianos_registrados_exterior.sql](assets/colombianos_registrados_exterior.sql), el cual contiene la creación de la base de datos y las tablas.

### Configuración

En el archivo [.env](/.env) encontrarás variables de conexión a la base de datos y la aplicación de Dash[^2].

- Las variables que comienzan en pg_* son exclusivamente para la conexión con PostgreSQL. La única que __no deberías manipular es `pg_database`__
- Las variables con dash_* son para la conexión con la aplicación Dash[^2].
- La variable localhost es exclusivamente para el contenedor.

### Pasos finales

Lo único que resta es ejecutar el archivo [app.py](/src/app.py) o [cli_app.py](/src/cli_app.py).

## En contenedor

Únicamente debes asegurarte de cumplir con los requisitos. Al poner en ejecución el contenedor se ejecutará automáticamente el archivo [app.py](/src/app.py)

### Requisitos

- [`docker compose`](https://docs.docker.com/compose/)

### Pasos

```bash
docker compose up --build
```

Puedes ver constantemente el estado del contenedor con

```bash
docker logs dash_app
```

[^1]: [Colombianos registrados en el exterior](https://www.datos.gov.co/Estad-sticas-Nacionales/Colombianos-registrados-en-el-exterior/y399-rzwf)

[^2]: [Dash Ploty](https://dash.plotly.com/)