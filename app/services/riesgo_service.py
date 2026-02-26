from app.models.config import Rubro

class RiesgoService:
    """Servicio para clasificar el nivel de riesgo del negocio"""
    
    # Tabla de clasificación de riesgos por rubro
    RIESGOS = {
        # BAJO RIESGO (ITSE Posterior)
        "bajo": [
            "Bodega / Minimarket",
            "Peluquería / Barbería",
            "Librería / Papelería",
            "Tienda de ropa",
            "Internet / Cabina pública",
            "Panadería",
            "Venta de repuestos",
            "Ferretería",
            "Bazar",
            "Florería"
        ],
        
        # MEDIO RIESGO (ITSE Posterior)
        "medio": [
            "Restaurante",
            "Farmacia / Botica",
            "Veterinaria",
            "Taller mecánico",
            "Gimnasio",
            "Clínica veterinaria",
            "Cevichería",
            "Chifa",
            "Pollería",
            "Cafetería"
        ],
        
        # ALTO RIESGO (ITSE Previo)
        "alto": [
            "Discoteca / Karaoke",
            "Pub / Bar",
            "Centro nocturno",
            "Fábrica pequeña",
            "Imprenta",
            "Carpintería",
            "Metal mecánica"
        ],
        
        # MUY ALTO RIESGO (ITSE Previo)
        "muy_alto": [
            "Gasolinera",
            "Planta industrial",
            "Depósito de gas",
            "Pirotecnia",
            "Productos químicos"
        ]
    }
    
    @staticmethod
    def clasificar_riesgo(nombre_rubro: str) -> dict:
        """
        Clasifica el nivel de riesgo según el rubro del negocio
        Retorna: dict con nivel_riesgo, requiere_itse_previa, monto
        """
        nombre_rubro = nombre_rubro.lower().strip()
        
        for nivel, rubros in RiesgoService.RIESGOS.items():
            for rubro in rubros:
                if rubro.lower() in nombre_rubro or nombre_rubro in rubro.lower():
                    # Tarifas según nivel de riesgo
                    tarifas = {
                        "bajo": 140.00,
                        "medio": 150.00,
                        "alto": 170.00,
                        "muy_alto": 192.00
                    }
                    
                    return {
                        "nivel_riesgo": nivel,
                        "requiere_itse_previa": nivel in ["alto", "muy_alto"],
                        "monto": tarifas[nivel],
                        "descripcion": f"Licencia para negocio de {nivel} riesgo"
                    }
        
        # Por defecto: riesgo medio
        return {
            "nivel_riesgo": "medio",
            "requiere_itse_previa": False,
            "monto": 150.00,
            "descripcion": "Licencia para negocio de riesgo medio"
        }
    
    @staticmethod
    def get_anexos_requeridos(nivel_riesgo: str) -> list:
        """
        Retorna lista de anexos requeridos según nivel de riesgo
        """
        anexos_base = [
            {
                "tipo": "anexo_18",
                "nombre": "Anexo 18 - Fotos del local",
                "obligatorio": True,
                "descripcion": "Subir 3 fotos del local (exterior, interior, fachada)"
            }
        ]
        
        if nivel_riesgo in ["bajo", "medio"]:
            anexos_base.extend([
                {
                    "tipo": "anexo_1",
                    "nombre": "Anexo 1 - Solicitud de inspección",
                    "obligatorio": True,
                    "descripcion": "Formulario de solicitud de inspección técnica"
                },
                {
                    "tipo": "anexo_2",
                    "nombre": "Anexo 2 - Características de la vivienda",
                    "obligatorio": True,
                    "descripcion": "Declaración de características (noble/rústico)"
                },
                {
                    "tipo": "anexo_4",
                    "nombre": "Anexo 4 - Declaración de seguridad",
                    "obligatorio": True,
                    "descripcion": "Llaves termomagnéticas, extintores vigentes, sin cable mellizo"
                }
            ])
        
        return anexos_base