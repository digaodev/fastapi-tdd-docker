from typing import Annotated

from fastapi import Depends, FastAPI

from fastapi_tdd_docker.config import Settings, get_settings

app = FastAPI()

SettingsDep = Annotated[Settings, Depends(get_settings)]


@app.get('/ping')
def ping(settings: Settings = SettingsDep):
    print(settings)
    return {'ping': 'pong!', 'env': settings.environment, 'test': settings.testing}
