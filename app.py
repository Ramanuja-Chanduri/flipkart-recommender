from flask import render_template, Flask, request, Response

from flipkart.data_ingestion import DataIngestor
from flipkart.rag_chain import RAGChainBuilder
from flipkart.config import config


def create_app():
    app = Flask(__name__)

    vector_store = DataIngestor().ingest(load_existing=True)
    rag_chain = RAGChainBuilder(vector_store=vector_store).build_chain()

    @app.route("/")
    def index():
        return render_template("index.html")
    
    @app.route("/get", methods=["POST"])
    def get_response():
        user_input = request.form.get("msg")
        response = rag_chain.invoke(
            {"input" : user_input},
            config= {"configurable": {"session_id": "use-session"}}
        )["answer"]

        return response
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)