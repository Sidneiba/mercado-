from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
import math

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'  # Troque por algo único
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////data/data/com.termux/files/home/mamao-chat/database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelos do banco de dados
class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    senha = db.Column(db.String(6), nullable=False)
    endereco = db.Column(db.String(200), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    cep = db.Column(db.String(10), nullable=False)
    latitude = db.Column(db.Float, default=0.0)
    longitude = db.Column(db.Float, default=0.0)

class Lojista(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    senha = db.Column(db.String(6), nullable=False)
    endereco = db.Column(db.String(200), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    cep = db.Column(db.String(10), nullable=False)
    raio = db.Column(db.Integer, default=5)
    online = db.Column(db.Boolean, default=False)
    latitude = db.Column(db.Float, default=0.0)
    longitude = db.Column(db.Float, default=0.0)

class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    categoria = db.Column(db.String(50), nullable=False)
    subcategoria = db.Column(db.String(50))
    unidade = db.Column(db.String(20), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    codigo = db.Column(db.String(10), nullable=False)
    disponivel = db.Column(db.Boolean, default=True)
    preco = db.Column(db.Float, nullable=False)
    localizacao = db.Column(db.String(50))
    custo_unitario = db.Column(db.Float)
    fornecedor = db.Column(db.String(100))
    data_validade = db.Column(db.String(10))
    lojista_id = db.Column(db.Integer, db.ForeignKey('lojista.id'), nullable=False)

class Pedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    lojista_id = db.Column(db.Integer, db.ForeignKey('lojista.id'), nullable=False)
    itens = db.Column(db.String(500), nullable=False)
    total = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default="Em andamento")
    endereco_entrega = db.Column(db.String(200))
    forma_pagamento = db.Column(db.String(50))

class Mensagem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'))
    lojista_id = db.Column(db.Integer, db.ForeignKey('lojista.id'))
    texto = db.Column(db.String(500), nullable=True)
    remetente = db.Column(db.String(10), nullable=False)

# Função pra calcular distância
def calcular_distancia(lat1, lon1, lat2, lon2):
    if not all([lat1, lon1, lat2, lon2]):
        return float('inf')
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

# Rotas
@app.route('/')
def abertura():
    return render_template('index.html', pagina='abertura')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        tipo = request.form['tipo']
        nome = request.form['nome']
        senha = request.form['senha']
        if tipo == 'cliente':
            cliente = Cliente.query.filter_by(nome=nome, senha=senha).first()
            if cliente:
                session['cliente_id'] = cliente.id
                session['tipo'] = 'cliente'
                return redirect(url_for('painel'))
            flash('Nome ou senha inválidos!')
        elif tipo == 'lojista':
            lojista = Lojista.query.filter_by(nome=nome, senha=senha).first()
            if lojista:
                lojista.online = True
                db.session.commit()
                session['lojista_id'] = lojista.id
                session['tipo'] = 'lojista'
                return redirect(url_for('caixa'))
            flash('Nome ou senha inválidos!')
    return render_template('index.html', pagina='login')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        tipo = request.form['tipo']
        nome = request.form['nome']
        senha = request.form['senha']
        endereco = request.form['endereco']
        telefone = request.form['telefone']
        cep = request.form['cep']
        latitude = float(request.form.get('latitude', 0.0))
        longitude = float(request.form.get('longitude', 0.0))
        if tipo == 'cliente':
            if Cliente.query.filter_by(nome=nome).first():
                flash('Cliente já cadastrado!')
            else:
                cliente = Cliente(nome=nome, senha=senha, endereco=endereco, telefone=telefone, cep=cep, latitude=latitude, longitude=longitude)
                db.session.add(cliente)
                db.session.commit()
                session['cliente_id'] = cliente.id
                session['tipo'] = 'cliente'
                return redirect(url_for('painel'))
        elif tipo == 'lojista':
            raio = int(request.form.get('raio', 5))  # Pega o raio só pra lojista, default 5 se não vier
            if Lojista.query.filter_by(nome=nome).first():
                flash('Lojista já cadastrado!')
            else:
                lojista = Lojista(nome=nome, senha=senha, endereco=endereco, telefone=telefone, cep=cep, raio=raio, latitude=latitude, longitude=longitude)
                db.session.add(lojista)
                db.session.commit()
                session['lojista_id'] = lojista.id
                session['tipo'] = 'lojista'
                return redirect(url_for('caixa'))
        flash('Erro no cadastro, tente novamente!')
    return render_template('index.html', pagina='cadastro')

@app.route('/painel', methods=['GET', 'POST'])
def painel():
    if 'tipo' not in session or session['tipo'] != 'cliente':
        return redirect(url_for('login'))
    cliente = Cliente.query.get(session['cliente_id'])
    lojistas = [l for l in Lojista.query.filter_by(online=True).all() if calcular_distancia(cliente.latitude, cliente.longitude, l.latitude, l.longitude) <= min(l.raio, 10)]
    lojista_id = session.get('lojista_selecionado', lojistas[0].id if lojistas else None)
    if not lojista_id:
        return render_template('index.html', pagina='painel_cliente', cliente=cliente, lojistas=lojistas, produtos=[], carrinho_itens=[], total=0)
    produtos = Produto.query.filter_by(lojista_id=lojista_id, disponivel=True).all()
    if 'carrinho' not in session:
        session['carrinho'] = []
    if request.method == 'POST':
        acao = request.form.get('acao')
        if acao == 'selecionar_lojista':
            session['lojista_selecionado'] = int(request.form['lojista_id'])
            session.modified = True
        elif acao == 'adicionar':
            produto_id = int(request.form['produto_id'])
            produto = Produto.query.get(produto_id)
            session['carrinho'].append({'id': produto.id, 'nome': produto.nome, 'preco': produto.preco, 'lojista_id': lojista_id})
            session.modified = True
        elif acao == 'pagar':
            carrinho_itens = [item for item in session['carrinho'] if item['lojista_id'] == lojista_id]
            if carrinho_itens:
                total = sum(item['preco'] for item in carrinho_itens)
                itens_texto = ", ".join(f"{item['nome']} (R${item['preco']:.2f})" for item in carrinho_itens)
                pedido = Pedido(cliente_id=cliente.id, lojista_id=lojista_id, itens=itens_texto, total=total, endereco_entrega=cliente.endereco, forma_pagamento="A combinar")
                db.session.add(pedido)
                db.session.commit()
                session['carrinho'] = [item for item in session['carrinho'] if item['lojista_id'] != lojista_id]
                session.modified = True
                return redirect(url_for('chat', lojista_id=lojista_id))
    carrinho_itens = [item for item in session['carrinho'] if item['lojista_id'] == lojista_id]
    total = sum(item['preco'] for item in carrinho_itens)
    lojista_selecionado = Lojista.query.get(lojista_id)
    return render_template('index.html', pagina='painel_cliente', cliente=cliente, lojistas=lojistas, produtos=produtos, carrinho_itens=carrinho_itens, total=total, lojista_selecionado=lojista_selecionado)

@app.route('/caixa', methods=['GET', 'POST'])
def caixa():
    if 'tipo' not in session or session['tipo'] != 'lojista':
        return redirect(url_for('login'))
    lojista = Lojista.query.get(session['lojista_id'])
    if request.method == 'POST':
        acao = request.form.get('acao')
        if acao == 'abrir_loja':
            lojista.online = True
            db.session.commit()
        elif acao == 'fechar_loja':
            lojista.online = False
            db.session.commit()
        elif acao == 'finalizar_pedido':
            pedido_id = int(request.form['pedido_id'])
            pedido = Pedido.query.get(pedido_id)
            pedido.status = "Finalizado"
            db.session.commit()
        elif acao == 'cancelar_pedido':
            pedido_id = int(request.form['pedido_id'])
            pedido = Pedido.query.get(pedido_id)
            pedido.status = "Cancelado"
            db.session.commit()
    pedidos_abertos = Pedido.query.filter_by(lojista_id=lojista.id, status="Em andamento").all()
    catalogo = Produto.query.filter_by(lojista_id=lojista.id, disponivel=True).all()
    return render_template('index.html', pagina='caixa', lojista=lojista, pedidos_abertos=pedidos_abertos, catalogo=catalogo)

@app.route('/estoque', methods=['GET', 'POST'])
def estoque():
    if 'tipo' not in session or session['tipo'] != 'lojista':
        return redirect(url_for('login'))
    lojista = Lojista.query.get(session['lojista_id'])
    if not lojista.online:
        flash("A loja deve estar online para gerenciar o estoque!")
        return redirect(url_for('caixa'))
    if request.method == 'POST':
        acao = request.form.get('acao')
        if acao == 'adicionar_produto':
            nome = request.form['nome']
            tipo = request.form['tipo']
            categoria = request.form['categoria']
            subcategoria = request.form.get('subcategoria', '')
            unidade = request.form['unidade']
            quantidade = int(request.form['quantidade'])
            codigo = request.form['codigo']
            preco = float(request.form['preco'])
            localizacao = request.form['localizacao']
            custo_unitario = float(request.form.get('custo_unitario', 0))
            fornecedor = request.form.get('fornecedor', '')
            data_validade = request.form.get('data_validade', '')
            produto = Produto(nome=nome, tipo=tipo, categoria=categoria, subcategoria=subcategoria, unidade=unidade, quantidade=quantidade, codigo=codigo, preco=preco, localizacao=localizacao, custo_unitario=custo_unitario, fornecedor=fornecedor, data_validade=data_validade, lojista_id=lojista.id)
            db.session.add(produto)
            db.session.commit()
        elif acao == 'atualizar_estoque':
            produto_id = int(request.form['produto_id'])
            quantidade = int(request.form['quantidade'])
            produto = Produto.query.get(produto_id)
            produto.quantidade = quantidade
            produto.disponivel = quantidade > 0
            db.session.commit()
        elif acao == 'alterar_raio':
            lojista.raio = int(request.form['raio'])
            db.session.commit()
    estoque = Produto.query.filter_by(lojista_id=lojista.id).all()
    return render_template('index.html', pagina='estoque', lojista=lojista, estoque=estoque)

@app.route('/chat/<int:lojista_id>', methods=['GET', 'POST'])
def chat(lojista_id):
    if 'tipo' not in session:
        return redirect(url_for('login'))
    lojista = Lojista.query.get(lojista_id)
    if session['tipo'] == 'cliente':
        cliente = Cliente.query.get(session['cliente_id'])
        if request.method == 'POST':
            acao = request.form.get('acao')
            if acao == 'confirmar_pagamento':
                pedido_id = int(request.form['pedido_id'])
                pedido = Pedido.query.get(pedido_id)
                if pedido.status == "Em andamento":
                    pedido.forma_pagamento = "Confirmado pelo cliente"
                    db.session.commit()
            elif acao == 'confirmar_entrega':
                pedido_id = int(request.form['pedido_id'])
                pedido = Pedido.query.get(pedido_id)
                if pedido.status == "Em andamento" and pedido.forma_pagamento == "Confirmado pelo cliente":
                    pedido.status = "Finalizado"
                    db.session.commit()
            else:
                texto = request.form['texto']
                mensagem = Mensagem(cliente_id=cliente.id, lojista_id=lojista_id, texto=texto, remetente='cliente')
                db.session.add(mensagem)
                db.session.commit()
        mensagens = Mensagem.query.filter_by(cliente_id=cliente.id, lojista_id=lojista_id).all()
        pedidos_abertos = Pedido.query.filter_by(cliente_id=cliente.id, lojista_id=lojista_id, status="Em andamento").all()
        return render_template('index.html', pagina='chat', cliente=cliente, lojista=lojista, mensagens=mensagens, pedidos_abertos=pedidos_abertos)
    elif session['tipo'] == 'lojista':
        cliente_id = request.args.get('cliente_id')
        if not cliente_id:
            return redirect(url_for('caixa'))
        cliente = Cliente.query.get(int(cliente_id))
        if request.method == 'POST':
            texto = request.form['texto']
            mensagem = Mensagem(cliente_id=cliente.id, lojista_id=lojista_id, texto=texto, remetente='lojista')
            db.session.add(mensagem)
            db.session.commit()
        mensagens = Mensagem.query.filter_by(cliente_id=cliente.id, lojista_id=lojista_id).all()
        pedidos_abertos = Pedido.query.filter_by(cliente_id=cliente.id, lojista_id=lojista_id, status="Em andamento").all()
        return render_template('index.html', pagina='chat', cliente=cliente, lojista=lojista, mensagens=mensagens, pedidos_abertos=pedidos_abertos)

@app.route('/logout')
def logout():
    if 'tipo' in session and session['tipo'] == 'lojista':
        lojista = Lojista.query.get(session['lojista_id'])
        lojista.online = False
        db.session.commit()
    session.clear()
    return redirect(url_for('abertura'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
