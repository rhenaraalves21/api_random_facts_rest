from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import facts_pb2

app = Flask(__name__)

# PERMITIR SOMENTE REQUISIÇÕES DO FRONT NA PORTA 5500
CORS(app, resources={r"/*": {"origins": [
    "http://localhost:5500",
    "http://127.0.0.1:5500"
]}})

# Armazenamento em memória para o CRUD
facts_storage = {}
fact_id_counter = 1

favorites_storage = {}
favorite_id_counter = 1

# ==================== UTILIDADES ====================

def dict_to_xml(data, root_name='response'):
    """Converte dicionário para XML"""
    root = ET.Element(root_name)
    
    def build_xml(parent, item):
        if isinstance(item, dict):
            for key, val in item.items():
                child = ET.SubElement(parent, str(key))
                build_xml(child, val)
        elif isinstance(item, list):
            for elem in item:
                list_item = ET.SubElement(parent, 'item')
                build_xml(list_item, elem)
        else:
            parent.text = str(item)
    
    build_xml(root, data)
    return ET.tostring(root, encoding='unicode')

def format_response(data, format_type='json'):
    """Formata resposta em JSON ou XML"""
    if format_type.lower() == 'xml':
        xml_data = dict_to_xml(data)
        return Response(xml_data, mimetype='application/xml')
    else:
        return jsonify(data)

def get_format():
    """Obtém formato de resposta da requisição"""
    return request.args.get('format', 'json').lower()

# ==================== ROTAS CRUD DE FACTS ====================

@app.route('/api/facts/random', methods=['GET'])
def get_random_fact():
    """GET: Obtém um fact aleatório da API externa"""
    try:
        response = requests.get('https://uselessfacts.jsph.pl/api/v2/facts/random')
        response.raise_for_status()
        data = response.json()
        
        result = {
            'success': True,
            'source': 'external_api',
            'fact': data
        }
        
        return format_response(result, get_format())
    except Exception as e:
        return format_response({
            'success': False,
            'error': str(e)
        }, get_format()), 500

@app.route('/api/facts/today', methods=['GET'])
def get_today_fact():
    """GET: Obtém o fact do dia da API externa"""
    try:
        response = requests.get('https://uselessfacts.jsph.pl/api/v2/facts/today')
        response.raise_for_status()
        data = response.json()
        
        result = {
            'success': True,
            'source': 'external_api',
            'fact': data
        }
        
        return format_response(result, get_format())
    except Exception as e:
        return format_response({
            'success': False,
            'error': str(e)
        }, get_format()), 500

@app.route('/api/facts', methods=['GET'])
def get_all_facts():
    """GET: Lista todos os facts armazenados (com Protocol Buffer)"""
    format_type = get_format()
    
    if format_type == 'protobuf' or format_type == 'proto':
        # Retorna em Protocol Buffer (formato binário)
        facts_list = facts_pb2.FactsList()
        
        for fact_id, fact_data in facts_storage.items():
            fact = facts_list.facts.add()
            fact.id = fact_id
            fact.text = fact_data.get('text', '')
            fact.source = fact_data.get('source', '')
            fact.language = fact_data.get('language', 'en')
            fact.permalink = fact_data.get('permalink', '')
            fact.saved_at = fact_data.get('saved_at', '')
        
        # Serializa para formato binário Protocol Buffer
        serialized = facts_list.SerializeToString()
        
        # Retorna como binário com Content-Type correto
        response = Response(serialized, mimetype='application/x-protobuf')
        response.headers['Content-Disposition'] = 'attachment; filename=facts.pb'
        return response
    
    # Retorna em JSON ou XML
    result = {
        'success': True,
        'count': len(facts_storage),
        'facts': list(facts_storage.values())
    }
    
    return format_response(result, format_type)

@app.route('/api/facts', methods=['POST'])
def create_fact():
    """POST: Salva um novo fact"""
    global fact_id_counter
    
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return format_response({
                'success': False,
                'error': 'Campo "text" é obrigatório'
            }, get_format()), 400
        
        fact = {
            'id': fact_id_counter,
            'text': data['text'],
            'source': data.get('source', 'user'),
            'language': data.get('language', 'en'),
            'permalink': data.get('permalink', ''),
            'saved_at': datetime.now().isoformat()
        }
        
        facts_storage[fact_id_counter] = fact
        fact_id_counter += 1
        
        result = {
            'success': True,
            'message': 'Fact criado com sucesso',
            'fact': fact
        }
        
        return format_response(result, get_format()), 201
    except Exception as e:
        return format_response({
            'success': False,
            'error': str(e)
        }, get_format()), 500

@app.route('/api/facts/<int:fact_id>', methods=['GET'])
def get_fact(fact_id):
    """GET: Obtém um fact específico por ID"""
    if fact_id not in facts_storage:
        return format_response({
            'success': False,
            'error': 'Fact não encontrado'
        }, get_format()), 404
    
    result = {
        'success': True,
        'fact': facts_storage[fact_id]
    }
    
    return format_response(result, get_format())

@app.route('/api/facts/<int:fact_id>', methods=['DELETE'])
def delete_fact(fact_id):
    """DELETE: Remove um fact"""
    if fact_id not in facts_storage:
        return format_response({
            'success': False,
            'error': 'Fact não encontrado'
        }, get_format()), 404
    
    deleted_fact = facts_storage.pop(fact_id)
    
    result = {
        'success': True,
        'message': 'Fact deletado com sucesso',
        'deleted_fact': deleted_fact
    }
    
    return format_response(result, get_format())

# ==================== FUNCIONALIDADE EXTRA 1: FAVORITOS ====================

@app.route('/api/favorites', methods=['GET'])
def get_favorites():
    """GET: Lista todos os facts favoritos"""
    result = {
        'success': True,
        'count': len(favorites_storage),
        'favorites': list(favorites_storage.values())
    }
    
    return format_response(result, get_format())

@app.route('/api/favorites', methods=['POST'])
def add_favorite():
    """POST: Adiciona um fact aos favoritos"""
    global favorite_id_counter
    
    try:
        data = request.get_json()
        
        if not data or 'fact_text' not in data:
            return format_response({
                'success': False,
                'error': 'Campo "fact_text" é obrigatório'
            }, get_format()), 400
        
        favorite = {
            'id': favorite_id_counter,
            'fact_text': data['fact_text'],
            'notes': data.get('notes', ''),
            'added_at': datetime.now().isoformat()
        }
        
        favorites_storage[favorite_id_counter] = favorite
        favorite_id_counter += 1
        
        result = {
            'success': True,
            'message': 'Favorito adicionado com sucesso',
            'favorite': favorite
        }
        
        return format_response(result, get_format()), 201
    except Exception as e:
        return format_response({
            'success': False,
            'error': str(e)
        }, get_format()), 500

@app.route('/api/favorites/<int:favorite_id>', methods=['DELETE'])
def delete_favorite(favorite_id):
    """DELETE: Remove um favorito"""
    if favorite_id not in favorites_storage:
        return format_response({
            'success': False,
            'error': 'Favorito não encontrado'
        }, get_format()), 404
    
    deleted_favorite = favorites_storage.pop(favorite_id)
    
    result = {
        'success': True,
        'message': 'Favorito removido com sucesso',
        'deleted_favorite': deleted_favorite
    }
    
    return format_response(result, get_format())

# ==================== FUNCIONALIDADE EXTRA 2: ESTATÍSTICAS ====================

@app.route('/api/stats', methods=['GET'])
def get_statistics():
    """GET: Obtém estatísticas do sistema"""
    total_facts = len(facts_storage)
    total_favorites = len(favorites_storage)
    
    # Conta facts por fonte
    sources_count = {}
    for fact in facts_storage.values():
        source = fact.get('source', 'unknown')
        sources_count[source] = sources_count.get(source, 0) + 1
    
    # Conta facts por idioma
    languages_count = {}
    for fact in facts_storage.values():
        lang = fact.get('language', 'unknown')
        languages_count[lang] = languages_count.get(lang, 0) + 1
    
    result = {
        'success': True,
        'statistics': {
            'total_facts': total_facts,
            'total_favorites': total_favorites,
            'facts_by_source': sources_count,
            'facts_by_language': languages_count,
            'generated_at': datetime.now().isoformat()
        }
    }
    
    return format_response(result, get_format())

# ==================== ROTA RAIZ ====================

@app.route('/', methods=['GET'])
def home():
    """Página inicial com documentação"""
    docs = {
        'message': 'API REST de Facts - Documentação',
        'version': '1.0.0',
        'endpoints': {
            'CRUD de Facts': {
                'GET /api/facts/random': 'Obtém fact aleatório da API externa',
                'GET /api/facts/today': 'Obtém fact do dia',
                'GET /api/facts': 'Lista todos os facts (suporta Protocol Buffer)',
                'POST /api/facts': 'Cria um novo fact',
                'GET /api/facts/<id>': 'Obtém fact por ID',
                'DELETE /api/facts/<id>': 'Deleta um fact'
            },
            'Favoritos': {
                'GET /api/favorites': 'Lista favoritos',
                'POST /api/favorites': 'Adiciona favorito',
                'DELETE /api/favorites/<id>': 'Remove favorito'
            },
            'Estatísticas': {
                'GET /api/stats': 'Obtém estatísticas do sistema'
            }
        },
        'formatos': {
            'json': 'Adicione ?format=json (padrão)',
            'xml': 'Adicione ?format=xml',
            'protobuf': 'Adicione ?format=protobuf (apenas GET /api/facts)'
        }
    }
    
    return jsonify(docs)

if __name__ == '__main__':
    app.run(debug=True, port=5000)