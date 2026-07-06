import os
import sys
from engine import DraftSystem, SquadBoard


def clear_screen():
    """Cleans up the terminal interface for a crisp arcade game feel."""
    os.system("cls" if os.name == "nt" else "clear")


def display_pitch(board):
    """Prints a clean, text-based spreadsheet representation of your squad's current state."""
    print("\n========================================================")
    print(f"🏟️  YOUR SQUAD ACTIVE LINEUP ({board.formation_name})")
    print("========================================================")

    # Print the active 11 slots
    for slot in board.slots:
        player = board.pitch[slot]
        if player is not None:
            eff_ovr, color, _ = player.get_effective_rating(slot)
            # Formatting color dots for easy scanning
            dot = (
                "🟢"
                if color == "GREEN"
                else "🟡" if color == "YELLOW" else "🔴"
            )
            print(
                f"  {dot} [{slot:<3}] {player.name:<25} | Base: {player.base_ovr} -> Play OVR: {eff_ovr:<2}"
            )
        else:
            print(
                f"  ⚪ [{slot:<3}] ------------------------- EMPTY -------------------------"
            )

    print("--------------------------------------------------------")
    print("🪑 BENCH SQUAD:")
    if not board.bench:
        print("  (Empty)")
    else:
        bench_names = [f"{p.name} ({p.primary_pos})" for p in board.bench]
        print("  " + ", ".join(bench_names))
    print("========================================================\n")


def run_draft_session():
    # 1. Initialize the dataset engine
    try:
        system = DraftSystem()
    except FileNotFoundError:
        print(
            "❌ Error: 'master_draft_pool.csv' not found. Please run 'py pipeline.py' first!"
        )
        sys.exit()

    clear_screen()
    print("⚡ WELCOME TO THE RETRO-MODERN FUT DRAFT SIMULATOR ⚡\n")
    print("Available Formations:")
    formations_list = list(system.formations.keys())
    for f_idx, f_name in enumerate(formations_list):
        print(f" [{f_idx + 1}] {f_name}")

    # 2. Let user choose formation
    while True:
        try:
            f_choice = int(input("\nSelect your formation number: ")) - 1
            if 0 <= f_choice < len(formations_list):
                f_name = formations_list[f_choice]
                break
            print("❌ Out of bounds. Choose a valid formation number.")
        except ValueError:
            print("❌ Please input a valid integer.")

    # 3. Initialize the board structure
    board = SquadBoard(f_name, system.formations)
    total_allowed_picks = 16  # 11 starters + 5 bench options

    # 4. Main Draft Loop
    for current_pick in range(1, total_allowed_picks + 1):
        clear_screen()
        print(f"🏆 CHOICE PICK {current_pick} / {total_allowed_picks}")
        display_pitch(board)

        # Generate 5 completely random cards from history (Chaos Style)
        options = system.generate_global_chaos_pool(count=5)

        print("--- AVAILABLE TRANSFER MARKET PLAYER OPTIONS ---")
        for idx, player in enumerate(options):
            print(
                f" [{idx + 1}] {player.name:<25} | Nat Pos: {player.primary_pos:<3} | OVR: {player.base_ovr:<2} | {player.era}"
            )
        print("------------------------------------------------")

        # Get user selection choice
        while True:
            try:
                selection = int(input(f"\nSelect a player to draft (1-5): ")) - 1
                if 0 <= selection <= 4:
                    chosen_player = options[selection]
                    break
                print("❌ Out of bounds. Choose a number between 1 and 5.")
            except ValueError:
                print("❌ Please input a valid integer.")

        # Snap player into the matrix board automatically
        clear_screen()
        snap_message = board.auto_snap_player(chosen_player)
        print(f"\n📢 {snap_message}")
        input("\nPress Enter to continue to next pick...")

    # 5. Final Draft Summary Screen
    clear_screen()
    print("🏁 DRAFT COMPLETE! FINAL TEAM ROSTER:")
    display_pitch(board)

    # Calculate final average team rating based on active playing overalls
    active_ratings = []
    for slot in board.slots:
        player = board.pitch[slot]
        if player is not None:
            eff_ovr, _, _ = player.get_effective_rating(slot)
            active_ratings.append(eff_ovr)

    team_rating = (
        sum(active_ratings) // len(active_ratings) if active_ratings else 0
    )
    print(f"📊 YOUR SQUAD SPREADSHEET FINAL TEAM RATING: ⭐ {team_rating} ⭐\n")


if __name__ == "__main__":
    run_draft_session()