from flask import Flask, render_template, request, redirect, url_for, session, flash
import re

app = Flask(__name__)
app.secret_key = 'chave_secreta_louvemos_digital'

# LISTA DE NOTAS PARA TRANSPOSIÇÃO DE TOM (Matriz de 12 semitons)
NOTAS = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

# BANCO DE DADOS EM MEMÓRIA (Músicas Padrão)
musicas = {
    1: {
        'titulo': 'Exemplo de Cifra',
        'artista': 'Ministério de Música',
        'tom': 'E',
        'letra': 'G        D\nLouvemos ao Senhor\nEm        C\nCom toda nossa alma e amor'
    }
}
proximo_id = 2

# FUNÇÃO MATEMÁTICA PARA MUDAR O TOM DOS ACORDES
def transpor_letra(texto, semitons):
    if semitons == 0:
        return texto
    
    def transpor_acorde(match):
        acorde = match.group(0)
        nota_match = re.match(r'[A-G]#?', acorde)
        if not nota_match:
            return acorde
        
        nota_original = nota_match.group(0)
        resto_acorde = acorde[len(nota_original):]
        
        if nota_original in NOTAS:
            idx = NOTAS.index(nota_original)
            novo_idx = (idx + semitons) % 12
            return NOTAS[novo_idx] + resto_acorde
        return acorde

    # Detecta padrões de acordes isolados nas linhas de cifra
    padrao_acorde = r'\b[A-G](#)?(m|maj|min|7|9|4|sus|aug|dim)?\b'
    return re.sub(padrao_acorde, transpor_acorde, texto)

# ROTA DA PÁGINA INICIAL (LISTA DE MÚSICAS)
@app.route('/')
def index():
    busca = request.args.get('busca', '').lower()
    musicas_filtradas = {}
    
    for id_m, m in musicas.items():
        if busca in m['titulo'].lower() or busca in m['artista'].lower():
            musicas_filtradas[id_m] = m
            
    return render_template('index.html', musicas=musicas_filtradas, logado=session.get('logado'))

# ROTA DA ABA DE LETRAS E MUDANÇA DE TOM
@app.route('/musica/<int:id_musica>')
def ver_musica(id_musica):
    semitons = request.args.get('semitons', default=0, type=int)
    musica = musicas.get(id_musica)
    
    if not musica:
        flash('Música não encontrada!', 'danger')
        return redirect(url_for('index'))
        
    letra_transposta = transpor_letra(musica['letra'], semitons)
    
    return render_template('musica.html', 
                           musica=musica, 
                           id_musica=id_musica, 
                           letra_transposta=letra_transposta, 
                           semitons=semitons)

# ROTA DE LOGIN DO ADMINISTRADOR
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        senha = request.form.get('senha')
        
        if usuario == 'admin' and senha == 'admin123':
            session['logado'] = True
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Usuário ou senha incorretos.', 'danger')
            
    return render_template('login.html')

# ROTA PARA LOGOUT
@app.route('/logout')
def logout():
    session.pop('logado', None)
    flash('Você saiu da Área do Administrador.', 'info')
    return redirect(url_for('index'))

# ROTA PARA ADICIONAR NOVA MÚSICA
@app.route('/adicionar', methods=['POST'])
def adicionar():
    global proximo_id
    if not session.get('logado'):
        return redirect(url_for('login'))
        
    musicas[proximo_id] = {
        'titulo': request.form.get('titulo'),
        'artista': request.form.get('artista'),
        'tom': request.form.get('tom'),
        'letra': request.form.get('letra')
    }
    proximo_id += 1
    flash('Música adicionada com sucesso!', 'success')
    return redirect(url_for('index'))

# ROTA PARA EXIBIR TELA DE EDIÇÃO
@app.route('/editar/<int:id_musica>', methods=['GET', 'POST'])
def editar(id_musica):
    if not session.get('logado'):
        return redirect(url_for('login'))
        
    musica = musicas.get(id_musica)
    if not musica:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        musica['titulo'] = request.form.get('titulo')
        musica['artista'] = request.form.get('artista')
        musica['tom'] = request.form.get('tom')
        musica['letra'] = request.form.get('letra')
        flash('Música atualizada com sucesso!', 'success')
        return redirect(url_for('index'))
        
    return render_template('editar.html', musica=musica, id_musica=id_musica)

# ROTA PARA EXCLUIR MÚSICA
@app.route('/deletar/<int:id_musica>')
def deletar(id_musica):
    if not session.get('logado'):
        return redirect(url_for('login'))
        
    if id_musica in musicas:
        del musicas[id_musica]
        flash('Música excluída com sucesso!', 'warning')
        
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)