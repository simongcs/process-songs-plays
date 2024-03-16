from src.api.api import app
# from src.api.app import create_app


def main():
    # app = create_app()
    app.run(host="0.0.0.0", debug=True, port=8080)


if __name__ == "__main__":
    main()
