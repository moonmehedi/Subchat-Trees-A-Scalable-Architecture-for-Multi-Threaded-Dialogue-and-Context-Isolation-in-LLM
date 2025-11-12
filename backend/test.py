from src.cores.config import settings

def test_settings():
    print("Testing configuration settings...")
    print(settings.app_name)
    print(settings.version)
    print(settings.debug)
    print(settings.host)
    print(settings.port)
    print(settings.openai_api_key)
    print(settings.groq_api_key)
    print(settings.default_model_name)

if __name__ == "__main__":
    test_settings()