import random
from sanic import Sanic
from sanic import response
import core


app = Sanic(__name__)

ROOT = """
<html>
<head>
 <script src="/scripts/refresh.js"></script>
</head>
<body onload="ready()">
<img id="image" src="/current.jpg" width="100%" height="100%" />
</body>
</html>
"""

SCRIPT = """
function refresh_image() {
    var w = window.innerWidth;
    var h = window.innerHeight;

    var img_url = "/current.jpg?width="+w+"&height="+h+"&random="+new Date().getTime();
    document.getElementById('image').src = img_url;
}

function ready() {
    window.setInterval(refresh_image, 2*1000);
}
"""


@app.route("/")
async def get_root(request):
    return response.html(ROOT, status=200)


@app.route("/scripts/refresh.js")
async def get_refresh_js(request):
    return response.text(SCRIPT, status=200, content_type="text/javascript")


@app.route("/current.jpg")
async def get_current_image(request):
    width = request.args.get("width", 300)
    height = request.args.get("height", 500)

    while True:
        filename = random.choice(core.photos)

        try:
            core.image(filename, width=int(width), height=int(height))
            break
        except core.ImageBuildError as e:
            print(f"Image {filename} failed: {str(e)}")
            continue

    return await response.file_stream("output.jpg")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
