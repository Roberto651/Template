from flask import Flask, Response, request
from flask_sqlalchemy import SQLAlchemy
import json

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/receitas'

db = SQLAlchemy(app)

# MODELOS
class Ingrediente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50))
    unidade = db.Column(db.String(50))

    def to_json(self):
        return {"id": self.id, "nome": self.nome, "unidade": self.unidade}


class Receita(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    modo_preparo = db.Column(db.Text)
    ingredientes = db.relationship("ReceitaIngrediente", backref="receita", cascade="all, delete-orphan")

    def to_json(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "modo_preparo": self.modo_preparo,
            "ingredientes": [ri.to_json() for ri in self.ingredientes]
        }


class ReceitaIngrediente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    receita_id = db.Column(db.Integer, db.ForeignKey("receita.id"))
    ingrediente_id = db.Column(db.Integer, db.ForeignKey("ingrediente.id"))
    quantidade = db.Column(db.Float)

    ingrediente = db.relationship("Ingrediente")

    def to_json(self):
        return {
            "ingrediente": self.ingrediente.to_json(),
            "quantidade": self.quantidade
        }

# FUNÇÃO AUXILIAR
def gera_response(status, nome_do_conteudo, conteudo, mensagem=False):
    body = {}
    body[nome_do_conteudo] = conteudo

    if mensagem:
        body["mensagem"] = mensagem

    return Response(json.dumps(body), status=status, mimetype="application/json")

# ROTAS INGREDIENTES
@app.route("/ingredientes", methods=["GET"])
def seleciona_ingredientes():
    ingredientes_objetos = Ingrediente.query.all()
    ingredientes_json = [ingrediente.to_json() for ingrediente in ingredientes_objetos]
    return gera_response(200, "ingredientes", ingredientes_json)


@app.route("/ingrediente/<int:id>", methods=["GET"])
def seleciona_ingrediente(id):
    ingrediente_objeto = Ingrediente.query.get(id)
    if not ingrediente_objeto:
        return gera_response(404, "ingrediente", {}, "Ingrediente não encontrado")
    return gera_response(200, "ingrediente", ingrediente_objeto.to_json())


@app.route("/ingrediente", methods=["POST"])
def cria_ingrediente():
    body = request.get_json()
    try:
        ingrediente = Ingrediente(nome=body["nome"], unidade=body["unidade"])
        db.session.add(ingrediente)
        db.session.commit()
        return gera_response(201, "ingrediente", ingrediente.to_json(), "Criado com sucesso")
    except Exception as e:
        print(e)
        return gera_response(400, "ingrediente", {}, "Erro ao cadastrar")


@app.route("/ingrediente/<int:id>", methods=["PUT"])
def atualiza_ingrediente(id):
    ingrediente_objeto = Ingrediente.query.get(id)
    if not ingrediente_objeto:
        return gera_response(404, "ingrediente", {}, "Ingrediente não encontrado")

    body = request.get_json()
    try:
        if 'nome' in body:
            ingrediente_objeto.nome = body['nome']
        if 'unidade' in body:
            ingrediente_objeto.unidade = body['unidade']

        db.session.commit()
        return gera_response(200, "ingrediente", ingrediente_objeto.to_json(), "Atualizado com sucesso")
    except Exception as e:
        print(e)
        return gera_response(400, "ingrediente", {}, "Erro ao atualizar")


@app.route("/ingrediente/<int:id>", methods=["DELETE"])
def deleta_ingrediente(id):
    ingrediente_objeto = Ingrediente.query.get(id)
    if not ingrediente_objeto:
        return gera_response(404, "ingrediente", {}, "Ingrediente não encontrado")
    try:
        db.session.delete(ingrediente_objeto)
        db.session.commit()
        return gera_response(200, "ingrediente", ingrediente_objeto.to_json(), "Deletado com sucesso")
    except Exception as e:
        print(e)
        return gera_response(400, "ingrediente", {}, "Erro ao deletar")

# ROTAS RECEITAS
@app.route("/receitas", methods=["GET"])
def seleciona_receitas():
    receitas = Receita.query.all()
    receitas_json = [r.to_json() for r in receitas]
    return gera_response(200, "receitas", receitas_json)


@app.route("/receita/<int:id>", methods=["GET"])
def seleciona_receita(id):
    receita = Receita.query.get(id)
    if not receita:
        return gera_response(404, "receita", {}, "Receita não encontrada")
    return gera_response(200, "receita", receita.to_json())


@app.route("/receita", methods=["POST"])
def cria_receita():
    body = request.get_json()
    try:
        nova_receita = Receita(nome=body["nome"], modo_preparo=body["modo_preparo"])
        db.session.add(nova_receita)
        db.session.flush()  # garante o ID para associar os ingredientes

        for item in body["ingredientes"]:
            ingrediente_id = item["ingrediente_id"]
            quantidade = item["quantidade"]

            ingrediente = Ingrediente.query.get(ingrediente_id)
            if not ingrediente:
                db.session.rollback()
                return gera_response(400, "receita", {}, f"Ingrediente com id {ingrediente_id} não encontrado.")

            ri = ReceitaIngrediente(receita_id=nova_receita.id, ingrediente_id=ingrediente_id, quantidade=quantidade)
            db.session.add(ri)

        db.session.commit()
        return gera_response(201, "receita", nova_receita.to_json(), "Receita criada com sucesso")
    except Exception as e:
        print(e)
        db.session.rollback()
        return gera_response(400, "receita", {}, "Erro ao cadastrar receita")


@app.route("/receita/<int:id>", methods=["PUT"])
def atualiza_receita(id):
    receita = Receita.query.get(id)
    if not receita:
        return gera_response(404, "receita", {}, "Receita não encontrada")

    body = request.get_json()

    try:
        # Atualiza campos simples
        if "nome" in body:
            receita.nome = body["nome"]
        if "modo_preparo" in body:
            receita.modo_preparo = body["modo_preparo"]

        # Atualiza ingredientes se enviados
        if "ingredientes" in body:
            # Remove ingredientes anteriores
            ReceitaIngrediente.query.filter_by(receita_id=receita.id).delete()

            # Adiciona os novos ingredientes
            for item in body["ingredientes"]:
                ingrediente_id = item["ingrediente_id"]
                quantidade = item["quantidade"]

                ingrediente = Ingrediente.query.get(ingrediente_id)
                if not ingrediente:
                    db.session.rollback()
                    return gera_response(400, "receita", {}, f"Ingrediente com id {ingrediente_id} não encontrado.")

                novo_ingrediente = ReceitaIngrediente(
                    receita_id=receita.id,
                    ingrediente_id=ingrediente_id,
                    quantidade=quantidade
                )
                db.session.add(novo_ingrediente)

        db.session.commit()
        return gera_response(200, "receita", receita.to_json(), "Receita atualizada com sucesso")
    except Exception as e:
        print(e)
        db.session.rollback()
        return gera_response(400, "receita", {}, "Erro ao atualizar receita")


@app.route("/receita/<int:id>", methods=["DELETE"])
def deleta_receita(id):
    receita = Receita.query.get(id)
    if not receita:
        return gera_response(404, "receita", {}, "Receita não encontrada")
    try:
        db.session.delete(receita)
        db.session.commit()
        return gera_response(200, "receita", receita.to_json(), "Receita deletada com sucesso")
    except Exception as e:
        print(e)
        return gera_response(400, "receita", {}, "Erro ao deletar receita")

# EXECUÇÃO
if __name__ == "__main__":
    app.run(debug=True)
