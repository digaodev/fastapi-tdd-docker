from fastapi import Depends, FastAPI

from fastapi_tdd_docker.config import Settings, get_settings

app = FastAPI()


@app.get('/ping')
def pong(settings: Settings = Depends(get_settings)):
    print(settings)
    return {'ping': 'pong!', 'env': settings.environment, 'test': settings.testing}
