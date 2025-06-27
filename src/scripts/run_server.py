import uvicorn
from buscador.app_new import app

if __name__ == "__main__":
    # Para desenvolvimento local fora do Docker, pode-se usar "127.0.0.1".
    # Para execução dentro do Docker, "0.0.0.0" é necessário
    # para que a porta seja exposta corretamente.
    # O reload=True reinicia o servidor automaticamente quando há alterações no código.
    uvicorn.run("buscador.app_new:app", host="0.0.0.0", port=8000, reload=True)
