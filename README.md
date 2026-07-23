# 🎁 Invisible Friend - Sistema de Amigo Invisible Escalable

Una aplicación profesional y escalable para generar y enviar asignaciones de **Amigo Invisible** (Secret Santa) con validación de restricciones, manejo robusto de errores, logging centralizado y pruebas unitarias.

## 🌟 Características

✅ **Generación inteligente de asignaciones** - Algoritmo cíclico que forma un ciclo perfecto
✅ **Validación de restricciones** - Evita parejas prohibidas configurables
✅ **Envío de emails** - Integración con Gmail SMTP
✅ **Envío explícito** - Por defecto simula; solo `--enviar` abre conexión real
✅ **Configuración centralizada** - YAML + variables de entorno
✅ **Type hints completos** - Verificado con mypy
✅ **Logging extenso** - Rastreo de eventos y errores
✅ **Pruebas unitarias** - 73 tests, 97% de cobertura
✅ **Manejo robusto de errores** - Excepciones específicas
✅ **Arquitectura escalable** - Separación de responsabilidades

---

## 📁 Estructura del Proyecto

```
Pinvisiblefriend/
├── src/invisible_friend/        # Paquete principal (src-layout)
│   ├── __init__.py              # __version__ (leído de los metadatos)
│   ├── __main__.py              # CLI: InvisibleFriendApp + argparse
│   ├── config.py                # Gestión de configuración (YAML + .env)
│   ├── models.py                # Dataclasses (Persona, Asignacion, ConfigData)
│   ├── exceptions.py            # Excepciones personalizadas
│   ├── validators.py            # Validación de parejas
│   ├── services/
│   │   ├── secret_santa.py      # Lógica de generación de asignaciones
│   │   └── email_service.py     # Servicio de envío de emails
│   ├── utils/
│   │   ├── logger.py            # Logging centralizado
│   │   └── file_handler.py      # I/O de archivos JSON
│   └── templates/
│       └── email_template.py    # Templates de emails
├── config/
│   ├── settings.example.yaml    # Template de participantes y restricciones
│   └── settings.yaml            # PRIVADO: tus participantes reales
├── tests/                       # Suite de pytest (conftest + 8 módulos)
├── scripts/
│   └── demo.py                  # Script de demostración
├── .env                         # PRIVADO: credenciales de Gmail
├── .env.example                 # Template de variables de entorno
├── main.py                      # Lanzador desde la raíz
├── pyproject.toml               # Configuración del proyecto y dependencias
├── CHANGELOG.md                 # Historial de cambios (Keep a Changelog)
├── LICENSE                      # Licencia MIT
├── NOTICE.md                    # Atribuciones de terceros
└── README.md
```

> Los directorios `output/` y `logs/` se crean solos en la primera ejecución y
> no se versionan: contienen datos personales de los participantes.

---

## 🚀 Instalación Rápida

Requiere **Python 3.11 o superior**.

```bash
# 1. Crear y activar un entorno virtual
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\Activate.ps1

# 2. Instalar el proyecto (editable) y las herramientas de desarrollo
pip install -e ".[dev]"

# 3. Configurar credenciales (PRIVADO)
cp .env.example .env
# Editar .env con tus credenciales de Gmail

# 4. Configurar personas y restricciones (PRIVADO)
cp config/settings.example.yaml config/settings.yaml
# Editar config/settings.yaml con TUS personas y restricciones

# 5. Verificar que todo carga
python scripts/demo.py
```

> El proyecto usa **src-layout**, así que hay que instalarlo (`pip install -e .`)
> para que `import invisible_friend` funcione. Los tests no lo necesitan:
> `pythonpath` está configurado en `pyproject.toml`.

### 🔑 Variables de entorno (`.env`)

| Variable | Descripción |
|----------|-------------|
| `MAILSENDER` | Cuenta de Gmail desde la que se envían los emails |
| `PASSWORD` | **Contraseña de aplicación** de esa cuenta, no la contraseña normal |

Se generan en [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
(requiere verificación en dos pasos activada).

### ⚙️ Configuración (`config/settings.yaml`)

| Clave | Descripción | Por defecto |
|-------|-------------|-------------|
| `app.max_attempts` | Intentos máximos para encontrar un ciclo válido | `100` |
| `email.smtp_server` | Servidor SMTP | `smtp.gmail.com` |
| `email.smtp_port` | Puerto SMTP (SSL) | `465` |
| `personas` | Lista de `{nombre, email}` participantes | — |
| `restricciones` | Pares `[A, B]` que no pueden tocarse | `[]` |

Las restricciones son **bidireccionales**: `["Alice", "Bob"]` impide tanto que Alice
le regale a Bob como al revés.

### 🔐 Estructura de Privacidad

```
Repositorio Git
├── .env.example                ✅ Incluir en Git (template)
├── .env                        ❌ NO incluir (privado, en .gitignore)
├── config/
│   ├── settings.example.yaml   ✅ Incluir en Git (template)
│   └── settings.yaml           ❌ NO incluir (privado, en .gitignore)
├── output/                     ❌ NO incluir (asignaciones reales)
├── logs/                       ❌ NO incluir (emails en los logs)
├── .gitignore
└── ...
```

**Archivos privados (NO se versionan):**
- `.env` - Contiene tus credenciales de Gmail
- `config/settings.yaml` - Contiene nombres y emails reales
- `output/` - Las asignaciones generadas (destripan el sorteo)
- `logs/` - Los logs registran los emails de los participantes

**Templates públicos (SÍ se versionan):**
- `.env.example` - Estructura sin valores reales
- `config/settings.example.yaml` - Estructura sin datos sensibles

### ⚠️ Validación de Datos

- **Nombre**: Obligatorio, cadena no vacía
- **Email**: Obligatorio, debe ser un email válido (ej: persona@example.com)
- **Restricciones**: Pares de nombres que NO pueden ser amigos invisibles (mutuos)

---

## 💻 Uso

### Ejecución básica (modo seguro: simula los emails)
```bash
python main.py
```

Genera las asignaciones, las muestra por consola, las guarda en
`output/asignaciones.json` y **simula** el envío sin abrir ninguna conexión.

### Con envío real de emails
```bash
python main.py --enviar
```

### Opciones disponibles
```bash
python main.py --help
```

| Flag | Descripción | Por defecto |
|------|-------------|-------------|
| `--enviar` | Envía los emails de verdad | desactivado (simula) |
| `--config PATH` | Ruta al YAML de participantes | `config/settings.yaml` |
| `--output PATH` | Dónde guardar el JSON de asignaciones | `output/asignaciones.json` |
| `--version` | Muestra la versión | — |

### Formas equivalentes de ejecutarlo
```bash
python main.py --enviar             # lanzador desde la raíz
python -m invisible_friend --enviar # como módulo
invisible-friend --enviar           # console script (tras pip install)
```

### Uso programático
```python
from pathlib import Path
from invisible_friend.__main__ import InvisibleFriendApp

app = InvisibleFriendApp(Path("config/settings.yaml"))
asignaciones = app.generar_asignaciones()
app.mostrar_asignaciones(asignaciones)
app.guardar_asignaciones(asignaciones)
app.enviar_emails(asignaciones, simular=True)
```

---

## 🧪 Pruebas Unitarias

```bash
# Ejecutar todos los tests
pytest

# Con reporte de cobertura
pytest --cov=invisible_friend --cov-report=term-missing

# Tests específicos
pytest tests/test_validators.py -v
```

Ningún test abre un socket ni lee tu `.env` o tu `config/settings.yaml`: el SMTP
va parcheado y los datos son ficticios.

### Linting y tipos
```bash
ruff check .        # lint
ruff format .       # formateo
mypy src            # verificación de tipos
```

---

## 🏗️ Arquitectura de Componentes

| Módulo | Responsabilidad |
|--------|-----------------|
| **Config** | Cargar YAML, variables de entorno, validar configuración |
| **ParejaValidator** | Validar pares permitidos/prohibidos de forma bidireccional |
| **SecretSantaService** | Generar ciclos válidos de asignaciones |
| **EmailService** | Crear y enviar emails vía SMTP |
| **EmailTemplate** | Cuerpo del email en texto plano y HTML |
| **FileHandler** | Guardar/cargar datos en JSON |
| **LoggerConfig** | Sistema de logging centralizado (consola + archivo) |
| **InvisibleFriendApp** | Orquesta el flujo completo desde el CLI |

---

## 📊 Logging

Logs disponibles en:
- **Consola**: Nivel INFO y superior
- **Archivo**: `logs/invisible_friend.log`

---

## 🛡️ Manejo de Errores

Excepciones específicas para cada caso:

```python
from invisible_friend.exceptions import (
    ConfigError,           # Errores de configuración
    ValidationError,       # Errores de validación
    AssignmentError,       # Errores en asignaciones
    EmailError,            # Errores en envío de emails
)
```

Todas heredan de `InvisibleFriendError`, así que puedes capturarlas de golpe.

---

## ✨ Características Avanzadas

- ✅ Ciclo garantizado (cada persona regala una vez y recibe una vez)
- ✅ Validación bidireccional de restricciones
- ✅ Reintentos automáticos para generar asignaciones válidas
- ✅ Templates de emails personalizables
- ✅ Simulación de envío sin riesgo (comportamiento por defecto)
- ✅ Type hints completos (verificado con mypy)
- ✅ Cobertura de tests unitarios
- ✅ Manejo centralizado de configuración

---

## 📝 Licencia

Este proyecto está bajo licencia **MIT** - ver archivo [LICENSE](LICENSE) para detalles.

### Atribuciones

Este proyecto utiliza las siguientes librerías bajo licencia MIT:

- **PyYAML** - Parser YAML: https://pyyaml.org/
- **python-dotenv** - Carga de variables de entorno: https://github.com/theskumar/python-dotenv

Para más información sobre atribuciones, ver [NOTICE.md](NOTICE.md)

---
