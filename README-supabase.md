# Supabase Integration for AI-Powered Recipe Recommender

This project uses Supabase (https://supabase.com) as the database backend to store user data, preferences, and saved recipes.

## Setup Instructions

### 1. Environment Configuration

The application uses the following environment variables for Supabase configuration:

```
REACT_APP_SUPABASE_URL=https://your-project-url.supabase.co
REACT_APP_SUPABASE_ANON_KEY=your-anon-key
```

These are stored in a `.env` file in the `frontend` directory.

### 2. Database Schema

The application uses the following tables in Supabase:

- `profiles` - Stores user profile information
- `saved_recipes` - Stores saved recipes for each user
- `shopping_lists` - Stores user shopping lists

To create these tables, run the SQL script in `supabase_schema.sql` in the Supabase SQL editor.

### 3. Row-Level Security (RLS)

The SQL schema includes Row-Level Security policies that ensure users can only access their own data. The policies are set up to:

- Allow users to view, update, and insert their own profile data
- Allow users to insert, view, and delete their own saved recipes
- Allow users to insert, view, update, and delete their own shopping lists

### 4. Database Triggers

The schema includes a trigger that creates a new profile entry whenever a new user signs up through Supabase Auth.

## API Utilities

The application includes several utility files for interacting with Supabase:

### 1. Authentication (`supabaseClient.js`)

- `signUp(email, password)` - Register a new user
- `signIn(email, password)` - Sign in an existing user
- `signOut()` - Sign out the current user
- `getCurrentUser()` - Get the current authenticated user
- `getSession()` - Get the current session information

### 2. User Profiles (`userProfile.js`)

- `getUserProfile(userId)` - Get a user's profile data
- `createUserProfile(profile)` - Create a new user profile
- `updateUserProfile(userId, updates)` - Update a user's profile
- `getUserPreferences(userId)` - Get a user's preferences
- `updateUserPreferences(userId, preferences)` - Update a user's preferences

## Components

The application includes several components that interact with Supabase:

### 1. Auth Context

The `AuthContext.jsx` provides authentication state across the application. It includes:

- Current user state
- Session state
- Loading state
- Authentication state listener

### 2. User Interface

- `Login.jsx` - Login form component
- `Register.jsx` - Registration form component
- `ProfileUpdate.jsx` - Profile update component
- `UserProfile.tsx` - User profile page with tabs for account info and preferences

## Getting Started

1. Sign up for a Supabase account at https://supabase.com
2. Create a new project
3. Get your project URL and anon key from the project settings
4. Create a `.env` file in the `frontend` directory with your Supabase credentials
5. Run the SQL schema in the Supabase SQL editor
6. Start the application

## Authentication Flow

1. Users can sign up with email and password
2. On signup, a profile record is automatically created via database trigger
3. Users can sign in with email and password
4. Authentication state is maintained across the application

## Working with User Data

1. User authentication is handled by Supabase Auth
2. User profiles and preferences are stored in the `profiles` table
3. User's saved recipes are stored in the `saved_recipes` table
4. User's shopping lists are stored in the `shopping_lists` table

## Security Considerations

- Never expose your service role key in client-side code
- Use the anon key for client-side operations
- Always use Row-Level Security to protect data
- Validate inputs on both client and server sides
- Consider implementing email verification for user signup 