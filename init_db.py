from app import db, Cliente, Lojista, Produto, Pedido, Mensagem
import os

# Caminho do banco de dados
db_path = '/data/data/com.termux/files/home/mamao-chat/database.db'

# Apaga o banco antigo se existir
if os.path.exists(db_path):
    os.remove(db_path)

# Cria todas as tabelas
with db.app.app_context():
    db.create_all()

    # Adiciona dados iniciais
    if not Lojista.query.filter_by(nome="Mercado do Bairro (Simulação)").first():
        lojista = Lojista(nome="Mercado do Bairro (Simulação)", senha="123456", endereco="Rua Teste, 123", telefone="11987654321", cep="12345-678", raio=5, latitude=-23.5505, longitude=-46.6333)
        db.session.add(lojista)
        db.session.commit()
        produtos = [
            Produto(nome="Coca-Cola 2L", tipo="Refrigerante", categoria="Bebidas", subcategoria="Refrigerantes", unidade="2L", quantidade=999, codigo="001", preco=15.0, localizacao="Prateleira 1", custo_unitario=10.0, fornecedor="Coca-Cola Co", lojista_id=lojista.id),
            Produto(nome="Pizza", tipo="Congelada", categoria="Alimentos", subcategoria="Congelados", unidade="un", quantidade=999, codigo="002", preco=30.0, localizacao="Câmara Fria 1", custo_unitario=20.0, fornecedor="Pizzaria Local", lojista_id=lojista.id),
            Produto(nome="Arroz", tipo="Grão", categoria="Alimentos", subcategoria="Não perecíveis", unidade="1kg", quantidade=999, codigo="003", preco=10.0, localizacao="Prateleira 2", custo_unitario=7.0, fornecedor="Arroz Bom", lojista_id=lojista.id),
        ]
        db.session.add_all(produtos)
        db.session.commit()

print("Banco de dados inicializado com sucesso!"
