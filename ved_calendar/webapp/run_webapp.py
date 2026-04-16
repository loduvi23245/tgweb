import uvicorn
import os

uvicorn.run(
    "webapp.main:app",
    host="0.0.0.0",
    port=int(os.environ.get("PORT", 8000)),
    reload=False
)
