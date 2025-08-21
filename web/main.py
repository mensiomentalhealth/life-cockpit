#!/usr/bin/env python3
"""
Web Dashboard Server
Main entry point for the web dashboard
"""

import uvicorn
from message_dashboard import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
