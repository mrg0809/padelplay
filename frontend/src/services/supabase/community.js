import { supabase } from "../supabase";

// Fetch players that the current user is following
export const fetchFollowing = async (userId) => { 
  try {
    const { data, error } = await supabase
      .from('follows')
      .select('followed_id')
      .eq("follower_id", userId);

    if (error) throw error;
    
    // Get the IDs of followed users
    const followedIds = data.map(item => item.followed_id);
    
    // Now fetch the actual player data for these users
    if (followedIds.length === 0) return [];
    
    const { data: playersData, error: playersError } = await supabase
      .from('players')
      .select('*')
      .in('user_id', followedIds);
      
    if (playersError) throw playersError;
    return playersData;
  } catch (error) {
    console.error("Error fetching following:", error);
    throw error;
  }
};

// Fetch followers of the current user
export const fetchFollowers = async (userId) => {
  try {
    const { data, error } = await supabase
      .from('follows')
      .select('follower_id')
      .eq("followed_id", userId);

    if (error) throw error;
    
    // Get the IDs of followers
    const followerIds = data.map(item => item.follower_id);
    
    // Now fetch the actual player data for these users
    if (followerIds.length === 0) return [];
    
    const { data: playersData, error: playersError } = await supabase
      .from('players')
      .select('*')
      .in('user_id', followerIds);
      
    if (playersError) throw playersError;
    return playersData;
  } catch (error) {
    console.error("Error fetching followers:", error);
    throw error;
  }
};

// Fetch suggested players to follow
export const fetchSuggestedPlayers = async (userId, followingIds = []) => {
  try {
    // If followingIds is not provided, fetch them first
    if (followingIds.length === 0) {
      const { data: followingIdsData, error: followingIdsError } = await supabase
        .from("follows")
        .select("followed_id")
        .eq("follower_id", userId);

      if (followingIdsError) throw followingIdsError;
      followingIds = followingIdsData.map((f) => f.followed_id);
    }

    // Get players that the user is not following
    const { data: players, error } = await supabase
      .from("players")
      .select("*")
      .neq("user_id", userId)
      .limit(20); // Limit to avoid too many results

    if (error) throw error;

    // Filter out players that the user is already following
    const filteredPlayers = players.filter(player => 
      !followingIds.includes(player.user_id));
      
    // Return a limited number of suggestions
    return filteredPlayers.slice(0, 10);
  } catch (error) {
    console.error("Error fetching suggested players:", error);
    throw error;
  }
};

// Unfollow a player using Supabase
export const unfollowPlayerSupabase = async (followerId, followedId) => {
  try {
    const { error } = await supabase
      .from('follows')
      .delete()
      .eq('follower_id', followerId)
      .eq('followed_id', followedId);

    if (error) throw error;
    return { success: true };
  } catch (error) {
    console.error("Error unfollowing player:", error);
    throw error;
  }
};

// Follow a player using Supabase
export const followPlayerSupabase = async (followerId, followedId) => {
  try {
    const { error } = await supabase
      .from('follows')
      .insert([{ follower_id: followerId, followed_id: followedId }]);

    if (error) throw error;
    return { success: true };
  } catch (error) {
    console.error("Error following player:", error);
    throw error;
  }
};

// Check if a user is following another user
export const isFollowingPlayer = (followingList, playerId) => {
  if (!followingList || !Array.isArray(followingList)) return false;
  return followingList.some(player => player.user_id === playerId);
};
