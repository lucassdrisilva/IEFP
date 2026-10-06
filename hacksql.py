#começar a configutar os tokens para o postman


from flask import Flask, request, jsonify
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity
) 


import mysql.connector

app = Flask(__name__)
#funçao para conectar ao mysql do xampp
app.config["JWT_SECRET_KEY"] = "senha_super_secreta_123"

jwt = JWTManager(app)

def get_db_connection(database):
    return mysql.connector.connect(
        host = "localhost",
        user = "root", #usuario padrao do xammp
        password = "",  #senha padrao do xampp 
        database = database
            )
@app.route("/")
def home():
    return "Api do Servidor ativa e rodando!"







#Rota de login usando parametização segura




@app.route("/login", methods=["POST"])
def login():

    print("--json recebido:",request.get_json(silent=True))
    print("--Formr recebido;,",request.form)

    data = request.get_json()

    base = data["database"]

    conn = get_db_connection(base)
    #data = request.get_json(silent=True)

    if not data:
    # Recebe os dados enviadops via formulario json
        data = request.form
    username = data.get("username")
    password = data.get("password")


    if not username or not password:
        return jsonify({"status;":"erro","mensagem":"Preencha usuário e senha"}), 400
        

 
    try:
        conn = get_db_connection(base)
        cursor = conn.cursor(dictionary=True)


        #Consulta segura placehoders
        query = "SELECT id, username FROM usuarios WHERE username = %s AND password = %s"
        cursor.execute(query,(username, password))

        usuario_encontrado = cursor.fetchone()



        if usuario_encontrado:
            token = create_access_token(
                identity=usuario_encontrado["username"]
            )
            return jsonify({
                "status":"sucesso",
                "token":token
                
            })
        else:
            return jsonify({
                "status":"erro",
                "mensagem": "Credenciais invalidas."
                
            }),401
    except Exception as err:
        return jsonify({"status":"erro","mensagem": f"Erro no banco de dados:{err}"}),500

    finally:
        
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()
@app.route("/usuarios", methods=["GET"])
@jwt_required()
def listar_usuarios():

    conn = get_db_connection("sistema_teste")
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT id, username FROM usuarios"
    )
    usuarios = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(usuarios)




@app.route("/bases", methods=["GET"])
@jwt_required()
def listar_bases():

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password=""
    )
    cursor = conn.cursor()

    cursor.execute("SHOW DATABASES")

    bases = cursor.fetchall()

    resultado = []

    for base in bases:
        resultado.append(base[0])

    cursor.close()
    conn.close()

    return jsonify(resultado)

@app.route("/usuarios", methods=["POST"])
@jwt_required()
def criar_usuarios():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    conn = get_db_connection("sistema_teste")
    cursor = conn.cursor()

    query = """
    INSERT INTO usuarios
    (username, password)
    VALUES (%s, %s)
    """
    cursor.execute(
        query,
        (username, password)
    )
    conn.commit()
    
    cursor.close()
    conn.close()

    
    return jsonify({
        "status": "sucesso",
        "mensagem": "Utilizador criado!"
        })
   # }
if __name__ == "__main__":

    # host= 0.0.0.0' permite que outros computadores de rede acessem na porta 5000
    app.run(host="0.0.0.0", port=5000, debug=True)
