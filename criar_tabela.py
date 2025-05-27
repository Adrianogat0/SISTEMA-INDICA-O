import sqlite3

def criar_tabelas():
    conexao = sqlite3.connect('banco.db')
    cursor = conexao.cursor()

    # Tabela de clientes
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

    # Tabela de indicações
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

    conexao.commit()
    conexao.close()
    print("Tabelas criadas ou atualizadas com sucesso.")

if __name__ == "__main__":
    criar_tabelas()

