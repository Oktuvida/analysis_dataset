# Analysis of a dataset using relational and entity-relationship diagrams, PostreSQL database and Python.

*Read this in other languages: [English](README.md), [Español](README.es.md)*.

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

## Setup.

### Requeriments

- [`python3.10`](https://www.python.org/downloads/release/python-3100/)
- [postgresql >= 13](https://www.postgresql.org/download/)

### Development environment

we use [`venv`](https://docs.python.org/3/library/venv.html). If you also want to use the same tool, you can open a command terminal and type the following:
- Unix-Like:
```bash
# Adjusting python environment
python -m venv env
source ./env/bin/activate
pip install -r requeriments.txt

# Creating database and tables

# It is assumed that no authentication is required for this
# As well as that the current user is in the role "postgres"
db_name="colombianos_registrados_exterior"
user="postgres"
file="./data/${db_name}.sql"

psql -lqt | awk '{print $1}' | grep -qw $db_name 
    || createdb -O $user $db_name
psql -d $db_name -f $file
```
- Windows (You have to make sure python is in your [path](https://docs.python.org/3/using/windows.html)):
```powershell
# Adjusting python environment
python -m venv env
.\env\Scripts\activate
pip install -r requeriments.txt
```

### Environment variables

They are present in the file [settings.py](settings.py). The only ones you should modify are the connection ones.

```python
class Connection:
    DATABASE = "hi_mom" # The name of your database.
    USER = "n_word" # The user you will connect with
    PASSWORD = "123" # The password for that user
    HOST = "127.0.0.1" # The IP address
    PORT = "5432" # The port on which the PostgreSQL service is located
```
