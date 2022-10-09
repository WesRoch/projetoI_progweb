from app import app
import os
from waitress import serve

port = int(os.environ.get("PORT", 5000))
app.run(debug=True, host='0.0.0.0', port=port)
# server(app, host='0.0.0.0', port=port)
