"""Tests para la carga de configuración (YAML + variables de entorno)."""

from pathlib import Path

import pytest

from invisible_friend.config import Config
from invisible_friend.exceptions import ConfigError

YAML_MINIMO = """
app:
  max_attempts: 50

email:
  smtp_server: "smtp.example.com"
  smtp_port: 587

personas:
  - nombre: "Alice"
    email: "alice@example.com"
  - nombre: "Bob"
    email: "bob@example.com"

restricciones:
  - ["Alice", "Bob"]
"""


@pytest.fixture
def yaml_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """settings.yaml temporal, con el CWD aislado del .env real del repo."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("MAILSENDER", raising=False)
    monkeypatch.delenv("PASSWORD", raising=False)
    ruta = tmp_path / "settings.yaml"
    ruta.write_text(YAML_MINIMO, encoding="utf-8")
    return ruta


def test_carga_env_desde_la_raiz(yaml_path: Path, tmp_path: Path) -> None:
    """Encuentra el .env en la raíz del proyecto."""
    (tmp_path / ".env").write_text("MAILSENDER=raiz@example.com\n", encoding="utf-8")

    config = Config(yaml_path)

    assert config.email_sender == "raiz@example.com"


def test_ignora_un_env_en_config(yaml_path: Path, tmp_path: Path) -> None:
    """El .env vive solo en la raíz: un config/.env residual no se carga."""
    (tmp_path / "config").mkdir()
    (tmp_path / "config" / ".env").write_text("MAILSENDER=viejo@example.com\n", encoding="utf-8")

    config = Config(yaml_path)

    with pytest.raises(ConfigError, match="MAILSENDER"):
        _ = config.email_sender


def test_sin_env_no_falla(yaml_path: Path) -> None:
    """La ausencia de .env no rompe la carga: solo falta el secreto."""
    config = Config(yaml_path)

    assert len(config.personas) == 2
    with pytest.raises(ConfigError):
        _ = config.email_sender


def test_parsea_personas_y_restricciones(yaml_path: Path) -> None:
    """Lee la lista de participantes y los pares prohibidos del YAML."""
    config = Config(yaml_path)

    assert [p.nombre for p in config.personas] == ["Alice", "Bob"]
    assert config.restricciones == [["Alice", "Bob"]]


def test_lee_valores_de_app_y_email(yaml_path: Path) -> None:
    """Toma max_attempts y los datos SMTP del YAML."""
    config = Config(yaml_path)

    assert config.max_intentos == 50
    assert config.smtp_server == "smtp.example.com"
    assert config.smtp_port == 587


def test_aplica_defaults_si_faltan_secciones(yaml_path: Path, tmp_path: Path) -> None:
    """Un YAML sin app/email usa los valores por defecto."""
    ruta = tmp_path / "settings.yaml"
    ruta.write_text('personas:\n  - nombre: "Alice"\n    email: "alice@example.com"\n', "utf-8")

    config = Config(ruta)

    assert config.max_intentos == 100
    assert config.smtp_server == "smtp.gmail.com"
    assert config.smtp_port == 465


def test_archivo_inexistente_lanza_config_error(yaml_path: Path, tmp_path: Path) -> None:
    """Un settings.yaml que no existe falla de forma explícita."""
    with pytest.raises(ConfigError, match="no encontrado"):
        Config(tmp_path / "no_existe.yaml")


def test_yaml_malformado_lanza_config_error(yaml_path: Path) -> None:
    """Un YAML sintácticamente inválido se traduce a ConfigError."""
    yaml_path.write_text("personas: [\n  - roto", encoding="utf-8")

    with pytest.raises(ConfigError):
        Config(yaml_path)


def test_yaml_vacio_lanza_config_error(yaml_path: Path) -> None:
    """Un archivo de configuración vacío no es utilizable."""
    yaml_path.write_text("", encoding="utf-8")

    with pytest.raises(ConfigError, match="vacío"):
        Config(yaml_path)


def test_secretos_desde_entorno(yaml_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """MAILSENDER y PASSWORD se leen del entorno."""
    monkeypatch.setenv("MAILSENDER", "remitente@example.com")
    monkeypatch.setenv("PASSWORD", "app-password")

    config = Config(yaml_path)

    assert config.email_sender == "remitente@example.com"
    assert config.email_password == "app-password"


@pytest.mark.parametrize("variable", ["MAILSENDER", "PASSWORD"])
def test_secreto_ausente_lanza_config_error(yaml_path: Path, variable: str) -> None:
    """Un secreto sin configurar falla ruidosamente, no en silencio."""
    config = Config(yaml_path)

    with pytest.raises(ConfigError, match=variable):
        _ = config.email_sender if variable == "MAILSENDER" else config.email_password
