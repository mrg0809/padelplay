import api from "../api"

// Fetch posts for a specific club
export const fetchClubPosts = async (clubId) => {
  try {
    const response = await api.get(`community/posts/club/${clubId}`);
    return response.data.posts;
  } catch (error) {
    console.error("Error fetching club posts:", error);
    throw error;
  }
};

// Follow a player
export const followPlayer = async (followedId) => {
  try {
    const response = await api.post('community/follow', {
      followed_id: followedId
    });
    return response.data;
  } catch (error) {
    console.error("Error following player:", error);
    throw error;
  }
};

// Unfollow a player
export const unfollowPlayer = async (followedId) => {
  try {
    const response = await api.delete('community/unfollow', {
      data: { followed_id: followedId }
    });
    return response.data;
  } catch (error) {
    console.error("Error unfollowing player:", error);
    throw error;
  }
};

// Search players by name
export const searchPlayersByName = async (searchQuery) => {
  try {
    const response = await api.get(`players/search?query=${encodeURIComponent(searchQuery)}`);
    return response.data;
  } catch (error) {
    console.error("Error searching players:", error);
    throw error;
  }
};
