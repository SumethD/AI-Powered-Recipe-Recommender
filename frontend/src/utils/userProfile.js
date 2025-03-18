import { supabase } from './supabaseClient';

// Table name for user profiles
const USER_PROFILES_TABLE = 'profiles';

/**
 * Fetch a user profile by user ID
 * @param {string} userId - The user's UUID from Supabase auth
 * @returns {Promise<Object>} - The user profile data and any error
 */
export const getUserProfile = async (userId) => {
  const { data, error } = await supabase
    .from(USER_PROFILES_TABLE)
    .select('*')
    .eq('id', userId)
    .single();
  
  return { data, error };
};

/**
 * Create a new user profile
 * @param {Object} profile - The profile data to insert
 * @returns {Promise<Object>} - The inserted profile data and any error
 */
export const createUserProfile = async (profile) => {
  const { data, error } = await supabase
    .from(USER_PROFILES_TABLE)
    .insert([profile])
    .select();
  
  return { data, error };
};

/**
 * Update a user profile
 * @param {string} userId - The user's UUID from Supabase auth
 * @param {Object} updates - The profile fields to update
 * @returns {Promise<Object>} - The updated profile data and any error
 */
export const updateUserProfile = async (userId, updates) => {
  const { data, error } = await supabase
    .from(USER_PROFILES_TABLE)
    .update(updates)
    .eq('id', userId)
    .select();
  
  return { data, error };
};

/**
 * Get user preferences
 * @param {string} userId - The user's UUID from Supabase auth
 * @returns {Promise<Object>} - The user preferences data and any error
 */
export const getUserPreferences = async (userId) => {
  const { data, error } = await supabase
    .from(USER_PROFILES_TABLE)
    .select('preferences')
    .eq('id', userId)
    .single();
  
  return { data: data?.preferences, error };
};

/**
 * Update user preferences
 * @param {string} userId - The user's UUID from Supabase auth
 * @param {Object} preferences - The preferences to update
 * @returns {Promise<Object>} - The updated preferences data and any error
 */
export const updateUserPreferences = async (userId, preferences) => {
  const { data, error } = await supabase
    .from(USER_PROFILES_TABLE)
    .update({ preferences })
    .eq('id', userId)
    .select('preferences');
  
  return { data: data?.[0]?.preferences, error };
}; 