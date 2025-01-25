from app import create_app

app = create_app()

if __name__ == '__main__':
    # Use a different port than the backend
    app.run()
