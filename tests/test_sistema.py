# -*- coding: utf-8 -*-
"""
Pruebas unitarias para el Sistema Integral de Citas Médicas y Facturación.
"""

import os
import sys
import tempfile
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from modelos import (
    Paciente, Medico,
    CitaGeneral, CitaEspecialidad, CitaEmergencia,
    CitaTelemedicina, CitaDomiciliaria, CitaLaboratorio
)
from facturacion import (
    FacturadorClinico, calcular_liquidacion,
    generar_correlativo_sunat, formatear_comprobante_consola
)
from gestor import GestorClinico
from formato_tablero import ancho_visible, ANCHO_TABLERO


class TestSistemaClinico(unittest.TestCase):
    def setUp(self):
        self.medico = Medico("10293847", "Alejandro", "Vargas", "987111222", "CMP-45890", "Cardiología", 100.0, ("08:00", "14:00"))
        self.paciente_part = Paciente("74859612", "Carlos", "Pérez", "999123456", 30, "PARTICULAR", ("Penicilina",), "O+", "carlos@mail.com")
        self.paciente_sis = Paciente("45123678", "Marcos", "Soto", "999888777", 65, "SIS")

    def test_polimorfismo_tarifas_6_modalidades(self):
        c_gen = CitaGeneral("CIT-101", self.paciente_part, self.medico, "2026-11-26", "09:00", "Control")
        c_esp = CitaEspecialidad("CIT-102", self.paciente_part, self.medico, "2026-11-26", "10:00", "Eco", True)
        c_emg = CitaEmergencia("EMG-103", self.paciente_sis, self.medico, "2026-11-26", "11:00", "Fiebre", nivel_triaje=2)
        c_tel = CitaTelemedicina("TEL-104", self.paciente_part, self.medico, "2026-11-26", "12:00", "Consulta")
        c_dom = CitaDomiciliaria("DOM-105", self.paciente_part, self.medico, "2026-11-26", "13:00", "Visita", "Av. Lima 10", "Ate Vitarte", False)
        c_lab = CitaLaboratorio("LAB-106", self.paciente_part, self.medico, "2026-11-26", "08:30", "Examen", "Hemograma Completo")

        self.assertEqual(c_gen.calcular_tarifa_final(), 100.0)
        self.assertEqual(c_esp.calcular_tarifa_final(), 170.0)   # 100*1.25 + 45
        self.assertEqual(c_emg.calcular_tarifa_final(), 23.0)    # (100*1.4 + 90) * 0.10
        self.assertEqual(c_tel.calcular_tarifa_final(), 85.0)    # 100*0.85
        self.assertEqual(c_dom.calcular_tarifa_final(), 185.0)   # 100*1.3 + 35 + 20
        self.assertEqual(c_lab.calcular_tarifa_final(), 75.0)    # 100*0.4 + 35

    def test_correo_real_y_cupon(self):
        self.assertEqual(self.paciente_part.correo, "carlos@mail.com")
        self.assertEqual(self.paciente_sis.correo, "45123678@clinica-atevitarte.pe")
        c = CitaGeneral("CIT-201", self.paciente_part, self.medico, "2026-11-26", "09:00", "Chequeo")
        c.aplicar_cupon_campania(20.0)
        self.assertEqual(c.calcular_tarifa_final(), 80.0)

    def test_facturacion_y_sobrecarga(self):
        sub, igv, tot = calcular_liquidacion(100.0)
        self.assertEqual((sub, igv, tot), (100.0, 18.0, 118.0))

        c = CitaGeneral("CIT-101", self.paciente_part, self.medico, "2026-11-26", "09:00", "Chequeo")
        f = FacturadorClinico()

        # Pago insuficiente en efectivo
        res_bad = f.liquidar_comprobante(50.0, c)
        self.assertFalse(f.ultimo_pago_aprobado)
        self.assertIn("PAGO INCOMPLETO", res_bad)

        # Pago completo en efectivo
        res_ok = f.liquidar_comprobante(150.0, c)
        self.assertTrue(f.ultimo_pago_aprobado)
        self.assertIn("Vuelto: S/ 32.00", res_ok)

        # Pago digital, POS y mixto
        f.liquidar_comprobante("YAPE-12345", c)
        self.assertTrue(f.ultimo_pago_aprobado)

        f.liquidar_comprobante({"banco": "BCP", "cuotas": 2}, c)
        self.assertTrue(f.ultimo_pago_aprobado)

        res_mix_bad = f.liquidar_comprobante([("EFECTIVO", 50.0), ("YAPE", 20.0)], c)
        self.assertFalse(f.ultimo_pago_aprobado)
        self.assertIn("INCOMPLETO", res_mix_bad)

        corr = generar_correlativo_sunat("CIT-101", "FACTURA")
        self.assertTrue(corr.startswith("F002-"))
        self.assertNotIn("--", corr)

    def test_gestor_fases_agenda_y_persistencia(self):
        with tempfile.TemporaryDirectory() as tmp:
            ruta = os.path.join(tmp, "test_clinica.json")
            g = GestorClinico(precargar_datos=False, ruta_datos=ruta)
            self.assertFalse(g.verificar_fase(2)[0])

            g.agregar_paciente(self.paciente_part)
            self.assertTrue(g.verificar_fase(2)[0])
            self.assertFalse(g.verificar_fase(3)[0])

            self.paciente_part.registrar_signos_vitales("120/80", 72, 98, 36.6, 70.0, 1.75)
            self.assertTrue(g.verificar_fase(3)[0])

            # Validar horario fuera de turno y cruce
            ok_fuera, _ = g.horario_medico_disponible(g.medicos[0], "2026-11-26", "20:00")
            self.assertFalse(ok_fuera)

            c = CitaGeneral("CIT-900", self.paciente_part, g.medicos[0], "2026-11-26", "09:00", "Control")
            g.agregar_cita(c)
            ok_cruce, _ = g.horario_medico_disponible(g.medicos[0], "2026-11-26", "09:00")
            self.assertFalse(ok_cruce)

            g.guardar_datos()
            g2 = GestorClinico(precargar_datos=False, ruta_datos=ruta)
            self.assertEqual(len(g2.pacientes), 1)
            self.assertEqual(len(g2.citas), 1)
            self.assertEqual(g2.buscar_cita_por_codigo("CIT-900").paciente.correo, "carlos@mail.com")

    def test_alineacion_tableros_78_cols(self):
        self.paciente_part.registrar_signos_vitales("120/80", 72, 98, 36.6, 70.0, 1.75)
        c = CitaGeneral("CIT-101", self.paciente_part, self.medico, "2026-11-26", "09:00", "Chequeo")
        for doc in (
            self.paciente_part.generar_carnet_digital(),
            c.generar_receta_medica(),
            formatear_comprobante_consola(c, "BOLETA")
        ):
            for linea in doc.splitlines():
                self.assertEqual(ancho_visible(linea), ANCHO_TABLERO + 6)


if __name__ == "__main__":
    unittest.main()
