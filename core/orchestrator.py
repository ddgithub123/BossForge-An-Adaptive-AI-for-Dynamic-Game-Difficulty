# core/orchestrator.py (Enhanced with Manual Input)
import time
from engine.cns_manager import read_params, write_params
from engine.mugen_runner import MugenRunner
from engine.log_parser import parse_winner
from engine.input_manager import InputCounter
from data.fight_data import append_row, compute_update
from ai.adaptive_boss import AdaptiveBoss

class Orchestrator:
    def __init__(self, cfg, paths, auto_mode=False):
        self.cfg = cfg
        self.paths = paths
        self.runner = MugenRunner(paths["MUGEN_EXE"], paths["MUGEN_WORKDIR"])
        self.ai = AdaptiveBoss(cfg)
        self.ic = InputCounter("config/settings.yaml")
        self.auto_mode = auto_mode  # If True, always default to P2 win
        
        # Track statistics
        self.total_matches = 0
        self.p1_wins = 0
        self.p2_wins = 0

    def run_one_match(self):
        current_aggr, current_react = read_params(self.paths["BOSS_CNS_PATH"])
        write_params(self.paths["BOSS_CNS_PATH"], current_aggr, current_react)
        
        print(f"\n{'='*70}")
        print(f"  MATCH #{self.total_matches + 1}")
        print(f"{'='*70}")
        print(f"  Boss Aggression:   {current_aggr:.3f}")
        print(f"  Boss Reaction:     {current_react:.3f}s")
        print(f"{'='*70}\n")
        print("  Starting M.U.G.E.N... Fight!\n")

        # Start counting inputs
        self.ic.start()
        
        # Run match
        fight_time = self.runner.run_match()
        
        # Stop input counter
        self.ic.stop()

        attack_inputs = int(self.ic.count)
        attack_rate = attack_inputs / max(0.001, fight_time)

        # Try automatic detection first
        win = parse_winner(self.paths["LOG_PATH"], debug=False)
        
        # If automatic detection failed, ask user
        if win is None:
            win = self._ask_user_for_winner()
        
        # Log the result
        self._log_match_result(win, current_aggr, current_react, 
                               attack_inputs, attack_rate, fight_time)
        
        # Update AI parameters
        new_aggr, new_react = self.ai.update(
            self.paths["FIGHT_LOGS_CSV"], 
            current_aggr, 
            current_react, 
            compute_update
        )
        write_params(self.paths["BOSS_CNS_PATH"], new_aggr, new_react)
        
        # Display statistics
        self._display_statistics()
        
        print("\n  Press Ctrl+C anytime to stop training...\n")

    def _ask_user_for_winner(self):
        """
        Ask user who won the match.
        Returns: 1 (P1 won), 0 (P2 won)
        """
        if self.auto_mode:
            print("  [AUTO MODE] Defaulting to P2 (Boss) win")
            return 0
        
        print(f"\n{'='*70}")
        print("  WHO WON THE MATCH?")
        print(f"{'='*70}")
        print("  1 - You (Player 1) won")
        print("  0 - Boss (Player 2) won")
        print("  (Press Enter for P2 win)")
        print(f"{'='*70}")
        
        while True:
            try:
                response = input("  Winner [1/0]: ").strip()
                
                if response == "1":
                    print("  ✓ Recorded: PLAYER 1 WINS\n")
                    return 1
                elif response == "0" or response == "":
                    print("  ✓ Recorded: PLAYER 2 (BOSS) WINS\n")
                    return 0
                else:
                    print("  ✗ Invalid input. Please enter 1 or 0.")
            except KeyboardInterrupt:
                print("\n  Using default: P2 win")
                return 0
            except Exception:
                print("  ✗ Error reading input. Using default: P2 win")
                return 0

    def _log_match_result(self, win, aggr, react, attack_inputs, attack_rate, fight_time):
        """Log match result and update statistics"""
        self.total_matches += 1
        
        if win == 1:
            self.p1_wins += 1
        else:
            self.p2_wins += 1
        
        row = {
            "timestamp": int(time.time()),
            "aggression": round(aggr, 4),
            "reaction_time": round(react, 4),
            "attack_inputs": attack_inputs,
            "attack_rate": round(attack_rate, 4),
            "fight_time": round(fight_time, 3),
            "win": int(win)
        }
        append_row(self.paths["FIGHT_LOGS_CSV"], row)
        
        winner_text = "🎉 PLAYER 1 (YOU)" if win == 1 else "💀 PLAYER 2 (BOSS)"
        
        print(f"  {'─'*70}")
        print(f"  MATCH RESULT")
        print(f"  {'─'*70}")
        print(f"  Winner:         {winner_text}")
        print(f"  Fight Duration: {fight_time:.2f}s")
        print(f"  Your Attacks:   {attack_inputs} inputs ({attack_rate:.2f}/s)")
        print(f"  {'─'*70}")

    def _display_statistics(self):
        """Display running statistics"""
        if self.total_matches == 0:
            return
        
        p1_winrate = (self.p1_wins / self.total_matches) * 100
        p2_winrate = (self.p2_wins / self.total_matches) * 100
        
        # Calculate trend
        trend = "🔥 You're improving!" if p1_winrate > 40 else "💪 Keep training!"
        if p1_winrate > 60:
            trend = "🏆 You're dominating!"
        elif p1_winrate < 20:
            trend = "😰 Boss is too strong!"
        
        print(f"\n{'='*70}")
        print(f"  SESSION STATS - {self.total_matches} matches played")
        print(f"{'='*70}")
        print(f"  Your Wins (P1):    {self.p1_wins:3d}  ({p1_winrate:5.1f}%)  {'█' * int(p1_winrate/5)}")
        print(f"  Boss Wins (P2):    {self.p2_wins:3d}  ({p2_winrate:5.1f}%)  {'█' * int(p2_winrate/5)}")
        print(f"  {'─'*70}")
        print(f"  {trend}")
        print(f"{'='*70}")