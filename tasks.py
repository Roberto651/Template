from invoke import task

@task
def install(c):
    print("Instalando dependências...")
    c.run('pip install -r requirements.txt')

@task
def run(c):
    print("Rodando o projeto...")
    c.run('python app.py')

@task
def clean(c):
    print("Limpando arquivos temporários...")
    c.run('find . -type d -name "__pycache__" -exec rm -r {} +')
    c.run('find . -type f -name "*.pyc" -exec rm -f {} +')

@task
def venv(c):
    print("Criando ambiente virtual...")
    c.run('python3 -m venv venv')
    c.run('source venv/bin/activate && pip install -r requirements.txt')
