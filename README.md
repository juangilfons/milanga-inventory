## Instrucciones de configuración

1. Abrir terminal y ubicarse en el directorio donde quieran importar el proyecto.
   

2. Clonear repositorio de GitHub

```git clone https://github.com/juangilfons/milanga-inventory```

```cd milanga-inventory```


3. Crear y activar ambiente virtual (venv)

```python -m venv .venv```

MacOS/Linux: ```source venv/bin/activate```

Windows: ```venv\Scripts\activate```


4. instalar dependencias

```pip install -r requirements.txt```


5. realizar migraciones

```python manage.py migrate```


6. Correr servidor

```python manage.py runserver```

~

Al seguir estos pasos, el proyecto deberia estar configurado correctamente y debería estar levantado en localhost:8000.

En caso de estar usando MacOS, reemplazar los comandos 'python' con 'python3'
