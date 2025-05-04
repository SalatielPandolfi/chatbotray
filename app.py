from flask import Flask, render_template, request, jsonify
import openai
import time

app = Flask(__name__)

# 🔐 Configure sua chave e o ID do assistente aqui

openai.api_key = os.environ.get("OPENAI_API_KEY")
ASSISTANT_ID = os.environ.get("ASSISTANT_ID")


# Armazenar uma thread por sessão (aqui usamos apenas uma global para simplificar)
thread_id = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/perguntar', methods=['POST'])
def perguntar():
    global thread_id
    data = request.json
    user_message = data.get('mensagem')

    try:
        # Criar thread se ainda não existir
        if not thread_id:
            thread = openai.beta.threads.create()
            thread_id = thread.id

        # Enviar mensagem do usuário
        openai.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=user_message
        )

        # Executar o assistente
        run = openai.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=ASSISTANT_ID
        )

        # Esperar a conclusão do processamento
        while True:
            run_status = openai.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
            if run_status.status == 'completed':
                break
            time.sleep(1.5)

        # Buscar a última resposta do assistente
        messages = openai.beta.threads.messages.list(thread_id=thread_id)
        resposta = next((m.content[0].text.value for m in messages.data if m.role == 'assistant'), "Desculpe, houve um erro.")

        return jsonify({"resposta": resposta})

    except Exception as e:
        return jsonify({"resposta": f"Erro: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True)
