from flask import Flask
import uvicorn

app = Flask(__name__)


@app.route("/", methods=["GET"])
def root():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
