# Analysis of a dataset using relational and entity-relationship diagrams, PostreSQL database and Python.

*Read this in other languages: [English](/README.md), [Español](/README.es.md)*.

The dataset used here is public and can be consulted at [this link](https://www.datos.gov.co/Estad-sticas-Nacionales/Colombianos-registrados-en-el-exterior/y399-rzwf).

## Description

In the dataset we are presented with a general demographic scheme of a person and how many colombian emigrants belong to this person. In our analysis we agreed on the following data as variables of interest:

<center>

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

</center>

Regarding the implementation, given the relational diagram:

![relational diagram](/images/3FN.svg)

the large amount of identifiers not belonging to the dataset (which implies doing it manually) added to the dimension of the data present in the [CSV file](/data/colombianos_registrados_exterior.csv.zip), we consider more pertinent to use insertions with Python using hashmaps (dictionaries) and queues instead of using the native reader offered by PostgreSQL ([copy](https://www.postgresql.org/docs/current/sql-copy.html)).

At the same time, we consider ideal to compress the [CSV file](/data/colombianos_registrados_exterior.csv.zip) to optimize the space occupied in the repository.

# Directory structure

To begin with, there is the folder [entregas](/entregas/), which contains the project deliveries in .pdf format.

The [data](/data/) folder contains the database in sql format and the data in compressed .csv format.

Then there is the [modules](/modules/) folder, which refers to, as its name indicates, the Python modules. Given a language (for the moment CSV and SQL), first we have the [executor](/modules/executor.py), which executes the language statements (if available); the [parser](/modules/parser.py), a translator that converts the given parameters to a valid statement for the language; and the [reader](/modules/reader.py), which reads a file with the language format.

Finally we have the [main](/main.py).

There is the table_viewer to be able to visualize the data. This requires the name of the table; the filters, such as limiters, groupers and sorters; the columns to be displayed, being a list of strings or integers, or a slice over the columns to be displayed; and finally the option to display the name of the columns.

On the other hand, we have the function data_insertion where the csv executor is initialized; the invalid data; the columns, the initial value of its id as the record of the primary keys already entered for each table; and a single query that will serve as a queue to all the necessary inserts, separated by semicolon. The only thing left is to iterate the rows of the CSV, being the order of execution of the tables according to how many relations it has (from smallest to largest). When it finds that a tuple has not yet been added to the table, that is to say, that it is not yet in the table recorder, it will be added to the query queue.

Finally, the main function only verifies that the CSV file is decompressed and then immediately executes the data_insertion function.


## Setup.

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
