# Smart AI Learning Platform

A comprehensive learning assistant powered by AI to help users learn any subject through personalized educational content.

## Features

- **Subject-based Learning**: Explore various subjects including Technology, Science, Mathematics, Languages, Arts & Literature, History, Business, and Health
- **Multiple Learning Styles**: Choose from different learning formats:
  - Detailed Explanations
  - Study Notes & Summaries
  - Interactive Quizzes
  - Examples & Practice Problems
  - Hands-on Exercises
  - Structured Learning Paths
  - Visual Learning
  - Custom Questions
- **Dark/Light Mode**: Toggle between themes for comfortable viewing experience
- **Responsive Design**: Works on desktop, tablet, and mobile devices

## Tech Stack

### Frontend
- Next.js (React framework)
- TypeScript
- Tailwind CSS for styling
- Framer Motion for animations
- React Markdown for content rendering

### Backend
- FastAPI (Python)
- LangChain for AI chain orchestration
- OpenAI's GPT models

## Getting Started

### Prerequisites
- Node.js (v18+)
- Python (v3.9+)
- OpenAI API key

### Setup Backend

1. Navigate to the backend directory:
```
cd "Smart AI Learning Plateform/backend"
```

2. Create and activate a virtual environment:
```
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```
pip install -r requirements.txt
```

4. Set up environment variables:
   - Create or modify `.env` file with your OpenAI API key
   - Adjust allowed origins if needed

5. Start the backend server:
```
uvicorn main:app --reload
```

### Setup Frontend

1. Navigate to the frontend directory:
```
cd "Smart AI Learning Plateform/frontend"
```

2. Install dependencies:
```
npm install
```

3. Start the development server:
```
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser

## Usage

1. Select a subject category
2. Enter a topic you want to learn about
3. Choose your preferred learning style
4. For custom questions, enter your specific query
5. Click on the "Get [Learning Style]" button
6. View your personalized educational content

## License

MIT

## Acknowledgements

- OpenAI for providing the AI models
- LangChain for the framework to build AI applications
- NextJS team for the React framework