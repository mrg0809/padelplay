/**
 * Utility functions for community features
 */

/**
 * Formats player display name
 * @param {Object} player - Player object with first_name and last_name
 * @returns {String} Formatted full name
 */
export const formatPlayerName = (player) => {
  if (!player) return '';
  return `${player.first_name || ''} ${player.last_name || ''}`.trim() || 'Usuario';
};

/**
 * Gets default avatar image if player has no photo
 * @param {String} photoUrl - URL to player's photo
 * @returns {String} URL to use for avatar
 */
export const getPlayerAvatar = (photoUrl) => {
  return photoUrl || 'https://cdn.quasar.dev/img/avatar.png';
};

/**
 * Checks if a player is in a list of players by ID
 * @param {Array} playerList - List of player objects
 * @param {String} playerId - ID to check for
 * @returns {Boolean} True if player is in list
 */
export const isPlayerInList = (playerList, playerId) => {
  return playerList.some(player => player.user_id === playerId);
};

/**
 * Filters players based on search query
 * @param {Array} players - List of player objects
 * @param {String} query - Search query
 * @returns {Array} Filtered list of players
 */
export const filterPlayersByName = (players, query) => {
  if (!query) return players;
  
  const lowerQuery = query.toLowerCase();
  return players.filter(player => {
    const fullName = `${player.first_name} ${player.last_name}`.toLowerCase();
    return fullName.includes(lowerQuery);
  });
};
