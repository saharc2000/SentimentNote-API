# Notes API with Sentiment Analysis

This is a Flask-based RESTful API for managing notes with integrated sentiment analysis using MeaningCloud.
The API includes user registration, login, note creation, and sentiment analysis. 
JWT tokens are used for authentication.

## Features

- User registration and authentication using JWT.
- Create, retrieve, and manage notes.
- Automatic sentiment analysis of notes using the MeaningCloud API.
- Secure API endpoints with token-based authentication.
- Swagger API documentation.

## Prerequisites

- Python 3.7+
- pip (Python package installer)
- SQLite (for database)

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/BigVU_Task.git
   cd BigVU_Task

2. **Running the Application:**
   python -m app.app

3. **API Documentation**
The API uses Swagger for documentation.
Access the Swagger documentation: Visit http://127.0.0.1:3500/apidocs/ in your browser to see the interactive API documentation.

4. **Run Unit Tests:**:
   python -m unittest discover

Make sure to replace the placeholder section `yourusername` in the repository URL with the appropriate value.

