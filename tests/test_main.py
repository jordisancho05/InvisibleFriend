"""Tests del punto de entrada CLI.

Lo crítico aquí es que el envío real sea **opt-in**: la ejecución por defecto
nunca debe tocar la red.
"""

from pathlib import Path

import pytest

from invisible_friend.__main__ import InvisibleFriendApp, main, parse_args

YAML_MINIMO = """
personas:
  - nombre: "Alice"
    email: "alice@example.com"
  - nombre: "Bob"
    email: "bob@example.com"
  - nombre: "Charlie"
    email: "charlie@example.com"
"""


@pytest.fixture
def entorno(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Proyecto de mentira: settings.yaml propio y secretos de pega."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("MAILSENDER", "sender@example.com")
    monkeypatch.setenv("PASSWORD", "app-password")
    ruta = tmp_path / "settings.yaml"
    ruta.write_text(YAML_MINIMO, encoding="utf-8")
    return ruta


def test_por_defecto_simula(entorno: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Sin flags, los emails se simulan: simular=True."""
    llamadas: list[bool] = []
    monkeypatch.setattr(
        "invisible_friend.services.email_service.EmailService.enviar_asignaciones_masivas",
        lambda self, asignaciones, personas, simular=False: (llamadas.append(simular), (0, 0))[1],
    )

    app = InvisibleFriendApp(entorno)
    app.ejecutar_completo()

    assert llamadas == [True]


def test_flag_enviar_activa_el_envio(entorno: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Con enviar=True se pide un envío real: simular=False."""
    llamadas: list[bool] = []
    monkeypatch.setattr(
        "invisible_friend.services.email_service.EmailService.enviar_asignaciones_masivas",
        lambda self, asignaciones, personas, simular=False: (llamadas.append(simular), (3, 0))[1],
    )

    app = InvisibleFriendApp(entorno)
    app.ejecutar_completo(enviar=True)

    assert llamadas == [False]


def test_parse_args_por_defecto_no_envia() -> None:
    """El default de --enviar es False: hay que pedirlo explícitamente."""
    args = parse_args([])

    assert args.enviar is False
    assert args.config == Path("config/settings.yaml")
    assert args.output == Path("output/asignaciones.json")


def test_parse_args_acepta_los_flags() -> None:
    """--enviar, --config y --output se parsean como toca."""
    args = parse_args(["--enviar", "--config", "otro.yaml", "--output", "salida.json"])

    assert args.enviar is True
    assert args.config == Path("otro.yaml")
    assert args.output == Path("salida.json")


def test_main_usa_la_ruta_de_config_indicada(
    entorno: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """--config manda: la app se construye con ese YAML."""
    monkeypatch.setattr(
        "invisible_friend.services.email_service.EmailService.enviar_asignaciones_masivas",
        lambda self, asignaciones, personas, simular=False: (0, 0),
    )

    codigo = main(["--config", str(entorno), "--output", str(entorno.parent / "out.json")])

    assert codigo == 0
    assert (entorno.parent / "out.json").exists()


def test_main_devuelve_1_si_falla_la_config(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Un YAML inexistente termina con código de salida 1, sin traza cruda."""
    monkeypatch.chdir(tmp_path)

    assert main(["--config", str(tmp_path / "no_existe.yaml")]) == 1


def test_guarda_las_asignaciones_en_el_output(
    entorno: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """El JSON de asignaciones se escribe en la ruta pedida."""
    monkeypatch.setattr(
        "invisible_friend.services.email_service.EmailService.enviar_asignaciones_masivas",
        lambda self, asignaciones, personas, simular=False: (0, 0),
    )
    destino = entorno.parent / "resultado.json"

    app = InvisibleFriendApp(entorno)
    app.ejecutar_completo(output_path=destino)

    assert destino.exists()
