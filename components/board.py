"""Streamlit wrapper for the interactive, accessible ESP32 SVG board."""

from __future__ import annotations

from pathlib import Path

import streamlit.components.v1 as components

from data.board_definition import BOARD_COMPONENTS, board_pins


_COMPONENT_PATH = Path(__file__).with_name("board_component")
_interactive_board = components.declare_component(
    "spectra_esp32_board",
    path=str(_COMPONENT_PATH),
)


def render_board(
    *,
    selected: str,
    active_path: list[str],
    pin_states: dict[str, dict[str, str]],
    height: int = 424,
) -> str | None:
    """Render the board and return the ID clicked inside its SVG."""
    return _interactive_board(
        pins=board_pins(),
        components_data=list(BOARD_COMPONENTS.values()),
        selected=selected,
        active_path=active_path,
        pin_states=pin_states,
        height=height,
        default=selected,
        key="spectra_esp32_board",
    )
