# 🧪 GUIA DE TESTE - PhoneAid LED Controller

## Requisitos para Testar

```bash
pip install PyQt5 pyserial
```

## 1️⃣ Teste Rápido (Sem Arduino)

### Inicie a aplicação:
```bash
cd c:\Users\Carol\Desktop\ARDUINO PHONEAID
python app/main.py
```

A janela do aplicativo abrirá com 3 abas: **Instalador**, **Configurar LEDs**, **Efeitos**.

---

## 2️⃣ Testes por Aba

### **Aba 1: Configurar LEDs** ✓

1. Veja o total de LEDs atual (padrão: 92)
2. Expanda cada letra (P, H, O, N, E, A, I, D)
3. Modifique um range (ex: P de 14-25 para 14-30)
4. Clique **"Salvar Mapeamento"**
5. Verifique em `app/config.json` se as mudanças foram persistidas

**Esperado:** Arquivo JSON atualizado, mensagem de sucesso

---

### **Aba 2: Efeitos** ✓

#### **Teste 2a: Cor Sólida**
1. Abra a aba "Efeitos"
2. Preset selector mostra "Mês 1: Janeiro"
3. Type = "Cor sólida"
4. Cor 1 = vermelho (padrão)
5. Clique **"Visualizar Efeito"** → LEDs viram vermelho na preview linear
6. Mude Cor 1 para azul → Preview atualiza em tempo real
7. Clique **"Salvar como Preset"** → "Efeito salvo no mês 1"
8. Selecione **"Mês 2: Fevereiro"** → Carrega dados padrão
9. Clique **"Salvar como Preset"** → Fevereiro agora tem novo efeito
10. Volte a Janeiro → Vê o efeito vermelho

**Esperado:** Preview linear atualiza, presets salvos em `presets/efeitos.json`

---

#### **Teste 2b: Gradiente**
1. Type = "Gradiente"
2. Cor 1 = vermelho, Cor 2 = azul (padrão)
3. Clique **"Visualizar Efeito"** → LEDs fazem gradiente vermelho→azul
4. Mude Cor 2 para verde → Preview atualiza para vermelho→verde
5. **"Salvar como Preset"** em um mês
6. Altere cores e salve novamente → Sobrescreve preset

**Esperado:** Gradiente suave na preview linear

---

#### **Teste 2c: Onda**
1. Type = "Onda"
2. Velocidade = "Lento"
3. Largura = 10
4. Clique **"Visualizar Efeito"** → Onda se move pela fita
5. Mude Velocidade para "Turbo" → Movimento mais rápido
6. Mude Largura para 30 → Onda fica mais larga
7. Pause movendo o mouse (pausa a animação)

**Esperado:** Animação suave, parâmetros dinâmicos

---

#### **Teste 2d: Hover na Preview**
1. Passe o mouse sobre a fita linear
2. Veja tooltip com "LED 00", "LED 01", etc.
3. Veja as caixas das letras com ranges (P:00-05, etc.)

**Esperado:** Tooltip com número do LED, overlay visível

---

### **Aba 3: Instalador** ✓

#### **Teste 3a: Status de Conexão (SEM Arduino)**
1. Abra a aba "Instalador"
2. Status mostra "⚪ Nenhuma porta selecionada" (em vermelho)
3. Clique **"Atualizar Portas"** → Lista portas disponíveis no PC
4. Se Arduino conectado: aparece COM3, COM4, etc.
5. Selecione uma porta válida (mesmo sem Arduino)
6. Clique **"Conectar"** → Status fica "⚪ Arduino desconectado"

**Esperado:** Status atualiza, cores mudam (vermelho/verde)

---

#### **Teste 3b: Compilar Firmware**
1. Certifique que a aba "Configurar LEDs" tem dados válidos
2. Na aba "Instalador", Preset selector = "Mês 1: Janeiro"
3. Clique **"⚙️ Gerar Firmware"**
4. Code preview mostra código Arduino em verde (estilo terminal)
5. Status mostra "✅ Firmware gerado com sucesso!"

**Esperado:**
- Código C/C++ visível no preview
- `app/firmware/firmware.ino` criado/atualizado
- Contém `#include <FastLED.h>`, `#define NUM_LEDS 92`, structs de efeitos

---

#### **Teste 3c: Arquivo Gerado**
1. Abra `app/firmware/firmware.ino` em um editor
2. Veja estrutura:
```cpp
#include <FastLED.h>
#define NUM_LEDS 92
struct Effect { ... };
void setup() { FastLED.addLeds<WS2812B, DATA_PIN, GRB>(...); }
void loop() { apply_effect(...); }
```

**Esperado:** Firmware válido, compilável no Arduino IDE

---

## 3️⃣ Testes de Persistência

### Teste 3a: Config.json
1. Na aba "Configurar LEDs", altere o total de LEDs para 100
2. Salve
3. Feche a aplicação
4. Abra novamente
5. Verifique se total continua 100

**Esperado:** Dados persistidos em `app/config.json`

---

### Teste 3b: Presets.json
1. Na aba "Efeitos", crie 3 efeitos diferentes
2. Salve nos meses 1, 2, 3
3. Feche e reabra a aplicação
4. Navegue pelos 3 meses
5. Verifique se efeitos são carregados corretamente

**Esperado:** Dados persistidos em `app/presets/efeitos.json` com 12 entradas

---

## 4️⃣ Teste de Threading (Monitor Contínuo)

1. Abra a aba "Instalador"
2. Status mostra status inicial
3. Se Arduino conectado: plugue e desplugue o cabo USB
4. Status deve atualizar automaticamente (a cada ~2 segundos)
5. **NÃO** deve travar a UI durante checagem

**Esperado:** Status muda dinamicamente sem congelamento

---

## 5️⃣ Teste Sem Arduino (Simulado)

Tudo funciona 100% sem Arduino conectado:
- Preview linear funciona normalmente
- Presets salvam e carregam
- Firmware é gerado (não precisa upload real)
- Monitor detecta ausência de Arduino
- UI não trava

---

## 6️⃣ Checklist de Validação

- [ ] Aplicação inicia sem erros
- [ ] 3 abas aparecem e são navegáveis
- [ ] ConfigTab: salva mapeamento
- [ ] EffectsTab: preview linear atualiza
- [ ] EffectsTab: presets salvam (1-12)
- [ ] EffectsTab: hover mostra LED numbers
- [ ] InstallerTab: status se conecta/desconecta
- [ ] InstallerTab: gera firmware válido
- [ ] Firmware tem código C++ válido
- [ ] Dados persistem após reabrir
- [ ] UI não trava com monitor rodando
- [ ] Todas as 3 cores de efeitos funcionam (Sólida, Gradiente, Onda)

---

## 7️⃣ Teste com Arduino Real (Opcional)

Se tiver Arduino conectado:

1. Instale a biblioteca **FastLED** na Arduino IDE
   - Sketch → Include Library → Manage Libraries
   - Procure "FastLED" e instale

2. Compile firmware:
   - Abra `app/firmware/firmware.ino` na Arduino IDE
   - Verifique (checkmark icon)
   - Sem erros = sucesso!

3. Upload (manual):
   - Selecione placa e porta em Tools
   - Clique Upload
   - Arduino executa firmware

4. Conecte fita WS2812B conforme README (pino 6, 5V, GND)

5. LEDs devem ligar com o efeito compilado!

---

## 🐛 Se algo der errado:

### "ModuleNotFoundError: No module named 'PyQt5'"
```bash
pip install PyQt5
```

### "ModuleNotFoundError: No module named 'serial'"
```bash
pip install pyserial
```

### Aplicação trava ao abrir
- Feche completamente
- Delete `__pycache__` se houver erros
- Teste: `python -c "from PyQt5 import QtWidgets; print('OK')"`

### Preview não atualiza
- Clique "Visualizar Efeito" (começa animação)
- Mude um parâmetro (cor, velocidade, etc.)
- Preview deve atualizar

### Status não muda
- Aguarde ~2 segundos (intervalo do monitor)
- Se Arduino conectado, verifique drivers COM

---

## ✅ Resumo de Teste

**Tempo estimado:** 10-15 minutos

**O que validar:**
1. UI abre sem erros ✓
2. Dados salvam e carregam ✓
3. Preview linear funciona ✓
4. Firmware gera válido ✓
5. Monitor não bloqueia UI ✓

Se todos ✅, **sistema está pronto para produção!**

