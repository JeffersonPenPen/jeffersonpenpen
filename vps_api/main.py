import io
import random
import textwrap
import os
import time
from fastapi import FastAPI, Response, Request
from fastapi.responses import StreamingResponse
from PIL import Image, ImageDraw, ImageFont

app = FastAPI()

# Nomes dos arquivos locais na pasta vps_api
SCREEN_IMG = "Zoltar_Filipeta.png"
DOWNLOAD_IMG = "filipeta_download.png"
FONT_PATH = "SpecialElite-Regular.ttf"

# Cache simples para sincronizar a frase entre tela e download (chave é o IP)
# { "ip": ("frase", timestamp) }
quote_cache = {}
CACHE_TTL = 300  # 5 minutos

def get_user_quote(ip: str):
    """Garante que o usuário tenha a mesma frase para tela e download."""
    now = time.time()
    if ip in quote_cache:
        quote, ts = quote_cache[ip]
        if now - ts < CACHE_TTL:
            return quote
    
    # Se não houver cache ou expirou, sorteia uma nova
    fortunes = load_fortunes()
    new_quote = random.choice(fortunes)
    quote_cache[ip] = (new_quote, now)
    return new_quote

def load_fortunes():
    """Carrega as frases do arquivo de texto."""
    try:
        with open("fortunes.txt", "r", encoding="utf-8") as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        return ["O futuro é incerto, mas seu código não compila."]

def generate_fortune_image(mode: str, fortune: str):
    """Gera a imagem baseada nos parâmetros exatos solicitados."""
    
    if mode == "screen":
        base_path = SCREEN_IMG
        angle = -11  # Sinal corrigido para -11 conforme solicitado
        # Coordenadas do centro solicitadas: X=451, Y=591
        center_x, center_y = 451, 591
        text_color = (60, 60, 60, 255)
        font_size = 40  # 8.5% maior que a de download (37 * 1.085 = 40.1)
        wrap_width = 18
    else:
        base_path = DOWNLOAD_IMG
        angle = 0
        # Coordenadas do centro solicitadas: X=257, Y=512
        center_x, center_y = 257, 512
        text_color = (40, 40, 40, 255)
        font_size = 37
        wrap_width = 18

    # Abre a imagem base
    if not os.path.exists(base_path):
        img = Image.new("RGBA", (832, 1248), (255, 248, 220, 255))
    else:
        img = Image.open(base_path).convert("RGBA")
    
    # Prepara a fonte
    try:
        font = ImageFont.truetype(FONT_PATH, font_size)
    except:
        font = ImageFont.load_default()

    # Formata o texto
    wrapped_text = textwrap.fill(fortune, width=wrap_width)
    
    # Cria camada de texto
    txt_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(txt_layer)
    
    # Desenha o texto centralizado nas coordenadas solicitadas
    draw.multiline_text((center_x, center_y), wrapped_text, fill=text_color, font=font, anchor="mm", align="center", spacing=10)
    
    # Rotaciona apenas a camada de texto se necessário, usando o centro do texto
    if angle != 0:
        txt_layer = txt_layer.rotate(angle, resample=Image.BICUBIC, center=(center_x, center_y))
    
    # Combina as camadas
    final_img = Image.alpha_composite(img, txt_layer)
    
    buf = io.BytesIO()
    final_img.save(buf, format="PNG")
    buf.seek(0)
    return buf

@app.get("/api/quote")
async def get_quote(request: Request):
    ip = request.client.host
    fortune = get_user_quote(ip)
    buf = generate_fortune_image("screen", fortune)
    headers = {"Cache-Control": "no-cache, no-store, must-revalidate, max-age=0"}
    return StreamingResponse(buf, media_type="image/png", headers=headers)

@app.get("/api/download-quote")
async def download_quote(request: Request):
    ip = request.client.host
    fortune = get_user_quote(ip)
    buf = generate_fortune_image("download", fortune)
    headers = {"Content-Disposition": 'attachment; filename="Sorte_Zoltar.png"'}
    return StreamingResponse(buf, media_type="image/png", headers=headers)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
