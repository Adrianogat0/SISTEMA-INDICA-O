import sqlite3

def criar_banco():
    conexao = sqlite3.connect('banco.db')
    cursor = conexao.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            telefone TEXT,
            senha TEXT NOT NULL,
            indicacoes INTEGER DEFAULT 0,
            meses_bonus INTEGER DEFAULT 0,
            link_indicacao TEXT
        )
    ''')

    conexao.commit()
    conexao.close()

if __name__ == '__main__':
    criar_banco()
