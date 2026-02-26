class ZonificacionService:
    """Servicio para evaluar compatibilidad de zonificación"""
    
    # Zonas permitidas por tipo de negocio
    ZONAS_PERMITIDAS = {
        "bodega": ["ZR", "ZC", "ZT"],
        "minimarket": ["ZR", "ZC", "ZT"],
        "restaurante": ["ZC", "ZT", "ZI"],
        "farmacia": ["ZR", "ZC", "ZT"],
        "peluquería": ["ZR", "ZC", "ZT"],
        "librería": ["ZR", "ZC", "ZT"],
        "taller": ["ZC", "ZI"],
        "gimnasio": ["ZC", "ZT"],
        "discoteca": ["ZC"],
        "gasolinera": ["ZI"],
        "industrial": ["ZI"],
        "oficina": ["ZC", "ZT"],
        "colegio": ["ZR", "ZC"],
        "guardería": ["ZR", "ZC"]
    }
    
    # Distritos de Ica y sus zonas predominantes
    DISTRITOS = {
        "Ica": {
            "centro": "ZC",
            "residencial": "ZR",
            "periferia": "ZR"
        },
        "Parcona": "ZR",
        "La Tinguiña": "ZR",
        "Los Aquijes": "ZR",
        "Subtanjalla": "ZR",
        "Salas": "ZR",
        "Pueblo Nuevo": "ZR",
        "Tate": "ZR",
        "Yauca del Rosario": "ZR",
        "Santiago": "ZR",
        "Ocucaje": "ZR"
    }
    
    @staticmethod
    def evaluar_compatibilidad(rubro: str, distrito: str, direccion: str = "") -> dict:
        """
        Evalúa si el rubro es compatible con la zona
        Retorna: dict con compatible, mensaje, nivel_advertencia
        """
        rubro_lower = rubro.lower()
        distrito_lower = distrito.lower()
        
        # Determinar zona probable
        zona = "ZC"  # Por defecto zona comercial
        if "residencial" in direccion.lower() or "casa" in direccion.lower():
            zona = "ZR"
        elif "industrial" in direccion.lower() or "parque industrial" in direccion.lower():
            zona = "ZI"
        elif "huacachina" in direccion.lower() or "turístico" in direccion.lower():
            zona = "ZT"
        
        # Buscar zonas permitidas para este rubro
        zonas_permitidas = []
        for key, zonas in ZonificacionService.ZONAS_PERMITIDAS.items():
            if key in rubro_lower:
                zonas_permitidas = zonas
                break
        
        if not zonas_permitidas:
            zonas_permitidas = ["ZC", "ZI"]  # Por defecto
        
        # Evaluar compatibilidad
        compatible = zona in zonas_permitidas
        
        if compatible:
            return {
                "compatible": True,
                "mensaje": "✅ El rubro es compatible con la zona seleccionada",
                "nivel_advertencia": "bajo",
                "zona": zona,
                "zonas_permitidas": zonas_permitidas
            }
        else:
            return {
                "compatible": False,
                "mensaje": "⚠️ El rubro podría no ser compatible con esta zona. Se evaluará en la inspección técnica.",
                "nivel_advertencia": "medio",
                "zona": zona,
                "zonas_permitidas": zonas_permitidas,
                "recomendacion": "Verifica que tu local esté en zona comercial o industrial"
            }