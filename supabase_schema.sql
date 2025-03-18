-- Create profiles table
CREATE TABLE IF NOT EXISTS profiles (
  id UUID REFERENCES auth.users ON DELETE CASCADE PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  full_name TEXT,
  avatar_url TEXT,
  preferences JSONB DEFAULT '{}'::JSONB,
  dietary_restrictions TEXT[],
  favorite_cuisines TEXT[],
  saved_recipes JSONB DEFAULT '[]'::JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create RLS policies for profiles table
-- Enable RLS
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- Create policy for users to view their own profile
CREATE POLICY "Users can view their own profile" 
  ON profiles 
  FOR SELECT 
  USING (auth.uid() = id);

-- Create policy for users to update their own profile
CREATE POLICY "Users can update their own profile" 
  ON profiles 
  FOR UPDATE 
  USING (auth.uid() = id);

-- Create policy for users to insert their own profile
CREATE POLICY "Users can insert their own profile" 
  ON profiles 
  FOR INSERT 
  WITH CHECK (auth.uid() = id);

-- Create function to handle new user creation
CREATE OR REPLACE FUNCTION public.handle_new_user() 
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.profiles (id, email, full_name)
  VALUES (new.id, new.email, new.raw_user_meta_data->>'full_name');
  RETURN new;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create trigger for new user signup
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Create saved_recipes table to store user's saved recipes
CREATE TABLE IF NOT EXISTS saved_recipes (
  id SERIAL PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  recipe_id TEXT NOT NULL,
  recipe_data JSONB NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, recipe_id)
);

-- Enable RLS for saved_recipes
ALTER TABLE saved_recipes ENABLE ROW LEVEL SECURITY;

-- Create policy for users to view their own saved recipes
CREATE POLICY "Users can view their own saved recipes" 
  ON saved_recipes 
  FOR SELECT 
  USING (auth.uid() = user_id);

-- Create policy for users to insert their own saved recipes
CREATE POLICY "Users can insert their own saved recipes" 
  ON saved_recipes 
  FOR INSERT 
  WITH CHECK (auth.uid() = user_id);

-- Create policy for users to delete their own saved recipes
CREATE POLICY "Users can delete their own saved recipes" 
  ON saved_recipes 
  FOR DELETE 
  USING (auth.uid() = user_id);

-- Create shopping_lists table to store user's shopping lists
CREATE TABLE IF NOT EXISTS shopping_lists (
  id SERIAL PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  items JSONB NOT NULL DEFAULT '[]'::JSONB,
  recipes JSONB DEFAULT '[]'::JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS for shopping_lists
ALTER TABLE shopping_lists ENABLE ROW LEVEL SECURITY;

-- Create policy for users to view their own shopping lists
CREATE POLICY "Users can view their own shopping lists" 
  ON shopping_lists 
  FOR SELECT 
  USING (auth.uid() = user_id);

-- Create policy for users to insert their own shopping lists
CREATE POLICY "Users can insert their own shopping lists" 
  ON shopping_lists 
  FOR INSERT 
  WITH CHECK (auth.uid() = user_id);

-- Create policy for users to update their own shopping lists
CREATE POLICY "Users can update their own shopping lists" 
  ON shopping_lists 
  FOR UPDATE 
  USING (auth.uid() = user_id);

-- Create policy for users to delete their own shopping lists
CREATE POLICY "Users can delete their own shopping lists" 
  ON shopping_lists 
  FOR DELETE 
  USING (auth.uid() = user_id); 