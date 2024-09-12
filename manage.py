from plant_srv import create_app
from conf.config import settings


app = create_app()
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=settings.port)