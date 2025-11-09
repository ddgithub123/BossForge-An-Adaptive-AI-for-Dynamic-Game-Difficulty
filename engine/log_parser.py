# engine/log_parser.py
import os, re

def parse_winner(log_path, debug=False):
    """
    Return:
      1 -> Player1 won (human player)
      0 -> Player2 won (boss)
      None -> unknown
    
    This function searches recent lines in mugen.log for winner indicators.
    """
    if not os.path.exists(log_path):
        if debug: print("[log_parser] Log file not found:", log_path)
        return None
    
    try:
        with open(log_path, "r", errors="ignore", encoding="utf-8") as f:
            lines = f.read().splitlines()
    except Exception as e:
        if debug: print("[log_parser] Error reading log:", e)
        return None
    
    if len(lines) == 0:
        if debug: print("[log_parser] Log file is empty")
        return None
    
    # Look at the last 1000 lines for robustness
    tail = lines[-1000:]
    
    # Enhanced patterns - case insensitive, more variations
    patterns_p1 = [
        re.compile(r'player\s*1\s+wins', re.I),
        re.compile(r'p1\s+wins', re.I),
        re.compile(r'winner[:\s]*p1', re.I),
        re.compile(r'winner[:\s]*player\s*1', re.I),
        re.compile(r'kfm\s+wins', re.I),  # Specific to your character
        re.compile(r'^Winner:\s*1', re.I),
        re.compile(r'Player 1\s+Wins', re.I),
    ]
    
    patterns_p2 = [
        re.compile(r'player\s*2\s+wins', re.I),
        re.compile(r'p2\s+wins', re.I),
        re.compile(r'winner[:\s]*p2', re.I),
        re.compile(r'winner[:\s]*player\s*2', re.I),
        re.compile(r'bossforge\s+wins', re.I),  # Specific to your boss
        re.compile(r'^Winner:\s*2', re.I),
        re.compile(r'Player 2\s+Wins', re.I),
    ]
    
    # Search from the end (most recent)
    for line in reversed(tail):
        s = line.strip()
        if not s:
            continue
        
        # Check P1 patterns
        for pattern in patterns_p1:
            if pattern.search(s):
                if debug: print("[log_parser] P1 WIN detected:", s)
                return 1
        
        # Check P2 patterns
        for pattern in patterns_p2:
            if pattern.search(s):
                if debug: print("[log_parser] P2 WIN detected:", s)
                return 0
    
    # If no clear winner found, print debug info
    if debug:
        print("[log_parser] No clear winner found in log. Last 50 lines:")
        for line in tail[-50:]:
            if line.strip():
                print("  ", line.strip())
    
    return None


def parse_winner_from_rounds(log_path, debug=False):
    """
    Alternative method: Count round wins instead of match wins.
    Returns 1 if P1 won more rounds, 0 if P2 won more rounds, None if tie/unknown.
    """
    if not os.path.exists(log_path):
        return None
    
    try:
        with open(log_path, "r", errors="ignore", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        return None
    
    # Count round wins
    p1_rounds = len(re.findall(r'Round.*?P1\s+wins|P1.*?wins.*?round', content, re.I))
    p2_rounds = len(re.findall(r'Round.*?P2\s+wins|P2.*?wins.*?round', content, re.I))
    
    if debug:
        print(f"[log_parser:rounds] P1 rounds: {p1_rounds}, P2 rounds: {p2_rounds}")
    
    if p1_rounds > p2_rounds:
        return 1
    elif p2_rounds > p1_rounds:
        return 0
    else:
        return None


def test_log_parser():
    """Test function to check if log parsing works"""
    log_path = r"D:\mugen-1_1b1\mugen-1.1b1\mugen.log"
    
    print("=" * 60)
    print("TESTING LOG PARSER")
    print("=" * 60)
    
    result = parse_winner(log_path, debug=True)
    print(f"\nFinal result: {result}")
    print("  1 = P1 (human) won")
    print("  0 = P2 (boss) won")
    print("  None = Could not determine")
    
    print("\n" + "=" * 60)
    print("TESTING ROUND-BASED DETECTION")
    print("=" * 60)
    
    result2 = parse_winner_from_rounds(log_path, debug=True)
    print(f"\nRound-based result: {result2}")
    

if __name__ == "__main__":
    test_log_parser()