# 🏥 CLÍNICA DE ATE VITARTE S.A.C.
### Sistema Integral de Citas Médicas y Facturación Electrónica en Consola

Proyecto desarrollado para el curso **Lenguajes de Programación** (Semana 16 - POO Avanzada en Python)  
**Facultad de Ingeniería - Universidad Tecnológica del Perú (UTP)**  
**Líder de Proyecto:** Julibeth Antonela Jaimes Daza  

---

## 📋 Descripción del Proyecto

Sistema asistencial y financiero hospitalario en consola que implementa un flujo de trabajo clínico secuencial en **6 fases bloqueantes**, aplicando los conceptos avanzados de la Programación Orientada a Objetos (POO), principios Clean Code y estándares tributarios de facturación electrónica SUNAT en el Perú.

---

## 🏛️ Los 4 Pilares de la POO Implementados

1. **Abstracción**:
   - Clase abstracta `CitaMedica` que define los contratos polimórficos (`calcular_tarifa_final`, `tipo_servicio`, `obtener_detalles_servicio`).
   - Uso de módulos `abc.ABC` y `@abstractmethod`.

2. **Encapsulamiento**:
   - Atributos protegidos (`_dni`, `_nombres`, `_colegiatura`, etc.) con propiedades `@property` para lectura y métodos controlados de modificación.

3. **Herencia Simple y Múltiple Cooperativa**:
   - **Simple**: `Persona` $\rightarrow$ `Medico`, `Paciente`, `Enfermero`.
   - **Múltiple Cooperativa (MRO C3)**: `CitaMedica` hereda de:
     - `IdentificableMixin`: Gestión y validación de códigos de serie clínica.
     - `NotificableMixin`: Envío de confirmaciones por SMS, WhatsApp y Email.
     - `AuditableMixin`: Trazabilidad y bitácora inmutable de eventos.
     - `DescontableMixin`: Cupones y convenios promocionales.

4. **Polimorfismo Dinámico**:
   - Implementación especializada del cálculo de tarifa final en 6 subclases:
     - `CitaGeneral`
     - `CitaEspecialidad`
     - `CitaEmergencia` (según triaje Manchester niveles 1 a 5)
     - `CitaTelemedicina`
     - `CitaDomiciliaria` (zonificación Lima Este y ambulancia)
     - `CitaLaboratorio` (según examen analítico)

---

## ⚡ Sobrecarga de Métodos

Implementada en `facturacion.py`:
- **Por número de argumentos / defaults**: `calcular_presupuesto(...)` con parámetros opcionales y convenios institucionales (Comunidad UTP).
- **Por tipo de datos**: `@singledispatchmethod` en `liquidar_comprobante(...)` para procesar pagos en efectivo con vuelto, pasarelas digitales (Yape/Plin), tarjetas POS en cuotas y pagos mixtos.

---

## 🔄 Flujo Asistencial en 6 Fases

```
[ FASE 1: Admisión & Carnet Digital ]
                 ↓
[ FASE 2: Triaje Hospitalario & Signos Vitales (IMC) ]
                 ↓
[ FASE 3: Agendamiento de Citas Médicas ]
                 ↓
[ FASE 4: Consultorio Médico & Receta Oficial (CIE-10) ]
                 ↓
[ FASE 5: Caja & Facturación Electrónica SUNAT (IGV 18% + QR) ]
                 ↓
[ FASE 6: Auditoría Hospitalaria, BI & Cierre de Expediente ]
```

---

## 📁 Estructura del Código

```text
├── modelos.py        # Jerarquía de clases, Mixins, Personas y Citas Médicas
├── facturacion.py    # Sobrecarga con singledispatchmethod, IGV y QR ASCII
├── gestor.py         # Controlador de negocio y gestión del flujo por fases
├── main_citas.py     # Interfaz interactiva de consola con diseño ANSI
└── README.md         # Documentación del proyecto
```

---

## 🚀 Requisitos y Ejecución

- **Python 3.8+** (Recomendado Python 3.10 o superior)

### Ejecución en Windows:

```powershell
# Clona el repositorio
git clone https://github.com/Anto-Jaimes/CLINICA-ATE-PAYTON.git
cd CLINICA-ATE-PAYTON

# Ejecuta con el launcher de Python 3
py main_citas.py
```
