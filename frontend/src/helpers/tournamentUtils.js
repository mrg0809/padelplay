/**
 * Tournament utilities for frontend tournament bracket management
 */

/**
 * Get the display name for tournament systems
 * @param {string} system - Tournament system identifier
 * @returns {string} Human readable system name
 */
export function getTournamentSystemName(system) {
  const systems = {
    'round-robin': 'Round Robin',
    'eliminacion directa': 'Eliminación Directa',
    'combinado': 'Combinado (Grupos + Playoffs)',
    'liga': 'Liga (Todos vs Todos)'
  };
  return systems[system] || system;
}

/**
 * Format team name from team data
 * @param {Object} team - Team object with player information
 * @returns {string} Formatted team name
 */
export function formatTeamName(team) {
  if (!team) return 'Equipo no encontrado';
  
  if (team.player1 && team.player2) {
    const p1Name = `${team.player1.first_name} ${team.player1.last_name}`;
    const p2Name = `${team.player2.first_name} ${team.player2.last_name}`;
    return `${p1Name} / ${p2Name}`;
  }
  
  if (team.name) {
    return team.name;
  }
  
  return `Equipo ${team.id}`;
}

/**
 * Get color for tournament system
 * @param {string} system - Tournament system
 * @returns {string} Quasar color name
 */
export function getTournamentSystemColor(system) {
  const colors = {
    'round-robin': 'blue',
    'eliminacion directa': 'red',
    'combinado': 'purple',
    'liga': 'green'
  };
  return colors[system] || 'grey';
}

/**
 * Validate tournament match data
 * @param {Object} match - Match object
 * @returns {Object} Validation result with isValid and errors
 */
export function validateMatch(match) {
  const errors = [];
  
  if (!match.match_date) {
    errors.push('Fecha del partido es requerida');
  }
  
  if (!match.match_time) {
    errors.push('Hora del partido es requerida');
  }
  
  if (!match.court_id) {
    errors.push('Cancha asignada es requerida');
  }
  
  return {
    isValid: errors.length === 0,
    errors
  };
}

/**
 * Get all matches from tournament structure
 * @param {Object} tournamentData - Tournament data structure
 * @returns {Array} Array of all matches
 */
export function getAllMatches(tournamentData) {
  return tournamentData.matches || [];
}

/**
 * Check for scheduling conflicts
 * @param {Array} matches - Array of matches
 * @returns {Array} Array of conflicts found
 */
export function findSchedulingConflicts(matches) {
  const conflicts = [];
  const courtSchedule = {};
  
  matches.forEach((match, index) => {
    const key = `${match.court_id}_${match.match_date}_${match.match_time}`;
    
    if (courtSchedule[key]) {
      conflicts.push({
        type: 'court_time_conflict',
        matches: [courtSchedule[key], { ...match, index }],
        message: `Conflicto en cancha ${match.court_id} el ${match.match_date} a las ${match.match_time}`
      });
    } else {
      courtSchedule[key] = { ...match, index };
    }
  });
  
  return conflicts;
}

/**
 * Get tournament statistics
 * @param {Object} tournamentData - Tournament data
 * @returns {Object} Tournament statistics
 */
export function getTournamentStats(tournamentData) {
  const matches = getAllMatches(tournamentData);
  const dates = [...new Set(matches.map(m => m.match_date))];
  const courts = [...new Set(matches.map(m => m.court_id).filter(Boolean))];
  
  return {
    totalMatches: matches.length,
    totalDays: dates.length,
    courtsUsed: courts.length,
    averageMatchesPerDay: matches.length / Math.max(dates.length, 1),
    conflicts: findSchedulingConflicts(matches).length,
    system: tournamentData.system,
    systemName: getTournamentSystemName(tournamentData.system)
  };
}