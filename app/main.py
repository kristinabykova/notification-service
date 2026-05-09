from flask import Flask
import uvicorn

app = Flask(__name__)


@app.route("/")
def root():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
