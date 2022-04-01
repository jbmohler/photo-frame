from sanic import Sanic
from sanic import response

app = Sanic(__name__)

ROOT = """
<html>
<body>
<image src="/current.jpg" width="100%" height="100%" />
</body>
</html>
"""


@app.route("/")
async def root(req):
    return response.html(ROOT, status=200)


@app.route("/current.jpg")
async def root(req):
    import core
    import random

    filename = random.choice(core.photos)

    core.image(filename)

    return await response.file_stream("output.jpg")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
