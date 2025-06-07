from dotenv import load_dotenv
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
from io import BytesIO
import pytesseract
import time
from datetime import datetime

# --- Carregar variáveis do .env ---
load_dotenv()

cpf = os.getenv("CPF")
senha = os.getenv("SENHA")

if not cpf or not senha:
    raise ValueError("CPF e SENHA precisam estar definidos no arquivo .env")

# Configuração Tesseract
pytesseract.pytesseract.tesseract_cmd = "/opt/homebrew/bin/tesseract"  # adapte conforme seu sistema

# Maxima Navegador
chrome_options = Options()
chrome_options.add_argument("--start-maximized")

driver = webdriver.Chrome(options=chrome_options)

# Aguarda elemento visível 
def wait_visible(by, locator, timeout=15):
    return WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((by, locator)))

# Acessa a página Portal do Cidadao Pinheiro Machado
driver.get("https://pinheiromachado.govbr.cloud:8443/cidadao/servlet/br.com.cetil.ar.jvlle.hatendimento?")
wait_visible(By.ID, "_IDENTIFICACAO")

# Preenche CPF 
driver.find_element(By.ID, "_IDENTIFICACAO").send_keys(cpf)

# Preenche senha
driver.find_element(By.ID, "_SENHA").send_keys(senha)

# Capturar e reconhecer Captcha
captcha_img = wait_visible(By.XPATH, '//img[contains(@src, "login.jsp")]')
captcha_png = captcha_img.screenshot_as_png
captcha_image = Image.open(BytesIO(captcha_png))
captcha_text = pytesseract.image_to_string(captcha_image, config="--psm 7").strip()

print(f"Captcha reconhecido: {captcha_text}")

# Preencher Captcha
driver.find_element(By.ID, "_SEQUENCIA").send_keys(captcha_text)

# Clica no botão de entrar
driver.find_element(By.NAME, "BTN_CONFIRMAR").click()

# Aguardar carregamento
wait_visible(By.ID, "btnPesquisar")

# Clica no botão pesquisar para listar os boletos 
driver.find_element(By.ID, "btnPesquisar").click()

# Função para parsear datas
def parse_data(texto):
    try:
        return datetime.strptime(texto, "%d/%m/%Y")
    except Exception:
        return None

# Espera as linhas carregarem
WebDriverWait(driver, 15).until(
    EC.presence_of_all_elements_located((By.XPATH, '//span[starts-with(@id, "span__GRIDDATAVENCIMENTO_")]'))
)
linhas_venc = driver.find_elements(By.XPATH, '//span[starts-with(@id, "span__GRIDDATAVENCIMENTO_")]')

# Dicionário para armazenar vencimentos e seus índices
vencimentos = {}

# Mapeia vencimentos e seus índices
for i, span_venc in enumerate(linhas_venc, start=1):
    data_texto = span_venc.text.strip()
    data_venc = parse_data(data_texto)
    if data_venc is None:
        continue

    ano_span = driver.find_element(By.ID, f"span__GRIDANO_{str(i).zfill(4)}")
    ano = ano_span.text.strip()

    if ano != "2025":
        continue

    especie_span = driver.find_element(By.ID, f"span__GRIDESPECIETRIBUTO_{str(i).zfill(4)}")
    especie = especie_span.text.strip()

    situacao_span = driver.find_element(By.ID, f"span__GRIDSITUACAOPARCELA_{str(i).zfill(4)}")
    situacao = situacao_span.text.strip()

    if situacao != "Pendente":
        continue

    # Salva os índices por data de vencimento
    key = data_venc.strftime("%d/%m/%Y")
    if key not in vencimentos:
        vencimentos[key] = {}
    vencimentos[key][especie] = i

# Agora, procura vencimentos com IPTU e ColetaLixo na mesma data
boleto_selecionado = False
for data_venc, especies in vencimentos.items():
    if "IPTU" in especies and "ColetaLixo" in especies:
        idx_iptu = str(especies["IPTU"]).zfill(4)
        idx_lixo = str(especies["ColetaLixo"]).zfill(4)

        # Marca os dois checkboxes
        checkbox_iptu = driver.find_element(By.NAME, f"_GRIDIMPRIMEGUIA_{idx_iptu}")
        if not checkbox_iptu.is_selected():
            checkbox_iptu.click()
        print(f"Selecionado IPTU - Vencimento: {data_venc}")

        checkbox_lixo = driver.find_element(By.NAME, f"_GRIDIMPRIMEGUIA_{idx_lixo}")
        if not checkbox_lixo.is_selected():
            checkbox_lixo.click()
        print(f"Selecionado ColetaLixo - Vencimento: {data_venc}")

        boleto_selecionado = True
        break  # Sai após marcar o primeiro par encontrado

if not boleto_selecionado:
    print("Nenhum par de boletos IPTU e ColetaLixo pendentes encontrados para 2025.")

# Geração do boleto
if boleto_selecionado:
    try:
        btn_guia = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, '//input[@name="BTN_GUIA" and @value="Impressão de Guia de Recolhimento"]'))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn_guia)
        driver.execute_script("arguments[0].click();", btn_guia)

        # Aguarda modal abrir (ajuste ID conforme sua aplicação)
        WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.ID, "idDoElementoModal"))
        )
        print("Modal aberto com sucesso após clique no botão de gerar guia.")

    except Exception as e:
        print(f"Erro ao tentar clicar no botão de gerar guia e abrir o modal: {e}")
else:
    print("Nenhum boleto selecionado para gerar guia.")

# Encerrar
print("Processo concluído.")
time.sleep(5)
driver.quit()
