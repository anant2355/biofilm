from app.api.service import app
import os

if __name__ == "__main__":
    app.run(port=int(os.environ['API_PORT']),debug=True, host='0.0.0.0')
