# Análisis de un conjunto de datos usando diagramas relacionales y de entidad-relación, base de datos PostreSQL y Python

*Lee esto en otros idiomas: [English](/README.en.md), [Español](/README.md)*.

El conjunto de datos aquí usado es público y puede puede ser consultado en el [presente enlace](https://www.datos.gov.co/Estad-sticas-Nacionales/Colombianos-registrados-en-el-exterior/y399-rzwf).

## Descripción 

En el conjunto de datos nos presentan un esquema general demográfico de una persona y cuántos colombianos emigrantes pertenecen a esta. En nuestro análisis acordamos los siguientes datos como variables de interés:

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

En lo que respecta a la implementación, dado el diagrama entidad-relación:

<div align="center">

![Diagrama entidad-relación](/images/ER.svg)

</div>


O su equivalente al diagrama relacional:

<div align="center">

![Diagrama relacional](/images/3FN.svg)

</div>

nos llevó a tener gran cantidad de identificadores no pertenecientes al conjunto de datos (lo cual implica hacerlo manualmente) que, sumado a la dimensión de los datos presentes en el [archivo CSV](/data/colombianos_registrados_exterior.csv.zip), consideramos más pertinente usar inserciones con Python usando hashmaps (diccionarios) y colas en lugar de usar el lector nativo que ofrece PostgreSQL ([copy](https://www.postgresql.org/docs/current/sql-copy.html)).

A su vez, consideramos idóneo comprimir el [archivo CSV](/data/colombianos_registrados_exterior.csv.zip) para optimizar el espacio ocupado en el repositorio.

## Estructura del directorio

Para empezar, está la carpeta [entregas](/entregas/). En esta se tienen las entregas realizadas del proyecto en .pdf.

La carpeta [data](/data/) contiene la base de datos en formato .sql y los datos .csv comprimidos en formato .zip.

Después se tiene la carpeta [modules.py](/modules/), que hace referencia a, como indica su nombre, los modulos de Python. Dado un lenguaje (por el momento CSV y SQL), en primer lugar se tiene el archivo [executor.py](/modules/executor.py), que ejecuta las sentencias del lenguaje (si dispone de estas); el archivo [parser.py](/modules/parser.py), un traductor que convierte los parámetros dados a una sentencia válida para el lenguaje; el archivo [reader.py](/modules/reader.py), que lee un archivo con el formato del lenguaje; y el archivo [object.py](/modules/object.py), que crea objetos del lenguaje, como lo serían las tablas.

Finalmente tenemos el archivo [main.py](/main.py).

En este archivo se tiene un menú en el cual se pueden hacer dos acciones con respecto a la base de datos: insertar los datos del CSV a esta o visualizar las tuplas de sus tablas.

En la función main además de ejecutar este menu también se descomprime el archivo CSV en caso de no estarlo y se inicializan un equivalente de nuestras tablas de la base de datos en términos de código Python.

## Configuración

### Requisitos

- [`python3.10`](https://www.python.org/downloads/release/python-3100/)
- [postgresql >= 13](https://www.postgresql.org/download/)

### Entorno de desarrollo

- Unix-Like:
```bash
# Ajustando el entorno de python
env python3.10 -m venv env
source ./env/bin/activate
pip install -r requeriments.txt

# Creando base de datos y tablas
# Se asume que no se requiere autentificación para ello
user="postgres"
file="./data/colombianos_registrados_exterior.sql"

psql -U $user -d $user -f $file
```
- Windows (Tienes que asegurarte de que python y psql estén en tu path):
```powershell
# Ajustando el entorno de python
python -m venv env
.\env\Scripts\activate.bat
pip install -r requeriments.txt

# Creando base de datos y tablas
# Se asume que no se requiere autentificación para ello
$user = "postgres"
$file = "./data/colombianos_registrados_exterior.sql"
psql -U $user -d $user -f $file
```
### Variables de entorno

Están presentes en el archivo [settings.py](/settings.py). Las únicas que deberías modificar son las de conexión.

```python
class Connection:
    DATABASE = "hi_mom" # El nombre de tu base de datos
    USER = "n_word" # El usuario con el te conectarás
    PASSWORD = "123" # La contraseña de ese usuario
    HOST = "127.0.0.1" # La dirección IP
    PORT = "5432" # El puerto en el cual se encuentra el servicio PostgreSQL
```
