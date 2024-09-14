from conf.config import settings
from plant_srv import create_app

app = create_app()
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=settings.port)
