## Instrucciones de configuración

1. Clonear repositorio de GitHub

```git clone https://github.com/juangilfons/milanga-inventory```

```cd milanga-inventory```


2. Crear y activar ambiente virtual (venv)

```python -m venv .venv```

```source .venv/bin/activate```


3. instalar dependencias

```pip install -r requirements.txt```


4. realizar migraciones

```python manage.py migrate```


5. Correr servidor

```python manage.py runserver```

~

Al seguir estos pasos, el proyecto deberia estar configurado correctamente y debería estar levantado el en localhost:8000.

En caso de estar usando MacOS, reemplazar los comandos 'python' con 'python3'
