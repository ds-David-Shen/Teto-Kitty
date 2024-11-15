# score.py

# Attack table for various actions
attack_table = {
    "single": 0,
    "double": 1,
    "triple": 2,
    "quad": 4,
    "asd": 4,  # All Spin Double
    "ass": 2,  # All Spin Single
    "ast": 6,  # All Spin Triple
    "b2b": 1,  # Back-to-Back Bonus
}

# Combo table for combo bonuses
combo_table = [0, 0, 1, 1, 1, 2, 2, 3, 3, 4]

def calculate_score(cleared_lines, is_spin, is_b2b, combo, is_perfect_clear):
    """Calculate the score based on the number of lines cleared, spin detection, B2B, combo, and perfect clear."""
    # Determine the base score for lines cleared or spins
    if is_spin:
        if cleared_lines == 1:
            base_score = attack_table["ass"]
        elif cleared_lines == 2:
            base_score = attack_table["asd"]
        elif cleared_lines == 3:
            base_score = attack_table["ast"]
        else:
            base_score = 0
    else:
        if cleared_lines == 1:
            base_score = attack_table["single"]
        elif cleared_lines == 2:
            base_score = attack_table["double"]
        elif cleared_lines == 3:
            base_score = attack_table["triple"]
        elif cleared_lines == 4:
            base_score = attack_table["quad"]
        else:
            base_score = 0

    # Add B2B bonus if applicable
    if is_b2b and (cleared_lines == 4 or is_spin):
        base_score += attack_table["b2b"]

    # Add combo bonus if applicable
    combo_bonus = combo_table[combo] if combo < len(combo_table) else combo_table[-1]

    # Add perfect clear bonus if applicable
    if is_perfect_clear:
        base_score += 10

    return base_score + combo_bonus
