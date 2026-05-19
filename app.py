import os
from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)

app.secret_key = 'chave_secreta_para_o_cancioneiro'
SENHA_ADMIN = 'admin123'

PASTA_STATIC = os.path.join(app.root_path, 'static')

# Nosso "Banco de Dados" provisório
MUSICAS = [
    {
        "id": 1,
        "titulo": "Ninguém te Ama como Eu",
        "artista": "Anjos de Resgate",
        "tom": "G",
        "letra_cifra": "G                   Bm\nTenho esperado este momento\nC             Am          D\nTenho esperado que viesses a mim"
    },
    {
        "id": 2,
        "titulo": "Como És Lindo",
        "artista": "Vida Reluz",
        "tom": "D",
        "letra_cifra": "D              A         Bm\nOlho em teus olhos e calo-me\nG              Em        A\nBeijo teus pés e adoro-te"
    }
]

@app.route('/')
def home():
    termo_busca = request.args.get('search', '').strip().lower()
    if termo_busca:
        musicas_filtradas = [m for m in MUSICAS if termo_busca in m["titulo"].lower() or termo_busca in m["artista"].lower()]
    else:
        musicas_filtradas = MUSICAS

    eh_admin = session.get('admin_logado', False)
    return render_template('index.html', lista_de_musicas=musicas_filtradas, termo_busca=termo_busca, eh_admin=eh_admin)


# ROTA DA MÚSICA TOTALMENTE LIMPA E DIRETA
@app.route('/musica/<int:musica_id>')
def exibir_musica(musica_id):
    musica_encontrada = None
    for m in MUSICAS:
        if m["id"] == musica_id:
            musica_encontrada = m
            break
            
    if musica_encontrada:
        eh_admin = session.get('admin_logado', False)
        return render_template('musica.html', dados_da_musica=musica_encontrada, eh_admin=eh_admin)
    
    return "<h1>Música não encontrada!</h1>", 404


@app.route('/novo', methods=['GET', 'POST'])
def nova_musica():
    if not session.get('admin_logado', False):
        return redirect('/login')

    if request.method == 'POST':
        titulo = request.form['titulo']
        artista = request.form['artista']
        tom = request.form['tom'].upper().strip()
        letra_cifra = request.form['letra_cifra']
        
        novo_id = len(MUSICAS) + 1
        nova = {
            "id": novo_id,
            "titulo": titulo,
            "artista": artista,
            "tom": tom,
            "letra_cifra": letra_cifra
        }
        MUSICAS.append(nova)
        return redirect('/')
        
    return render_template('novo.html')


@app.route('/editar/<int:musica_id>', methods=['GET', 'POST'])
def editar_musica(musica_id):
    if not session.get('admin_logado', False):
        return redirect('/login')

    musica_encontrada = None
    for m in MUSICAS:
        if m["id"] == musica_id:
            musica_encontrada = m
            break

    if not musica_encontrada:
        return "<h1>Música não encontrada!</h1>", 404

    if request.method == 'POST':
        musica_encontrada['titulo'] = request.form['titulo']
        musica_encontrada['artista'] = request.form['artista']
        musica_encontrada['tom'] = request.form['tom'].upper().strip()
        musica_encontrada['letra_cifra'] = request.form['letra_cifra']
        return redirect(f'/musica/{musica_id}')

    return render_template('editar.html', musica=musica_encontrada)


@app.route('/deletar/<int:musica_id>', methods=['POST', 'GET'])
def deletar_musica(musica_id):
    if not session.get('admin_logado', False):
        return redirect('/login')
    
    global MUSICAS
    MUSICAS = [m for m in MUSICAS if m["id"] != musica_id]
    return redirect('/')


@app.route('/alterar-fundo', methods=['POST'])
def alterar_fundo():
    if not session.get('admin_logado', False):
        return redirect('/login')
        
    if 'imagem_fundo' in request.files:
        arquivo = request.files['imagem_fundo']
        if arquivo.filename != '':
            caminho_salvamento = os.path.join(PASTA_STATIC, 'unnamed.jpg')
            arquivo.save(caminho_salvamento)
            
    return redirect('/')


@app.route('/login', methods=['GET', 'POST'])
def login():
    erro = None
    if request.method == 'POST':
        senha_digitada = request.form['senha']
        if senha_digitada == SENHA_ADMIN:
            session['admin_logado'] = True
            return redirect('/')
        else:
            erro = "Senha incorreta! Tente novamente."
    return render_template('login.html', erro=erro)

@app.route('/logout')
def logout():
    session.pop('admin_logado', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))