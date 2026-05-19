from flask import Flask, render_template, request
import re

app = Flask(__name__)

# O TEU BANCO DE DADOS ORIGINAL (Exatamente como no print)
banco_musicas = {
    1: {
        'titulo': 'Caminho no deserto',
        'artista': 'Soraya Moraes',
        'tom': 'G',
        'cifra': 'G        D\nEstás aqui mudando histórias\nEm        C\nTe adorarei, te adorarei'
    }
}

# MATRIZ PARA TRANSPOSIÇÃO DE TOM
NOTAS = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

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

    padrao_acorde = r'\b[A-G](#)?(m|maj|min|7|9|4|sus|aug|dim)?\b'
    return re.sub(padrao_acorde, transpor_acorde, texto)

# A TUA ROTA DA PÁGINA INICIAL ORIGINAL
@app.route('/')
def index():
    return render_template('index.html', musicas=banco_musicas)

# A TUA ROTA DA MÚSICA CORRIGIDA (Mantendo o teu padrão)
@app.route('/musica/<int:id>')
def musica(id):
    semitons = request.args.get('semitons', default=0, type=int)
    musica_selecionada = banco_musicas.get(id)
    
    if not musica_selecionada:
        return "Música não encontrada", 404
        
    # Transpõe o texto que está na tua chave 'cifra'
    letra_filtrada = transpor_letra(musica_selecionada['cifra'], semitons)
    
    return render_template('musica.html', 
                           musica=musica_selecionada, 
                           id=id, 
                           letra_transposta=letra_filtrada, 
                           semitons=semitons)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)