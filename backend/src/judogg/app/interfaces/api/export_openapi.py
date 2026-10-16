import json

from judogg.app.interfaces.api.main import create_app

if __name__ == "__main__":
    print(json.dumps(create_app().openapi(), indent=2, ensure_ascii=False))
