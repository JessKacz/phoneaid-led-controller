"""
presets_manager.py - Gerenciador de presets mensais (até 12)
"""
import json
import os
from datetime import datetime


class PresetsManager:
    """
    Gerencia até 12 presets mensais (um para cada mês).
    Salva/carrega de presets/efeitos.json.
    """
    
    MONTHS = [
        "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
    ]
    
    @staticmethod
    def _create_default_presets():
        """Cria presets padrão dinamicamente"""
        return [
            {
                "mes": i + 1,
                "nome_mes": PresetsManager.MONTHS[i],
                "ativo": i == 0,  # Apenas janeiro ativo por padrão
                "tipo": "Cor sólida",
                "color1": "#FF0000",
                "color2": "#0000FF",
                "velocidade": "Médio",
                "wave_width": 10,
                "blink": False,
                "blink_speed": "Médio",
                "descricao": f"Efeito padrão de {PresetsManager.MONTHS[i]}"
            }
            for i in range(12)
        ]
    
    def __init__(self, presets_file=None):
        if presets_file is None:
            presets_file = os.path.join(
                os.path.dirname(__file__), "presets", "efeitos.json"
            )
        self.presets_file = presets_file
        self.presets = self._load_presets()
    
    def _load_presets(self):
        """Carrega presets do arquivo ou cria padrão"""
        os.makedirs(os.path.dirname(self.presets_file), exist_ok=True)
        
        if os.path.exists(self.presets_file) and os.path.getsize(self.presets_file) > 0:
            try:
                with open(self.presets_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("presets", self._create_default_presets())
            except Exception as e:
                print(f"Erro ao carregar presets: {e}. Usando padrão.")
                return self._create_default_presets()
        
        return self._create_default_presets()
    
    def save_presets(self):
        """Salva presets em arquivo"""
        os.makedirs(os.path.dirname(self.presets_file), exist_ok=True)
        with open(self.presets_file, "w", encoding="utf-8") as f:
            json.dump(
                {"presets": self.presets, "last_updated": datetime.now().isoformat()},
                f,
                indent=4,
                ensure_ascii=False
            )
    
    def get_preset(self, mes):
        """Retorna preset de um mês (1-12)"""
        if 1 <= mes <= 12:
            for preset in self.presets:
                if preset["mes"] == mes:
                    return preset
        return None
    
    def update_preset(self, mes, effect_data):
        """Atualiza preset de um mês com dados de efeito"""
        for preset in self.presets:
            if preset["mes"] == mes:
                preset.update(effect_data)
                preset["ativo"] = True
                self.save_presets()
                return True
        return False
    
    def get_all_presets(self):
        """Retorna todos os presets"""
        return self.presets.copy()
    
    def get_active_preset(self):
        """Retorna o preset ativo (ou o primeiro se nenhum estiver ativo)"""
        for preset in self.presets:
            if preset.get("ativo"):
                return preset
        return self.presets[0] if self.presets else None
    
    def set_active_preset(self, mes):
        """Define qual preset é o ativo (só um por vez)"""
        for preset in self.presets:
            preset["ativo"] = (preset["mes"] == mes)
        self.save_presets()
    
    def validate_preset(self, preset):
        """Valida se um preset tem os campos necessários"""
        required_fields = ["mes", "tipo", "color1"]
        return all(field in preset for field in required_fields)
