# API de Receitas

## Descrição
Esse projeto tem como objetivo desenvolver uma API de receitas, em que é possível cadastrar, visualizar, modificar e excluir ingredientes e receitas, ou seja, fazer o CRUD completo dos dois itens.

Cada ingrediente tem nome e unidade de medida, e cada receita tem seus ingredientes, quantidade de cada ingrediente e modo de preparo.

Cada receita só pode ser feita com os ingredientes já adicionados.

Por conta dessa regra de negócio, foram feitas 3 tabelas no banco de dados, a de ingredientes, receitas e também a que relaciona cada ingrediente com cada receita em que ele é usado.

O projeto foi feito usando o Framework Flask, da linguagem Python, e também o MySQL.

## Como utilizar
A API oferece os seguintes endpoints para CRUD (Criar, Ler, Atualizar e Deletar) de ingredientes e Receitas:

- **GET** `/ingredientes`: Retorna todos os ingredientes.
- **GET** `/ingrediente/<id>`: Retorna um ingrediente específico pelo id.
- **POST** `/ingrediente`: Adiciona um novo ingrediente.
- **PUT** `/ingrediente/<id>`: Atualiza as informações de um ingrediente existente.
- **DELETE** `/ingrediente/<id>`: Exclui um ingrediente.
 
- **GET** `/receitas`: Retorna todas as receitas.
- **GET** `/receita/<id>`: Retorna uma receita específica pelo id.
- **POST** `/receita`: Adiciona uma nova receita.
- **PUT** `/receita/<id>`: Atualiza as informações de uma receita existente.
- **DELETE** `/receita/<id>`: Exclui uma receita.

## Como executar o projeto localmente
1. Primeiramente **clone** deste repositório para sua máquina:
    ```bash
    git clone https://github.com/Roberto651/API_Receitas.git 
    cd API_Receitas

2. Instale as dependências no diretório do projeto usando o pip:
   ```bash
    pip install -r requirements.txt

3. Instale o MySQL(eu utilizei o Xampp, com o phpMyAdmin) e crie um banco de dados chamado receitas no MySQL:
   ```SQL
    CREATE DATABASE receitas;

4. Modifique a linha 7 do arquivo app.py, colocando os dados pedidos abaixo:
   ```bash
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://usuario:senha@localhost/receitas'

5. Agora, com tudo configurado, execute o seguinte comando no terminal:
   ```bash
    python .\app.py