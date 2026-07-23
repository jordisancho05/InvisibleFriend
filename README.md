# 🎁 Invisible Friend - Sistema de Amigo Invisible Escalable

Una aplicación profesional y escalable para generar y enviar asignaciones de **Amigo Invisible** (Secret Santa) con validación de restricciones, manejo robusto de errores, logging centralizado y pruebas unitarias.

## 🌟 Características

✅ **Generación inteligente de asignaciones** - Algoritmo cíclico que forma un ciclo perfecto  
✅ **Validación de restricciones** - Evita parejas prohibidas configurables  
✅ **Envío de emails** - Integración con Gmail SMTP  
✅ **Configuración centralizada** - YAML + variables de entorno  
✅ **Type hints completos** - Compatible con mypy  
✅ **Logging extenso** - Rastreo de eventos y errores  
✅ **Pruebas unitarias** - Cobertura completa  
✅ **Manejo robusto de errores** - Excepciones específicas  
✅ **Arquitectura escalable** - Separación de responsabilidades  

---

## 📁 Estructura del Proyecto

```
Pinvisiblefriend/
├── src/invisible_friend/        # Paquete principal (src-layout)
│   ├── config.py                # Gestión de configuración (YAML + .env)
│   ├── models.py                # Dataclasses (Persona, Asignacion)
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
│   ├── .env.example             # Template de variables de entorno
│   └── settings.example.yaml    # Template de participantes y restricciones
├── tests/
│   ├── test_validators.py       # Tests de validadores
│   ├── test_secret_santa.py     # Tests de lógica principal
│   └── test_email_service.py    # Tests de emails
├── main.py                      # Punto de entrada principal
├── examples.py                  # Script de demostración
├── pyproject.toml               # Configuración del proyecto y dependencias
├── LICENSE                      # Licencia MIT
├── NOTICE.md                    # Atribuciones de terceros
└── README.md
```

> Los directorios `output/` y `logs/` se crean solos en la primera ejecución y
> no se versionan: contienen datos personales de los participantes.

---

## 🚀 Instalación Rápida

```bash
# 1. Crear y activar un entorno virtual
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

# 2. Instalar el proyecto (editable) y las herramientas de desarrollo
pip install -e ".[dev]"

# 3. Configurar variables de entorno (PRIVADO)
cp config/.env.example config/.env
# Editar config/.env con tus credenciales de Gmail

# 4. Configurar personas y restricciones (PRIVADO)
cp config/settings.example.yaml config/settings.yaml
# Editar config/settings.yaml con TUS personas y restricciones

# 5. Verificar configuración
python examples.py
```

> El proyecto usa **src-layout**, así que hay que instalarlo (`pip install -e .`)
> para que `import invisible_friend` funcione. Los tests no lo necesitan:
> `pythonpath` está configurado en `pyproject.toml`.

### 🔐 Estructura de Privacidad

```
Repositorio Git
├── config/
│   ├── .env.example            ✅ Incluir en Git (template)
│   ├── .env                    ❌ NO incluir (privado, en .gitignore)
│   ├── settings.example.yaml   ✅ Incluir en Git (template)
│   └── settings.yaml           ❌ NO incluir (privado, en .gitignore)
├── output/                     ❌ NO incluir (asignaciones reales)
├── logs/                       ❌ NO incluir (emails en los logs)
├── .gitignore
└── ...
```

**Archivos privados (NO se versionan):**
- `config/.env` - Contiene tus credenciales de Gmail
- `config/settings.yaml` - Contiene nombres y emails reales
- `output/` - Las asignaciones generadas (destripan el sorteo)
- `logs/` - Los logs registran los emails de los participantes

**Templates públicos (SÍ se versionan):**
- `config/.env.example` - Estructura sin valores reales
- `config/settings.example.yaml` - Estructura sin datos sensibles

### ⚠️ Validación de Datos

- **Nombre**: Obligatorio, cadena no vacía
- **Email**: Obligatorio, debe ser un email válido (ej: persona@example.com)
- **Restricciones**: Pares de nombres que NO pueden ser amigos invisibles (mutuos)

---

## 💻 Uso

### Ejecución básica (modo seguro con simulación de emails)
```bash
python main.py
```

### Con envío real de emails
Editar `main.py` y cambiar:
```python
app.ejecutar_completo(enviar=True)
```

### Uso programático
```python
from main import InvisibleFriendApp

app = InvisibleFriendApp()
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
pytest --cov=invisible_friend --cov-report=html

# Tests específicos
pytest tests/test_validators.py -v
```

---

## 🏗️ Arquitectura de Componentes

| Módulo | Responsabilidad |
|--------|-----------------|
| **Config** | Cargar YAML, variables de entorno, validar configuración |
| **ParejaValidator** | Validar pares permitidos/prohibidos de forma bidireccional |
| **SecretSantaService** | Generar ciclos válidos de asignaciones |
| **EmailService** | Crear y enviar emails vía SMTP |
| **FileHandler** | Guardar/cargar datos en JSON |
| **LoggerConfig** | Sistema de logging centralizado (consola + archivo) |

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

---

## ✨ Características Avanzadas

- ✅ Ciclo garantizado (cada persona recibe exactamente una asignación)
- ✅ Validación bidireccional de restricciones
- ✅ Reintentos automáticos para generar asignaciones válidas
- ✅ Templates de emails personalizables
- ✅ Simulación de envío sin riesgo
- ✅ Type hints completos (compatible con mypy)
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

## 🎉 ¡Que disfrutes tu Amigo Invisible!