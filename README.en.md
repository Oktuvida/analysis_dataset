# Analysis of a dataset using relational and entity-relationship diagrams, PostreSQL database and Python

*Read this in other languages: [English](/README.en.md), [Español](/README.md)*.

The dataset used here is public and can be consulted at [this link](https://www.datos.gov.co/Estad-sticas-Nacionales/Colombianos-registrados-en-el-exterior/y399-rzwf).

## Description

In the dataset we are presented with a general demographic scheme of a person and how many colombian emigrants belong to this person. In our analysis we agreed on the following data as variables of interest:

<div align="center">

|        Variable        | Description                                                        |
| :--------------------: | :----------------------------------------------------------------- |
|          Age           | Current age given in years.                                        |
|     Specialization     | Career that the person performs.                                   |
|   Area of knowledge    | Field in which the specialization belongs.                         |
|     Academic level     | Educational level achieved.                                        |
|  Country of residence  | Current country where the person lives.                            |
| Office of registration | Place where the person carried out <br> his/her consular registration.  |
|         Gender         | Gender in which you are categorized; <br> male, female or unknown. |
|         Height         | Height in centimeters.                                             |
|   Number of persons    | The number of people who match <br>the demographic description.    |

</div>

Regarding the implementation, given the entity-relationship diagram:

<div align="center">

![entity-relationship diagram](/images/ER.svg)

</div>

Or its equivalent relational diagram:

<div align="center">

![relational diagram](/images/3FN.svg)

</div>

led us to have a large number of identifiers not belonging to the dataset (which implies doing it manually) which, added to the dimension of the data present in the [CSV file](/data/colombianos_registrados_exterior.csv.zip), we considered more pertinent to use Python insertions using hashmaps (dictionaries) and queues instead of using the native reader offered by PostgreSQL ([copy](https://www.postgresql.org/docs/current/sql-copy.html)).

At the same time, we consider ideal to compress the [CSV file](/data/colombianos_registrados_exterior.csv.zip) to optimize the space occupied in the repository.

## Directory structure

To begin with, there is the folder [entregas](/entregas/), which contains the project deliveries in .pdf format.

The [data](/data/) folder contains the database in .sql format and the data in .csv compressed in .zip format.

Then there is the folder [modules.py](/modules/), which refers to, as its name indicates, the Python modules. Given a language (for the moment CSV and SQL), first you have the file [executor.py](/modules/executor.py), which executes the language statements (if available); the file [parser.py](/modules/parser.py), a translator that converts the given parameters to a valid language statement; the file [reader.py](/modules/reader.py), which reads a file with the language format; and the file [object.py](/modules/object.py), which creates language objects, such as tables.

Finally we have the file [main.py](/main.py).

In this file we have a menu in which we can do two actions with respect to the database: insert the data from the CSV to this one or visualize the tuples of its tables.

In the main function, besides executing this menu, the CSV file is also decompressed in case it is not already there and an equivalent of our database tables are initialized in terms of Python code.

## Setup

### Requeriments

- [`python3.10`](https://www.python.org/downloads/release/python-3100/)
- [postgresql >= 13](https://www.postgresql.org/download/)

### Development environment

- Unix-Like:
```bash
# Adjusting python environment

env python3.10 -m venv env
source ./env/bin/activate
pip install -r requeriments.txt

# Creating database and tables
# It is assumed that no authentication is required for this
user="postgres"
file="./data/colombianos_registrados_exterior.sql"

psql -U $user -d $user -f $file
```
- Windows (You have to make sure python and psql are in your path):
```powershell
# Adjusting python environment
python -m venv env
.\env\Scripts\activate.bat
pip install -r requeriments.txt

# Creating database and tables
# It is assumed that no authentication is required for this
$user = "postgres"
$file = "./data/colombianos_registrados_exterior.sql"

psql -U $user -d $user -f $file
```

### Environment variables

They are present in the file [settings.py](/settings.py). The only ones you should modify are the connection ones.

```python
class Connection:
    DATABASE = "hi_mom" # The name of your database.
    USER = "n_word" # The user you will connect with
    PASSWORD = "123" # The password for that user
    HOST = "127.0.0.1" # The IP address
    PORT = "5432" # The port on which the PostgreSQL service is located
```
