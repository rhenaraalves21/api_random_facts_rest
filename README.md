# Random Facts - Projeto Web & Desktop

Este projeto consiste em:

* **Servidor REST**: disponibiliza endpoints para Facts (CRUD), Fact do Dia, Random Fact, Favoritos e Estatísticas.
* **Cliente Web**: interface web funcional para consumir todos os endpoints.
* **Cliente Desktop**: interface desktop em Tkinter (Python) para consumir os mesmos endpoints.

---

## Estrutura de pastas

```
api_random_facts_rest/
│
├── server/
│   ├── app.py               # Servidor REST (Flask)
│   └── ...                  # Dependências do servidor
│
├── client/
│   ├── 
│   │── desktop
│   │   ├── desktop_client.py    # Cliente Desktop em Python
│   ├── web/
│   │   ├── index.html       # Cliente Web
│   │   ├── style.css
│   │   └── app.js
│   └── ...                  
│
└── README.md
```

---

## Pré-requisitos

* **Python 3.10+**
* **Flask**
* **Requests** (para cliente desktop)
* Navegador moderno (para cliente web)

### Instalar dependências Python

```bash
pip install flask requests flask-cors
```

---

## 1️⃣ Executando o Servidor REST

1. Navegue até a pasta do servidor:

```bash
cd api_random_facts_rest/server
```

2. Execute o servidor:

```bash
python app.py
```

3. Por padrão, o servidor será iniciado em `http://127.0.0.1:5000`.

4. **CORS**: o servidor aceita requisições apenas do cliente web na porta 5500 (se necessário, ajuste no `app.py`).

---

## 2️⃣ Executando o Cliente Desktop (Python)

1. Abra um terminal e navegue até a pasta `client`:

```bash
cd api_random_facts_rest/client
```

2. Execute o cliente:

```bash
python desktop_client.py
```

3. Uma janela Tkinter será aberta com abas:

* **Facts Admin**: CRUD de Facts
* **Facts**: Fact do Dia e Random Fact, com botão de favoritar
* **Favoritos**: Listar e remover favoritos
* **Estatísticas**: Totais de Facts, Favoritos, por fonte e idioma

4. Funcionalidades:

* Criar, deletar e listar Facts
* Favoritar Facts do Dia ou Random com nota opcional
* Visualizar e remover favoritos
* Consultar estatísticas

---

## 3️⃣ Executando o Cliente Web

### Opção A: Abrir direto no navegador

1. Abra o arquivo `index.html` em um navegador.
2. Certifique-se de que o servidor REST (`app.py`) está rodando em `http://localhost:5000`.
3. Funcionalidades:

* Mesmas do cliente desktop
* Tabs: Facts Admin, Facts (Dia + Random), Favoritos, Estatísticas

---

### Opção B: Servir via servidor local (recomendado)

1. Navegue até a pasta do cliente web:

```bash
cd api_random_facts_rest/client/web
```

2. Inicie um servidor local com Python:

```bash
# Python 3
python -m http.server 5500
```

3. Abra o navegador e acesse:

```
http://localhost:5500
```

4. A página agora fará requisições corretamente para o servidor REST.

---

## 4️⃣ Resumo das Rotas do Servidor

| Endpoint              | Método | Função                                                    |
| --------------------- | ------ | --------------------------------------------------------- |
| `/api/facts`          | GET    | Listar Facts                                              |
| `/api/facts`          | POST   | Criar novo Fact                                           |
| `/api/facts/<id>`     | DELETE | Deletar Fact pelo ID                                      |
| `/api/facts/today`    | GET    | Obter Fact do Dia                                         |
| `/api/facts/random`   | GET    | Obter Random Fact                                         |
| `/api/favorites`      | GET    | Listar favoritos                                          |
| `/api/favorites`      | POST   | Adicionar favorito                                        |
| `/api/favorites/<id>` | DELETE | Remover favorito pelo ID                                  |
| `/api/stats`          | GET    | Estatísticas (total Facts, favoritos, por fonte e idioma) |

---

## 5️⃣ Dicas e Observações

* Sempre inicie o **servidor REST** antes de usar os clientes.
* Para favoritar Facts do Dia ou Random, será solicitado inserir uma nota opcional.
* Todas as listagens (Facts, Random, Favoritos, Estatísticas) estão formatadas de forma “humanizada”.
* Atualize as abas usando os botões de “Atualizar” para recarregar dados.
* Ajuste o endereço do servidor no cliente web (`app.js`) ou desktop (`desktop_client.py`) se não estiver usando localhost:5000.

---
