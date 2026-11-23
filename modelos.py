# -*- coding: utf-8 -*-
"""
================================================================================
CLÍNICA DE ATE VITARTE S.A.C. - SISTEMA DE CITAS MÉDICAS Y FACTURACIÓN
MÓDULO: modelos.py (Semana 16 - POO Avanzada en Consola)
CURSO: LENGUAJES DE PROGRAMACIÓN - UTP (FACULTAD DE INGENIERÍA)
EQUIPO 2 - LÍDER: JULIBETH ANTONELA JAIMES DAZA
================================================================================
DEMOSTRACIÓN INTEGRAL DE LOS 4 PILARES DE LA POO:
1. POO y Abstracción: Clases abstractas (ABC), mixins modulares y encapsulamiento.
2. Clases, Objetos y Constructores: Persona, Medico, Paciente, Enfermero, Citas.
3. Herencia Simple y Múltiple:
   - Simple: Persona -> Medico, Persona -> Paciente, Persona -> Enfermero.
   - Múltiple: CitaMedica(IdentificableMixin, NotificableMixin, AuditableMixin, DescontableMixin, ABC).
4. Polimorfismo Dinámico:
   - Sobreescritura de calcular_tarifa_final() en 6 subtipos de citas:
     General, Especialidad, Emergencia, Telemedicina, Domiciliaria, Laboratorio.
================================================================================
"""

from abc import ABC, abstractmethod
from datetime import datetime


# ==============================================================================
# 1. MIXINS PARA HERENCIA MÚLTIPLE COOPERATIVA
# ==============================================================================
class IdentificableMixin(object):
    """Mixin para gestión y validación de identificadores de serie clínica."""
    def __init__(self, codigo="", **kwargs):
        super(IdentificableMixin, self).__init__(**kwargs)
        self._codigo = str(codigo).strip().upper()

    @property
    def codigo(self):
        return self._codigo

    def validar_codigo(self) -> bool:
        """Valida que el código clínico cumpla con la nomenclatura institucional."""
        return len(self._codigo) >= 6 and "-" in self._codigo


class NotificableMixin(object):
    """Mixin para emisión multicanal de confirmaciones clínicas (SMS, Email, WhatsApp)."""
    def __init__(self, email_contacto="", telefono_contacto="", **kwargs):
        super(NotificableMixin, self).__init__(**kwargs)
        self._email = str(email_contacto).strip()
        self._telefono = str(telefono_contacto).strip()

    def enviar_sms(self, mensaje: str) -> str:
        return f"[SMS -> {self._telefono}] {mensaje}"

    def enviar_email(self, asunto: str, cuerpo: str) -> str:
        return f"[EMAIL -> {self._email} | Asunto: {asunto}] {cuerpo}"

    def enviar_whatsapp(self, mensaje: str) -> str:
        return f"[WHATSAPP OFICIAL -> +51 {self._telefono}] 🏥 Clínica Ate Vitarte: {mensaje}"


class AuditableMixin(object):
    """Mixin para auditoría de eventos clínicos y trazabilidad hospitalaria."""
    def __init__(self, creado_por="SISTEMA_VENTANILLA", **kwargs):
        super(AuditableMixin, self).__init__(**kwargs)
        self._creado_por = str(creado_por).strip()
        self._fecha_creacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._bitacora_eventos = [
            f"[{self._fecha_creacion}] Registro inicial creado por '{self._creado_por}'."
        ]

    @property
    def fecha_creacion(self):
        return self._fecha_creacion

    @property
    def creado_por(self):
        return self._creado_por

    @property
    def bitacora_eventos(self):
        return tuple(self._bitacora_eventos)

    def registrar_evento_auditoria(self, detalle: str):
        marca = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._bitacora_eventos.append(f"[{marca}] {detalle}")


class DescontableMixin(object):
    """Mixin para gestión de bonificaciones, convenios y promociones de salud."""
    def __init__(self, descuento_promocional: float = 0.0, **kwargs):
        super(DescontableMixin, self).__init__(**kwargs)
        self._descuento_promocional = float(descuento_promocional)

    @property
    def descuento_promocional(self):
        return self._descuento_promocional

    def aplicar_cupon_campania(self, monto_descuento: float):
        self._descuento_promocional = max(0.0, float(monto_descuento))


# ==============================================================================
# 2. JERARQUÍA DE PERSONAS (HERENCIA SIMPLE Y ENCAPSULAMIENTO)
# ==============================================================================
class Persona(object):
    """Clase base humana.
    Demuestra: Encapsulamiento con atributos protegidos (_dni, _nombres, _telefono) y getters.
    """
    total_personas_registradas = 0  # Atributo de clase compartido

    def __init__(self, dni: str, nombres: str, apellidos: str, telefono: str, correo: str = ""):
        self._dni = str(dni).strip()
        self._nombres = str(nombres).strip()
        self._apellidos = str(apellidos).strip()
        self._telefono = str(telefono).strip()
        self._correo = str(correo).strip() if correo else f"{self._dni}@clinica-atevitarte.pe"
        Persona.total_personas_registradas += 1

    @property
    def dni(self):
        return self._dni

    @property
    def nombre_completo(self):
        return f"{self._nombres} {self._apellidos}"

    @property
    def telefono(self):
        return self._telefono

    @property
    def correo(self):
        return self._correo

    def obtener_perfil(self) -> str:
        return f"DNI: {self._dni} | {self.nombre_completo} | Tel: {self._telefono}"


class Medico(Persona):
    """Herencia Simple: Especialización de Persona para médicos tratantes."""
    def __init__(self, dni: str, nombres: str, apellidos: str, telefono: str,
                 colegiatura: str, especialidad: str, tarifa_base: float,
                 horario_atencion: tuple = ("08:00", "14:00"), consultorio: str = "Piso 2 - Cons. 204"):
        super(Medico, self).__init__(dni, nombres, apellidos, telefono)
        self._colegiatura = str(colegiatura).strip().upper()
        self._especialidad = str(especialidad).strip()
        self._tarifa_base = float(tarifa_base)
        self._horario_atencion = tuple(horario_atencion)  # TUPLA inmutable
        self._consultorio = str(consultorio).strip()

    @property
    def colegiatura(self):
        return self._colegiatura

    @property
    def especialidad(self):
        return self._especialidad

    @property
    def tarifa_base(self):
        return self._tarifa_base

    @property
    def horario_atencion(self):
        return self._horario_atencion

    @property
    def consultorio(self):
        return self._consultorio

    def obtener_perfil(self) -> str:
        base = super(Medico, self).obtener_perfil()
        return (f"[MÉDICO] {base} | CMP: {self._colegiatura} | "
                f"Esp: {self._especialidad} | Base: S/ {self._tarifa_base:.2f} | "
                f"Horario: {self._horario_atencion[0]} a {self._horario_atencion[1]} | {self._consultorio}")


class Enfermero(Persona):
    """Herencia Simple: Personal de enfermería para triaje y asistencia domiciliaria."""
    def __init__(self, dni: str, nombres: str, apellidos: str, telefono: str,
                 colegiatura_cep: str, area: str = "Triaje Hospitalario", turno: str = "Mañana"):
        super(Enfermero, self).__init__(dni, nombres, apellidos, telefono)
        self._colegiatura_cep = str(colegiatura_cep).strip().upper()
        self._area = str(area).strip()
        self._turno = str(turno).strip()

    @property
    def colegiatura_cep(self):
        return self._colegiatura_cep

    @property
    def area(self):
        return self._area

    @property
    def turno(self):
        return self._turno

    def obtener_perfil(self) -> str:
        base = super(Enfermero, self).obtener_perfil()
        return f"[ENFERMERÍA] {base} | CEP: {self._colegiatura_cep} | Área: {self._area} | Turno: {self._turno}"


class Paciente(Persona):
    """Herencia Simple: Paciente afiliado al sistema con historial y signos vitales."""
    def __init__(self, dni: str, nombres: str, apellidos: str, telefono: str,
                 edad: int, tipo_seguro: str, alergias: tuple = (), tipo_sangre: str = "O+"):
        super(Paciente, self).__init__(dni, nombres, apellidos, telefono)
        self._edad = int(edad)
        self._tipo_seguro = str(tipo_seguro).upper().strip()  # PARTICULAR, EPS, SIS, CONVENIO_UTP
        self._alergias = tuple(alergias)                      # TUPLA inmutable
        self._tipo_sangre = str(tipo_sangre).strip().upper()
        self._signos_vitales = {}                             # Diccionario de últimos signos vitales
        self._historial_diagnosticos = []                     # Lista de diagnósticos previos

    @property
    def edad(self):
        return self._edad

    @property
    def tipo_seguro(self):
        return self._tipo_seguro

    @property
    def alergias(self):
        return self._alergias

    @property
    def tipo_sangre(self):
        return self._tipo_sangre

    @property
    def signos_vitales(self):
        return self._signos_vitales

    @property
    def historial_diagnosticos(self):
        return tuple(self._historial_diagnosticos)

    def es_mayor_de_edad(self) -> bool:
        return self._edad >= 18

    def registrar_signos_vitales(self, presion: str, pulso: int, saturacion: int,
                                 temperatura: float, peso_kg: float, talla_m: float):
        """Registra signos vitales y evalúa el Índice de Masa Corporal (IMC)."""
        imc = round(peso_kg / (talla_m ** 2), 2) if talla_m > 0 else 0.0
        
        if imc < 18.5:
            diag_imc = "Bajo Peso"
        elif 18.5 <= imc < 25.0:
            diag_imc = "Peso Saludable / Normal"
        elif 25.0 <= imc < 30.0:
            diag_imc = "Sobrepeso Grado I"
        else:
            diag_imc = "Obesidad (Riesgo Metabólico)"

        self._signos_vitales = {
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "presion": str(presion).strip(),
            "pulso_lpm": int(pulso),
            "saturacion_pct": int(saturacion),
            "temperatura_c": float(temperatura),
            "peso_kg": float(peso_kg),
            "talla_m": float(talla_m),
            "imc": imc,
            "diagnostico_nutricional": diag_imc
        }

    def agregar_diagnostico_historial(self, codigo_cie10: str, descripcion: str):
        fecha = datetime.now().strftime("%Y-%m-%d")
        self._historial_diagnosticos.append(f"[{fecha}] {codigo_cie10} - {descripcion}")

    def obtener_perfil(self) -> str:
        base = super(Paciente, self).obtener_perfil()
        alergias_txt = ", ".join(self._alergias) if self._alergias else "Ninguna"
        return (f"[PACIENTE] {base} | Edad: {self._edad} años | "
                f"Seguro: {self._tipo_seguro} | Alergias: {alergias_txt} | Sangre: {self._tipo_sangre}")

    def generar_carnet_digital(self) -> str:
        """Genera el Carnet Digital de Afiliado con diseño estilizado en consola."""
        alergias_txt = ", ".join(self._alergias) if self._alergias else "Ninguna registrada"
        seguro_badge = f"[ {self._tipo_seguro} ]"
        imc_txt = f"{self._signos_vitales.get('imc', 'N/A')} ({self._signos_vitales.get('diagnostico_nutricional', 'Sin registro')})" if self._signos_vitales else "Pendiente de Triaje"
        
        lineas = [
            "\033[1;96m╔══════════════════════════════════════════════════════════════════════════════════╗\033[0m",
            f"\033[1;96m║\033[0m  \033[44;1;97m CLINICA DE ATE VITARTE S.A.C. \033[0m   \033[1;93mCARNET DIGITAL DE AFILIADO AL SISTEMA\033[0m      \033[1;96m║\033[0m",
            "\033[1;96m╠══════════════════════════════════════════════════════════════════════════════════╣\033[0m",
            f"\033[1;96m║\033[0m  \033[1;93m┌──────────────┐\033[0m   \033[1;97mAfiliado  :\033[0m \033[1;96m{self.nombre_completo:<49}\033[0m\033[1;96m║\033[0m",
            f"\033[1;96m║\033[0m  \033[1;93m│  [ 👤 FOTO ] │\033[0m   \033[1;97mDNI       :\033[0m {self.dni:<18} \033[1;97mGrupo Sang:\033[0m \033[1;91m{self._tipo_sangre:<10}\033[0m \033[1;96m║\033[0m",
            f"\033[1;96m║\033[0m  \033[1;93m│   PACIENTE   │\033[0m   \033[1;97mCobertura :\033[0m \033[1;92m{seguro_badge:<18}\033[0m \033[1;97mEdad      :\033[0m {self._edad} anios      \033[1;96m║\033[0m",
            f"\033[1;96m║\033[0m  \033[1;93m│   TITULAR    │\033[0m   \033[1;97mTelefono  :\033[0m {self.telefono:<18} \033[1;97mEstado    :\033[0m \033[1;93mACTIVO         \033[0m \033[1;96m║\033[0m",
            f"\033[1;96m║\033[0m  \033[1;93m└──────────────┘\033[0m   \033[1;97mAlergias  :\033[0m \033[90m{alergias_txt[:48]:<49}\033[0m\033[1;96m║\033[0m",
            f"\033[1;96m║\033[0m  \033[1;97mSignos / IMC  :\033[0m   \033[1;94m{imc_txt[:64]:<64}\033[0m   \033[1;96m║\033[0m",
            "\033[1;96m╠══════════════════════════════════════════════════════════════════════════════════╣\033[0m",
            "\033[1;96m║\033[0m  \033[90m||| | ||||| || |||||| | ||||| ||| |||| | |||||| ||||| | ||| |||| | |||| |||||   \033[0m\033[1;96m║\033[0m",
            "\033[1;96m║\033[0m  \033[90mCredencial digital valida para atenciones ambulatorias, urgencias y telemedicina \033[0m\033[1;96m║\033[0m",
            "\033[1;96m╚══════════════════════════════════════════════════════════════════════════════════╝\033[0m"
        ]
        return "\n".join(lineas)


# ==============================================================================
# 3. HERENCIA MÚLTIPLE Y CLASE ABSTRACTA BASE (CitaMedica)
# ==============================================================================
class CitaMedica(IdentificableMixin, NotificableMixin, AuditableMixin, DescontableMixin, ABC):
    """
    Herencia Múltiple Cooperativa:
    Deriva simultáneamente de IdentificableMixin, NotificableMixin, AuditableMixin,
    DescontableMixin y ABC (Abstract Base Class).
    Demuestra: Resolución determinista con el Algoritmo C3 (MRO) y Polimorfismo.
    """
    total_citas_generadas = 0  # Atributo de clase

    def __init__(self, codigo: str, paciente: Paciente, medico: Medico, fecha: str, hora: str, motivo: str, creado_por="VENTANILLA"):
        super(CitaMedica, self).__init__(
            codigo=codigo,
            email_contacto=paciente.correo,
            telefono_contacto=paciente.telefono,
            creado_por=creado_por,
            descuento_promocional=0.0
        )
        self._paciente = paciente
        self._medico = medico
        self._fecha = fecha
        self._hora = hora
        self._motivo = motivo
        self._estado = "PROGRAMADA"  # PROGRAMADA, EN_ESPERA, ATENDIDA, CANCELADA
        self._receta_prescrita = []   # Lista de medicamentos prescritos
        self._indicaciones_medicas = ""
        CitaMedica.total_citas_generadas += 1

    @property
    def paciente(self):
        return self._paciente

    @property
    def medico(self):
        return self._medico

    @property
    def fecha(self):
        return self._fecha

    @property
    def hora(self):
        return self._hora

    @property
    def motivo(self):
        return self._motivo

    @property
    def estado(self):
        return self._estado

    @property
    def receta_prescrita(self):
        return tuple(self._receta_prescrita)

    @property
    def indicaciones_medicas(self):
        return self._indicaciones_medicas

    def marcar_en_espera(self):
        self._estado = "EN_ESPERA"
        self.registrar_evento_auditoria("Paciente ingresó a sala de espera.")

    def marcar_atendida(self):
        self._estado = "ATENDIDA"
        self.registrar_evento_auditoria("Atención médica culminada con éxito.")

    def marcar_cancelada(self, motivo: str = "Cancelación solicitada por usuario"):
        self._estado = "CANCELADA"
        self.registrar_evento_auditoria(f"Cita cancelada: {motivo}")

    def reprogramar(self, nueva_fecha: str, nueva_hora: str):
        anterior = f"{self._fecha} {self._hora}"
        self._fecha = nueva_fecha
        self._hora = nueva_hora
        self.registrar_evento_auditoria(f"Reprogramada de {anterior} a {nueva_fecha} {nueva_hora}.")

    def agregar_medicamento_receta(self, medicamento: str, dosis: str, frecuencia: str, duracion_dias: int):
        item = {
            "medicamento": str(medicamento).strip(),
            "dosis": str(dosis).strip(),
            "frecuencia": str(frecuencia).strip(),
            "duracion": f"{duracion_dias} días"
        }
        self._receta_prescrita.append(item)

    def establecer_indicaciones(self, texto: str):
        self._indicaciones_medicas = str(texto).strip()

    # MÉTODOS ABSTRACTOS POLIMÓRFICOS
    @abstractmethod
    def calcular_tarifa_final(self) -> float:
        """Contrato polimórfico: cada categoría de cita calcula su importe."""
        pass

    @abstractmethod
    def tipo_servicio(self) -> str:
        """Retorna la denominación del tipo de servicio asistencial."""
        pass

    @abstractmethod
    def obtener_detalles_servicio(self) -> str:
        """Detalle complementario específico de cada subclase."""
        pass

    def generar_receta_medica(self) -> str:
        """Genera e imprime el documento de Receta Médica Oficial en consola."""
        fecha_actual = datetime.now().strftime("%d/%m/%Y")
        lineas = [
            "\033[1;92m╔════════════════════════════════════════════════════════════════════════════════════════╗\033[0m",
            f"\033[1;92m║\033[0m  \033[42;1;30m CLINICA DE ATE VITARTE S.A.C. \033[0m   \033[1;97mRECETA Y PRESCRIPCIÓN MÉDICA OFICIAL\033[0m       \033[1;92m║\033[0m",
            f"\033[1;92m║\033[0m  \033[90mRUC: 20548963211 • Av. Nicolás Ayllón 5840, Ate • Tel: (01) 351-8900\033[0m                \033[1;92m║\033[0m",
            "\033[1;92m╠════════════════════════════════════════════════════════════════════════════════════════╣\033[0m",
            f"\033[1;92m║\033[0m  \033[1;93mCÓDIGO CITA :\033[0m {self.codigo:<20} \033[1;93mFECHA EMISIÓN :\033[0m {fecha_actual:<24} \033[1;92m║\033[0m",
            f"\033[1;92m║\033[0m  \033[1;97mPACIENTE    :\033[0m {self.paciente.nombre_completo:<42} \033[1;97mDNI:\033[0m {self.paciente.dni:<11} \033[1;92m║\033[0m",
            f"\033[1;92m║\033[0m  \033[1;97mMÉDICO      :\033[0m Dr(a). {self.medico.nombre_completo:<37} \033[1;97mCMP:\033[0m {self.medico.colegiatura:<11} \033[1;92m║\033[0m",
            f"\033[1;92m║\033[0m  \033[1;97mESPECIALIDAD:\033[0m {self.medico.especialidad:<42} \033[1;97mSEGURO:\033[0m {self.paciente.tipo_seguro:<8} \033[1;92m║\033[0m",
            f"\033[1;92m║\033[0m  \033[1;97mDIAGNÓSTICO :\033[0m {self.motivo:<68} \033[1;92m║\033[0m",
            "\033[1;92m╠════════════════════════════════════════════════════════════════════════════════════════╣\033[0m",
            f"\033[1;92m║\033[0m  \033[1;93mFARMACOTERAPIA PRESCRITA:\033[0m                                                             \033[1;92m║\033[0m"
        ]

        if self._receta_prescrita:
            for i, med in enumerate(self._receta_prescrita, 1):
                farma = f"  {i}. {med['medicamento']} ({med['dosis']}) - Tomar {med['frecuencia']} por {med['duracion']}."
                lineas.append(f"\033[1;92m║\033[0m  \033[1;97m{farma:<84}\033[0m\033[1;92m║\033[0m")
        else:
            lineas.append(f"\033[1;92m║\033[0m  \033[90m  1. Paracetamol 500mg - Tomar 1 tableta cada 8 horas si hay dolor o fiebre (3 días).\033[0m \033[1;92m║\033[0m")
            lineas.append(f"\033[1;92m║\033[0m  \033[90m  2. Hidratación oral continua (abundante líquido tibio).\033[0m                             \033[1;92m║\033[0m")

        ind_texto = self._indicaciones_medicas if self._indicaciones_medicas else "Reposo relativo por 48 horas. Control de signos y reevaluación si persisten síntomas."
        lineas.extend([
            "\033[1;92m╠════════════════════════════════════════════════════════════════════════════════════════╣\033[0m",
            f"\033[1;92m║\033[0m  \033[1;93mINDICACIONES Y CUIDADOS GENERALES:\033[0m                                                    \033[1;92m║\033[0m",
            f"\033[1;92m║\033[0m  \033[1;97m  {ind_texto[:82]:<82}\033[0m\033[1;92m║\033[0m",
            "\033[1;92m╠════════════════════════════════════════════════════════════════════════════════════════╣\033[0m",
            f"\033[1;92m║\033[0m  \033[90mFIRMA Y SELLO DIGITAL CMP: __________________________   SELLO DE DISPENSACIÓN FARMACIA\033[0m\033[1;92m║\033[0m",
            "\033[1;92m╚════════════════════════════════════════════════════════════════════════════════════════╝\033[0m"
        ])
        return "\n".join(lineas)


# ==============================================================================
# 4. POLIMORFISMO DINÁMICO: 6 SUBCLASES ESPECIALIZADAS DE CITA
# ==============================================================================

class CitaGeneral(CitaMedica):
    """Subclase 1: Consulta de medicina general preventiva con cobertura por seguro."""
    def tipo_servicio(self) -> str:
        return "Medicina General"

    def obtener_detalles_servicio(self) -> str:
        return "Atención ambulatoria preventiva en consultorio estándar."

    def calcular_tarifa_final(self) -> float:
        tarifa = self._medico.tarifa_base
        if self._paciente.tipo_seguro == "SIS":
            tarifa *= 0.20  # 80% cubierto por el Estado
        elif self._paciente.tipo_seguro == "EPS":
            tarifa *= 0.50  # 50% copago seguro privado
        elif self._paciente.tipo_seguro == "CONVENIO_UTP":
            tarifa *= 0.70  # 30% beneficio comunidad universitaria
        subtotal = max(0.0, tarifa - self._descuento_promocional)
        return round(subtotal, 2)


class CitaEspecialidad(CitaMedica):
    """Subclase 2: Consulta especializada con posible instrumental y procedimientos."""
    def __init__(self, codigo: str, paciente: Paciente, medico: Medico,
                 fecha: str, hora: str, motivo: str, requiere_instrumental: bool = False,
                 procedimiento: str = "Evaluación Diagnóstica Avanzada", creado_por="VENTANILLA"):
        super(CitaEspecialidad, self).__init__(codigo, paciente, medico, fecha, hora, motivo, creado_por)
        self._requiere_instrumental = bool(requiere_instrumental)
        self._procedimiento = str(procedimiento).strip()

    @property
    def requiere_instrumental(self):
        return self._requiere_instrumental

    @property
    def procedimiento(self):
        return self._procedimiento

    def tipo_servicio(self) -> str:
        return f"Especialidad ({self._medico.especialidad})"

    def obtener_detalles_servicio(self) -> str:
        inst = "Con instrumental quirúrgico/biomédico" if self._requiere_instrumental else "Sin instrumental adicional"
        return f"Procedimiento: {self._procedimiento} | {inst}"

    def calcular_tarifa_final(self) -> float:
        tarifa = self._medico.tarifa_base * 1.25  # +25% honorario especialista
        if self._requiere_instrumental:
            tarifa += 45.0  # Insumos / esterilización / equipos
        if self._paciente.tipo_seguro == "EPS":
            tarifa *= 0.60
        elif self._paciente.tipo_seguro == "SIS":
            tarifa *= 0.35
        elif self._paciente.tipo_seguro == "CONVENIO_UTP":
            tarifa *= 0.75
        subtotal = max(0.0, tarifa - self._descuento_promocional)
        return round(subtotal, 2)


class CitaEmergencia(CitaMedica):
    """Subclase 3: Atención de urgencia priorizada según nivel de triaje hospitalario (1 al 5)."""
    def __init__(self, codigo: str, paciente: Paciente, medico: Medico,
                 fecha: str, hora: str, motivo: str, nivel_triaje: int = 3, creado_por="TRIAJE_URGENCIAS"):
        super(CitaEmergencia, self).__init__(codigo, paciente, medico, fecha, hora, motivo, creado_por)
        self._nivel_triaje = int(nivel_triaje)

    @property
    def nivel_triaje(self):
        return self._nivel_triaje

    def tipo_servicio(self) -> str:
        return f"Urgencia (Triaje Nivel {self._nivel_triaje})"

    def obtener_badge_triaje(self) -> str:
        niveles = {
            1: ("\033[41;1;97m TRIAJE 1: RESUCITACIÓN / PARO CARDÍACO \033[0m", "Atención Inmediata (0 min)"),
            2: ("\033[45;1;97m TRIAJE 2: EMERGENCIA CRÍTICA / INFARTO \033[0m", "Tiempo máx espera: 10 min"),
            3: ("\033[43;1;30m TRIAJE 3: URGENCIA SEVERA / FIEBRE ALTA \033[0m", "Tiempo máx espera: 30 min"),
            4: ("\033[44;1;97m TRIAJE 4: URGENCIA MENOR / TRAUMATISMO \033[0m", "Tiempo máx espera: 60 min"),
            5: ("\033[42;1;30m TRIAJE 5: NO URGENTE / CONTROL LEVE \033[0m", "Tiempo máx espera: 120 min")
        }
        badge, tiempo = niveles.get(self._nivel_triaje, ("\033[43;1;30m TRIAJE GENERAL \033[0m", "Estándar"))
        return f"{badge} -> {tiempo}"

    def obtener_detalles_servicio(self) -> str:
        return f"Clasificación Manchester: Nivel {self._nivel_triaje} | Tópico de Emergencias"

    def calcular_tarifa_final(self) -> float:
        recargos = {1: 120.0, 2: 90.0, 3: 60.0, 4: 30.0, 5: 10.0}
        adicional = recargos.get(self._nivel_triaje, 40.0)
        tarifa = (self._medico.tarifa_base * 1.40) + adicional
        if self._paciente.tipo_seguro == "EPS":
            tarifa *= 0.40
        elif self._paciente.tipo_seguro == "SIS":
            tarifa *= 0.10  # Ley de Emergencia Médica en Perú
        elif self._paciente.tipo_seguro == "CONVENIO_UTP":
            tarifa *= 0.60
        subtotal = max(0.0, tarifa - self._descuento_promocional)
        return round(subtotal, 2)


class CitaTelemedicina(CitaMedica):
    """Subclase 4 (NUEVA): Consulta médica virtual a distancia.
    Ahorra costos de infraestructura (-15%) y genera enlace digital tokenizado.
    """
    def __init__(self, codigo: str, paciente: Paciente, medico: Medico,
                 fecha: str, hora: str, motivo: str, plataforma: str = "Google Meet Clínico",
                 creado_por="PORTAL_WEB"):
        super(CitaTelemedicina, self).__init__(codigo, paciente, medico, fecha, hora, motivo, creado_por)
        self._plataforma = str(plataforma).strip()
        self._enlace_sala = f"https://telemedicina.clinica-atevitarte.pe/sala/{self._codigo.lower()}"

    @property
    def plataforma(self):
        return self._plataforma

    @property
    def enlace_sala(self):
        return self._enlace_sala

    def tipo_servicio(self) -> str:
        return f"Telemedicina ({self._plataforma})"

    def obtener_detalles_servicio(self) -> str:
        return f"Sala Virtual: {self._enlace_sala} | Enlace seguro con encriptación TLS 1.3"

    def calcular_tarifa_final(self) -> float:
        # 15% de descuento directo por modalidad no presencial
        tarifa = self._medico.tarifa_base * 0.85
        if self._paciente.tipo_seguro == "SIS":
            tarifa *= 0.15  # Cobertura prioritaria Minsa Teleatiendo
        elif self._paciente.tipo_seguro == "EPS":
            tarifa *= 0.45
        elif self._paciente.tipo_seguro == "CONVENIO_UTP":
            tarifa *= 0.65
        subtotal = max(0.0, tarifa - self._descuento_promocional)
        return round(subtotal, 2)


class CitaDomiciliaria(CitaMedica):
    """Subclase 5 (NUEVA): Atención médica y paramédica en el domicilio del paciente.
    Aplica recargos por desplazamiento geográfico en distritos de Lima Este.
    """
    def __init__(self, codigo: str, paciente: Paciente, medico: Medico,
                 fecha: str, hora: str, motivo: str, direccion: str,
                 distrito: str = "Ate Vitarte", requiere_ambulancia: bool = False,
                 creado_por="URGENCIAS_MOVIL"):
        super(CitaDomiciliaria, self).__init__(codigo, paciente, medico, fecha, hora, motivo, creado_por)
        self._direccion = str(direccion).strip()
        self._distrito = str(distrito).strip()
        self._requiere_ambulancia = bool(requiere_ambulancia)

    @property
    def direccion(self):
        return self._direccion

    @property
    def distrito(self):
        return self._distrito

    @property
    def requiere_ambulancia(self):
        return self._requiere_ambulancia

    def tipo_servicio(self) -> str:
        amb = " (Con Ambulancia Móvil)" if self._requiere_ambulancia else ""
        return f"Atención Domiciliaria{amb}"

    def obtener_detalles_servicio(self) -> str:
        return f"Dir: {self._direccion}, {self._distrito} | Unidad Asistencial Móvil Sede Este"

    def calcular_tarifa_final(self) -> float:
        # Tarifario de movilidad por zonificación en Lima Este
        recargos_zona = {
            "Ate Vitarte": 35.0,
            "Santa Anita": 45.0,
            "Huaycán": 50.0,
            "Salamanca": 40.0,
            "Chaclacayo": 65.0,
            "La Molina": 55.0
        }
        costo_traslado = recargos_zona.get(self._distrito, 45.0)
        costo_soporte = 60.0 if self._requiere_ambulancia else 20.0
        tarifa = (self._medico.tarifa_base * 1.30) + costo_traslado + costo_soporte
        if self._paciente.tipo_seguro == "EPS":
            tarifa *= 0.55
        elif self._paciente.tipo_seguro == "SIS":
            tarifa *= 0.30
        elif self._paciente.tipo_seguro == "CONVENIO_UTP":
            tarifa *= 0.70
        subtotal = max(0.0, tarifa - self._descuento_promocional)
        return round(subtotal, 2)


class CitaLaboratorio(CitaMedica):
    """Subclase 6 (NUEVA): Procedimiento diagnóstico y toma de muestras analíticas."""
    def __init__(self, codigo: str, paciente: Paciente, medico: Medico,
                 fecha: str, hora: str, motivo: str, tipo_examen: str = "Hemograma Completo",
                 horas_entrega: int = 12, creado_por="LABORATORIO_CENTRAL"):
        super(CitaLaboratorio, self).__init__(codigo, paciente, medico, fecha, hora, motivo, creado_por)
        self._tipo_examen = str(tipo_examen).strip()
        self._horas_entrega = int(horas_entrega)

    @property
    def tipo_examen(self):
        return self._tipo_examen

    @property
    def horas_entrega(self):
        return self._horas_entrega

    def tipo_servicio(self) -> str:
        return f"Laboratorio ({self._tipo_examen})"

    def obtener_detalles_servicio(self) -> str:
        return f"Análisis: {self._tipo_examen} | Entrega de resultados en {self._horas_entrega} horas hábiles"

    def calcular_tarifa_final(self) -> float:
        aranceles_lab = {
            "Hemograma Completo": 35.0,
            "Perfil Lipídico": 55.0,
            "Glucosa e Insulina": 40.0,
            "Rayos X Torácico": 75.0,
            "Ecografía Abdominal": 110.0,
            "Prueba Rápida Bioquímica": 45.0
        }
        costo_analisis = aranceles_lab.get(self._tipo_examen, 50.0)
        tarifa = (self._medico.tarifa_base * 0.40) + costo_analisis
        if self._paciente.tipo_seguro == "EPS":
            tarifa *= 0.40
        elif self._paciente.tipo_seguro == "SIS":
            tarifa *= 0.20
        elif self._paciente.tipo_seguro == "CONVENIO_UTP":
            tarifa *= 0.60
        subtotal = max(0.0, tarifa - self._descuento_promocional)
        return round(subtotal, 2)
