
# 📑 Automação de Emissão de Boletos no Portal do Cidadão de Pinheiro Machado

## 📌 Descrição

Este projeto é um script em Python que utiliza **Selenium** para automatizar o acesso e a emissão de boletos de **IPTU** e **Taxa de Coleta de Lixo** no Portal do Cidadão de Pinheiro Machado.

A aplicação faz login no portal utilizando CPF e senha (configurados em um arquivo `.env`), reconhece automaticamente o CAPTCHA via **OCR (Tesseract)**, acessa a listagem de boletos pendentes e seleciona os boletos dos anos e meses configurados.

Além disso, o script verifica se há boletos pendentes para o **mês atual** e o **próximo mês**, e caso existam, **seleciona tanto o IPTU quanto a Coleta de Lixo** quando tiverem a mesma data de vencimento — permitindo emitir juntos a guia de recolhimento.

## ⚙️ Como funciona

1. **Carregamento de Variáveis de Ambiente**  
   O CPF e a senha do usuário são lidos de um arquivo `.env` para maior segurança.

2. **Inicialização do WebDriver**  
   Abre uma instância do navegador Google Chrome maximizada para interação.

3. **Reconhecimento de CAPTCHA**  
   Utiliza a biblioteca `pytesseract` para ler e interpretar a imagem de CAPTCHA exibida na tela de login.

4. **Login no Sistema**  
   Preenche os campos de CPF, senha e código do CAPTCHA automaticamente e acessa a área de boletos.

5. **Listagem e Seleção de Boletos Pendentes**  
   - Aguarda a tabela de boletos ser carregada.
   - Percorre as linhas da tabela verificando:
     - **Data de vencimento**
     - **Ano**
     - **Tipo do tributo (IPTU ou Coleta de Lixo)**
     - **Situação (Pendente)**
   - Quando encontra boletos do **mesmo ano e mesma data de vencimento**, seleciona automaticamente os dois (IPTU e Coleta de Lixo).

6. **Geração da Guia de Recolhimento**
   - Clica no botão de gerar guia.
   - Aguarda a abertura do modal onde normalmente estaria o link de emissão do boleto.

7. **Finalização**
   - Exibe mensagens de log no terminal.
   - Encerra o navegador.

## 📈 Justificativa e Utilidade

Esse tipo de automação é extremamente útil para **imobiliárias**, **administradores de imóveis** e **proprietários que gerenciam múltiplos imóveis**, pois permite agilizar a emissão de boletos municipais, eliminando a necessidade de acessar manualmente o portal para cada imóvel, lidar com CAPTCHAs e localizar boletos individualmente.

Especialmente em cidades menores onde os sistemas online ainda têm muitas limitações de usabilidade, esse script ajuda a centralizar e acelerar a emissão de guias de pagamento.

## ⚠️ Dificuldades e Desafios Técnicos

A maior dificuldade enfrentada nesse projeto foi **lidar com modais no site**, já que:

- Os modais são abertos via JavaScript dinâmico.
- Não possuem identificadores HTML fixos padronizados.
- Muitas vezes exigem manipulação de `scrollIntoView` e execução de JavaScript via Selenium para clicar corretamente nos botões.
- Nem sempre a abertura do modal é instantânea, exigindo controle cuidadoso de tempo de espera e verificações condicionais.

Além disso, o reconhecimento do CAPTCHA também exige boa configuração do **Tesseract OCR**, especialmente para adaptar ao ambiente macOS (usando `/opt/homebrew/bin/tesseract`).

## 📦 Requisitos

- Python 3.x  
- Google Chrome  
- [Tesseract OCR](https://tesseract-ocr.github.io/)  
- [Selenium](https://selenium-python.readthedocs.io/)  
- [Pillow (PIL)](https://pillow.readthedocs.io/en/stable/)  
- `python-dotenv`  
- Um arquivo `.env` com as variáveis:
  ```
  CPF=seu_cpf_aqui
  SENHA=sua_senha_aqui
  ```

## 📜 Como rodar

1. Instale as dependências:
   ```bash
   pip install selenium pillow pytesseract python-dotenv
   ```

2. Ajuste o caminho do `pytesseract` no script conforme seu sistema:
   ```python
   pytesseract.pytesseract.tesseract_cmd = "/opt/homebrew/bin/tesseract"
   ```

3. Configure o arquivo `.env` com seu CPF e senha.

4. Execute o script:
   ```bash
   python nome_do_script.py
   ```
