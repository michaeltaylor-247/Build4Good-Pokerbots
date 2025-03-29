def get_mdf(pot_size, bet_size):
    return pot_size / float(pot_size + bet_size)

def normalize_preflop(score, min_score=19.3, max_score=94.0):
    normalized = (score - min_score) / (max_score - min_score) * 100
    return max(0, min(100, normalized)) 


RANK_MAP = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6,
    '7': 7, '8': 8, '9': 9, 'T': 10,
    'J': 11, 'Q': 12, 'K': 13, 'A': 14
}

def rank_value(card_str):
    rank_char = card_str[0]
    return RANK_MAP[rank_char]

def normalize_preflop(score, min_score=19.3, max_score=94.0):
    normalized = (score - min_score) / (max_score - min_score) * 100
    return max(0, min(100, normalized))  

def preflop_eval(cards):
    ranks = sorted([rank_value(c) for c in cards], reverse=True)
    distinct_ranks = len(set(ranks))
    strength = 0

    # Base Strength from Cards
    strength = sum(ranks)   

    # Kicker Bonus
    strength += 0.5 * ranks[0] + 0.3 * ranks[1] + 0.2 * ranks[2]

    # Broadway Bonus
    if min(ranks) >= 10:
        strength += 8

    # Pair/Trip Bonus
    if distinct_ranks == 1: strength += 30
    elif distinct_ranks == 2: strength += 10

    # Connectivity bonus - potential strights
    gap1 = ranks[0] - ranks[1]
    gap2 = ranks[1] - ranks[2]

    for gap in (gap1, gap2):
        if gap == 1:
            strength += 4
        elif gap == 2:
            strength += 2
        elif gap > 3:
            strength -= 1

    # Suit Bonus - potential flush
    suits = [c[1] for c in cards]
    suit_count = {}
    for s in suits:
        suit_count[s] = suit_count.get(s, 0) + 1
    max_suit_count = max(suit_count.values())

    # On Suit bonus -- all 3 onsuit, bigger bonus
    if max_suit_count == 3: strength += 8
    elif max_suit_count == 2: strength += 4

    strength = normalize_preflop(strength)
    return strength

def normalize_postflop(score, min_score=35.9, max_score=130.6):
    normalized = (score - min_score) / (max_score - min_score) * 100
    return max(0, min(100, normalized))


def postflop_eval(cards, board):
    all_cards = cards + board
    ranks = sorted([rank_value(c) for c in all_cards], reverse=True)
    suits = [c[1] for c in all_cards]
    
    rank_counts = {r: ranks.count(r) for r in set(ranks)}
    suit_counts = {s: suits.count(s) for s in set(suits)}
    strength = 0

    # Base Strength
    strength += sum(ranks)

    # Kicker Bonus
    top_kickers = sorted(set(ranks), reverse=True)[:3]
    if len(top_kickers) >= 3:
        strength += 0.5 * top_kickers[0] + 0.3 * top_kickers[1] + 0.2 * top_kickers[2]

    # Hand-type bonuses
    counts = list(rank_counts.values())
    if 4 in counts: strength += 80  
    elif 3 in counts and 2 in counts: strength += 60 # Full hose
    elif 3 in counts: strength += 40 
    elif counts.count(2) >= 2: strength += 25  #two pair
    elif 2 in counts: strength += 15

    # Flush potential
    max_suit = max(suit_counts.values())
    if max_suit >= 5:
        strength += 50  # Made flush
    elif max_suit == 4:
        strength += 20  # Flush draw

    # Straight potential 
    unique_ranks = sorted(set(ranks))
    for i in range(len(unique_ranks) - 4):
        window = unique_ranks[i:i+5]
        if window[-1] - window[0] == 4:
            strength += 40  # Made straight
            break
    else:
        # Draws
        for i in range(len(unique_ranks) - 2):
            gap = unique_ranks[i+2] - unique_ranks[i]
            if gap == 2:
                strength += 6 
            elif gap == 3:
                strength += 3 

    # Broadway bonus; if all ranks >= 10
    if len(ranks) >= 5 and min(ranks[:5]) >= 10:
        strength += 5

    strength = normalize_postflop(strength)
    return strength