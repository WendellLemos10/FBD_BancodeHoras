import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import psycopg2

# Função para se conectar ao banco de dados PostgreSQL
def conectar_banco():
    try:
        con = psycopg2.connect(
            host="localhost",
            database="BancoDeHoras",
            user="postgres",
            password="postgres"
        )
        return con
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao conectar ao banco de dados: {e}")
        return None

# Função para consultar todos os usuários
def consultar_usuarios():
    con = conectar_banco()
    if con:
        try:
            cursor = con.cursor()
            cursor.execute("SELECT * FROM usuarioComum ORDER BY id")  # Ordenar por ID
            usuarios = cursor.fetchall()

            # Limpa a árvore antes de adicionar novos usuários
            for item in tree.get_children():
                tree.delete(item)

            # Exibe os usuários na árvore
            for usuario in usuarios:
                # Adiciona um botão "X" para deletar
                tree.insert("", tk.END, values=usuario + ("X",))

            cursor.close()
            con.close()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao consultar usuários: {e}")

def atualizar_usuario(usuario_id, campo, novo_valor):
    con = conectar_banco()
    if con:
        try:
            cursor = con.cursor()
            cursor.execute(f"UPDATE usuarioComum SET {campo} = %s WHERE id = %s", (novo_valor, usuario_id))
            con.commit()
            messagebox.showinfo("Sucesso!", f"{campo} atualizado com sucesso!")
            consultar_usuarios()  # Reordenar e atualizar a exibição
            cursor.close()
            con.close()
        except Exception as e:
            messagebox.showerror("Erro!", f"Erro ao atualizar {campo}: {e}")

def abrir_popup_edicao(usuario_id, campo, valor_atual):
    popup = tk.Toplevel(root)
    popup.title(f"Editar {campo}")

    # Configura o tamanho da pop-up (opcional)
    popup.geometry("300x150")

    # Centraliza a pop-up na tela
    largura_popup = popup.winfo_width()
    altura_popup = popup.winfo_height()
    largura_tela = root.winfo_screenwidth()
    altura_tela = root.winfo_screenheight()

    pos_x = (largura_tela // 2) - (largura_popup // 2)
    pos_y = (altura_tela // 2) - (altura_popup // 2)

    popup.geometry(f"+{pos_x}+{pos_y}")

    tk.Label(popup, text=f"Novo {campo}:").pack(pady=5)
    entry_novo_valor = tk.Entry(popup, width=30)
    entry_novo_valor.pack(pady=5)
    entry_novo_valor.insert(0, valor_atual)

    def salvar_edicao():
        novo_valor = entry_novo_valor.get().strip()
        if not novo_valor:
            messagebox.showwarning("Aviso!", f"{campo} nao pode ser vazio!")
            return

        if campo == "saldo_horas":
            try:
                novo_valor = int(novo_valor)
            except ValueError:
                messagebox.showwarning("Aviso!", "Saldo de horas deve ser um numero inteiro!")
                return

        atualizar_usuario(usuario_id, campo, novo_valor)
        popup.destroy()

    tk.Button(popup, text="Salvar", command=salvar_edicao).pack(pady=5)
    popup.transient(root)
    popup.grab_set()
    root.wait_window(popup)

def on_tree_click(event):
    item = tree.identify('item', event.x, event.y)
    if not item:
        return

    valores = tree.item(item, 'values')
    usuario_id = valores[0]

    # Identificar a coluna clicada
    col = tree.identify_column(event.x)

    if col == "#3":  # Coluna de email (coluna 3)
        abrir_popup_edicao(usuario_id, "email", valores[2])
    elif col == "#5":  # Coluna de saldo de horas (coluna 5)
        abrir_popup_edicao(usuario_id, "saldo_horas", valores[4])

# Função para buscar usuários pelo nome
def buscar_usuario():
    filtro = entry_filtro_var.get().strip() + '%'

    con = conectar_banco()
    if con:
        try:
            cursor = con.cursor()
            cursor.execute("SELECT * FROM usuarioComum WHERE nome ILIKE %s or cpf ILIKE %s or email ILIKE %s ORDER BY id", (filtro, filtro, filtro))
            usuarios = cursor.fetchall()

            # Limpa a árvore antes de adicionar os novos resultados
            for item in tree.get_children():
                tree.delete(item)

            # Exibe os usuários encontrados
            if usuarios:
                for usuario in usuarios:
                    tree.insert("", tk.END, values=usuario + ("X",))

            cursor.close()
            con.close()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao buscar usuários: {e}")

# Função para excluir usuário
def excluir_usuario(usuario_id):
    con = conectar_banco()
    if con:
        try:
            cursor = con.cursor()
            cursor.execute("DELETE FROM usuarioComum WHERE id = %s", (usuario_id,))
            con.commit()
            messagebox.showinfo("Sucesso!", "Usuario deletado com sucesso!")
            consultar_usuarios()  # Reordenar e atualizar a exibição
            cursor.close()
            con.close()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao excluir usuario: {e}")

# Função para tratar o clique no botão "X" para deletar
def on_delete_click(event):
    item = tree.identify('item', event.x, event.y)
    if item:
        col = tree.identify_column(event.x)
        if col == "#6":  # Coluna "Deletar" que é a coluna 6
            usuario_id = tree.item(item, 'values')[0]  # ID do usuário
            if messagebox.askyesno("Confirmacao", f"Você tem certeza que deseja excluir o usuário com ID {usuario_id}?"):
                excluir_usuario(usuario_id)

# Função para inserir o usuário
def inserir_usuario():
    id_usuario = entry_id.get().strip()
    nome = entry_nome_insert.get().strip()
    email = entry_email.get().strip()
    cpf = entry_cpf.get().strip()
    saldo_horas = entry_saldo_horas.get().strip()

    if not id_usuario or not nome or not email or not cpf or not saldo_horas:
        messagebox.showwarning("Aviso!", "Todos os campos são obrigatórios")
        return

    try:
        id_usuario = int(id_usuario)
        saldo_horas = int(saldo_horas)
    except:
        messagebox.showwarning("Aviso!", "ID e Saldo de Horas devem ser números inteiros!")
        return

    con = conectar_banco()
    if con:
        try:
            cursor = con.cursor()
            cursor.execute(
                "INSERT INTO usuarioComum (id, nome, email, cpf, saldo_horas) VALUES (%s, %s, %s, %s, %s)",
                (id_usuario, nome, email, cpf, saldo_horas)
            )
            con.commit()
            messagebox.showinfo("Sucesso!", "Usuário adicionado com sucesso!")

            entry_id.delete(0, tk.END)
            entry_nome_insert.delete(0, tk.END)
            entry_email.delete(0, tk.END)
            entry_cpf.delete(0, tk.END)
            entry_saldo_horas.delete(0, tk.END)

            consultar_usuarios()  # Reordenar e atualizar a exibição

            cursor.close()
            con.close()
        except Exception as e:
            messagebox.showerror("Erro!", f"Erro ao inserir usuário: {e}")

# Configuração da interface gráfica com Tkinter
root = tk.Tk()
root.title("Banco De Horas")

# Frame principal
frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

# Campo de entrada para o nome do usuário
entry_filtro_var = tk.StringVar()
entry_filtro_var.trace_add("write", lambda *args: buscar_usuario())

tk.Label(frame, text="Buscar usuario:").pack()
entry_filtro = tk.Entry(frame, textvariable=entry_filtro_var, width=30)
entry_filtro.pack(pady=5)

# Árvore (Treeview) para exibir os dados dos usuários
columns = ("ID", "Nome", "Email", "CPF", "Saldo de Horas", "Deletar")
tree = ttk.Treeview(frame, columns=columns, show="headings", height=10)

# Definindo os cabeçalhos das colunas
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, anchor="center", width=150)

tree.pack(padx=10, pady=10)

tree.bind("<ButtonRelease-1>", on_tree_click)

# Tratamento do clique para deletar
tree.bind("<Button-1>", on_delete_click)

tk.Label(frame, text="ID:").pack()
entry_id = tk.Entry(frame, width=30)
entry_id.pack(pady=2)

tk.Label(frame, text="Nome:").pack()
entry_nome_insert = tk.Entry(frame, width=30)
entry_nome_insert.pack(pady=2)

tk.Label(frame, text="Email:").pack()
entry_email = tk.Entry(frame, width=30)
entry_email.pack(pady=2)

tk.Label(frame, text="CPF:").pack()
entry_cpf = tk.Entry(frame, width=30)
entry_cpf.pack(pady=2)

tk.Label(frame, text="Saldo de Horas:").pack()
entry_saldo_horas = tk.Entry(frame, width=30)
entry_saldo_horas.pack(pady=2)

btn_inserir = tk.Button(frame, text="Inserir Usuario", command=inserir_usuario)
btn_inserir.pack(pady=5)

# Consultar os usuários e preencher a árvore
consultar_usuarios()

# Inicia a interface gráfica
root.mainloop()