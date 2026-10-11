"""
Tests for common app — service functions and utilities.
"""
import pytest
from common.services import (
    generate_invite_code,
    generate_map_link,
    calculate_distance,
    get_emergency_numbers,
)


class TestGenerateInviteCode:
    """Test invite code generation."""

    def test_format(self):
        """Invite code should be 8 chars with a dash in the middle."""
        code = generate_invite_code()
        assert len(code) == 9  # 8 chars + 1 dash
        assert code[4] == '-'
        parts = code.split('-')
        assert len(parts) == 2
        assert len(parts[0]) == 4
        assert len(parts[1]) == 4

    def test_uppercase(self):
        """Invite code should be uppercase alphanumeric."""
        code = generate_invite_code()
        clean = code.replace('-', '')
        assert clean.isalnum()
        assert clean.isupper()

    def test_no_ambiguous_chars(self):
        """Should not contain ambiguous characters like 0, O, I, 1."""
        code = generate_invite_code()
        clean = code.replace('-', '')
        for char in clean:
            assert char in 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'

    def test_unique(self):
        """Multiple calls should generate different codes."""
        codes = {generate_invite_code() for _ in range(100)}
        assert len(codes) > 90  # At least 90% unique


class TestGenerateMapLink:
    """Test OpenStreetMap link generation."""

    def test_valid_coordinates(self):
        link = generate_map_link(42.8746, 74.5698)
        assert link == 'https://www.openstreetmap.org/?mlat=42.8746&mlon=74.5698#map=16/42.8746/74.5698'

    def test_negative_coordinates(self):
        link = generate_map_link(-1.0, -1.0)
        assert 'openstreetmap.org' in link
        assert '-1.0' in link


class TestCalculateDistance:
    """Test Haversine distance calculation."""

    def test_zero_distance(self):
        """Same point should return 0."""
        dist = calculate_distance(42.8746, 74.5698, 42.8746, 74.5698)
        assert dist == 0

    def test_bishkek_to_osh(self):
        """Bishkek to Osh is approximately 300km."""
        dist = calculate_distance(42.8746, 74.5698, 40.5133, 72.8161)
        # ~300 km ± 20 km
        assert 280_000 < dist < 320_000

    def test_symmetric(self):
        """Distance should be the same regardless of order."""
        d1 = calculate_distance(42.0, 74.0, 40.0, 72.0)
        d2 = calculate_distance(40.0, 72.0, 42.0, 74.0)
        assert abs(d1 - d2) < 0.001


class TestGetEmergencyNumbers:
    """Test Kyrgyzstan emergency numbers."""

    def test_has_all_numbers(self):
        numbers = get_emergency_numbers()
        assert numbers == {
            'general': '112',
            'police': '102',
            'ambulance': '103',
            'fire': '101',
        }
