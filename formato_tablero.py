# -*- coding: utf-8 -*-
"""
================================================================================
CLÍNICA DE ATE VITARTE S.A.C.
MÓDULO: formato_tablero.py - Motor de Renderizado Tabular y Alineación ANSI
================================================================================
Garantiza que todos los marcos, cuadros, tablas, carnets, recetas y comprobantes
tengan una alineación milimétrica en cualquier terminal (ancho estándar 78 cols),
calculando el ancho visual real y descartando secuencias de escape ANSI.
================================================================================
"""

import re

# Paleta cromática ANSI estándar (centralizada para todo el sistema)
C_RESET = "\033[0m"
C_BOLD = "\033[1m"
C_DIM = "\033[2m"
C_CYAN = "\033[1;96m"
C_GOLD = "\033[1;93m"
C_GREEN = "\033[1;92m"
C_MAGENTA = "\033[1;95m"
C_BLUE = "\033[1;94m"
C_RED = "\033[1;91m"
C_WHITE = "\033[1;97m"
C_GRAY = "\033[90m"
C_ORANGE = "\033[38;5;208m"
C_CORAL = "\033[38;5;209m"

# Fondos cromáticos de alto contraste para encabezados y badges
BG_HEADER = "\033[44;1;97m"
BG_ALERT = "\033[41;1;97m"
BG_SUCCESS = "\033[42;1;30m"
BG_ACTIVE = "\033[43;1;30m"
BG_TOTAL = "\033[42;1;30m"
BG_FASE1 = "\033[45;1;97m"
BG_FASE2 = "\033[46;1;30m"
BG_FASE3 = "\033[44;1;97m"
BG_FASE4 = "\033[43;1;30m"
BG_FASE5 = "\033[42;1;30m"
BG_FASE6 = "\033[41;1;97m"
BG_AUX = "\033[48;5;24;1;97m"

# Ancho interior estándar para tableros (ancho total en consola: 78 columnas)
ANCHO_TABLERO = 72


def ancho_visible(texto: str) -> int:
    """Calcula la longitud visible en consola eliminando secuencias de escape ANSI."""
    sin_ansi = re.sub(r'\033\[[0-9;]*[a-zA-Z]', '', str(texto))
    return len(sin_ansi)


def fila_doble(contenido: str = "", ancho: int = ANCHO_TABLERO, color: str = C_CYAN) -> str:
    """Retorna una fila con bordes dobles (║ ... ║) con ancho visual exacto."""
    v_len = ancho_visible(contenido)
    pad = max(0, ancho - v_len)
    return f"  {color}║{C_RESET} {contenido}{' ' * pad} {color}║{C_RESET}"


def fila_simple(contenido: str = "", ancho: int = ANCHO_TABLERO, color: str = C_GOLD) -> str:
    """Retorna una fila con bordes simples (│ ... │) con ancho visual exacto."""
    v_len = ancho_visible(contenido)
    pad = max(0, ancho - v_len)
    return f"  {color}│{C_RESET} {contenido}{' ' * pad} {color}│{C_RESET}"


def borde_sup_doble(ancho: int = ANCHO_TABLERO, color: str = C_CYAN) -> str:
    """Retorna el borde superior doble: ╔══════════╗"""
    return f"  {color}╔{'═' * (ancho + 2)}╗{C_RESET}"


def borde_inf_doble(ancho: int = ANCHO_TABLERO, color: str = C_CYAN) -> str:
    """Retorna el borde inferior doble: ╚══════════╝"""
    return f"  {color}╚{'═' * (ancho + 2)}╝{C_RESET}"


def borde_sep_doble(ancho: int = ANCHO_TABLERO, color: str = C_CYAN) -> str:
    """Retorna un separador horizontal doble: ╠══════════╣"""
    return f"  {color}╠{'═' * (ancho + 2)}╣{C_RESET}"


def borde_sup_simple(ancho: int = ANCHO_TABLERO, color: str = C_GOLD, titulo: str = "") -> str:
    """Retorna el borde superior simple con título opcional centrado: ┌── TITULO ──┐"""
    if titulo:
        t_len = ancho_visible(titulo)
        disponible = (ancho + 2) - t_len - 2
        izq = max(2, disponible // 2)
        der = max(2, disponible - izq)
        return f"  {color}┌{'─' * izq} {titulo} {'─' * der}┐{C_RESET}"
    return f"  {color}┌{'─' * (ancho + 2)}┐{C_RESET}"


def borde_inf_simple(ancho: int = ANCHO_TABLERO, color: str = C_GOLD) -> str:
    """Retorna el borde inferior simple: └──────────┘"""
    return f"  {color}└{'─' * (ancho + 2)}┘{C_RESET}"


def borde_sep_simple(ancho: int = ANCHO_TABLERO, color: str = C_GOLD) -> str:
    """Retorna un separador horizontal simple: ├──────────┤"""
    return f"  {color}├{'─' * (ancho + 2)}┤{C_RESET}"


def caja_titulo(titulo: str, color_borde: str = C_CYAN, bg_badge: str = BG_HEADER, ancho: int = ANCHO_TABLERO) -> str:
    """Renderiza una cabecera de sección en caja doble con badge cromático."""
    return "\n".join([
        "",
        borde_sup_doble(ancho, color_borde),
        fila_doble(f"  {bg_badge} {titulo} {C_RESET}", ancho, color_borde),
        borde_inf_doble(ancho, color_borde),
        ""
    ])


def truncar_texto(texto: str, max_len: int) -> str:
    """Trunca un texto agregando '...' si excede max_len."""
    texto = str(texto).strip()
    if len(texto) <= max_len:
        return texto
    return texto[:max(0, max_len - 3)] + "..."
