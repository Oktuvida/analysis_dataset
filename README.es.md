# Análisis de un conjunto de datos usando diagramas relacionales y de entidad-relación, base de datos PostreSQL y Python.

*Lee esto en otros idiomas: [English](/README.md), [Español](/README.es.md)*.

El conjunto de datos aquí usado es público y puede puede ser consultado en el [presente enlace](https://www.datos.gov.co/Estad-sticas-Nacionales/Colombianos-registrados-en-el-exterior/y399-rzwf).

## Descripción 

En el conjunto de datos nos presentan un esquema general demográfico de una persona y cuántos colombianos emigrantes pertenecen a esta. En nuestro análisis acordamos los siguientes datos como variables de interés:

<center>

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

</center>

En lo que respecta a la implementación, dado el diagrama relacional:

![Diagrama relacional](/images/3FN.svg)

la gran cantidad de identificadores no pertenecientes al dataset (lo cual implica hacerlo manualmente) sumado a la dimensión de los datos presentes en el [archivo CSV](/data/colombianos_registrados_exterior.csv.zip), consideramos más pertinente usar inserciones con Python usando hashmaps (diccionarios) y colas en lugar de usar el lector nativo que ofrece PostgreSQL ([copy](https://www.postgresql.org/docs/current/sql-copy.html)).

A su vez, consideramos idóneo comprimir el [archivo CSV](/data/colombianos_registrados_exterior.csv.zip) para optimizar el espacio ocupado en el repositorio.

## Estructura del directorio

Para empezar, está la carpeta [entregas](/entregas/), en esta se tienen las entregas realizadas del proyecto en .pdf.

La carpeta [data](/data/) contiene la base de datos en formato sql y los datos en .csv comprimidos.

Después se tiene la carpeta [modules](/modules/), que hace referencia a, como indica su nombre, los modulos de Python. Dado un lenguaje (por el momento CSV y SQL), en primer lugar se tiene el [executor](/modules/executor.py), que ejecuta las sentencias del lenguaje (si dispone de estas); el [parser](/modules/parser.py), un traductor que convierte los parámetros dados a una sentencia válida para el lenguaje; y el [reader](/modules/reader.py), que lee un archivo con el formato del lenguaje.

Finalmente tenemos el [main](/main.py).

Alli está el table_viewer para poder visualizar los datos. Este requiere el nombre de la tabla; los filtros, como por ejemplo los limitadores, agrupadores y ordenadores; las columnas que se quieren mostrar, siendo una lista de strings o integers, o un slice sobre las columnas que se desea mostrar; y finalmente la opcion de mostrar el nombre de las columnas.

Por otro lado, se tiene la función data_insertion donde se inicializa el ejecutor csv; los datos invalidos; las columnas, el valor inicial de su id como el registro de las llaves primarias ya ingresadas de cada tabla; y una única consulta que servirá como cola a todos los inserts necesarios, separados por punto y coma. Lo único que resta es iterar las filas del CSV, siendo el orden de ejecución de las tablas según cuantas relaciones tenga esta (de menor a mayor). En el momento que encuentre que alguna tupla aún no ha sido agregada a la tabla, es decir, que aún no este en registrador de la tabla, será agregada a la cola de la query.

Finalmente en la función main únicamente se verifica que el archivo CSV esté descomprimido para inmediatamente después ejecutar la función data_insertion.

## Configuración.

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
