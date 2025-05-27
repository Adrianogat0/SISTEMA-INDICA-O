from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import urllib.parse

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'

def get_db_connection():
    conn = sqlite3.connect('banco.db')
    conn.row_factory = sqlite3.Row
    return conn

# Página inicial
@app.route('/')
def home():
    return render_template('index.html')

# Página de cadastro
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        telefone = request.form['telefone']
        senha = request.form['senha']

        mensagem = f"Olá Adriano! o meu amigo {nome} me indicou que você trabalha com Canais IPTV, gostaria de estar fazendo um teste contigo !!!"
        mensagem_codificada = urllib.parse.quote(mensagem)
        link = f"https://wa.me/5594984252041?text={mensagem_codificada}"

        try:
            conexao = get_db_connection()
            conexao.execute('''
                INSERT INTO clientes (nome, email, telefone, senha, link_indicacao)
                VALUES (?, ?, ?, ?, ?)
            ''', (nome, email, telefone, senha, link))
            conexao.commit()
            conexao.close()
            return redirect('/')
        except Exception as e:
            return f"Erro ao cadastrar: {str(e)}"

    return render_template('cadastro.html')

# Login do cliente
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        conn = get_db_connection()
        cliente = conn.execute("SELECT * FROM clientes WHERE email = ? AND senha = ?", (email, senha)).fetchone()
        conn.close()

        if cliente:
            session['cliente_id'] = cliente['id']
            session['cliente_nome'] = cliente['nome']
            return redirect('/painel')
        else:
            return "Email ou senha incorretos."

    return render_template('login.html')

# Painel do cliente
@app.route('/painel')
def painel():
    if 'cliente_id' not in session:
        return redirect('/login')

    cliente_id = session['cliente_id']
    conn = get_db_connection()

    cliente = conn.execute("SELECT nome, email, indicacoes, meses_bonus, link_indicacao FROM clientes WHERE id = ?", (cliente_id,)).fetchone()
    indicacoes = conn.execute("SELECT nome, email, assinou FROM indicacoes WHERE cliente_id = ?", (cliente_id,)).fetchall()
    conn.close()

    indicados = [{'nome': i['nome'], 'email': i['email'], 'assinou': bool(i['assinou'])} for i in indicacoes]

    total_indicados = len(indicados)
    total_assinantes = sum(1 for i in indicados if i['assinou'])
    progresso_percent = int((total_assinantes / total_indicados) * 100) if total_indicados > 0 else 0

    return render_template('painel.html',
                           cliente=cliente,
                           indicados=indicados,
                           total_indicados=total_indicados,
                           total_assinantes=total_assinantes,
                           progresso_percent=progresso_percent)

# Rota para indicar amigo
@app.route('/indicar_amigo', methods=['POST'])
def indicar_amigo():
    if 'cliente_id' not in session:
        return redirect('/login')

    cliente_id = session['cliente_id']
    nome_amigo = request.form['nome_amigo']

    try:
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO indicacoes (cliente_id, nome, email, assinou)
            VALUES (?, ?, ?, ?)
        ''', (cliente_id, nome_amigo, '', 0))
        conn.commit()
        conn.close()

        nome_cliente = session.get('cliente_nome')
        mensagem = f"""👤 Indicado: *{nome_amigo}*

🔰Plano mensal = R$ 30,00
🔏Ativação da Licença Anual GRÁTIS
⏳Teste GRÁTIS de 3 horas

📺TV Ao Vivo  ⚽Futebol  🎬Filmes  🎞Séries
🌐Notícias 🥅Sportv 🥊UFC 📽Novelas
👧🏼Infantil 🔞Adulto 🍿Telecine 🏰Disney

🪀 Clique para falar com Adriano:
https://wa.me/5594984252041?text={urllib.parse.quote(f'Olá Adriano! Fui indicado por: *{nome_cliente}* e quero um TESTE!')}"""

        return redirect(f'https://wa.me/?text={urllib.parse.quote(mensagem)}')

    except Exception as e:
        return f"Erro ao salvar indicação: {str(e)}"

# Decorador para proteger rotas do admin
def admin_login_required(func):
    from functools import wraps
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get('admin_logado'):
            return redirect(url_for('home'))
        return func(*args, **kwargs)
    return wrapper

# Login do admin
@app.route('/login_admin', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        senha = request.form.get('senha')

        if usuario == 'Admin' and senha == '03122023':
            session['admin_logado'] = True
            return redirect('/admin')
        else:
            return render_template('login_admin.html', erro='Usuário ou senha incorretos.')

    return render_template('login_admin.html')

# Painel do admin - lista de clientes
@app.route('/admin')
@admin_login_required
def admin():
    conn = get_db_connection()
    clientes = conn.execute('SELECT id, nome, email, indicacoes, meses_bonus FROM clientes').fetchall()
    conn.close()
    return render_template('admin.html', clientes=clientes)

# Editar indicações do cliente
@app.route('/admin/cliente/<int:cliente_id>', methods=['GET', 'POST'])
@admin_login_required
def admin_cliente(cliente_id):
    conn = get_db_connection()
    cliente = conn.execute('SELECT id, nome, email, indicacoes, meses_bonus FROM clientes WHERE id = ?', (cliente_id,)).fetchone()
    if not cliente:
        conn.close()
        return "Cliente não encontrado", 404

    if request.method == 'POST':
        assinou_ids = request.form.getlist('assinou')
        indicacoes = conn.execute('SELECT id FROM indicacoes WHERE cliente_id = ?', (cliente_id,)).fetchall()
        for ind in indicacoes:
            status = 1 if str(ind['id']) in assinou_ids else 0
            conn.execute('UPDATE indicacoes SET assinou = ? WHERE id = ?', (status, ind['id']))
        conn.commit()

        aprovadas = conn.execute('SELECT COUNT(*) as total FROM indicacoes WHERE cliente_id = ? AND assinou = 1', (cliente_id,)).fetchone()['total']
        meses_bonus = (aprovadas // 6) * 12
        conn.execute('UPDATE clientes SET indicacoes = ?, meses_bonus = ? WHERE id = ?', (aprovadas, meses_bonus, cliente_id))
        conn.commit()
        conn.close()
        return redirect(url_for('admin_cliente', cliente_id=cliente_id))

    indicacoes = conn.execute('SELECT id, nome, email, assinou FROM indicacoes WHERE cliente_id = ?', (cliente_id,)).fetchall()
    conn.close()
    return render_template('admin_cliente.html', cliente=cliente, indicacoes=indicacoes)

# Logout do admin
@app.route('/logout_admin')
@admin_login_required
def logout_admin():
    session.pop('admin_logado', None)
    return redirect('/')

# Logout do cliente
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


