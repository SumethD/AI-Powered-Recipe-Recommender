# AI-Powered Recipe Recommender Frontend

This is the frontend for the AI-Powered Recipe Recommender application. It's built with React, TypeScript, and Material-UI.

## Getting Started

### Prerequisites

- Node.js (v14 or higher)
- npm or yarn

### Installation

1. Install dependencies:
   ```
   npm install
   ```
   or
   ```
   yarn install
   ```

2. Start the development server:
   ```
   npm start
   ```
   or
   ```
   yarn start
   ```

3. Open your browser and navigate to `http://localhost:3000`

## Project Structure

- `src/`: Source code
  - `components/`: Reusable UI components
  - `context/`: React context providers
  - `pages/`: Page components
  - `services/`: API service functions
  - `App.tsx`: Main application component
  - `index.tsx`: Entry point

## Features

- Search for recipes based on available ingredients
- Filter recipes by dietary restrictions, cuisine, and more
- Get AI-powered recipe modifications
- Save favorite recipes
- Chat with AI for cooking advice

## Available Scripts

- `npm start`: Runs the app in development mode
- `npm build`: Builds the app for production
- `npm test`: Runs tests
- `npm eject`: Ejects from Create React App

## Backend Integration

The frontend communicates with the backend API running on `http://localhost:5000`. Make sure the backend server is running before using the frontend.

## Technologies Used

- React
- TypeScript
- Material-UI
- React Router
- Axios
- Context API for state management
