from interfaz import *


if __name__ == "__main__":
    ruta_archivo_actual = os.path.abspath(__file__)
    dir_inicial = os.path.dirname(os.path.dirname(ruta_archivo_actual))
    interfaz_inicial(dir_inicial)