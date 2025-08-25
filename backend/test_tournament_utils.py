#!/usr/bin/env python3
"""
Test script for tournament utilities functions
This tests the logic without requiring database connections
"""

import sys
import os
from unittest.mock import MagicMock, patch
import importlib

# Mock all the dependencies before importing
sys.modules['supabase'] = MagicMock()
sys.modules['app.db.connection'] = MagicMock()

# Mock supabase module
mock_supabase = MagicMock()
sys.modules['app.db.connection'].supabase = mock_supabase

sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from datetime import datetime, timedelta
import math
import random

# Now import our module
from app.utils import tournament_utils


def test_generate_round_robin_logic():
    """Test round-robin tournament generation logic"""
    print("Testing Round-Robin Tournament Generation Logic...")
    
    # Test the helper function directly
    tournament = {
        "id": "tournament-1",
        "system": "round-robin",
        "start_date": "2024-01-15",
        "start_time": "09:00:00",
        "courts_used": ["court-1", "court-2"]
    }
    
    # Mock teams data
    teams = []
    for i in range(8):  # 8 teams for 2 groups of 4
        teams.append({
            "id": f"team-{i+1}",
            "player1": {"first_name": f"Player{i*2+1}", "last_name": "A"},
            "player2": {"first_name": f"Player{i*2+2}", "last_name": "B"}
        })
    
    # Test the internal function directly
    result = tournament_utils._generate_round_robin_preview(tournament, teams, tournament["courts_used"])
    
    print(f"✓ Generated {len(result['structure']['groups'])} groups")
    print(f"✓ Total matches: {len(result['matches'])}")
    
    # Verify structure
    assert result["system"] == "round-robin"
    assert len(result['structure']['groups']) == 2  # 8 teams = 2 groups of 4
    assert result["editable"] == True
    
    # Check each group has correct number of matches (4 teams = 6 matches per group)
    total_expected_matches = 0
    for group in result['structure']['groups']:
        group_size = len(group['teams'])
        expected_matches = (group_size * (group_size - 1)) // 2
        total_expected_matches += expected_matches
    
    assert len(result['matches']) == total_expected_matches
    print(f"✓ Correct number of matches generated: {total_expected_matches}")
    return True


def test_elimination_logic():
    """Test elimination bracket logic"""
    print("\nTesting Elimination Tournament Generation Logic...")
    
    tournament = {
        "id": "tournament-2", 
        "system": "eliminacion directa",
        "start_date": "2024-01-15",
        "start_time": "10:00:00",
        "courts_used": ["court-1", "court-2"]
    }
    
    # Mock 8 teams for clean bracket
    teams = []
    for i in range(8):
        teams.append({
            "id": f"team-{i+1}",
            "player1": {"first_name": f"Player{i*2+1}", "last_name": "A"},
            "player2": {"first_name": f"Player{i*2+2}", "last_name": "B"}
        })
    
    result = tournament_utils._generate_elimination_preview(tournament, teams, tournament["courts_used"])
    
    print(f"✓ Generated bracket with {result['structure']['rounds']} rounds")
    print(f"✓ Total matches: {len(result['matches'])}")
    
    # Verify structure
    assert result["system"] == "eliminacion directa"
    assert result['structure']['rounds'] == 3  # 8 teams = 3 rounds (QF, SF, F)
    assert result["editable"] == True
    
    # Check correct number of matches (8 teams = 7 matches total)
    assert len(result['matches']) == 7
    print(f"✓ Correct elimination bracket structure")
    return True


def test_round_names_logic():
    """Test round naming functions"""
    print("\nTesting Round Name Generation...")
    
    # Test elimination round names
    names_3 = tournament_utils._get_round_names(3)
    assert names_3 == ["Cuartos de Final", "Semifinal", "Final"]
    
    names_2 = tournament_utils._get_round_names(2)
    assert names_2 == ["Semifinal", "Final"]
    
    names_1 = tournament_utils._get_round_names(1)
    assert names_1 == ["Final"]
    
    names_4 = tournament_utils._get_round_names(4)
    assert names_4 == ["Octavos de Final", "Cuartos de Final", "Semifinal", "Final"]
    
    print("✓ Round names generated correctly")
    
    # Test playoff round names
    playoff_names = tournament_utils._get_playoff_round_names(3)
    assert playoff_names == ["Cuartos de Final", "Semifinal", "Final"]
    
    print("✓ Playoff round names generated correctly")
    return True


def test_combined_logic():
    """Test combined tournament logic"""
    print("\nTesting Combined Tournament Generation Logic...")
    
    tournament = {
        "id": "tournament-3",
        "system": "combinado", 
        "start_date": "2024-01-15",
        "start_time": "09:00:00",
        "courts_used": ["court-1", "court-2", "court-3"]
    }
    
    # Mock 12 teams for 3 groups of 4, then 6 team playoff
    teams = []
    for i in range(12):
        teams.append({
            "id": f"team-{i+1}",
            "player1": {"first_name": f"Player{i*2+1}", "last_name": "A"},
            "player2": {"first_name": f"Player{i*2+2}", "last_name": "B"}
        })
    
    result = tournament_utils._generate_combined_preview(tournament, teams, tournament["courts_used"])
    
    print(f"✓ Generated {len(result['structure']['groups'])} groups")
    print(f"✓ Generated playoffs with {result['structure']['playoff_rounds']} rounds")
    print(f"✓ Total matches: {len(result['matches'])}")
    
    # Verify structure
    assert result["system"] == "combinado"
    assert len(result['structure']['groups']) == 3  # 12 teams = 3 groups
    assert result['structure']['playoff_rounds'] >= 1
    assert result["editable"] == True
    
    print(f"✓ Combined tournament structure is correct")
    return True


def test_liga_logic():
    """Test liga tournament logic"""
    print("\nTesting Liga Tournament Generation Logic...")
    
    tournament = {
        "id": "tournament-4",
        "system": "liga",
        "start_date": "2024-01-15", 
        "start_time": "09:00:00",
        "courts_used": ["court-1", "court-2"]
    }
    
    # Mock 6 teams
    teams = []
    for i in range(6):
        teams.append({
            "id": f"team-{i+1}",
            "player1": {"first_name": f"Player{i*2+1}", "last_name": "A"},
            "player2": {"first_name": f"Player{i*2+2}", "last_name": "B"}
        })
    
    result = tournament_utils._generate_league_preview(tournament, teams, tournament["courts_used"])
    
    print(f"✓ Total matches: {len(result['matches'])}")
    
    # Verify structure  
    assert result["system"] == "liga"
    # 6 teams = 15 matches (n*(n-1)/2)
    expected_matches = (len(teams) * (len(teams) - 1)) // 2
    assert len(result['matches']) == expected_matches
    assert result["editable"] == True
    
    print(f"✓ Liga tournament has correct number of matches: {expected_matches}")
    return True


def main():
    """Run all tests"""
    print("=" * 60)
    print("Testing Enhanced Tournament Utilities (Logic Only)")
    print("=" * 60)
    
    try:
        test_round_names_logic()
        test_elimination_logic()
        test_generate_round_robin_logic() 
        test_combined_logic()
        test_liga_logic()
        
        print("\n" + "=" * 60)
        print("✅ All logic tests passed! Tournament utilities working correctly.")
        print("✅ The enhanced tournament bracket system is ready for deployment.")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        print("=" * 60)
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)