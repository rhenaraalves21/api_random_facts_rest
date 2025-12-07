import tkinter as tk
from tkinter import ttk, messagebox
import requests

# -----------------------
# CONFIG
# -----------------------
BASE = "http://127.0.0.1:5000"
API_FACTS = f"{BASE}/api/facts"
API_RANDOM = f"{BASE}/api/facts/random"
API_TODAY  = f"{BASE}/api/facts/today"
API_FAV    = f"{BASE}/api/favorites"
API_STATS  = f"{BASE}/api/stats"

# -----------------------
# HELPERS
# -----------------------
def extract_fact_text_from_external_response(resp_json):
    """
    Extrai o texto do payload das rotas externas (/random e /today).
    A API que você usa costuma retornar algo como:
    { "success": True, "source": "...", "fact": { ... } }
    Mas pode variar - verificamos algumas chaves possíveis.
    """
    if not isinstance(resp_json, dict):
        return None

    # caso padrão que você usou: {'success':True, 'source':..., 'fact': {...}}
    fact = resp_json.get("fact") or resp_json.get("message") or resp_json.get("data")
    if isinstance(fact, dict):
        # chaves comuns: 'text', 'fact', 'message', 'body'
        for key in ("text", "fact", "message", "body"):
            if key in fact and isinstance(fact[key], str):
                return fact[key]
        # se a própria fact for dict com 'text' field
        if "text" in fact and isinstance(fact["text"], str):
            return fact["text"]
    # caso a API retorne diretamente um string
    if isinstance(resp_json.get("text"), str):
        return resp_json.get("text")
    # fallback: try top-level 'message' or 'text'
    if isinstance(resp_json.get("message"), str):
        return resp_json.get("message")
    if isinstance(resp_json.get("data"), str):
        return resp_json.get("data")
    return None

def safe_json(res):
    try:
        return res.json()
    except Exception:
        return None

# -----------------------
# FACTS ADMIN (CRUD)
# -----------------------
def load_facts():
    try:
        res = requests.get(API_FACTS + "?format=json", timeout=6)
        data = safe_json(res)
        if not data:
            messagebox.showerror("Erro", f"Resposta inválida ao carregar facts:\n{res.text}")
            return
        facts = data.get("facts", [])
        facts_box.delete("1.0", tk.END)
        for f in facts:
            facts_box.insert(tk.END, f"ID: {f.get('id')}\n")
            facts_box.insert(tk.END, f"Texto: {f.get('text')}\n")
            facts_box.insert(tk.END, f"Fonte: {f.get('source')}\n")
            facts_box.insert(tk.END, f"Idioma: {f.get('language','')}\n")
            facts_box.insert(tk.END, f"Salvo em: {f.get('saved_at','')}\n")
            facts_box.insert(tk.END, "-" * 60 + "\n")
    except Exception as e:
        messagebox.showerror("Erro", f"Falha ao carregar facts:\n{e}")

def create_fact_admin():
    text = entry_text.get().strip()
    source = entry_source.get().strip()
    lang = entry_language.get().strip()

    if not text:
        messagebox.showwarning("Aviso", "O campo 'Texto' é obrigatório.")
        return

    payload = {"text": text}
    if source: payload["source"] = source
    if lang: payload["language"] = lang

    try:
        res = requests.post(API_FACTS, json=payload, timeout=6)
        data = safe_json(res) or {}
        if res.status_code == 201:
            messagebox.showinfo("Sucesso", "Fact criado com sucesso.")
            entry_text.delete(0, tk.END)
            entry_source.delete(0, tk.END)
            entry_language.delete(0, tk.END)
            load_facts()
        else:
            messagebox.showerror("Erro", f"Status {res.status_code}: {data.get('error', res.text)}")
    except Exception as e:
        messagebox.showerror("Erro", f"Falha ao criar fact:\n{e}")

def delete_fact_admin():
    fid = entry_delete_id.get().strip()
    if not fid.isdigit():
        messagebox.showwarning("Aviso", "ID inválido. Informe um número.")
        return
    try:
        res = requests.delete(f"{API_FACTS}/{fid}", timeout=6)
        data = safe_json(res) or {}
        if res.status_code == 200:
            messagebox.showinfo("Sucesso", "Fact deletado.")
            entry_delete_id.delete(0, tk.END)
            load_facts()
        else:
            messagebox.showerror("Erro", f"Status {res.status_code}: {data.get('error', res.text)}")
    except Exception as e:
        messagebox.showerror("Erro", f"Falha ao deletar fact:\n{e}")

# -----------------------
# FACTS (USER) - Today & Random + Favoritar (popup)
# -----------------------
current_today_fact = None
current_random_fact = None

def load_today_fact():
    global current_today_fact
    try:
        res = requests.get(API_TODAY + "?format=json", timeout=6)
        data = safe_json(res)
        if not data:
            messagebox.showerror("Erro", "Resposta inválida para fact do dia.")
            return
        # tentar extrair texto
        text = extract_fact_text_from_external_response(data)
        if not text:
            # talvez a API retorne em data['fact']['text']
            if isinstance(data.get("fact"), dict) and data["fact"].get("text"):
                text = data["fact"]["text"]
        if not text:
            text = str(data)
        current_today_fact = {"text": text, "raw": data}
        today_text_var.set(text)
    except Exception as e:
        messagebox.showerror("Erro", f"Falha ao carregar Fact do Dia:\n{e}")

def load_random_fact():
    global current_random_fact
    try:
        res = requests.get(API_RANDOM + "?format=json", timeout=6)
        data = safe_json(res)
        if not data:
            messagebox.showerror("Erro", "Resposta inválida para random fact.")
            return
        text = extract_fact_text_from_external_response(data)
        if not text and isinstance(data.get("fact"), dict):
            text = data["fact"].get("text")
        if not text:
            text = str(data)
        current_random_fact = {"text": text, "raw": data}
        random_text_var.set(text)
    except Exception as e:
        messagebox.showerror("Erro", f"Falha ao carregar Random Fact:\n{e}")

def open_fav_popup(from_which):
    """
    from_which: 'today' or 'random'
    pega o texto do fact atual correspondente e abre popup para inserir nota
    """
    if from_which == "today":
        fact = current_today_fact
    else:
        fact = current_random_fact

    if not fact:
        messagebox.showwarning("Aviso", "Não há fact carregado para favoritar.")
        return

    popup = tk.Toplevel(root)
    popup.title("Adicionar Favorito")

    popup_w = 400
    popup_h = 220
    popup.geometry(f"{popup_w}x{popup_h}")

    # -------------------------------
    # 🔵 CENTRALIZAR O POPUP
    root.update_idletasks()
    main_x = root.winfo_x()
    main_y = root.winfo_y()
    main_w = root.winfo_width()
    main_h = root.winfo_height()

    pos_x = main_x + (main_w // 2) - (popup_w // 2)
    pos_y = main_y + (main_h // 2) - (popup_h // 2)

    tk.Label(popup, text="Texto do Fact:", font=("Arial", 10, "bold")).pack(anchor="w", padx=10, pady=(10,0))
    tk.Label(popup, text=fact["text"], wraplength=360, justify="left").pack(anchor="w", padx=10)

    tk.Label(popup, text="Nota (opcional):").pack(anchor="w", padx=10, pady=(10,0))
    note_entry = tk.Entry(popup, width=60)
    note_entry.pack(padx=10, pady=(0,10))

    def save_favorite():
        notes = note_entry.get().strip()
        payload = {"fact_text": fact["text"], "notes": notes}
        try:
            res = requests.post(API_FAV, json=payload, timeout=6)
            data = safe_json(res) or {}
            if res.status_code == 201:
                messagebox.showinfo("Sucesso", "Favorito salvo com sucesso.")
                popup.destroy()
                load_favorites()
                # se a aba facts estiver ativa, atualiza tb a lista se necessário
            else:
                messagebox.showerror("Erro", f"Status {res.status_code}: {data.get('error', res.text)}")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao salvar favorito:\n{e}")

    btn_frame = tk.Frame(popup)
    btn_frame.pack(pady=5)
    tk.Button(btn_frame, text="Salvar", command=save_favorite, width=12).pack(side="left", padx=6)
    tk.Button(btn_frame, text="Cancelar", command=popup.destroy, width=12).pack(side="left", padx=6)

# -----------------------
# FAVORITOS - listar e remover
# -----------------------
def load_favorites():
    try:
        res = requests.get(API_FAV + "?format=json", timeout=6)
        data = safe_json(res)
        if not data:
            messagebox.showerror("Erro", "Resposta inválida ao carregar favoritos.")
            return
        favs = data.get("favorites", [])
        fav_box.delete("1.0", tk.END)
        for f in favs:
            fav_box.insert(tk.END, f"ID: {f.get('id')}\n")
            fav_box.insert(tk.END, f"Texto: {f.get('fact_text')}\n")
            fav_box.insert(tk.END, f"Notas: {f.get('notes','')}\n")
            fav_box.insert(tk.END, f"Adicionado em: {f.get('added_at','')}\n")
            fav_box.insert(tk.END, "-" * 60 + "\n")
    except Exception as e:
        messagebox.showerror("Erro", f"Falha ao carregar favoritos:\n{e}")

def remove_favorite():
    fid = entry_fav_delete.get().strip()
    if not fid.isdigit():
        messagebox.showwarning("Aviso", "ID inválido.")
        return
    try:
        res = requests.delete(f"{API_FAV}/{fid}", timeout=6)
        data = safe_json(res) or {}
        if res.status_code == 200:
            messagebox.showinfo("Sucesso", "Favorito removido.")
            entry_fav_delete.delete(0, tk.END)
            load_favorites()
        else:
            messagebox.showerror("Erro", f"Status {res.status_code}: {data.get('error', res.text)}")
    except Exception as e:
        messagebox.showerror("Erro", f"Falha ao remover favorito:\n{e}")

# -----------------------
# ESTATÍSTICAS
# -----------------------
def load_stats():
    try:
        res = requests.get(API_STATS + "?format=json", timeout=6)
        data = safe_json(res)
        if not data:
            messagebox.showerror("Erro", "Resposta inválida ao carregar estatísticas.")
            return
        stats = data.get("statistics", {})
        stats_box.delete("1.0", tk.END)
        stats_box.insert(tk.END, f"Total de Facts: {stats.get('total_facts',0)}\n")
        stats_box.insert(tk.END, f"Total de Favoritos: {stats.get('total_favorites',0)}\n\n")
        stats_box.insert(tk.END, "Facts por Fonte:\n")
        for src, cnt in stats.get("facts_by_source", {}).items():
            stats_box.insert(tk.END, f" - {src}: {cnt}\n")
        stats_box.insert(tk.END, "\nFacts por Idioma:\n")
        for lang, cnt in stats.get("facts_by_language", {}).items():
            stats_box.insert(tk.END, f" - {lang}: {cnt}\n")
        stats_box.insert(tk.END, f"\nGerado em: {stats.get('generated_at','')}\n")
    except Exception as e:
        messagebox.showerror("Erro", f"Falha ao carregar estatísticas:\n{e}")

# -----------------------
# GUI
# -----------------------
root = tk.Tk()
root.title("Cliente Desktop - Facts API")
root.geometry("820x700")

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

# -- TAB 1: Facts Admin (CRUD)
tab_admin = ttk.Frame(notebook)
notebook.add(tab_admin, text="Facts Admin")

tk.Label(tab_admin, text="Criar novo Fact", font=("Arial", 11, "bold")).pack(anchor="w", padx=10, pady=(10,0))
tk.Label(tab_admin, text="Texto:").pack(anchor="w", padx=10)
entry_text = tk.Entry(tab_admin, width=90)
entry_text.pack(padx=10)

tk.Label(tab_admin, text="Fonte:").pack(anchor="w", padx=10, pady=(6,0))
entry_source = tk.Entry(tab_admin, width=50)
entry_source.pack(padx=10)

tk.Label(tab_admin, text="Idioma:").pack(anchor="w", padx=10, pady=(6,0))
entry_language = tk.Entry(tab_admin, width=20)
entry_language.pack(padx=10)

tk.Button(tab_admin, text="Criar Fact", command=create_fact_admin, width=18).pack(pady=10)

tk.Label(tab_admin, text="Deletar Fact por ID", font=("Arial", 11, "bold")).pack(anchor="w", padx=10, pady=(10,0))
entry_delete_id = tk.Entry(tab_admin, width=15)
entry_delete_id.pack(padx=10)

tk.Button(tab_admin, text="Deletar Fact", command=delete_fact_admin, width=18).pack(pady=8)

tk.Label(tab_admin, text="Lista de Facts", font=("Arial", 11, "bold")).pack(anchor="w", padx=10, pady=(10,0))
facts_box = tk.Text(tab_admin, height=18, width=100)
facts_box.pack(padx=10, pady=(0,10))

tk.Button(tab_admin, text="Atualizar Lista", command=load_facts).pack(pady=(0,10))

# -- TAB 2: Facts (user)
tab_facts = ttk.Frame(notebook)
notebook.add(tab_facts, text="Facts")

tk.Label(tab_facts, text="Fact do Dia", font=("Arial", 11, "bold")).pack(anchor="w", padx=10, pady=(10,0))
today_text_var = tk.StringVar()
today_label = tk.Label(tab_facts, textvariable=today_text_var, wraplength=760, justify="left")
today_label.pack(anchor="w", padx=10, pady=(0,6))

btns_frame = tk.Frame(tab_facts)
btns_frame.pack(anchor="w", padx=10, pady=(0,6))
tk.Button(btns_frame, text="Favoritar Fact do Dia", command=lambda: open_fav_popup("today")).pack(side="left", padx=6)
tk.Button(btns_frame, text="Atualizar Fact do Dia", command=load_today_fact).pack(side="left", padx=6)

tk.Label(tab_facts, text="Random Fact", font=("Arial", 11, "bold")).pack(anchor="w", padx=10, pady=(12,0))
random_text_var = tk.StringVar()
random_label = tk.Label(tab_facts, textvariable=random_text_var, wraplength=760, justify="left")
random_label.pack(anchor="w", padx=10, pady=(0,6))

btns_frame2 = tk.Frame(tab_facts)
btns_frame2.pack(anchor="w", padx=10, pady=(0,6))
tk.Button(btns_frame2, text="Obter Random Fact", command=load_random_fact).pack(side="left", padx=6)
tk.Button(btns_frame2, text="Favoritar Random Fact", command=lambda: open_fav_popup("random")).pack(side="left", padx=6)

# -- TAB 3: Favoritos
tab_fav = ttk.Frame(notebook)
notebook.add(tab_fav, text="Favoritos")

tk.Label(tab_fav, text="Lista de Favoritos", font=("Arial", 11, "bold")).pack(anchor="w", padx=10, pady=(10,0))
fav_box = tk.Text(tab_fav, height=20, width=100)
fav_box.pack(padx=10, pady=(0,10))

tk.Label(tab_fav, text="Remover Favorito por ID", font=("Arial", 11, "bold")).pack(anchor="w", padx=10)
entry_fav_delete = tk.Entry(tab_fav, width=20)
entry_fav_delete.pack(padx=10, pady=(6,0))
tk.Button(tab_fav, text="Remover Favorito", command=remove_favorite, width=18).pack(pady=8)
tk.Button(tab_fav, text="Atualizar Favoritos", command=load_favorites).pack(pady=(0,10))

# -- TAB 4: Estatísticas
tab_stats = ttk.Frame(notebook)
notebook.add(tab_stats, text="Estatísticas")

tk.Button(tab_stats, text="Atualizar Estatísticas", command=load_stats).pack(pady=8)
stats_box = tk.Text(tab_stats, height=25, width=100)
stats_box.pack(padx=10, pady=(0,10))

# -----------------------
# Eventos: ao trocar de aba, atualiza conteúdo relevante
# -----------------------
def on_tab_changed(event):
    selected = event.widget.tab('current')['text']
    if selected == "Facts Admin":
        load_facts()
    elif selected == "Facts":
        # carregar automaticamente fact do dia ao abrir
        load_today_fact()
    elif selected == "Favoritos":
        load_favorites()
    elif selected == "Estatísticas":
        load_stats()

notebook.bind("<<NotebookTabChanged>>", on_tab_changed)

# Inicial load
load_facts()
load_favorites()
load_stats()
load_today_fact()

root.mainloop()