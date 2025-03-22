import { createClient } from '@supabase/supabase-js';

// Get Supabase URL and anon key from environment variables
const supabaseUrl = process.env.REACT_APP_SUPABASE_URL;
const supabaseAnonKey = process.env.REACT_APP_SUPABASE_ANON_KEY;

// Verify that environment variables are available
if (!supabaseUrl || !supabaseAnonKey) {
  console.error('Supabase URL or Anon Key not found in environment variables');
  throw new Error('Supabase configuration missing. Please check your .env file.');
}

// Create a single supabase client for interacting with your database
export const supabase = createClient(supabaseUrl, supabaseAnonKey);

// Function to test the Supabase connection
export const testConnection = async (): Promise<boolean> => {
  try {
    console.log("Testing Supabase connection...");
    const { data, error } = await supabase.from('saved_recipes').select('count').limit(1);
    
    if (error) {
      console.error("Supabase connection test failed:", error);
      return false;
    }
    
    console.log("Supabase connection successful:", data);
    return true;
  } catch (err) {
    console.error("Error testing Supabase connection:", err);
    return false;
  }
};

export default supabase; 