import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    # Use the PORT environment variable provided by Render, with a fallback to 5000
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)