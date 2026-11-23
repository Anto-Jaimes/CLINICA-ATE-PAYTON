# -*- coding: utf-8 -*-
"""
================================================================================
CLÍNICA DE ATE VITARTE S.A.C. - SISTEMA ASISTENCIAL Y FINANCIERO
MÓDULO: main_citas.py (Interfaz de Consola por Fases Secuenciales Bloqueantes)
ARQUITECTURA: Clean Code • Interfaz ANSI Rica en Colores • Workflow Hospitalario
LÍDER DE PROYECTO: JULIBETH ANTONELA JAIMES DAZA
================================================================================
"""

import sys
import os

# Configuración universal para UTF-8 y soporte ANSI en terminales Windows
if sys.version_info[0] >= 3:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    if hasattr(sys.stderr, "reconfigure"):
        try:
            sys.stderr.reconfigure(encoding="utf-8")
        except Exception:
            pass

os.system("")

# Paleta cromática ANSI multicolor de alto impacto
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

BG_HEADER = "\033[44;1;97m"
BG_ALERT = "\033[41;1;97m"
BG_SUCCESS = "\033[42;1;30m"
BG_ACTIVE = "\033[43;1;30m"

from gestor import GestorClinico


def limpiar_pantalla():
    """Limpia la terminal según el sistema operativo."""
    os.system("cls" if os.name == "nt" else "clear")


def pausar():
    """Pausa interactiva con indicador estético."""
    print(f"\n{C_GRAY}────────────────────────────────────────────────────────────────────────────────────────{C_RESET}")
    input(f"  {C_GOLD}➤{C_RESET} {C_WHITE}Presione ENTER para continuar...{C_RESET}")


def imprimir_banner_institucional():
    """Imprime el encabezado oficial de la Clínica de Ate Vitarte S.A.C."""
    print(f"""
{C_CYAN}╔═════════════════════════════════════════════════════════════════════════════════════════════════════════════╗{C_RESET}
{C_CYAN}║{C_RESET}  {BG_HEADER}      CLÍNICA DE ATE VITARTE S.A.C.      {C_RESET}   {C_GOLD}[ SISTEMA INTEGRAL ASISTENCIAL Y FINANCIERO ]{C_RESET}        {C_CYAN}║{C_RESET}
{C_CYAN}║{C_RESET}  {C_WHITE}Gestión Hospitalaria por Fases Secuenciales • Admisión, Triaje, Consultorio, Facturación & BI{C_RESET}       {C_CYAN}║{C_RESET}
{C_CYAN}║{C_RESET}  {C_MAGENTA}Sede Ate Vitarte{C_RESET}  •  {C_GOLD}Arquitectura Clean Code en Python{C_RESET}  •  {C_GREEN}Líder: Julibeth Antonela Jaimes Daza{C_RESET}       {C_CYAN}║{C_RESET}
{C_CYAN}╚═════════════════════════════════════════════════════════════════════════════════════════════════════════════╝{C_RESET}
""")


def imprimir_barra_progreso_flujo(gestor):
    """Muestra la barra gráfica de progreso del ciclo hospitalario."""
    pct = gestor.calcular_porcentaje_flujo()
    barras_llenas = int(pct / 5)
    barras_vacias = 20 - barras_llenas
    barra_grafica = f"{C_GREEN}{'█' * barras_llenas}{C_GRAY}{'░' * barras_vacias}{C_RESET}"
    print(f"  {C_WHITE}PROGRESO DEL CICLO CLÍNICO:{C_RESET} [{barra_grafica}] {C_GOLD}{pct}% COMPLETADO{C_RESET}")
    print(f"  {C_GRAY}─────────────────────────────────────────────────────────────────────────────────────────────{C_RESET}")


def mostrar_pantalla_bloqueo(numero_fase: int, razon: str, sugerencia: str):
    """Pantalla de alta seguridad cuando el usuario intenta ingresar a una fase no desbloqueada."""
    limpiar_pantalla()
    imprimir_banner_institucional()
    print(f"""
  {C_RED}╔══════════════════════════════════════════════════════════════════════════════════════════╗{C_RESET}
  {C_RED}║{C_RESET}  {BG_ALERT}    ⛔ PROTOCOLO CLÍNICO: FASE ASISTENCIAL BLOQUEADA TEMPORALMENTE    {C_RESET}            {C_RED}║{C_RESET}
  {C_RED}╠══════════════════════════════════════════════════════════════════════════════════════════╣{C_RESET}
  {C_RED}║{C_RESET}                                                                                          {C_RED}║{C_RESET}
  {C_RED}║{C_RESET}   {C_WHITE}No es posible acceder a la {C_GOLD}FASE {numero_fase}{C_WHITE} del flujo asistencial.{C_RESET}                             {C_RED}║{C_RESET}
  {C_RED}║{C_RESET}                                                                                          {C_RED}║{C_RESET}
  {C_RED}║{C_RESET}   {C_GOLD}MOTIVO CLÍNICO:{C_RESET}                                                                        {C_RED}║{C_RESET}
  {C_RED}║{C_RESET}   {C_RED}• {razon:<83}{C_RESET}{C_RED}║{C_RESET}
  {C_RED}║{C_RESET}                                                                                          {C_RED}║{C_RESET}
  {C_RED}║{C_RESET}   {C_CYAN}ACCIÓN REQUERIDA PARA DESBLOQUEAR:{C_RESET}                                                     {C_RED}║{C_RESET}
  {C_RED}║{C_RESET}   {C_GREEN}➤ {sugerencia:<83}{C_RESET}{C_RED}║{C_RESET}
  {C_RED}║{C_RESET}                                                                                          {C_RED}║{C_RESET}
  {C_RED}╚══════════════════════════════════════════════════════════════════════════════════════════╝{C_RESET}
""")


def imprimir_menu_fases(gestor):
    """Despliega el menú principal estructurado en las 6 Fases Secuenciales con badges dinámicos."""
    imprimir_barra_progreso_flujo(gestor)

    b1 = gestor.obtener_estado_visual_fase(1)
    b2 = gestor.obtener_estado_visual_fase(2)
    b3 = gestor.obtener_estado_visual_fase(3)
    b4 = gestor.obtener_estado_visual_fase(4)
    b5 = gestor.obtener_estado_visual_fase(5)
    b6 = gestor.obtener_estado_visual_fase(6)

    print(f"""
  {C_GOLD}┌───────────────────────── FLUJO ASISTENCIAL POR FASES CLÍNICAS ──────────────────────────┐{C_RESET}
  {C_GOLD}│{C_RESET}                                                                                          {C_GOLD}│{C_RESET}
  {C_GOLD}│{C_RESET}   {C_MAGENTA}FASE 1: ADMISIÓN Y AFILIACIÓN{C_RESET}                                            {b1}   {C_GOLD}│{C_RESET}
  {C_GOLD}│{C_RESET}     {C_GOLD}[ 1 ]{C_RESET} {C_WHITE}Afiliación de Paciente al Padrón{C_RESET} {C_GRAY}(Alta, DNI, Seguro y Carnet Digital){C_RESET}      {C_GOLD}│{C_RESET}
  {C_GOLD}│{C_RESET}                                                                                          {C_GOLD}│{C_RESET}
  {C_GOLD}│{C_RESET}   {C_CYAN}FASE 2: TRIAJE HOSPITALARIO Y EVALUACIÓN{C_RESET}                                   {b2}   {C_GOLD}│{C_RESET}
  {C_GOLD}│{C_RESET}     {C_GOLD}[ 2 ]{C_RESET} {C_WHITE}Toma de Signos Vitales y Cálculo de IMC{C_RESET} {C_GRAY}(Presión, SpO2, Pulso, Diagnóstico){C_RESET} {C_GOLD}│{C_RESET}
  {C_GOLD}│{C_RESET}                                                                                          {C_GOLD}│{C_RESET}
  {C_GOLD}│{C_RESET}   {C_BLUE}FASE 3: AGENDAMIENTO ASISTENCIAL{C_RESET}                                           {b3}   {C_GOLD}│{C_RESET}
  {C_GOLD}│{C_RESET}     {C_GOLD}[ 3 ]{C_RESET} {C_WHITE}Programación de Cita Polimórfica{C_RESET} {C_GRAY}(General, Especialidad, Urgencia, etc.){C_RESET}    {C_GOLD}│{C_RESET}
  {C_GOLD}│{C_RESET}                                                                                          {C_GOLD}│{C_RESET}
  {C_GOLD}│{C_RESET}   {C_GOLD}FASE 4: ACTO MÉDICO Y CONSULTORIO{C_RESET}                                         {b4}   {C_GOLD}│{C_RESET}
  {C_GOLD}│{C_RESET}     {C_GOLD}[ 4 ]{C_RESET} {C_WHITE}Atención Médica y Receta Oficial{C_RESET} {C_GRAY}(Diagnóstico CIE-10 y Fármacos prescritos){C_RESET} {C_GOLD}│{C_RESET}
  {C_GOLD}│{C_RESET}                                                                                          {C_GOLD}│{C_RESET}
  {C_GOLD}│{C_RESET}   {C_GREEN}FASE 5: CAJA Y TESORERÍA FISCAL{C_RESET}                                           {b5}   {C_GOLD}│{C_RESET}
  {C_GOLD}│{C_RESET}     {C_GOLD}[ 5 ]{C_RESET} {C_WHITE}Facturación Electrónica SUNAT (18%){C_RESET} {C_GRAY}(Boleta/Factura, Código QR y Pago){C_RESET}       {C_GOLD}│{C_RESET}
  {C_GOLD}│{C_RESET}                                                                                          {C_GOLD}│{C_RESET}
  {C_GOLD}│{C_RESET}   {C_ORANGE}FASE 6: AUDITORÍA Y CIERRE GERENCIAL{C_RESET}                                      {b6}   {C_GOLD}│{C_RESET}
  {C_GOLD}│{C_RESET}     {C_GOLD}[ 6 ]{C_RESET} {C_WHITE}Tablero BI Gerencial y Archivo en Disco{C_RESET} {C_GRAY}(Gráficos de barras y Auditoría){C_RESET}   {C_GOLD}│{C_RESET}
  {C_GOLD}│{C_RESET}                                                                                          {C_GOLD}│{C_RESET}
  {C_GOLD}├──────────────────────────────────────────────────────────────────────────────────────────┤{C_RESET}
  {C_GOLD}│{C_RESET}   {C_WHITE}CONSULTAS Y GESTIÓN AUXILIAR:{C_RESET}                                                           {C_GOLD}│{C_RESET}
  {C_GOLD}│{C_RESET}     {C_CYAN}[ 7 ]{C_RESET} {C_WHITE}Directorio de Médicos Especialistas y Horarios{C_RESET}                               {C_GOLD}│{C_RESET}
  {C_GOLD}│{C_RESET}     {C_CYAN}[ 8 ]{C_RESET} {C_WHITE}Expediente Clínico Digital por DNI{C_RESET}                                           {C_GOLD}│{C_RESET}
  {C_GOLD}│{C_RESET}     {C_GOLD}[ 9 ]{C_RESET} {C_WHITE}Reiniciar Flujo Asistencial a Cero{C_RESET} {C_GRAY}(Para probar bloqueo paso a paso){C_RESET}         {C_GOLD}│{C_RESET}
  {C_GOLD}│{C_RESET}     {C_RED}[ 0 ]{C_RESET} {C_WHITE}Cerrar Sesión del Sistema{C_RESET}                                                     {C_GOLD}│{C_RESET}
  {C_GOLD}└──────────────────────────────────────────────────────────────────────────────────────────┘{C_RESET}
""")


def menu_directorio_medicos(gestor):
    """Despliega el directorio médico oficial de la sede."""
    print(f"\n{C_CYAN}╔════════════════════════════════════════════════════════════════════════════════════════════════════╗{C_RESET}")
    print(f"{C_CYAN}║{C_RESET}                       {C_WHITE}DIRECTORIO DE MÉDICOS ESPECIALISTAS Y CONSULTORIOS{C_RESET}                           {C_CYAN}║{C_RESET}")
    print(f"{C_CYAN}╠══════════╦════════════════════════╦════════════════════╦══════════════╦═════════════════╦══════════════╣{C_RESET}")
    print(f"{C_CYAN}║{C_RESET} {C_GOLD}COLEG.{C_RESET}   {C_CYAN}║{C_RESET} {C_GOLD}MÉDICO ASIGNADO{C_RESET}        {C_CYAN}║{C_RESET} {C_GOLD}ESPECIALIDAD{C_RESET}       {C_CYAN}║{C_RESET} {C_GOLD}TARIFA BASE{C_RESET}    {C_CYAN}║{C_RESET} {C_GOLD}HORARIO TURNO{C_RESET}   {C_CYAN}║{C_RESET} {C_GOLD}CONSULTORIO{C_RESET}    {C_CYAN}║{C_RESET}")
    print(f"{C_CYAN}╠══════════╬════════════════════════╬════════════════════╬══════════════╬═════════════════╬══════════════╣{C_RESET}")
    for m in gestor.medicos:
        horario = f"{m.horario_atencion[0]} a {m.horario_atencion[1]}"
        print(f"{C_CYAN}║{C_RESET} {m.colegiatura:<8} {C_CYAN}║{C_RESET} Dr(a). {m.nombre_completo:<16} {C_CYAN}║{C_RESET} {m.especialidad:<18} {C_CYAN}║{C_RESET} {C_GREEN}S/ {m.tarifa_base:8.2f}{C_RESET} {C_CYAN}║{C_RESET} {horario:<15} {C_CYAN}║{C_RESET} {m.consultorio:<12} {C_CYAN}║{C_RESET}")
    print(f"{C_CYAN}╚══════════╩════════════════════════╩════════════════════╩══════════════╩═════════════════╩══════════════╝{C_RESET}")


def ejecutar_consola():
    """Bucle maestro del sistema con verificación estricta de fases."""
    gestor = GestorClinico(precargar_datos=True)

    while True:
        limpiar_pantalla()
        imprimir_banner_institucional()
        imprimir_menu_fases(gestor)

        opcion = input(f"  {C_CYAN}➤ Ingrese una opción [0 - 9]:{C_RESET} ").strip()

        if opcion == "1":
            # FASE 1: Siempre accesible
            gestor.ejecutar_fase1_admision()
            pausar()

        elif opcion == "2":
            # FASE 2: Triaje
            desbloqueada, razon, sug = gestor.verificar_fase(2)
            if not desbloqueada:
                mostrar_pantalla_bloqueo(2, razon, sug)
            else:
                gestor.ejecutar_fase2_triaje()
            pausar()

        elif opcion == "3":
            # FASE 3: Agendamiento
            desbloqueada, razon, sug = gestor.verificar_fase(3)
            if not desbloqueada:
                mostrar_pantalla_bloqueo(3, razon, sug)
            else:
                gestor.ejecutar_fase3_agendamiento()
            pausar()

        elif opcion == "4":
            # FASE 4: Acto Médico
            desbloqueada, razon, sug = gestor.verificar_fase(4)
            if not desbloqueada:
                mostrar_pantalla_bloqueo(4, razon, sug)
            else:
                gestor.ejecutar_fase4_acto_medico()
            pausar()

        elif opcion == "5":
            # FASE 5: Facturación
            desbloqueada, razon, sug = gestor.verificar_fase(5)
            if not desbloqueada:
                mostrar_pantalla_bloqueo(5, razon, sug)
            else:
                gestor.ejecutar_fase5_facturacion()
            pausar()

        elif opcion == "6":
            # FASE 6: Auditoría y Cierre
            desbloqueada, razon, sug = gestor.verificar_fase(6)
            if not desbloqueada:
                mostrar_pantalla_bloqueo(6, razon, sug)
            else:
                gestor.ejecutar_fase6_auditoria_cierre()
            pausar()

        elif opcion == "7":
            menu_directorio_medicos(gestor)
            pausar()

        elif opcion == "8":
            dni = input(f"\n  {C_GOLD}>>{C_RESET} {C_WHITE}Ingrese DNI del paciente:{C_RESET} ").strip()
            p = gestor.buscar_paciente_por_dni(dni)
            if not p:
                print(f"  {C_RED}[ERROR]{C_RESET} Paciente no encontrado con DNI {dni}.")
            else:
                print("\n" + p.generar_carnet_digital())
                citas_p = [c for c in gestor.citas if c.paciente.dni == p.dni]
                print(f"\n  {C_GOLD}Historial Asistencial ({len(citas_p)} cita(s)):{C_RESET}")
                for c in citas_p:
                    print(f"    • [{c.codigo}] {c.fecha} {c.hora} | Dr(a). {c.medico.nombre_completo:<20} | {c.tipo_servicio():<26} | Estado: {c.estado}")
            pausar()

        elif opcion == "9":
            gestor.reiniciar_flujo_a_cero()
            pausar()

        elif opcion == "0":
            limpiar_pantalla()
            imprimir_banner_institucional()
            print(f"""
  {BG_SUCCESS}       SESIÓN ASISTENCIAL FINALIZADA CORRECTAMENTE       {C_RESET}

  {C_GREEN}✔{C_RESET} {C_WHITE}Todas las transacciones asistenciales y comprobantes fueron procesados en memoria.{C_RESET}
  {C_CYAN}✦{C_RESET} {C_GRAY}Sistema Hospitalario desarrollado para la Clínica de Ate Vitarte S.A.C.{C_RESET}
  {C_GOLD}●{C_RESET} {C_GRAY}Líder de Proyecto: Julibeth Antonela Jaimes Daza • Clean Code Architecture.{C_RESET}\n
""")
            sys.exit(0)

        else:
            print(f"\n  {C_RED}[ALERTA] Opción no válida.{C_RESET} Digite un número del 0 al 9.")
            pausar()


if __name__ == "__main__":
    ejecutar_consola()
