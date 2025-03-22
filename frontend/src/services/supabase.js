import { createClient } from '@supabase/supabase-js';

const supabaseUrl = 'https://osewztkmvcajdtgzkonl.supabase.co';
const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9zZXd6dGttdmNhamR0Z3prb25sIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDIyODg5MTMsImV4cCI6MjA1Nzg2NDkxM30.4v8xLJbIGJ1nvC0ADeugLmaqSfcNj-c-OUsjnLn2rWY';

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Supabase URL and Anon Key must be provided in .env');
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