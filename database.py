import sqlite3
import logging

def criar_banco():
    """Create database and tables if they don't exist"""
    try:
        conexao = sqlite3.connect('banco.db')
        cursor = conexao.cursor()

        # Create clientes table
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

        conexao.commit()
        conexao.close()
        logging.info("Database created successfully")
        
    except Exception as e:
        logging.error(f"Error creating database: {str(e)}")

if __name__ == '__main__':
    criar_banco()
