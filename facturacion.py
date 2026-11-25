# -*- coding: utf-8 -*-
"""
================================================================================
CLÍNICA DE ATE VITARTE S.A.C. - SISTEMA DE CITAS MÉDICAS Y FACTURACIÓN
MÓDULO: facturacion.py (Semana 16 - Sobrecarga y Facturación Electrónica en Consola)
CURSO: LENGUAJES DE PROGRAMACIÓN - UTP (FACULTAD DE INGENIERÍA)
EQUIPO 2 - LÍDER: JULIBETH ANTONELA JAIMES DAZA
================================================================================
DEMOSTRACIÓN TÉCNICA DE SOBRECARGA DE MÉTODOS EN PYTHON:
1. Sobrecarga por número de parámetros (defaults, booleanos opcionales y kwargs).
2. Sobrecarga por tipo de dato mediante el decorador canónico @singledispatchmethod:
   - int / float: Pago en efectivo con cálculo de vuelto y desglose de denominaciones.
   - str: Pasarelas digitales y transferencias (Yape, Plin, Tunki, CCI).
   - dict: Procesamiento de POS para tarjetas de débito/crédito con cuotas.
   - list / tuple: Liquidación combinada / pago mixto multicanal.
================================================================================
"""

import zlib
from datetime import datetime
from functools import singledispatchmethod
from formato_tablero import (
    C_RESET, C_CYAN, C_GOLD, C_GREEN, C_RED, C_WHITE, C_GRAY,
    BG_TOTAL, BG_HEADER, ANCHO_TABLERO, fila_doble, borde_sup_doble,
    borde_inf_doble, borde_sep_doble, truncar_texto
)

# Tasa tributaria oficial SUNAT en el Perú
TASA_IGV = 0.18


def generar_correlativo_sunat(codigo_cita: str, tipo_doc: str = "BOLETA") -> str:
    """Genera un número correlativo determinista de comprobante (B002/F002)."""
    prefijo = "B002" if tipo_doc.upper() == "BOLETA" else "F002"
    num = zlib.crc32(str(codigo_cita).encode("utf-8")) % 9000 + 1000
    return f"{prefijo}-{num}"


def calcular_liquidacion(subtotal: float) -> tuple:
    """
    Función pura que retorna una TUPLA inmutable: (base_imponible, igv, total).
    Demuestra el uso de Tuplas para encapsular retornos fiscales íntegros.
    """
    subtotal = float(subtotal)
    igv = round(subtotal * TASA_IGV, 2)
    total = round(subtotal + igv, 2)
    return (subtotal, igv, total)


def generar_qr_ascii(correlativo: str, total_monto: float, codigo_cita: str = "") -> list:
    """Genera una matriz representativa de código QR en arte ASCII/bloques Unicode para consola."""
    hash_corto = f"{zlib.crc32(f'{correlativo}{total_monto:.2f}{codigo_cita}'.encode('utf-8')):08x}"
    filas = [
        "  \033[1;97m█▀▀▀▀▀█ ▄▄ █ █ █▀▀▀▀▀█\033[0m   \033[90m[CÓDIGO QR SUNAT]\033[0m",
        "  \033[1;97m█ ███ █ █▄▀█▀█ █ ███ █\033[0m   \033[90mDocumento Electrónico\033[0m",
        f"  \033[1;97m█ ▀▀▀ █ █ ▀▄ █ █ ▀▀▀ █\033[0m   \033[90mSerie: {correlativo}\033[0m",
        f"  \033[1;97m▀▀▀▀▀▀▀ ▀▄█ ▀▄ ▀▀▀▀▀▀▀\033[0m   \033[90mImporte: S/ {total_monto:.2f}\033[0m",
        f"  \033[1;97m██▄▀▄▄▀ ▀▀██ █ ▄▀█ ▄▄█\033[0m   \033[90mHash: {hash_corto}e3b0c4\033[0m",
        "  \033[1;97m█▀▀▀▀▀█ ▄█▄▀██ █ ▀ █▀█\033[0m   \033[90mAutorizado por OSE SUNAT\033[0m",
        "  \033[1;97m█ ███ █ █▄▀ █▄ █▄█ █▀█\033[0m   \033[90mConsulta en clinica-atevitarte.pe\033[0m",
        "  \033[1;97m█ ▀▀▀ █ ▀ █▀ █ █ ▄ █▄█\033[0m",
        "  \033[1;97m▀▀▀▀▀▀▀ ▀▀  ▀▀ ▀   ▀▀▀\033[0m"
    ]
    return filas


class FacturadorClinico:
    """
    Módulo de Facturación y Liquidación de Honorarios Médicos.
    Demuestra las dos técnicas canónicas de SOBRECARGA DE MÉTODOS en Python:
    1. Sobrecarga por número y tipos de parámetros en firmas flexibles.
    2. Sobrecarga por tipo de dato con @singledispatchmethod.
    """

    def __init__(self):
        self.ultimo_pago_aprobado = False

    # --------------------------------------------------------------------------
    # TÉCNICA 1: Sobrecarga por firma de parámetros (Descuentos y Convenios)
    # --------------------------------------------------------------------------
    def calcular_presupuesto(self, tarifa_base: float, descuento_campania: float = 0.0,
                             aplica_convenio_utp: bool = False, incluye_medicamentos: bool = False,
                             kit_laboratorio: bool = False) -> float:
        """
        Simula sobrecarga de métodos en Python para cotizaciones clínicas:
        - calcular_presupuesto(tarifa_base)
        - calcular_presupuesto(tarifa_base, descuento_campania)
        - calcular_presupuesto(tarifa_base, descuento_campania, aplica_convenio_utp=True)
        - calcular_presupuesto(tarifa_base, descuento, convenio, incluye_medicamentos=True)
        - calcular_presupuesto(tarifa_base, descuento, convenio, med, kit_laboratorio=True)
        """
        subtotal = float(tarifa_base) - float(descuento_campania)
        if aplica_convenio_utp:
            subtotal *= 0.85  # 15% descuento institucional comunidad UTP
        if incluye_medicamentos:
            subtotal += 35.0  # Kit farmacológico ambulatorio
        if kit_laboratorio:
            subtotal += 45.0  # Insumos de bioseguridad y reactivos analíticos
        return round(max(0.0, subtotal), 2)

    # --------------------------------------------------------------------------
    # TÉCNICA 2: Sobrecarga por tipo de dato con @singledispatchmethod
    # --------------------------------------------------------------------------
    @singledispatchmethod
    def liquidar_comprobante(self, forma_pago, cita):
        """Método base sobrecargado: delega la liquidación según el tipo de datos."""
        raise NotImplementedError(f"Forma de pago no admitida por la tesorería de la clínica: {type(forma_pago)}")

    @liquidar_comprobante.register(float)
    @liquidar_comprobante.register(int)
    def _(self, efectivo_recibido: float, cita) -> str:
        """Sobrecarga 1: Pago en Ventanilla (Efectivo con Vuelto y Desglose)."""
        _, _, total_a_pagar = calcular_liquidacion(cita.calcular_tarifa_final())
        efectivo_recibido = float(efectivo_recibido)
        vuelto = round(efectivo_recibido - total_a_pagar, 2)

        if vuelto < 0:
            self.ultimo_pago_aprobado = False
            return (f"[VENTANILLA - PAGO INCOMPLETO] Cita {cita.codigo} | Total: S/ {total_a_pagar:.2f} | "
                    f"Recibido: S/ {efectivo_recibido:.2f} | Saldo pendiente: S/ {abs(vuelto):.2f}")

        self.ultimo_pago_aprobado = True
        # Desglose de billetes y monedas del vuelto en consola
        desglose = []
        resto = int(vuelto)
        for billete in (100, 50, 20, 10):
            cant = resto // billete
            if cant > 0:
                desglose.append(f"{cant}x S/{billete}")
                resto %= billete
        centavos = round(vuelto - int(vuelto), 2)
        if centavos > 0:
            desglose.append(f"S/ {resto + centavos:.2f} en monedas")
        elif resto > 0:
            desglose.append(f"{resto}x S/1 moneda")

        detalle_vuelto = f" (Desglose: {', '.join(desglose)})" if desglose else " (Exacto, sin cambio)"

        return (f"[VENTANILLA - EFECTIVO] Cita {cita.codigo} | Total Facturado: S/ {total_a_pagar:.2f} | "
                f"Recibido: S/ {efectivo_recibido:.2f} | Vuelto: S/ {vuelto:.2f}{detalle_vuelto}")

    @liquidar_comprobante.register(str)
    def _(self, codigo_digital: str, cita) -> str:
        """Sobrecarga 2: Pasarelas Digitales (Yape, Plin, Transferencia Bancaria CCI)."""
        _, _, total_a_pagar = calcular_liquidacion(cita.calcular_tarifa_final())
        token = codigo_digital.strip()
        if not token:
            self.ultimo_pago_aprobado = False
            return f"[BILLETERA DIGITAL - ERROR] Token de operación vacío para Cita {cita.codigo}."
        self.ultimo_pago_aprobado = True
        pasarela = "YAPE" if "YAPE" in token.upper() else ("PLIN" if "PLIN" in token.upper() else "TRANSFERENCIA_CCI")
        return (f"[BILLETERA DIGITAL - {pasarela}] Cita {cita.codigo} | Total: S/ {total_a_pagar:.2f} | "
                f"Operación Confirmada con Token: '{token}' | Aprobación OSE en línea")

    @liquidar_comprobante.register(dict)
    def _(self, datos_tarjeta: dict, cita) -> str:
        """Sobrecarga 3: Terminal POS Bancario (Tarjeta Crédito/Débito con cuotas)."""
        _, _, total_a_pagar = calcular_liquidacion(cita.calcular_tarifa_final())
        titular = datos_tarjeta.get("titular", cita.paciente.nombre_completo)
        banco = datos_tarjeta.get("banco", "BCP").upper()
        tipo_tarjeta = datos_tarjeta.get("tipo", "DÉBITO").upper()
        cuotas = max(1, int(datos_tarjeta.get("cuotas", 1)))
        cod_aut = zlib.crc32(cita.codigo.encode("utf-8")) % 899999 + 100000

        if cuotas > 1:
            valor_cuota = round(total_a_pagar / cuotas, 2)
            detalle_cuotas = f"en {cuotas} cuotas de S/ {valor_cuota:.2f}"
        else:
            detalle_cuotas = "al contado (01 cuota sin interés)"

        self.ultimo_pago_aprobado = True
        return (f"[POS ELECTRÓNICO - {banco} ({tipo_tarjeta})] Cita {cita.codigo} | Titular: {titular} | "
                f"Importe: S/ {total_a_pagar:.2f} {detalle_cuotas} | Autorización: AUT-{cod_aut}")

    @liquidar_comprobante.register(list)
    @liquidar_comprobante.register(tuple)
    def _(self, pagos_mixtos: list, cita) -> str:
        """Sobrecarga 4: Liquidación combinada / Pago mixto en múltiples canales."""
        _, _, total_a_pagar = calcular_liquidacion(cita.calcular_tarifa_final())
        suma_cubierta = sum(float(item[1]) for item in pagos_mixtos if len(item) >= 2)
        canales = [f"{item[0]}: S/ {float(item[1]):.2f}" for item in pagos_mixtos if len(item) >= 2]
        diferencia = round(suma_cubierta - total_a_pagar, 2)

        if diferencia < 0:
            self.ultimo_pago_aprobado = False
            return (f"[PAGO MIXTO INCOMPLETO] Cita {cita.codigo} | Total: S/ {total_a_pagar:.2f} | "
                    f"Cubierto: S/ {suma_cubierta:.2f} | Saldo pendiente: S/ {abs(diferencia):.2f}")

        self.ultimo_pago_aprobado = True
        return (f"[PAGO MIXTO COMBINADO] Cita {cita.codigo} | Total: S/ {total_a_pagar:.2f} | "
                f"Canales: [{', '.join(canales)}] | Cubierto: S/ {suma_cubierta:.2f} (Vuelto: S/ {diferencia:.2f})")


def formatear_comprobante_consola(cita, tipo_doc: str = "BOLETA") -> str:
    """
    Diseña una salida en consola con formato de Comprobante de Pago Electrónico Oficial SUNAT.
    Garantiza alineación milimétrica con bordes calculados dinámicamente en consola (78 cols).
    """
    subtotal, igv, total = calcular_liquidacion(cita.calcular_tarifa_final())
    fecha_emision = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    correlativo = generar_correlativo_sunat(cita.codigo, tipo_doc)

    lineas = [
        borde_sup_doble(ANCHO_TABLERO, C_GOLD),
        fila_doble(f"  {BG_HEADER} CLINICA DE ATE VITARTE S.A.C. {C_RESET}  {C_WHITE}RUC: 20548963211{C_RESET} • {C_GOLD}SEDE ATE{C_RESET}", ANCHO_TABLERO, C_GOLD),
        fila_doble(f"  {C_GRAY}Av. Nicolás Ayllón 5840 - Ate Vitarte, Lima - Tel: (01) 351-8900{C_RESET}", ANCHO_TABLERO, C_GOLD),
        fila_doble(f"  {C_GOLD}COMPROBANTE SUNAT:{C_RESET} {C_WHITE}{tipo_doc} ELECTRÓNICA N° {correlativo}{C_RESET}", ANCHO_TABLERO, C_GOLD),
        borde_sep_doble(ANCHO_TABLERO, C_GOLD),
        fila_doble(f"  {C_CYAN}DATOS DEL PACIENTE Y EMISIÓN:{C_RESET}", ANCHO_TABLERO, C_GOLD),
        fila_doble(f"    • Fecha/Hora Emisión : {C_WHITE}{fecha_emision}{C_RESET} | {C_GREEN}EMITIDO / PAGADO{C_RESET}", ANCHO_TABLERO, C_GOLD),
        fila_doble(f"    • Paciente Afiliado  : {C_WHITE}{truncar_texto(cita.paciente.nombre_completo, 25):<25}{C_RESET} (DNI: {cita.paciente.dni})", ANCHO_TABLERO, C_GOLD),
        fila_doble(f"    • Cobertura / Cita   : {C_GOLD}{cita.paciente.tipo_seguro:<16}{C_RESET} | Código: {C_WHITE}{cita.codigo}{C_RESET}", ANCHO_TABLERO, C_GOLD),
        fila_doble(f"    • Médico Tratante    : Dr(a). {truncar_texto(cita.medico.nombre_completo, 20):<20} (CMP: {cita.medico.colegiatura})", ANCHO_TABLERO, C_GOLD),
        borde_sep_doble(ANCHO_TABLERO, C_GOLD),
        fila_doble(f"  {C_CYAN}DETALLE DE LA PRESTACIÓN DE SALUD:{C_RESET}", ANCHO_TABLERO, C_GOLD),
        fila_doble(f"    • Tipo de Servicio   : {C_WHITE}{truncar_texto(cita.tipo_servicio(), 43)}{C_RESET}", ANCHO_TABLERO, C_GOLD),
        fila_doble(f"    • Especificación     : {C_GRAY}{truncar_texto(cita.obtener_detalles_servicio(), 43)}{C_RESET}", ANCHO_TABLERO, C_GOLD),
        fila_doble(f"    • Motivo Clínico     : {C_GRAY}{truncar_texto(cita.motivo, 43)}{C_RESET}", ANCHO_TABLERO, C_GOLD),
        borde_sep_doble(ANCHO_TABLERO, C_GOLD),
        fila_doble(f"  {C_CYAN}LIQUIDACIÓN TRIBUTARIA (SOLES):{C_RESET}", ANCHO_TABLERO, C_GOLD),
        fila_doble(f"    1. Tarifa Base Profesional        : S/ {cita.medico.tarifa_base:>8.2f}", ANCHO_TABLERO, C_GOLD),
        fila_doble(f"    2. Cobertura Seguro ({cita.paciente.tipo_seguro:<11}) : [ APLICADO AL COPAGO ]", ANCHO_TABLERO, C_GOLD),
        fila_doble(f"    3. Subtotal / Base Imponible      : {C_WHITE}S/ {subtotal:>8.2f}{C_RESET}", ANCHO_TABLERO, C_GOLD),
        fila_doble(f"    4. Impuesto General Ventas (18%)  : {C_WHITE}S/ {igv:>8.2f}{C_RESET}", ANCHO_TABLERO, C_GOLD),
        fila_doble(f"  {C_GRAY}{'─' * 66}{C_RESET}", ANCHO_TABLERO, C_GOLD),
        fila_doble(f"    {BG_TOTAL} TOTAL A LIQUIDAR / PAGADO : S/ {total:>8.2f} {C_RESET}", ANCHO_TABLERO, C_GOLD),
        borde_sep_doble(ANCHO_TABLERO, C_GOLD)
    ]

    # Incorporar representación del código QR en consola alineado milimétricamente
    qr_filas = generar_qr_ascii(correlativo, total, cita.codigo)
    for q in qr_filas:
        lineas.append(fila_doble(f"  {q}", ANCHO_TABLERO, C_GOLD))

    lineas.extend([
        borde_sep_doble(ANCHO_TABLERO, C_GOLD),
        fila_doble(f"  {C_GRAY}Representación impresa del Comprobante Fiscal Digital SUNAT.{C_RESET}", ANCHO_TABLERO, C_GOLD),
        fila_doble(f"  {C_GRAY}Clínica de Ate Vitarte S.A.C. - Sistema Desarrollado en Python.{C_RESET}", ANCHO_TABLERO, C_GOLD),
        borde_inf_doble(ANCHO_TABLERO, C_GOLD)
    ])

    return "\n".join(lineas)
