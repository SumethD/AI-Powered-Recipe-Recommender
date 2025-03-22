import { createClient } from '@supabase/supabase-js';

// Get Supabase URL and anon key from environment variables
const supabaseUrl = process.env.REACT_APP_SUPABASE_URL || 'https://osewztkmvcajdtgzkonl.supabase.co';
const supabaseAnonKey = process.env.REACT_APP_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9zZXd6dGttdmNhamR0Z3prb25sIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDIyODg5MTMsImV4cCI6MjA1Nzg2NDkxM30.4v8xLJbIGJ1nvC0ADeugLmaqSfcNj-c-OUsjnLn2rWY';

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