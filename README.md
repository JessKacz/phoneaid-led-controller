# PhoneAid LED Controller

Sistema de controle de LEDs para fachada com interface desktop intuitiva. Permite mapear, configurar e criar efeitos luminosos customizados para uma fita contínua de LEDs WS2812B (Neopixel) conectada via Arduino.

## 🎯 Características

- **Mapear LEDs por letra** — Configure quantos LEDs controlam cada letra (P, H, O, N, E, A, I, D)
- **Preview em tempo real** — Visualize a fita linear com overlay das letras antes de fazer upload
- **12 Presets Mensais** — Salve até 12 efeitos diferentes (um para cada mês/estação)
- **3 Tipos de Efeitos** — Cor Sólida, Gradiente e Onda (com parâmetros customizáveis)
- **Gerar Firmware** — Compile automaticamente código Arduino (.ino) com os efeitos salvos
- **Monitoramento de Conexão** — Veja o status do Arduino em tempo real durante execução
- **Hover para detalhes** — Passe o mouse sobre a fita para ver o número de cada LED

## 🏗️ Arquitetura

```
PHONEAID LED Controller
├── Interface Desktop (PyQt5)
│   ├── Aba "Configurar LEDs" → Mapear LEDs por letra
│   ├── Aba "Efeitos" → Editor visual de efeitos + preview linear
│   └── Aba "Instalador" → Compilar firmware + upload para Arduino
├── Gerenciador de Configuração
│   ├── config.json → Mapeamento e efeito atual
│   └── presets/efeitos.json → Até 12 presets mensais
├── Monitor de Conexão
│   └── Thread background monitorando status Arduino
└── Firmware Generator
    └── Gera código Arduino customizado com efeitos compilados
```

## 📦 Dependências

- Python 3.8+
- PyQt5
- pyserial
- FastLED (Arduino library)

Instale as dependências Python:

```bash
pip install -r requirements.txt
```

## 🚀 Como Usar

### 1. Executar a Aplicação

```bash
python app/main.py
```

### 2. Configurar Mapeamento de LEDs

1. Vá à aba **"Configurar LEDs"**
2. Defina o **total de LEDs** na fita
3. Para cada letra (P, H, O, N, E, A, I, D), defina o intervalo de LEDs
   - Exemplo: Letra P usa LEDs 00 até 05
4. Clique **"Salvar Mapeamento"**

### 3. Criar/Editar Efeitos

1. Vá à aba **"Efeitos"**
2. Escolha o tipo de efeito (Cor Sólida, Gradiente, Onda)
3. Configure cores e velocidade
4. Veja o **preview linear** em tempo real (mostra a fita com overlay das letras)
5. Clique **"Salvar como Preset"** e escolha um mês (01-12)

### 4. Fazer Upload para o Arduino

1. Vá à aba **"Instalador"**
2. Conecte seu Arduino via USB
3. Selecione o preset que quer enviar
4. Clique **"Compilar Firmware"** (gera código Arduino)
5. Verifique o preview do código gerado
6. Clique **"Fazer Upload"** (envia para o Arduino)
7. Desconecte e o Arduino ficará rodando o novo efeito

## 📋 Estrutura de Arquivos

```
phoneaid-led-controller/
├── app/
│   ├── main.py                  # Ponto de entrada da aplicação
│   ├── config_manager.py        # Gerencia config.json e persistência
│   ├── serial_utils.py          # Utilidades de comunicação serial
│   ├── config.json              # Configuração do mapeamento
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── effects_tab.py       # Aba de efeitos com preview
│   │   ├── config_tab.py        # Aba de configuração de LEDs
│   │   ├── installer_tab.py     # Aba de compilação e upload
│   │   └── widgets.py           # Widget de preview linear
│   ├── presets/
│   │   └── efeitos.json         # 12 presets mensais
│   ├── firmware/
│   │   └── firmware_template.ino # Template para gerar firmware
│   └── firmware_generator.py    # Gerador de código Arduino
├── assets/
│   └── icon_phoneaid.png        # Ícone da aplicação
├── requirements.txt
└── README.md
```

## 🎨 Preview Linear

O preview mostra uma fita contínua de LEDs (círculos coloridos) com overlay das letras:

```
LED 00  LED 01  LED 02  ...  LED 91
  ●─────●─────●─────●─────...─●

  [P:00-05]  [H:06-11]  [O:12-18] ...
```

- **Circulos** = LEDs individuais com suas cores atuais
- **Rótulos** = Letra e range de LEDs (ex: P:00-05)
- **Hover** = Passe o mouse para ver o número exato do LED

## ⚙️ Efeitos Disponíveis

### Cor Sólida
Uma cor única em todos os LEDs. Opção de piscar (com velocidade ajustável).

```json
{
  "tipo": "Cor sólida",
  "color1": "#FF0000",
  "velocidade": null
}
```

### Gradiente
Transição suave entre duas cores. Opção de piscar alternado.

```json
{
  "tipo": "Gradiente",
  "color1": "#FF0000",
  "color2": "#0000FF",
  "velocidade": "Médio"
}
```

### Onda
Movimento contínuo de uma cor que passa pela fita.

```json
{
  "tipo": "Onda",
  "color1": "#FF0000",
  "color2": "#000000",
  "velocidade": "Lento",
  "wave_width": 15
}
```

## 🔧 Hardware

- **Arduino** (Uno, Mega, Nano)
- **Fita WS2812B (Neopixel)** — LEDs RGB endereçáveis
- **Fonte de alimentação** — 5V/2A+ (depende da quantidade de LEDs)
- **Capacitor** — 100µF entre 5V e GND (perto dos LEDs)
- **Resistor** — 330Ω no sinal de dados (DIN)

### Conexão Típica

```
Arduino Pin 6 (DATA_PIN) → 330Ω Resistor → WS2812B DIN
Arduino 5V → WS2812B 5V
Arduino GND → WS2812B GND
```

## 📡 Fluxo de Dados

1. **Usuário edita efeito** na interface
2. **Preview atualiza em tempo real** mostrando como ficará
3. **Salva preset** em JSON (até 12 por mês)
4. **Gera firmware** compilando código Arduino customizado
5. **Faz upload** via Arduino IDE ou CLI
6. **Arduino rebooteia** e roda novo efeito indefinidamente
7. **Próxima mudança?** Repita o processo

## 🔌 Status de Conexão

Durante a execução da aplicação, o status de conexão com o Arduino é monitorado em background:

- 🟢 **Conectado** — Arduino foi detectado na porta serial
- 🔴 **Desconectado** — Arduino não está conectado ou foi desconectado
- 🟡 **Erro** — Problema de driver ou permissão

Verifique o status na aba "Instalador" antes de fazer upload.

## 🆕 Detecção automática e Firmware Multi-Portas

Novas funcionalidades adicionadas (desde dezembro/2025):

- Botão **🔎 Encontrar Arduino** na aba **Instalador** — varre as portas seriais do sistema, tenta uma validação mínima de comunicação e seleciona automaticamente a porta onde um Arduino plausível foi encontrado. Se nada for encontrado, o app mostra instruções úteis (verificar cabo, drivers, Gerenciador de Dispositivos no Windows).
- Detecção usa heurística (descrição/VID/PID e tentativa de abrir a porta). Para detecção mais robusta é possível usar um handshake (PING/PONG) — isso requer que o firmware rodando no Arduino responda ao ping.

### Firmware multi-portas

O gerador de firmware agora suporta gerar código que controla várias saídas (portas) do Arduino em paralelo. Por limitações da biblioteca FastLED, os pinos de dados precisam ser constantes em tempo de compilação — por isso o gerador cria chamadas `FastLED.addLeds<WS2812B, PIN, GRB>(...)` separadas para cada pino listado.

Onde configurar os pinos:
- Você pode definir quais pinos serão usados editando o `app/config.json` adicionando a chave `"data_pins": [2,3,4]` (exemplo) ou deixá-la ausente para usar o padrão `[2,3,4,5,6,7]`.

Observações importantes:
- Se você usar menos portas que o padrão, o gerador irá criar apenas as chamadas necessárias (por exemplo, 3 pinos → 3 chamadas `addLeds`).
- Ao colar o código no Arduino IDE, a compilação funciona porque cada pino aparece como constante no código gerado (resolve o erro de "not usable in a constant expression").
- Se quiser que a detecção seja estrita (confirmação via handshake), podemos incluir um pequeno handler serial no firmware gerado para responder a um `PING` com `PONG` — recomendo isso para instalações onde vários dispositivos USB podem confundir a heurística.

Para quaisquer ajustes de pinos ou integração handshake, veja as seções de configuração ou abra uma issue no repositório.

## 🐛 Troubleshooting

### Arduino não detectado
- Verifique o cabo USB (tente outro)
- Instale drivers CH340 (comum em Arduino clones)
- Tente em outra porta USB

### Firmware não compila
- Verifique se a biblioteca FastLED está instalada (Arduino IDE → Sketch → Include Library → Manage Libraries)
- Confirme que o total de LEDs e mapeamento estão corretos em "Configurar LEDs"

### LEDs não ligam após upload
- Verifique alimentação (5V) na fita
- Confirme que o DATA_PIN (Arduino pino 6) está conectado corretamente
- Teste com um LED simples antes de toda a fita

## 📝 Changelog

### v1.0.0 (2025-12-08)
- ✅ Interface desktop com 3 abas
- ✅ Configuração de mapeamento de LEDs
- ✅ Editor visual de efeitos com preview linear
- ✅ Sistema de 12 presets mensais
- ✅ Gerador de firmware automático
- ✅ Monitor de conexão em tempo real
- ✅ Suporte a Cor Sólida, Gradiente e Onda

## 📄 Licença

Projeto de código aberto. Use livremente.

## 👤 Autor

Desenvolvido para a **PhoneAid**.

## 💡 Roadmap

- [ ] Mais efeitos (Pulsação, Arco-Íris, Efeito de Fogo)
- [ ] Sincronização de efeitos entre múltiplos Arduino
- [ ] Interface web para controle remoto
- [ ] Histórico de efeitos e rollback
- [ ] Exportar/importar presets entre máquinas

---

**Dúvidas ou sugestões?** Abra uma issue no repositório.
