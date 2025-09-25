# AviFlux

AviFlux is a full-stack web application built with a modern tech stack featuring a FastAPI backend and React frontend.

## Project Structure

```
AviFlux/
├── backend/                 # FastAPI backend application
│   ├── app.py              # Main FastAPI application
│   └── requirements.txt    # Python dependencies
├── frontend/               # React frontend application
│   ├── src/               # React source code
│   ├── public/            # Static assets
│   ├── package.json       # Node.js dependencies
│   └── vite.config.ts     # Vite configuration
└── ai/                    # AI-related modules (future implementation)
```

## Tech Stack

### Backend
- **FastAPI** - Modern, fast web framework for building APIs
- **Uvicorn** - ASGI server implementation
- **Pydantic** - Data validation using Python type annotations

### Frontend
- **React 19** - User interface library
- **TypeScript** - Type-safe JavaScript
- **Vite** - Fast build tool and dev server
- **ESLint** - Code linting and quality

## Getting Started

### Prerequisites
- Python 3.8+ 
- Node.js 16+
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the development server:
   ```bash
   python app.py
   ```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install Node.js dependencies:
   ```bash
   npm install
   ```

3. Run the development server:
   ```bash
   npm run dev
   ```

The React app will be available at `http://localhost:5173`

## API Endpoints

The backend provides the following endpoints:

- `GET /` - Root endpoint with welcome message
- `GET /api/health` - Health check endpoint
- `GET /api/greet?name={name}` - Greeting endpoint with optional name parameter
- `POST /api/echo` - Echo endpoint that returns the sent message

## Development

### Backend Development
- The FastAPI server runs with hot reload enabled
- API documentation is automatically generated and available at `http://localhost:8000/docs`

### Frontend Development  
- The Vite dev server provides hot module replacement
- TypeScript compilation and linting are configured

## CORS Configuration

The backend is configured to accept requests from common development servers:
- `http://localhost:3000` (Create React App default)
- `http://localhost:5173` (Vite default)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test your changes
5. Submit a pull request

## License

This project is open source and available under the [MIT License](LICENSE).

## Future Plans

The `ai/` directory is prepared for future AI-related features and integrations.