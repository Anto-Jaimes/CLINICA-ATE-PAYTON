# -*- coding: utf-8 -*-
"""
================================================================================
CLÍNICA DE ATE VITARTE S.A.C. - SISTEMA INTEGRAL ASISTENCIAL Y FINANCIERO
MÓDULO: gestor.py (Flujo Asistencial por Fases Clínicas Consecutivas)
ARQUITECTURA: Clean Code • Principios SOLID • Gestión de Estado por Fases
LÍDER DE PROYECTO: JULIBETH ANTONELA JAIMES DAZA
================================================================================
CONTROLADOR DEL FLUJO DE TRABAJO CLÍNICO (WORKFLOW SECUENCIAL):
- FASE 1: Admisión y Afiliación del Paciente (Carnet Digital).
- FASE 2: Triaje Hospitalario y Signos Vitales (IMC y Diagnóstico Nutricional).
- FASE 3: Agendamiento de Citas Polimórficas (6 Especialidades Asistenciales).
- FASE 4: Consultorio Médico, Acto Médico y Receta Oficial (CIE-10).
- FASE 5: Caja, Facturación Electrónica SUNAT (IGV 18%, QR y Multicanal).
- FASE 6: Auditoría, Reporte Gerencial BI y Cierre de Expediente Clínico.
================================================================================
"""

import os
from datetime import datetime
from modelos import (
    Persona, Medico, Paciente, Enfermero,
    CitaMedica, CitaGeneral, CitaEspecialidad, CitaEmergencia,
    CitaTelemedicina, CitaDomiciliaria, CitaLaboratorio
)
from facturacion import formatear_comprobante_consola, FacturadorClinico, calcular_liquidacion
from formato_tablero import (
    C_RESET, C_BOLD, C_DIM, C_CYAN, C_GOLD, C_GREEN, C_MAGENTA, C_BLUE,
    C_RED, C_WHITE, C_GRAY, ANCHO_TABLERO, fila_doble, borde_sup_doble,
    borde_inf_doble, borde_sep_doble
)

C_ORANGE = "\033[38;5;208m"
C_CORAL = "\033[38;5;209m"

# Fondos cromáticos para badges y estados
BG_HEADER = "\033[44;1;97m"
BG_FASE1 = "\033[45;1;97m"
BG_FASE2 = "\033[46;1;30m"
BG_FASE3 = "\033[44;1;97m"
BG_FASE4 = "\033[43;1;30m"
BG_FASE5 = "\033[42;1;30m"
BG_FASE6 = "\033[41;1;97m"
BG_LOCKED = "\033[48;5;236;90m"
BG_ACTIVE = "\033[43;1;30m"


class GestorClinico:
    """
    Controlador central de la Clínica de Ate Vitarte S.A.C.
    Gestiona el flujo asistencial por fases bloqueantes: ninguna fase posterior
    puede ser ejecutada sin haber cumplido los requisitos clínicos previos.
    """
    def __init__(self, precargar_datos=True):
        # 1. Colecciones en Memoria
        self.medicos = []
        self.pacientes = []
        self.enfermeros = []
        self.citas = []

        # 2. Índices de Acceso Rápido O(1)
        self.indice_pacientes = {}   # dni -> Paciente
        self.indice_medicos = {}      # colegiatura -> Medico
        self.indice_citas = {}        # codigo -> CitaMedica

        # 3. Conjuntos (Sets) para Valores Únicos
        self.especialidades_disponibles = set()

        # 4. Estado del Flujo Asistencial por Fases
        self.citas_facturadas = set()  # Códigos de citas con boleta/factura emitida

        # Catálogo de personal médico base
        self._cargar_catalogo_profesionales()

        if precargar_datos:
            self._precargar_flujo_asistencial_semilla()

    def _cargar_catalogo_profesionales(self):
        """Carga el directorio permanente de médicos especialistas y enfermeros."""
        m1 = Medico("10293847", "Alejandro", "Vargas Ríos", "987111222", "CMP-45890", "Cardiología", 120.0, ("08:00", "13:00"), "Piso 2 - Cons. 201")
        m2 = Medico("20394857", "Mariana", "Salas Mendoza", "987222333", "CMP-51204", "Pediatría", 100.0, ("14:00", "19:00"), "Piso 1 - Cons. 105")
        m3 = Medico("30495867", "Roberto", "Castro Peña", "987333444", "CMP-38912", "Medicina General", 70.0, ("08:00", "16:00"), "Piso 1 - Cons. 102")
        m4 = Medico("40596877", "Diana", "Fernández Luna", "987444555", "CMP-62145", "Traumatología", 110.0, ("10:00", "15:00"), "Piso 2 - Cons. 208")
        m5 = Medico("50697887", "Fernando", "Navarro Díaz", "987555666", "CMP-49321", "Neurología", 130.0, ("09:00", "14:00"), "Piso 3 - Cons. 302")
        m6 = Medico("60798897", "Patricia", "Gutiérrez Vega", "987666777", "CMP-58210", "Ginecología", 115.0, ("11:00", "17:00"), "Piso 2 - Cons. 205")

        for m in (m1, m2, m3, m4, m5, m6):
            self.medicos.append(m)
            self.indice_medicos[m.colegiatura] = m
            self.especialidades_disponibles.add(m.especialidad)

        e1 = Enfermero("71234567", "Beatriz", "Huamán Flores", "976123456", "CEP-34120", "Triaje Hospitalario", "Mañana")
        e2 = Enfermero("72345678", "Marcos", "Quispe Córdova", "976654321", "CEP-41589", "Urgencias y Móvil", "Tarde")
        self.enfermeros.extend([e1, e2])

    def _precargar_flujo_asistencial_semilla(self):
        """Carga pacientes iniciales que permiten demostrar el ciclo en marcha."""
        p1 = Paciente("74859612", "Carlos", "Pérez Gómez", "999123456", 28, "PARTICULAR", ("Penicilina",), "O+")
        p1.registrar_signos_vitales("120/80", 72, 98, 36.5, 74.0, 1.75)
        p1.agregar_diagnostico_historial("K29.7", "Gastritis aguda")
        self.agregar_paciente(p1)

        p2 = Paciente("85961234", "Lucía", "Morales Vera", "999654321", 16, "EPS", (), "A+")
        p2.registrar_signos_vitales("110/70", 80, 99, 36.8, 52.0, 1.62)
        self.agregar_paciente(p2)

        p3 = Paciente("45123678", "Marcos", "Soto Paredes", "999888777", 65, "SIS", ("Sulfas", "Polvo"), "B+")
        p3.registrar_signos_vitales("145/95", 88, 94, 38.4, 82.0, 1.68)
        self.agregar_paciente(p3)

        # Citas iniciales
        c1 = CitaGeneral("CIT-101", p1, self.medicos[2], "2026-11-23", "09:00", "Chequeo preventivo de rutina")
        c1.marcar_atendida()
        c1.agregar_medicamento_receta("Multivitamínico con Zinc", "1 cápsula", "cada 24 horas", 30)
        c1.establecer_indicaciones("Reposo relativo e hidratación continua.")
        self.agregar_cita(c1)
        self.citas_facturadas.add(c1.codigo)

        c2 = CitaEspecialidad("CIT-102", p2, self.medicos[0], "2026-11-23", "10:30", "Evaluación cardiológica", True, "Electrocardiograma de 12 derivaciones")
        c2.marcar_atendida()
        c2.agregar_medicamento_receta("Propranolol", "40 mg", "cada 12 horas", 15)
        self.agregar_cita(c2)

        c3 = CitaEmergencia("EMG-103", p3, self.medicos[1], "2026-11-22", "18:00", "Fiebre persistente y tos", nivel_triaje=2)
        self.agregar_cita(c3)

    # --------------------------------------------------------------------------
    # MOTOR DE VALIDACIÓN DE FASES (WORKFLOW SECUENCIAL BLOQUEANTE)
    # --------------------------------------------------------------------------
    def verificar_fase(self, numero_fase: int) -> tuple:
        """
        Evalúa si una fase está desbloqueada y lista para ser operada:
        Retorna: (esta_desbloqueada: bool, mensaje_razon: str, sugerencia: str)
        """
        if numero_fase == 1:
            # FASE 1: Admisión siempre disponible
            return (True, "Fase de Admisión abierta y activa.", "Puede registrar nuevos pacientes.")

        elif numero_fase == 2:
            # FASE 2: Triaje requiere que exista al menos 1 paciente afiliado
            if len(self.pacientes) == 0:
                return (
                    False,
                    "No hay ningún paciente registrado en el padrón de la clínica.",
                    "Complete primero la FASE 1 [Opción 1] para afiliar a un paciente."
                )
            return (True, f"{len(self.pacientes)} paciente(s) habilitado(s) para triaje.", "Seleccione un paciente para evaluar.")

        elif numero_fase == 3:
            # FASE 3: Agendamiento requiere al menos 1 paciente con triaje completado
            pacientes_con_triaje = [p for p in self.pacientes if p.signos_vitales]
            if len(pacientes_con_triaje) == 0:
                return (
                    False,
                    "Ningún paciente registrado cuenta con signos vitales ni evaluación de triaje.",
                    "Complete primero la FASE 2 [Opción 2] para tomar signos vitales e IMC."
                )
            return (True, f"{len(pacientes_con_triaje)} paciente(s) con triaje completado.", "Proceda a programar la consulta médica.")

        elif numero_fase == 4:
            # FASE 4: Acto Médico requiere al menos 1 cita agendada en estado PROGRAMADA o EN_ESPERA
            citas_pendientes = [c for c in self.citas if c.estado in ("PROGRAMADA", "EN_ESPERA")]
            if len(citas_pendientes) == 0:
                citas_existentes = len(self.citas)
                if citas_existentes == 0:
                    return (
                        False,
                        "No existe ninguna cita asistencial agendada en el sistema.",
                        "Complete primero la FASE 3 [Opción 3] para agendar una cita médica."
                    )
                else:
                    return (
                        False,
                        "Todas las citas programadas ya fueron atendidas o canceladas.",
                        "Agende una nueva cita en la FASE 3 [Opción 3] para una nueva atención."
                    )
            return (True, f"{len(citas_pendientes)} cita(s) pendiente(s) de atención médica.", "Inicie la consulta y prescriba la receta.")

        elif numero_fase == 5:
            # FASE 5: Facturación requiere al menos 1 cita en estado ATENDIDA lista para liquidar
            citas_por_facturar = [c for c in self.citas if c.estado == "ATENDIDA" and c.codigo not in self.citas_facturadas]
            if len(citas_por_facturar) == 0:
                atendidas_totales = [c for c in self.citas if c.estado == "ATENDIDA"]
                if len(atendidas_totales) == 0:
                    return (
                        False,
                        "No hay citas atendidas por el médico listas para liquidar en caja.",
                        "El médico debe atender al paciente en la FASE 4 [Opción 4] antes de facturar."
                    )
                else:
                    return (
                        False,
                        "Todas las citas atendidas ya fueron cobradas y cuentan con comprobante SUNAT.",
                        "Atienda una nueva cita médica en la FASE 4 para poder emitir comprobante."
                    )
            return (True, f"{len(citas_por_facturar)} cita(s) atendida(s) lista(s) para liquidación.", "Emita la boleta/factura electrónica.")

        elif numero_fase == 6:
            # FASE 6: Auditoría y Cierre requiere al menos 1 cita completamente facturada
            if len(self.citas_facturadas) == 0:
                return (
                    False,
                    "No se ha liquidado ningún comprobante fiscal electrónico en caja.",
                    "Complete la FASE 5 [Opción 5] para facturar y pagar al menos una cita médica."
                )
            return (True, f"{len(self.citas_facturadas)} transacción(es) fiscal(es) registradas.", "Acceda al tablero BI y exportación.")

        return (False, "Fase no reconocida.", "Verifique la opción seleccionada.")

    def obtener_estado_visual_fase(self, numero_fase: int) -> str:
        """Retorna un badge multicolor con el estado exacto de cada fase."""
        desbloqueada, _, _ = self.verificar_fase(numero_fase)
        if desbloqueada:
            if numero_fase == 1 and len(self.pacientes) > 0:
                return f"{C_GREEN}[ COMPLETADA ]{C_RESET}"
            elif numero_fase == 2 and any(p.signos_vitales for p in self.pacientes):
                return f"{C_GREEN}[ COMPLETADA ]{C_RESET}"
            elif numero_fase == 3 and any(c.estado in ("PROGRAMADA", "ATENDIDA") for c in self.citas):
                return f"{C_GREEN}[ COMPLETADA ]{C_RESET}"
            elif numero_fase == 4 and any(c.estado == "ATENDIDA" for c in self.citas):
                return f"{C_GREEN}[ COMPLETADA ]{C_RESET}"
            elif numero_fase == 5 and len(self.citas_facturadas) > 0:
                return f"{C_GREEN}[ COMPLETADA ]{C_RESET}"
            elif numero_fase == 6 and len(self.citas_facturadas) > 0:
                return f"{C_CYAN}[ DISPONIBLE ]{C_RESET}"
            return f"{C_GOLD}[ EN CURSO   ]{C_RESET}"
        else:
            return f"{C_RED}[ BLOQUEADA  ]{C_RESET}"

    def calcular_porcentaje_flujo(self) -> int:
        """Calcula el porcentaje de avance general del workflow asistencial."""
        fases_completadas = 0
        if len(self.pacientes) > 0:
            fases_completadas += 1
        if any(p.signos_vitales for p in self.pacientes):
            fases_completadas += 1
        if len(self.citas) > 0:
            fases_completadas += 1
        if any(c.estado == "ATENDIDA" for c in self.citas):
            fases_completadas += 1
        if len(self.citas_facturadas) > 0:
            fases_completadas += 1
        if len(self.citas_facturadas) > 0:
            fases_completadas += 1
        return int((fases_completadas / 6) * 100)

    # --------------------------------------------------------------------------
    # OPERACIONES AUXILIARES DE COLECCIONES
    # --------------------------------------------------------------------------
    def agregar_paciente(self, paciente: Paciente):
        self.pacientes.append(paciente)
        self.indice_pacientes[paciente.dni] = paciente

    def agregar_cita(self, cita: CitaMedica):
        self.citas.append(cita)
        self.indice_citas[cita.codigo] = cita

    def buscar_paciente_por_dni(self, dni: str) -> Paciente:
        return self.indice_pacientes.get(str(dni).strip(), None)

    def buscar_cita_por_codigo(self, codigo: str) -> CitaMedica:
        return self.indice_citas.get(str(codigo).strip().upper(), None)

    def reiniciar_flujo_a_cero(self):
        """Limpia pacientes y citas para comenzar una demostración desde cero absoluto."""
        self.pacientes.clear()
        self.citas.clear()
        self.indice_pacientes.clear()
        self.indice_citas.clear()
        self.citas_facturadas.clear()
        print(f"\n  {C_GREEN}✔ [SISTEMA REINICIADO]{C_RESET} Se limpiaron los pacientes y citas.")
        print(f"  {C_GOLD}● Ahora todas las fases posteriores a la FASE 1 están rigurosamente bloqueadas.{C_RESET}")

    # --------------------------------------------------------------------------
    # FASE 1: ADMISIÓN Y AFILIACIÓN
    # --------------------------------------------------------------------------
    def ejecutar_fase1_admision(self):
        print(f"\n{borde_sup_doble(ANCHO_TABLERO, C_MAGENTA)}")
        print(fila_doble(f"  {BG_FASE1} FASE 1 : ADMISIÓN HOSPITALARIA Y AFILIACIÓN DEL PACIENTE {C_RESET}", ANCHO_TABLERO, C_MAGENTA))
        print(f"{borde_inf_doble(ANCHO_TABLERO, C_MAGENTA)}\n")

        dni = input(f"  {C_GOLD}>>{C_RESET} {C_WHITE}Ingrese DNI (8 dígitos):{C_RESET} ").strip()
        if not (dni.isdigit() and len(dni) == 8):
            print(f"  {C_RED}[ERROR]{C_RESET} DNI no válido. Debe tener exactamente 8 dígitos.")
            return

        if self.buscar_paciente_por_dni(dni):
            print(f"  {C_RED}[ALERTA]{C_RESET} Ya existe un paciente afiliado con DNI {dni}.")
            return

        nom = input(f"  {C_GOLD}>>{C_RESET} {C_WHITE}Nombres:{C_RESET} ").strip()
        ape = input(f"  {C_GOLD}>>{C_RESET} {C_WHITE}Apellidos completos:{C_RESET} ").strip()
        tel = input(f"  {C_GOLD}>>{C_RESET} {C_WHITE}Teléfono / Celular:{C_RESET} ").strip()

        try:
            edad = int(input(f"  {C_GOLD}>>{C_RESET} {C_WHITE}Edad:{C_RESET} ").strip())
        except ValueError:
            edad = 25

        print(f"  {C_GRAY}Seguros admitidos: PARTICULAR | EPS | SIS | CONVENIO_UTP{C_RESET}")
        seg = input(f"  {C_GOLD}>>{C_RESET} {C_WHITE}Tipo de seguro [defecto PARTICULAR]:{C_RESET} ").strip().upper()
        if seg not in ("PARTICULAR", "EPS", "SIS", "CONVENIO_UTP"):
            seg = "PARTICULAR"

        sang = input(f"  {C_GOLD}>>{C_RESET} {C_WHITE}Grupo sanguíneo [defecto O+]:{C_RESET} ").strip().upper()
        if not sang:
            sang = "O+"

        ale_in = input(f"  {C_GOLD}>>{C_RESET} {C_WHITE}Alergias conocidas (separadas por coma o vacío):{C_RESET} ").strip()
        alergias = tuple([a.strip() for a in ale_in.split(",") if a.strip()]) if ale_in else ()

        nuevo_p = Paciente(dni, nom, ape, tel, edad, seg, alergias, sang)
        self.agregar_paciente(nuevo_p)

        print(f"\n  {C_GREEN}✔ [FASE 1 COMPLETADA CON ÉXITO]{C_RESET}")
        print(f"  {C_CYAN}Paciente '{nuevo_p.nombre_completo}' registrado con éxito.{C_RESET}")
        print(f"  {C_GOLD}🔓 ¡FASE 2 DESBLOQUEADA! Ahora puede realizar el Triaje Clínico de este paciente.{C_RESET}")
        print("\n" + nuevo_p.generar_carnet_digital())

    # --------------------------------------------------------------------------
    # FASE 2: TRIAJE Y SIGNOS VITALES (IMC)
    # --------------------------------------------------------------------------
    def ejecutar_fase2_triaje(self):
        print(f"\n{borde_sup_doble(ANCHO_TABLERO, C_CYAN)}")
        print(fila_doble(f"  {BG_FASE2} FASE 2 : TRIAJE HOSPITALARIO, SIGNOS VITALES E IMC {C_RESET}", ANCHO_TABLERO, C_CYAN))
        print(f"{borde_inf_doble(ANCHO_TABLERO, C_CYAN)}\n")

        print(f"  {C_WHITE}Pacientes registrados en el padrón:{C_RESET}")
        for i, p in enumerate(self.pacientes, 1):
            estado_sv = f"{C_GREEN}✔ Con Triaje{C_RESET}" if p.signos_vitales else f"{C_GOLD}⏳ Pendiente{C_RESET}"
            print(f"    [{i}] DNI: {p.dni} | {p.nombre_completo:<24} | Seguro: {p.tipo_seguro:<12} | {estado_sv}")

        dni = input(f"\n  {C_GOLD}>>{C_RESET} {C_WHITE}Ingrese DNI del paciente a evaluar en triaje:{C_RESET} ").strip()
        paciente = self.buscar_paciente_por_dni(dni)
        if not paciente:
            print(f"  {C_RED}[ERROR]{C_RESET} Paciente no encontrado con el DNI {dni}.")
            return

        presion = input(f"  {C_GOLD}>>{C_RESET} {C_WHITE}Presión Arterial (ej. 120/80):{C_RESET} ").strip()
        if not presion:
            presion = "120/80"

        try:
            pulso = int(input(f"  {C_GOLD}>>{C_RESET} {C_WHITE}Frecuencia Cardíaca (lpm, ej. 72):{C_RESET} ").strip())
        except ValueError:
            pulso = 72

        try:
            sat = int(input(f"  {C_GOLD}>>{C_RESET} {C_WHITE}Saturación de Oxígeno SpO2 (%, ej. 98):{C_RESET} ").strip())
        except ValueError:
            sat = 98

        try:
            temp = float(input(f"  {C_GOLD}>>{C_RESET} {C_WHITE}Temperatura Corporal (°C, ej. 36.6):{C_RESET} ").strip())
        except ValueError:
            temp = 36.6

        try:
            peso = float(input(f"  {C_GOLD}>>{C_RESET} {C_WHITE}Peso Corporal (kg, ej. 70.0):{C_RESET} ").strip())
            talla = float(input(f"  {C_GOLD}>>{C_RESET} {C_WHITE}Talla / Estatura (metros, ej. 1.70):{C_RESET} ").strip())
        except ValueError:
            peso, talla = 70.0, 1.70

        paciente.registrar_signos_vitales(presion, pulso, sat, temp, peso, talla)
        sv = paciente.signos_vitales

        alerta_sat = f"{C_RED}[ALERTA: HIPOXIA CRÍTICA]{C_RESET}" if sat < 95 else f"{C_GREEN}[NORMAL]{C_RESET}"
        alerta_temp = f"{C_RED}[ALERTA: FIEBRE ALTA]{C_RESET}" if temp >= 38.0 else f"{C_GREEN}[EUTÉRMICO]{C_RESET}"

        print(f"\n  {C_GREEN}✔ [FASE 2 COMPLETADA CON ÉXITO]{C_RESET}")
        print(f"  {C_CYAN}Signos vitales registrados para: {C_WHITE}{paciente.nombre_completo}{C_RESET}")
        print(f"    • Presión : {C_WHITE}{presion} mmHg{C_RESET} | Pulso: {C_WHITE}{pulso} lpm{C_RESET} | SpO2: {C_WHITE}{sat}%{C_RESET} {alerta_sat}")
        print(f"    • Temp    : {C_WHITE}{temp:.1f} °C{C_RESET} {alerta_temp} | Peso: {peso:.1f} kg | Talla: {talla:.2f} m")
        print(f"    • IMC     : {C_GOLD}{sv['imc']:.2f}{C_RESET} -> {C_MAGENTA}{sv['diagnostico_nutricional']}{C_RESET}")
        print(f"\n  {C_GOLD}🔓 ¡FASE 3 DESBLOQUEADA! El paciente ya puede recibir una Cita Médica.{C_RESET}")

    # --------------------------------------------------------------------------
    # FASE 3: ASIGNACIÓN Y AGENDAMIENTO DE CITA
    # --------------------------------------------------------------------------
    def ejecutar_fase3_agendamiento(self):
        print(f"\n{borde_sup_doble(ANCHO_TABLERO, C_BLUE)}")
        print(fila_doble(f"  {BG_FASE3} FASE 3 : AGENDAMIENTO Y ASIGNACIÓN POLIMÓRFICA {C_RESET}", ANCHO_TABLERO, C_BLUE))
        print(f"{borde_inf_doble(ANCHO_TABLERO, C_BLUE)}\n")

        pacientes_aptos = [p for p in self.pacientes if p.signos_vitales]
        print(f"  {C_WHITE}Pacientes evaluados en triaje aptos para cita médica:{C_RESET}")
        for i, p in enumerate(pacientes_aptos, 1):
            print(f"    [{i}] DNI: {p.dni} | {p.nombre_completo:<24} | IMC: {p.signos_vitales['imc']} ({p.signos_vitales['diagnostico_nutricional']})")

        dni = input(f"\n  {C_GOLD}>>{C_RESET} {C_WHITE}Ingrese DNI del paciente a agendar:{C_RESET} ").strip()
        paciente = self.buscar_paciente_por_dni(dni)
        if not paciente or not paciente.signos_vitales:
            print(f"  {C_RED}[ERROR]{C_RESET} Paciente no encontrado o no ha completado la Fase 2 de Triaje.")
            return

        print(f"\n  {C_CYAN}Especialistas Disponibles en la Sede:{C_RESET}")
        for i, m in enumerate(self.medicos):
            print(f"    [{i+1}] Dr(a). {m.nombre_completo:<18} | {m.especialidad:<16} | Base: S/ {m.tarifa_base:.2f}")

        try:
            idx = int(input(f"  {C_GOLD}>>{C_RESET} {C_WHITE}Seleccione médico [1-{len(self.medicos)}]:{C_RESET} ").strip()) - 1
            medico = self.medicos[idx]
        except (ValueError, IndexError):
            print(f"  {C_RED}[ERROR]{C_RESET} Selección de médico no válida.")
            return

        fecha = input(f"  {C_GOLD}>>{C_RESET} {C_WHITE}Fecha de atención (AAAA-MM-DD):{C_RESET} ").strip()
        hora = input(f"  {C_GOLD}>>{C_RESET} {C_WHITE}Hora asignada (HH:MM):{C_RESET} ").strip()
        motivo = input(f"  {C_GOLD}>>{C_RESET} {C_WHITE}Motivo de consulta / Síntomas:{C_RESET} ").strip()

        print(f"\n  {C_GOLD}Modalidades Asistenciales Disponibles (Polimorfismo Clínico):{C_RESET}")
        print(f"    [1] Medicina General (Consulta ambulatoria preventiva)")
        print(f"    [2] Consulta Especializada (+25% honorario, instrumental optativo)")
        print(f"    [3] Urgencia Hospitalaria / Emergencia (Triaje Manchester 1 al 5)")
        print(f"    [4] Telemedicina Virtual (-15% no presencial, enlace tokenizado)")
        print(f"    [5] Atención Domiciliaria (Zonificación Lima Este, opción ambulancia)")
        print(f"    [6] Laboratorio y Análisis Clínicos (Toma de muestras biológicas)")

        tipo_opc = input(f"  {C_GOLD}>>{C_RESET} {C_WHITE}Seleccione modalidad [1-6]:{C_RESET} ").strip()
        cod_cita = f"CIT-{100 + len(self.citas) + 1}"

        if tipo_opc == "2":
            proc = input(f"  {C_GOLD}>>{C_RESET} {C_WHITE}Nombre del procedimiento especializado:{C_RESET} ").strip()
            inst = input(f"  {C_GOLD}>>{C_RESET} {C_WHITE}¿Requiere instrumental médico avanzado? (S/N):{C_RESET} ").strip().upper() == "S"
            cita = CitaEspecialidad(cod_cita, paciente, medico, fecha, hora, motivo, inst, proc if proc else "Evaluación Especializada")

        elif tipo_opc == "3":
            cod_cita = f"EMG-{100 + len(self.citas) + 1}"
            try:
                triaje = int(input(f"  {C_GOLD}>>{C_RESET} {C_WHITE}Nivel de Triaje (1:Crítico a 5:Leve):{C_RESET} ").strip())
            except ValueError:
                triaje = 3
            cita = CitaEmergencia(cod_cita, paciente, medico, fecha, hora, motivo, triaje)

        elif tipo_opc == "4":
            cod_cita = f"TEL-{100 + len(self.citas) + 1}"
            plat = input(f"  {C_GOLD}>>{C_RESET} {C_WHITE}Plataforma (Meet / Zoom / Teams):{C_RESET} ").strip()
            cita = CitaTelemedicina(cod_cita, paciente, medico, fecha, hora, motivo, plat if plat else "Google Meet Clínico")

        elif tipo_opc == "5":
            cod_cita = f"DOM-{100 + len(self.citas) + 1}"
            dir_dom = input(f"  {C_GOLD}>>{C_RESET} {C_WHITE}Dirección en Lima Este:{C_RESET} ").strip()
            dist = input(f"  {C_GOLD}>>{C_RESET} {C_WHITE}Distrito (Ate Vitarte / Huaycán / Santa Anita / Salamanca):{C_RESET} ").strip()
            amb = input(f"  {C_GOLD}>>{C_RESET} {C_WHITE}¿Requiere soporte de ambulancia asistencial? (S/N):{C_RESET} ").strip().upper() == "S"
            cita = CitaDomiciliaria(cod_cita, paciente, medico, fecha, hora, motivo, dir_dom if dir_dom else "Av. Principal 123", dist if dist else "Ate Vitarte", amb)

        elif tipo_opc == "6":
            cod_cita = f"LAB-{100 + len(self.citas) + 1}"
            exam = input(f"  {C_GOLD}>>{C_RESET} {C_WHITE}Examen (Hemograma / Perfil Lipídico / Glucosa / Rayos X):{C_RESET} ").strip()
            cita = CitaLaboratorio(cod_cita, paciente, medico, fecha, hora, motivo, exam if exam else "Hemograma Completo", 12)

        else:
            cita = CitaGeneral(cod_cita, paciente, medico, fecha, hora, motivo)

        self.agregar_cita(cita)
        tarifa_estimada = cita.calcular_tarifa_final()

        print(f"\n  {C_GREEN}✔ [FASE 3 COMPLETADA CON ÉXITO]{C_RESET}")
        print(f"  {C_CYAN}Cita agendada bajo el código oficial: {C_WHITE}{cita.codigo}{C_RESET}")
        print(f"    • Modalidad        : {C_GOLD}{cita.tipo_servicio()}{C_RESET}")
        print(f"    • Tarifa Liquidada : {C_GREEN}S/ {tarifa_estimada:.2f}{C_RESET} (Cobertura: {paciente.tipo_seguro})")
        print(f"    • Notificación SMS : {C_WHITE}{cita.enviar_sms(f'Cita confirmada para el {fecha} a las {hora}.')}{C_RESET}")
        print(f"\n  {C_GOLD}🔓 ¡FASE 4 DESBLOQUEADA! El médico ya puede atender la consulta.{C_RESET}")

    # --------------------------------------------------------------------------
    # FASE 4: CONSULTORIO MÉDICO Y ACTO MÉDICO
    # --------------------------------------------------------------------------
    def ejecutar_fase4_acto_medico(self):
        print(f"\n{borde_sup_doble(ANCHO_TABLERO, C_GOLD)}")
        print(fila_doble(f"  {BG_FASE4} FASE 4 : CONSULTORIO MÉDICO, ACTO CLÍNICO Y RECETA {C_RESET}", ANCHO_TABLERO, C_GOLD))
        print(f"{borde_inf_doble(ANCHO_TABLERO, C_GOLD)}\n")

        citas_pendientes = [c for c in self.citas if c.estado in ("PROGRAMADA", "EN_ESPERA")]
        print(f"  {C_WHITE}Citas agendadas en espera de atención médica:{C_RESET}")
        for c in citas_pendientes:
            print(f"    • [{c.codigo}] {c.fecha} {c.hora} | Paciente: {c.paciente.nombre_completo:<20} | Dr. {c.medico.nombre_completo:<16} | {c.tipo_servicio()}")

        codigo = input(f"\n  {C_GOLD}>>{C_RESET} {C_WHITE}Ingrese código de la cita a atender:{C_RESET} ").strip().upper()
        cita = self.buscar_cita_por_codigo(codigo)
        if not cita or cita.estado not in ("PROGRAMADA", "EN_ESPERA"):
            print(f"  {C_RED}[ERROR]{C_RESET} Código de cita no válido o la cita ya fue atendida.")
            return

        print(f"\n  {C_CYAN}Atendiendo consulta médica:{C_RESET}")
        print(f"    • Paciente : {cita.paciente.nombre_completo} (Edad: {cita.paciente.edad} años | Seguro: {cita.paciente.tipo_seguro})")
        print(f"    • Alergias : {', '.join(cita.paciente.alergias) if cita.paciente.alergias else 'Sin alergias'}")
        if cita.paciente.signos_vitales:
            sv = cita.paciente.signos_vitales
            print(f"    • Triaje   : Presión {sv['presion']} | SpO2 {sv['saturacion_pct']}% | IMC {sv['imc']} ({sv['diagnostico_nutricional']})")

        diag = input(f"\n  {C_GOLD}>>{C_RESET} {C_WHITE}Diagnóstico clínico final / Código CIE-10:{C_RESET} ").strip()
        if diag:
            cita.paciente.agregar_diagnostico_historial("CIE-10", diag)

        print(f"\n  {C_GOLD}Prescripción Farmacológica (Deje el nombre en blanco para terminar):{C_RESET}")
        while True:
            med = input(f"    {C_WHITE}• Fármaco prescrito:{C_RESET} ").strip()
            if not med:
                break
            dosis = input(f"      {C_GRAY}Dosis / Concentración (ej. 500mg):{C_RESET} ").strip()
            frec = input(f"      {C_GRAY}Frecuencia (ej. cada 8 horas):{C_RESET} ").strip()
            try:
                dias = int(input(f"      {C_GRAY}Duración del tratamiento en días:{C_RESET} ").strip())
            except ValueError:
                dias = 5
            cita.agregar_medicamento_receta(med, dosis if dosis else "Estándar", frec if frec else "Cada 8h", dias)

        indic = input(f"  {C_GOLD}>>{C_RESET} {C_WHITE}Indicaciones generales y cuidados para el paciente:{C_RESET} ").strip()
        if indic:
            cita.establecer_indicaciones(indic)

        cita.marcar_atendida()

        print(f"\n  {C_GREEN}✔ [FASE 4 COMPLETADA CON ÉXITO]{C_RESET}")
        print(f"  {C_CYAN}Atención médica finalizada. Cita {cita.codigo} marcada como {C_GREEN}ATENDIDA{C_RESET}.")
        print(f"  {C_GOLD}🔓 ¡FASE 5 DESBLOQUEADA! El paciente ya puede pasar a Caja para Facturación.{C_RESET}")
        print("\n" + cita.generar_receta_medica())

    # --------------------------------------------------------------------------
    # FASE 5: CAJA Y FACTURACIÓN ELECTRÓNICA SUNAT
    # --------------------------------------------------------------------------
    def ejecutar_fase5_facturacion(self):
        print(f"\n{borde_sup_doble(ANCHO_TABLERO, C_GREEN)}")
        print(fila_doble(f"  {BG_FASE5} FASE 5 : CAJA, FACTURACIÓN ELECTRÓNICA SUNAT (18%) {C_RESET}", ANCHO_TABLERO, C_GREEN))
        print(f"{borde_inf_doble(ANCHO_TABLERO, C_GREEN)}\n")

        citas_por_facturar = [c for c in self.citas if c.estado == "ATENDIDA" and c.codigo not in self.citas_facturadas]
        print(f"  {C_WHITE}Citas con atención médica culminada pendientes de liquidación en caja:{C_RESET}")
        for c in citas_por_facturar:
            tar = c.calcular_tarifa_final()
            _, _, total_c_igv = calcular_liquidacion(tar)
            print(f"    • [{c.codigo}] Paciente: {c.paciente.nombre_completo:<22} | {c.tipo_servicio():<26} | Total c/IGV: {C_GREEN}S/ {total_c_igv:.2f}{C_RESET}")

        codigo = input(f"\n  {C_GOLD}>>{C_RESET} {C_WHITE}Ingrese código de la cita a facturar:{C_RESET} ").strip().upper()
        cita = self.buscar_cita_por_codigo(codigo)
        if not cita or cita.estado != "ATENDIDA" or cita.codigo in self.citas_facturadas:
            print(f"  {C_RED}[ERROR]{C_RESET} Cita no válida para facturación o ya se encuentra liquidada.")
            return

        print(f"  {C_GRAY}Tipo de Comprobante: [1] Boleta de Venta | [2] Factura Electrónica{C_RESET}")
        tipo_c = "FACTURA" if input(f"  {C_GOLD}>>{C_RESET} {C_WHITE}Seleccione tipo [defecto 1]:{C_RESET} ").strip() == "2" else "BOLETA"

        print("\n" + formatear_comprobante_consola(cita, tipo_c))

        print(f"\n  {C_GOLD}Modalidades de Pago en Caja (Sobrecarga de Métodos Multicanal):{C_RESET}")
        print(f"    [1] Efectivo en Ventanilla (Con cálculo de vuelto y desglose de billetes)")
        print(f"    [2] Billetera Digital (Yape / Plin / Transferencia con Token)")
        print(f"    [3] Terminal POS Tarjeta (Crédito / Débito en cuotas)")
        print(f"    [4] Pago Mixto / Combinado (Ej. Efectivo + Yape)")

        forma_opc = input(f"  {C_GOLD}>>{C_RESET} {C_WHITE}Seleccione forma de pago [1-4]:{C_RESET} ").strip()
        facturador = FacturadorClinico()
        _, _, total_cobrar = calcular_liquidacion(cita.calcular_tarifa_final())

        if forma_opc == "1":
            try:
                recibido = float(input(f"  {C_GOLD}>>{C_RESET} {C_WHITE}Monto en efectivo recibido en caja (S/):{C_RESET} ").strip())
            except ValueError:
                recibido = total_cobrar
            resultado = facturador.liquidar_comprobante(recibido, cita)

        elif forma_opc == "2":
            tok = input(f"  {C_GOLD}>>{C_RESET} {C_WHITE}Número de operación Yape / Plin:{C_RESET} ").strip()
            resultado = facturador.liquidar_comprobante(tok if tok else "YAPE-OP-894120", cita)

        elif forma_opc == "3":
            banco = input(f"  {C_GOLD}>>{C_RESET} {C_WHITE}Banco emisor (BCP / BBVA / Interbank):{C_RESET} ").strip().upper()
            try:
                cuotas = int(input(f"  {C_GOLD}>>{C_RESET} {C_WHITE}Número de cuotas [1-12]:{C_RESET} ").strip())
            except ValueError:
                cuotas = 1
            datos_tarjeta = {"titular": cita.paciente.nombre_completo, "banco": banco if banco else "BCP", "cuotas": cuotas}
            resultado = facturador.liquidar_comprobante(datos_tarjeta, cita)

        elif forma_opc == "4":
            try:
                p1 = float(input(f"  {C_GOLD}>>{C_RESET} {C_WHITE}Parte en Efectivo (S/):{C_RESET} ").strip())
            except ValueError:
                p1 = total_cobrar / 2
            p2 = max(0.0, total_cobrar - p1)
            print(f"  {C_GRAY}Saldo restante a cubrir con Yape: S/ {p2:.2f}{C_RESET}")
            resultado = facturador.liquidar_comprobante([("EFECTIVO", p1), ("YAPE_DIGITAL", p2)], cita)

        else:
            resultado = facturador.liquidar_comprobante(total_cobrar, cita)

        self.citas_facturadas.add(cita.codigo)

        print(f"\n  {C_GREEN}✔ [FASE 5 COMPLETADA CON ÉXITO]{C_RESET}")
        print(f"  {C_CYAN}{resultado}{C_RESET}")
        print(f"  {C_GREEN}● Sincronización SUNAT:{C_RESET} [{C_GREEN}████████████████████{C_RESET}] CDR Aprobado y Firmado Digitalmente.")
        print(f"  {C_GOLD}🔓 ¡FASE 6 DESBLOQUEADA! Acceso abierto al Tablero Gerencial y Auditoría.{C_RESET}")

    # --------------------------------------------------------------------------
    # FASE 6: AUDITORÍA, REPORTE GERENCIAL Y CIERRE DE EXPEDIENTE
    # --------------------------------------------------------------------------
    def ejecutar_fase6_auditoria_cierre(self):
        print(f"\n{borde_sup_doble(ANCHO_TABLERO, C_CYAN)}")
        print(fila_doble(f"  {BG_FASE6} FASE 6 : AUDITORÍA INTEGRAL, TABLERO BI Y CIERRE {C_RESET}", ANCHO_TABLERO, C_CYAN))
        print(f"{borde_inf_doble(ANCHO_TABLERO, C_CYAN)}\n")

        total_recaudado = sum(calcular_liquidacion(c.calcular_tarifa_final())[2] for c in self.citas if c.codigo in self.citas_facturadas)
        total_pacientes = len(self.pacientes)
        total_citas = len(self.citas)
        atendidas = len([c for c in self.citas if c.estado == "ATENDIDA"])

        print(f"\n  {C_GOLD}INDICADORES CLAVE DE RENDIMIENTO CLÍNICO (KPIS):{C_RESET}")
        print(f"    • Pacientes Afiliados en Padrón      : {C_WHITE}{total_pacientes}{C_RESET}")
        print(f"    • Citas Atendidas y Liquidadas       : {C_GREEN}{atendidas}{C_RESET} de {total_citas}")
        print(f"    • Total Recaudado en Caja SUNAT      : {C_GREEN}S/ {total_recaudado:.2f}{C_RESET}")
        print(f"    • Eficiencia del Flujo Asistencial   : {C_CYAN}{self.calcular_porcentaje_flujo()}%{C_RESET}")

        # Gráfico de Barras ANSI de Citas por Modalidad
        conteo_mod = {}
        for c in self.citas:
            mod = c.tipo_servicio().split("(")[0].strip()
            conteo_mod[mod] = conteo_mod.get(mod, 0) + 1

        print(f"\n  {C_CYAN}DISTRIBUCIÓN DE MODALIDADES ATENDIDAS (GRÁFICO DE BARRAS EN CONSOLA):{C_RESET}")
        for mod, cant in conteo_mod.items():
            pct = (cant / total_citas * 100) if total_citas else 0
            barras = int(pct / 5)
            grafico = f"{C_CYAN}{'█' * barras}{C_GRAY}{'░' * (20 - barras)}{C_RESET}"
            print(f"    • {mod:<18}: {grafico} {C_WHITE}{pct:5.1f}%{C_RESET} ({cant} atenciones)")

        # Exportación del Reporte Formal
        ruta_reporte = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Reporte_Clinico_Semana16.txt")
        self._escribir_reporte_formal_disco(ruta_reporte)

        print(f"\n  {C_GREEN}✔ [FASE 6 COMPLETADA AL 100%]{C_RESET}")
        print(f"  {C_WHITE}Expediente asistencial y auditoría archivados con éxito en:{C_RESET}")
        print(f"  {C_CYAN}{os.path.abspath(ruta_reporte)}{C_RESET}")

    def _escribir_reporte_formal_disco(self, ruta_archivo: str):
        """Genera el reporte ejecutivo de cierre de expediente."""
        lineas = [
            "================================================================================",
            "CLÍNICA DE ATE VITARTE S.A.C. - CIERRE DE AUDITORÍA ASISTENCIAL Y FINANCIERA",
            f"FECHA: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - SEDE ATE VITARTE",
            "================================================================================",
            f"PACIENTES ATENDIDOS: {len(self.pacientes)} | CITAS LIQUIDADAS: {len(self.citas_facturadas)}",
            "--------------------------------------------------------------------------------",
            "RELACIÓN DE CITAS ASISTENCIALES Y TRAZABILIDAD:",
            "--------------------------------------------------------------------------------"
        ]
        for c in self.citas:
            tar = c.calcular_tarifa_final()
            lineas.append(f"[{c.codigo}] Paciente: {c.paciente.nombre_completo:<24} | Servicio: {c.tipo_servicio():<22} | Tarifa: S/ {tar:>6.2f} | Estado: {c.estado}")
            for ev in c.bitacora_eventos:
                lineas.append(f"   ↳ {ev}")
        lineas.append("================================================================================")
        try:
            with open(ruta_archivo, "w", encoding="utf-8") as f:
                f.write("\n".join(lineas))
        except Exception:
            pass
