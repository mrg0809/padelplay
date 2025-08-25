# Tournament Bracket Functionality Documentation

## Overview

The enhanced tournament functionality allows clubs to create comprehensive tournament brackets with proposed schedules that can be edited before finalizing. This system supports all major tournament formats and automatically generates proper bracket structures.

## Supported Tournament Systems

### 1. Round-Robin (`round-robin`)
- **Description**: Teams are divided into groups of 4 (or 5 if needed)
- **Format**: All teams within each group play against each other
- **Use Case**: Best for tournaments with 8-20 teams where all teams should get multiple games
- **Example**: 8 teams → 2 groups of 4 → 6 matches per group = 12 total matches

### 2. Single Elimination (`eliminacion directa`)
- **Description**: Traditional knockout bracket
- **Format**: Teams are eliminated after one loss
- **Use Case**: Best for tournaments with time constraints or when you want a clear winner quickly
- **Example**: 8 teams → 3 rounds (Quarterfinals, Semifinals, Final) = 7 total matches

### 3. Combined System (`combinado`)
- **Description**: Group stage followed by elimination playoffs
- **Format**: Round-robin groups, then top teams advance to knockout rounds
- **Use Case**: Perfect for larger tournaments that need both group play and knockout excitement
- **Example**: 12 teams → 3 groups of 4 → Top 2 per group → 6-team playoff bracket

### 4. Liga System (`liga`)
- **Description**: All teams play against all other teams
- **Format**: Single large round-robin group
- **Use Case**: Best for smaller tournaments (4-8 teams) where everyone should play everyone
- **Example**: 6 teams → Everyone plays everyone = 15 total matches

## How It Works

### 1. Tournament Creation
- Club creates tournament with basic details (dates, courts, system, etc.)
- Players register in teams of 2
- Club monitors registrations

### 2. Closing Tournament Registration
- When sufficient teams are registered, club can "close" the tournament
- This triggers the bracket generation process
- System creates a proposed schedule with:
  - Proper bracket structure based on selected system
  - Automatic date/time scheduling
  - Court assignments
  - Player name resolution

### 3. Schedule Review and Editing
- Club sees the complete proposed tournament structure
- Each match can be edited:
  - **Date**: When the match will be played
  - **Time**: Start time for the match
  - **Court**: Which court is assigned
- System validates for scheduling conflicts
- Visual representation varies by tournament system:
  - **Round-Robin**: Shows groups with all group matches
  - **Elimination**: Shows bracket rounds (QF, SF, F)
  - **Combined**: Shows both group phase and playoff brackets
  - **Liga**: Shows all matches in chronological order

### 4. Finalizing the Tournament
- Once club approves the schedule, they click "Guardar Cuadro"
- System:
  - Creates all matches in the database
  - Blocks courts for scheduled times (creates reservations)
  - Sets tournament status to "closed"
  - Prevents further team registrations

## Technical Features

### Backend Enhancements
- **Smart Bracket Generation**: Automatically creates proper tournament structures
- **Court Assignment**: Distributes matches across available courts
- **Scheduling Logic**: Spaces matches with proper intervals (1h 20min default)
- **Team Shuffling**: Randomizes team placement for fairness
- **Round Naming**: Proper Spanish round names (Cuartos, Semifinales, Final, etc.)

### Frontend Features
- **Visual Bracket Display**: Different layouts for each tournament system
- **Editable Schedule**: Inline editing of dates, times, and courts
- **Conflict Detection**: Warns about scheduling conflicts
- **Responsive Design**: Works on desktop and mobile
- **Real-time Updates**: Changes are reflected immediately in the interface

## User Experience Flow

1. **Club Dashboard** → **Mis Torneos** → **[Tournament List]**
2. Select tournament with sufficient registrations
3. Click **"Cerrar Torneo"** button
4. Review generated bracket structure
5. Edit any schedule details as needed
6. Click **"Guardar Cuadro"** to finalize
7. Tournament is now closed and courts are blocked

## Match Duration and Scheduling

- **Default Match Duration**: 1 hour
- **Match Interval**: 1 hour 20 minutes (includes 20 min buffer)
- **Court Blocking**: Courts are reserved for the full match duration
- **Multi-day Support**: Tournaments can span multiple days
- **Time Validation**: Prevents scheduling in the past

## Error Handling

- **Insufficient Teams**: Warns if not enough teams for tournament format
- **Court Conflicts**: Detects and prevents double-booking courts
- **Invalid Dates**: Validates all dates and times before saving
- **Database Errors**: Graceful error handling with user notifications

## Development Notes

### Backend Files Modified:
- `app/utils/tournament_utils.py`: Core bracket generation logic
- `app/routers/tournaments.py`: API endpoints for preview and saving
- Enhanced error handling and validation

### Frontend Files Modified:
- `src/pages/club/PreviewTournament.vue`: Complete rewrite with bracket visualization
- `src/pages/club/ListTournaments.vue`: Updated navigation
- `src/helpers/tournamentUtils.js`: New utility functions
- `src/router/routes.js`: Updated route configuration

### Testing:
- Comprehensive test suite in `backend/test_tournament_utils.py`
- Tests all tournament systems and edge cases
- Validates bracket generation logic

This implementation provides clubs with a professional tournament management system that handles all the complexity of bracket generation while giving them full control over the final schedule.