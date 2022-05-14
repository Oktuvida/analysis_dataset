class Connection:
    DATABASE = "colombianos_registrados_exterior"
    USER = "postgres"
    PASSWORD = None
    HOST = "127.0.0.1"
    PORT = "5432"

class Files:
    PATH = "data"
    CSV = PATH + "/colombianos_registrados_exterior.csv"

class Variables:
    class Sql:
        NULL_VALUE = "null"