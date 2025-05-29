import os
import sqlite3
import urllib.parse
import logging
from flask import Flask, render_template, request, redirect, session, url_for
from functools import wraps

# Configure logging for better debugging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "fallback_secret_key_for_development")

def get_db_connection():
    """Get database connection with proper row factory"""
    conn = sqlite3.connect('banco.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialize database tables if they don't exist"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create clientes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                telefone TEXT,
                senha TEXT NOT NULL,
                link_indicacao TEXT,
                indicacoes INTEGER DEFAULT 0,
                meses_bonus INTEGER DEFAULT 0
            )
        ''')
        
        # Create indicacoes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS indicacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id INTEGER NOT NULL,
                nome TEXT NOT NULL,
                email TEXT NOT NULL,
                assinou INTEGER DEFAULT 0,
                FOREIGN KEY (cliente_id) REFERENCES clientes(id)
            )
        ''')
        
        conn.commit()
        conn.close()
        logging.info("Database tables created successfully")
    except Exception as e:
        logging.error(f"Error initializing database: {str(e)}")

# Initialize database on startup
init_database()

# Admin login decorator
def admin_login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get('admin_logado'):
            return redirect(url_for('home'))
        return func(*args, **kwargs)
    return wrapper

# Routes
@app.route('/')
def home():
    """Home page with welcome message and navigation"""
    return render_template('index.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    """User registration page"""
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        telefone = request.form['telefone']
        senha = request.form['senha']

        # Create WhatsApp referral message
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
            logging.info(f"New user registered: {email}")
            return redirect('/')
        except sqlite3.IntegrityError:
            return render_template('cadastro.html', erro="Email já cadastrado!")
        except Exception as e:
            logging.error(f"Registration error: {str(e)}")
            return render_template('cadastro.html', erro="Erro ao cadastrar. Tente novamente.")

    return render_template('cadastro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        conn = get_db_connection()
        cliente = conn.execute("SELECT * FROM clientes WHERE email = ? AND senha = ?", (email, senha)).fetchone()
        conn.close()

        if cliente:
            session['cliente_id'] = cliente['id']
            session['cliente_nome'] = cliente['nome']
            logging.info(f"User logged in: {email}")
            return redirect('/painel')
        else:
            return render_template('login.html', erro="Email ou senha incorretos.")

    return render_template('login.html')

@app.route('/painel')
def painel():
    """User dashboard showing referrals and progress"""
    if 'cliente_id' not in session:
        return redirect('/login')

    cliente_id = session['cliente_id']
    conn = get_db_connection()

    # Get client data
    cliente = conn.execute("SELECT nome, email, indicacoes, meses_bonus, link_indicacao FROM clientes WHERE id = ?", (cliente_id,)).fetchone()
    indicacoes = conn.execute("SELECT nome, email, assinou FROM indicacoes WHERE cliente_id = ?", (cliente_id,)).fetchall()
    conn.close()

    # Process referral data
    indicados = [{'nome': i['nome'], 'email': i['email'], 'assinou': bool(i['assinou'])} for i in indicacoes]
    total_indicados = len(indicados)
    total_assinantes = sum(1 for i in indicados if i['assinou'])
    progresso_percent = int((total_assinantes / total_indicados) * 100) if total_indicados > 0 else 0
    show_parabens = total_assinantes >= 6

    return render_template('painel.html',
                           cliente=cliente,
                           indicados=indicados,
                           total_indicados=total_indicados,
                           total_assinantes=total_assinantes,
                           progresso_percent=progresso_percent,
                           show_parabens=show_parabens)

@app.route('/indicar_amigo', methods=['POST'])
def indicar_amigo():
    """Add new referral and redirect to WhatsApp"""
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
    
*✅(1 Ano GRÁTIS) indicando amigos*
*🔰Grupo VIP Promoção do dia*
*🔏Ativação da Licença Anual GRÁTIS*
*⏳Teste GRÁTIS de 3 horas*

*🔴Contém...*
 📺TV Ao Vivo     ⚽Futebol  
 🎬Filmes            🎞️Séries  
 🌐 Notícias        🥅Sportv 
 🥊UFC                📽️Novelas       
 👧🏼 Infantil          🔞Adulto 
 🍿Telecine         🏰Disney

_*CLIQUE NO LINK E PEÇA UM TESTE GRÁTIS😉*_

🪀https://wa.me/5594984252041?text={urllib.parse.quote(f'Olá Adriano! Fui indicado por: *{nome_cliente}* e quero um TESTE!')}"""

        return redirect(f'https://wa.me/?text={urllib.parse.quote(mensagem)}')

    except Exception as e:
        logging.error(f"Error adding referral: {str(e)}")
        return f"Erro ao salvar indicação: {str(e)}"

@app.route('/login_admin', methods=['GET', 'POST'])
def login_admin():
    """Admin login page"""
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        senha = request.form.get('senha')

        # Get admin credentials from environment variables with fallback
        admin_user = os.environ.get('ADMIN_USER', 'Admin')
        admin_pass = os.environ.get('ADMIN_PASS', '03122023')

        if usuario == admin_user and senha == admin_pass:
            session['admin_logado'] = True
            logging.info("Admin logged in")
            return redirect('/admin')
        else:
            return render_template('login_admin.html', erro='Usuário ou senha incorretos.')

    return render_template('login_admin.html')

@app.route('/admin')
@admin_login_required
def admin():
    """Admin dashboard showing all clients"""
    conn = get_db_connection()
    clientes = conn.execute('SELECT id, nome, email, indicacoes, meses_bonus FROM clientes').fetchall()
    conn.close()
    return render_template('admin.html', clientes=clientes)

@app.route('/admin/cliente/<int:cliente_id>', methods=['GET', 'POST'])
@admin_login_required
def admin_cliente(cliente_id):
    """Admin page to manage client referrals"""
    conn = get_db_connection()
    cliente = conn.execute('SELECT * FROM clientes WHERE id = ?', (cliente_id,)).fetchone()

    if not cliente:
        conn.close()
        return "Cliente não encontrado", 404

    if request.method == 'POST':
        assinou_ids = request.form.getlist('assinou')
        excluir_ids = request.form.getlist('excluir')

        # Delete selected referrals
        for excluido_id in excluir_ids:
            conn.execute('DELETE FROM indicacoes WHERE id = ?', (excluido_id,))

        # Update remaining referrals
        indicacoes = conn.execute('SELECT id FROM indicacoes WHERE cliente_id = ?', (cliente_id,)).fetchall()
        for ind in indicacoes:
            status = 1 if str(ind['id']) in assinou_ids else 0
            conn.execute('UPDATE indicacoes SET assinou = ? WHERE id = ?', (status, ind['id']))
        conn.commit()

        # Update client progress
        aprovadas = conn.execute('SELECT COUNT(*) FROM indicacoes WHERE cliente_id = ? AND assinou = 1', (cliente_id,)).fetchone()[0]
        meses_bonus = (aprovadas // 6) * 12
        conn.execute('UPDATE clientes SET indicacoes = ?, meses_bonus = ? WHERE id = ?', (aprovadas, meses_bonus, cliente_id))
        conn.commit()

        conn.close()
        logging.info(f"Admin updated referrals for client {cliente_id}")
        return redirect(url_for('admin_cliente', cliente_id=cliente_id))

    # Get referral data for display
    indicacoes = conn.execute('SELECT id, nome, email, assinou FROM indicacoes WHERE cliente_id = ?', (cliente_id,)).fetchall()
    aprovadas = conn.execute('SELECT COUNT(*) FROM indicacoes WHERE cliente_id = ? AND assinou = 1', (cliente_id,)).fetchone()[0]
    conn.close()

    show_parabens = aprovadas >= 6
    return render_template('admin_cliente.html', cliente=cliente, indicacoes=indicacoes, show_parabens=show_parabens)

@app.route('/logout_admin')
@admin_login_required
def logout_admin():
    """Admin logout"""
    session.pop('admin_logado', None)
    logging.info("Admin logged out")
    return redirect('/')

@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    return redirect('/login')

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(error):
    logging.error(f"Internal error: {str(error)}")
    return "Erro interno do servidor", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)



