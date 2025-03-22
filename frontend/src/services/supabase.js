import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.REACT_APP_SUPABASE_URL;
const supabaseAnonKey = process.env.REACT_APP_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseAnonKey) {
  console.error('Supabase URL or Anon Key not found in environment variables');
  throw new Error('Supabase configuration missing. Please check your .env file.');
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

// Test the connection to Supabase
export const testConnection = async () => {
  try {
    const { data, error } = await supabase.from('profiles').select('*').limit(1);
    if (error) {
      console.error('Error connecting to Supabase:', error.message);
      throw error;
    }
    console.log('Successfully connected to Supabase. Sample data:', data);
    return true;
  } catch (error) {
    console.error('Connection test failed:', error.message);
    return false;
  }
};