from app import app
app = app # Explicit exposure for Vercel

if __name__ == "__main__":
    app.run()
