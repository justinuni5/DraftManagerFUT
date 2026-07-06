import ast
import random
import pandas as pd


import ast
import random
import math
import pandas as pd

class PlayerCard:
    def __init__(self, data_row):
        self.uid = data_row["game_uid"]
        self.name = data_row["name"]
        self.era = data_row["era"]
        self.season = data_row["season"]
        self.age = int(data_row["age"]) if not pd.isna(data_row["age"]) else 25
        self.club = data_row["club"]
        self.base_ovr = int(data_row["overall"]) if not pd.isna(data_row["overall"]) else 80
        self.potential = int(data_row["potential"]) if not pd.isna(data_row["potential"]) else 80
        self.goals = 0
        self.assists = 0
        self.matches_played = 0
        
        # FIX #2: Handle position separation from combined strings (e.g., "CM-CAM-ST")
        raw_pos = str(data_row["primary_pos"])
        if "-" in raw_pos:
            positions_list = [p.strip().upper() for p in raw_pos.split("-")]
            self.primary_pos = positions_list[0]
            self.alt_positions = positions_list[1:]
        else:
            self.primary_pos = raw_pos.strip().upper()
            self.alt_positions = []

        # Safely parse supplementary alt positions list from dataset if any
        try:
            val = data_row["alt_positions"]
            if isinstance(val, str) and val.startswith("["):
                extra_alts = ast.literal_eval(val)
                for p in extra_alts:
                    if p not in self.alt_positions and p != self.primary_pos:
                        self.alt_positions.append(p.upper())
        except:
            pass

        # FIX #1: Safeguard NaN numbers from breaking the system integer conversion
        def safe_stat(val):
            if pd.isna(val) or val == "" or str(val).lower() == "nan":
                return 70  # Default fallback rating
            try:
                return int(float(val))
            except:
                return 70

        self.stats = {
            "PAC": safe_stat(data_row.get("PAC", 70)),
            "SHO": safe_stat(data_row.get("SHO", 70)),
            "PAS": safe_stat(data_row.get("PAS", 70)),
            "DRI": safe_stat(data_row.get("DRI", 70)),
            "DEF": safe_stat(data_row.get("DEF", 70)),
            "PHY": safe_stat(data_row.get("PHY", 70))
        }

    def add_match_stats(self, goals, assists):
        self.goals += goals
        self.assists += assists
        self.matches_played += 1
        
    def get_effective_rating(self, slot_name):
        """
        Calculates position suitability based on the user's custom matrix rules.
        Automatically normalizes specific formation roles (like LCB, RCM, LS) 
        into their generic core families (CB, CM, ST).
        Returns: (effective_ovr, color_tier, penalty_multiplier)
        """
        raw_slot = slot_name.upper().strip()
        
        # Bench players suffer no visual penalty calculations
        if raw_slot.startswith("BENCH"):
            return self.base_ovr, "GREEN", 1.0

        # --- POSITION NORMALIZATION LAYER ---
        # Map specific layout variants to their true generic football families
        slot = raw_slot
        if slot in ["LCB", "RCB"]:
            slot = "CB"
        elif slot in ["LCM", "RCM"]:
            slot = "CM"
        elif slot in ["LDM", "RDM"]:
            slot = "CDM"
        elif slot in ["LCAM", "RCAM"]:
            slot = "CAM"
        elif slot in ["LS", "RS"]:
            slot = "ST"

        # Gather all natural positions from the player's card
        all_greens = [self.primary_pos] + self.alt_positions

        if "RWM" in all_greens:
            all_greens.extend(["RW", "RM"])
        if "LWM" in all_greens:
            all_greens.extend(["LW", "LM"])
        
        # RULE 1: Direct or Alternate Match -> 100% GREEN
        if slot in all_greens:
            return self.base_ovr, "GREEN", 1.0

        # Extraordinary specific condition overrides requested by user:
        if slot == "RB" and "RWB" in all_greens:
            return self.base_ovr, "GREEN", 1.0
        if slot == "LB" and "LWB" in all_greens:
            return self.base_ovr, "GREEN", 1.0
        if slot == "CM" and ("CDM" in all_greens or "CAM" in all_greens):
            return self.base_ovr, "GREEN", 1.0

        # RULE 2: Proximity Checks -> YELLOW (10% deduction)
        is_yellow = False

        # Wingback to Midfield fallback check (Only if wide midfield isn't already green)
        if slot == "RM" and "RWB" in all_greens and "RM" not in all_greens:
            is_yellow = True
        elif slot == "LM" and "LWB" in all_greens and "LM" not in all_greens:
            is_yellow = True
            
        # Traditional proximity rules
        elif slot == "RM" and ("RB" in all_greens or "RWB" in all_greens):
            is_yellow = True
        elif (slot == "CAM" or slot == "ST") and "CF" in all_greens:
            is_yellow = True
        elif slot == "CB" and "CDM" in all_greens:
            is_yellow = True
        elif (slot == "CDM" or slot == "CAM") and "CM" in all_greens:
            is_yellow = True
        elif slot == "CF" and "CAM" in all_greens:
            is_yellow = True
        elif slot == "LW" and "LM" in all_greens:
            is_yellow = True
        elif slot == "LM" and "LW" in all_greens:
            is_yellow = True
        elif slot == "RW" and "RM" in all_greens:
            is_yellow = True
        elif slot == "RM" and "RW" in all_greens:
            is_yellow = True

        if is_yellow:
            effective_ovr = max(40, int(self.base_ovr * 0.9))
            return effective_ovr, "YELLOW", 0.9

        # RULE 3: Out of Position completely -> RED (40% deduction)
        effective_ovr = max(40, int(self.base_ovr * 0.6))
        return effective_ovr, "RED", 0.6


class DraftSystem:

    def __init__(self, csv_path="master_draft_pool.csv"):
        print("📥 Initializing Free-Snapping Engine & Loading Pool...")
        self.df = pd.read_csv(csv_path)

        # Uniform formation dictionaries
        self.formations = {
            "4-3-3": [
                "GK",
                "LB",
                "LCB",
                "RCB",
                "RB",
                "LCM",
                "CM",
                "RCM",
                "LW",
                "ST",
                "RW",
            ],
            "4-4-2": [
                "GK",
                "LB",
                "LCB",
                "RCB",
                "RB",
                "LM",
                "LCM",
                "RCM",
                "RM",
                "LS",
                "RS",
            ],
            "4-5-1 (1)": [
                "GK",
                "LB",
                "LCB",
                "RCB",
                "RB",
                "LDM",
                "RDM",
                "LCAM",
                "CAM",
                "RCAM",
                "ST",
            ],
            "4-5-1 (2)": [
                "GK",
                "LB",
                "LCB",
                "RCB",
                "RB",
                "LCDM",
                "RCDM",
                "LM",
                "RM",
                "CAM",
                "ST",
            ],
            "4-4-1-1": [
                "GK",
                "LB",
                "LCB",
                "RCB",
                "RB",
                "LM",
                "LCM",
                "RCM",
                "RM",
                "CF",
                "ST",
            ],
            "3-4-3": [
                "GK",
                "LCB",
                "CB",
                "RCB",
                "LM",
                "LCM",
                "RCM",
                "RM",
                "LW",
                "RW",
                "ST",
            ],
            "3-5-2": [
                "GK",
                "LCB",
                "CB",
                "RCB",
                "LM",
                "LDM",
                "CAM",
                "RDM",
                "RM",
                "LS",
                "RS",
            ],
        }

    def generate_global_chaos_pool(self, count=5):
        """Picks 5 completely random cards from the 1,648 master database archive."""
        sampled_records = self.df.sample(count).to_dict(orient="records")
        return [PlayerCard(r) for r in sampled_records]


class SquadBoard:

    def __init__(self, formation_name, formations_dict):
        self.formation_name = formation_name
        self.slots = formations_dict[formation_name]
        self.pitch = {slot: None for slot in self.slots}
        self.bench = []

    def auto_snap_player(self, player_card):
        """Scans the board and automatically houses a drafted card in its absolute best position fit."""
        # Phase 1: Natural Green Role Fit
        for slot in self.slots:
            if self.pitch[slot] is None:
                _, color, _ = player_card.get_effective_rating(slot)
                if color == "GREEN":
                    self.pitch[slot] = player_card
                    return f"🟢 Snapped {player_card.name} into natural role: {slot}"

        # Phase 2: Secondary Yellow Adaptability Fit
        for slot in self.slots:
            if self.pitch[slot] is None:
                _, color, _ = player_card.get_effective_rating(slot)
                if color == "YELLOW":
                    self.pitch[slot] = player_card
                    return f"🟡 Placed {player_card.name} into alternative role: {slot} (10% Penalty)"

        # Phase 3: Out-of-Position Red Crisis Placement
        for slot in self.slots:
            if self.pitch[slot] is None:
                self.pitch[slot] = player_card
                return f"🔴 Out-of-position crisis! {player_card.name} forced to play: {slot} (40% Penalty)"

        # Phase 4: Full pitch roster fallback
        self.bench.append(player_card)
        return f"📋 Lineup Full! Sent {player_card.name} to the Bench."

import random

import random

class Team:
    def __init__(self, name, base_ovr):
        self.name = name
        self.base_ovr = base_ovr

class LeagueManager:
    def __init__(self, user_squad, league_teams, user_team_name="YOUR TEAM"):
        self.user_squad = user_squad
        self.user_team_name = user_team_name
        
        # Full list of 20 teams (19 AI + YOUR CUSTOM TEAM NAME)
        self.teams = league_teams + [Team(self.user_team_name, 0)] 
        self.current_matchday = 0
        self.total_matchdays = 38
        
        # Initialize professional stats schema
        self.table = {
            t.name: {"MP": 0, "W": 0, "D": 0, "L": 0, "GD": 0, "PTS": 0, "GF": 0, "GA": 0} 
            for t in self.teams
        }
        
        # Generate the strict calendar schedule
        self.schedule = self._generate_schedule()

    def _generate_schedule(self):
        """Generates a perfectly balanced round-robin schedule for 20 teams."""
        temp_teams = list(self.table.keys())
        if self.user_team_name in temp_teams:
            # Keep User Team at position 0 to make the circle rotation algorithm work cleanly
            temp_teams.remove(self.user_team_name)
            temp_teams.insert(0, self.user_team_name)
            
        num_teams = len(temp_teams)
        first_half = []
        
        # Circle method rotation to generate 19 unique matchdays
        for round_num in range(num_teams - 1):
            matchups = []
            for i in range(num_teams // 2):
                home = temp_teams[i]
                away = temp_teams[num_teams - 1 - i]
                matchups.append((home, away))
            # Rotate teams leaving the first one fixed
            temp_teams = [temp_teams[0]] + [temp_teams[-1]] + temp_teams[1:-1]
            first_half.append(matchups)
            
        # The second half of the season mirrors the first half perfectly
        second_half = []
        for round_matchups in first_half:
            mirrored_matchups = [(away, home) for (home, away) in round_matchups]
            second_half.append(mirrored_matchups)
            
        return first_half + second_half

    def play_next_matchday(self):
        if self.current_matchday >= self.total_matchdays:
            return None, "SEASON OVER"
            
        current_fixtures = self.schedule[self.current_matchday]
        user_result_str = ""
        opponent_name = ""
        
        # Get User's actual dynamic OVR based on drafted squad
        user_pitch_players = [p for p in self.user_squad.pitch.values() if p]
        user_actual_ovr = sum(p.base_ovr for p in user_pitch_players) / len(user_pitch_players) if user_pitch_players else 75
        
        # Simulate all 10 matches scheduled for this specific matchday
        for home, away in current_fixtures:
            # Determine Team Ratings
            home_ovr = user_actual_ovr if home == self.user_team_name else next(t.base_ovr for t in self.teams if t.name == home)
            away_ovr = user_actual_ovr if away == self.user_team_name else next(t.base_ovr for t in self.teams if t.name == away)
            
            # Simulate Score based on OVR difference + slight home advantage + randomness
            home_score = max(0, int((home_ovr - 72) / 8) + random.randint(0, 2) + (1 if random.random() > 0.4 else 0))
            away_score = max(0, int((away_ovr - 72) / 8) + random.randint(0, 2))
            
            # Process Table updates
            self._update_table_row(home, home_score, away_score)
            self._update_table_row(away, away_score, home_score)
            
            # If this matchup involved the user, capture data for the UI return
            if home == self.user_team_name:
                self._distribute_stats(home_score)
                user_result_str = f"{home_score} - {away_score}"
                opponent_name = away
            elif away == self.user_team_name:
                self._distribute_stats(away_score)
                user_result_str = f"{away_score} - {home_score}"
                opponent_name = home

        self.current_matchday += 1
        return user_result_str, opponent_name

    def _distribute_stats(self, goals):
        if not hasattr(self.user_squad, 'pitch') or self.user_squad.pitch is None:
            return

        # 1. Define your exact tactical custom blueprints
        goal_multipliers = {
            "ST": 1.0, "LS": 1.0, "RS": 1.0,
            "CF": 0.85,
            "LW": 0.8, "RW": 0.8,
            "CAM": 0.7,
            "LM": 0.5, "RM": 0.5,
            "CM": 0.4, "LCM": 0.4, "RCM": 0.4, "LB": 0.4, "RB": 0.4,
            "CDM": 0.2,
            "CB": 0.05, "LCB": 0.05, "RCB": 0.05  # Included dynamic variations
        }

        assist_multipliers = {
            "CAM": 1.0,
            "LW": 0.82, "RW": 0.82,
            "CF": 0.75,
            "LM": 0.7, "RM": 0.7,
            "CM": 0.6, "LCM": 0.6, "RCM": 0.6, "LB": 0.6, "RB": 0.6,
            "LS": 0.5, "RS": 0.5,
            "ST": 0.4, "CDM": 0.4,
            "CB": 0.1, "LCB": 0.2, "RCB": 0.2
        }

        # 2. Build the population and goal scoring weights
        pitch_players = []
        g_weights = []
        
        for slot, player in self.user_squad.pitch.items():
            if player is not None and slot != "GK":
                pitch_players.append(player)
                # Fallback to 0.1 if a dynamic formation introduces a different slot variant name
                mult = goal_multipliers.get(slot, 0.1)
                g_weights.append(player.base_ovr * mult)
        
        if not pitch_players or goals == 0: 
            return

        # 3. Simulate match events loop
        for _ in range(goals):
            try:
                scorer = random.choices(pitch_players, weights=g_weights, k=1)[0]
                scorer.goals += 1
                
                # Process assist calculation
                if random.random() > 0.5:
                    possible_assisters = [p for p in pitch_players if p != scorer]
                    if possible_assisters:
                        a_weights = []
                        for p in possible_assisters:
                            # Trace player back to find their tactical slot name on the pitch layout
                            p_slot = next((s for s, pl in self.user_squad.pitch.items() if pl == p), "CM")
                            a_mult = assist_multipliers.get(p_slot, 0.4)
                            a_weights.append(p.base_ovr * a_mult)
                            
                        assister = random.choices(possible_assisters, weights=a_weights, k=1)[0]
                        assister.assists += 1
            except Exception:
                pass

    def _update_table_row(self, team_name, gf, ga):
        stats = self.table[team_name]
        stats["MP"] += 1
        stats["GF"] += gf
        stats["GA"] += ga
        stats["GD"] = stats["GF"] - stats["GA"]
        
        if gf > ga:
            stats["W"] += 1
            stats["PTS"] += 3
        elif gf == ga:
            stats["D"] += 1
            stats["PTS"] += 1
        else:
            stats["L"] += 1

    def get_sorted_table(self):
        return sorted(self.table.items(), key=lambda x: (x[1]['PTS'], x[1]['GD'], x[1]['GF']), reverse=True)


def get_premier_league_teams():
    team_ratings = {
        "Manchester City": 88,
        "Arsenal": 87,
        "Liverpool": 87,
        "Chelsea": 84,
        "Tottenham": 83,
        "Manchester United": 83,
        "Aston Villa": 82,
        "Newcastle": 82,
        "Brighton": 80,
        "West Ham": 79,
        "Crystal Palace": 78,
        "Bournemouth": 77,
        "Fulham": 77,
        "Everton": 76,
        "Brentford": 76,
        "Wolves": 75,
        "Nottingham Forest": 75,
        "Leicester City": 74,
        "Southampton": 73
    }
    return [Team(name, ovr) for name, ovr in team_ratings.items()]

# ==========================================
# TEST RUN VALIDATION MODULE
# ==========================================
if __name__ == "__main__":
    # Boot up structures
    system = DraftSystem()
    board = SquadBoard("4-3-3", system.formations)

    print("\n--- Simulating 5 Automated Picks ---")
    for pick in range(5):
        options = system.generate_global_chaos_pool(count=5)
        # Draft selection simulation logic picking the highest OVR card
        selected_player = max(options, key=lambda p: p.base_ovr)

        print(
            f"\nUser drafts: {selected_player.name} [Base OVR: {selected_player.base_ovr}]"
        )
        result_message = board.auto_snap_player(selected_player)
        print(result_message)

    # Output detailed analytical roster report
    print("\n==========================================")
    print("📋 CURRENT SQUAD SPREADSHEET STATUS")
    print("==========================================")

    active_players = [p for p in board.pitch.values() if p is not None]
    total_squad_count = len(active_players) + len(board.bench)

    print(f"Total Players Drafted: {total_squad_count} / 16")
    print(f"-> Active on Pitch: {len(active_players)}")
    print(f"-> Sitting on Bench: {len(board.bench)}")
    print("------------------------------------------")

    print("🛡️ LINEUP POSITIONS:")
    for slot, player in board.pitch.items():
        if player is not None:
            eff_ovr, color, _ = player.get_effective_rating(slot)
            print(f"  [{slot:<3}] {player.name:<25} - OVR: {eff_ovr} ({color})")
        else:
            print(f"  [{slot:<3}] EMPTY")

    print("\n🪑 BENCH:")
    if not board.bench:
        print("  (Empty)")
    for idx, player in enumerate(board.bench):
        print(f"  [{idx+1}] {player.name} (Nat Pos: {player.primary_pos})")
    print("==========================================")