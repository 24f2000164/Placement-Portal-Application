from app import create_app
import os
from dotenv import load_dotenv
load_dotenv()

from app import create_app


app = create_app('production' if os.environ.get('FLASK_ENV') == 'production' else 'development')

if __name__ == '__main__':
    app.run(debug=True, port=5000)

