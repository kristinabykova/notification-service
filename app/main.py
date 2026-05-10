from flask import Flask
from api.v1.notifications import router

app = Flask(__name__)

app.register_blueprint(router, url_prefix="/api/v1")


@app.route("/", methods=["GET"])
def root():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
