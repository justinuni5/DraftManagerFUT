import os
import pandas as pd

# Uniform master database columns
FINAL_COLUMNS = [
    "game_uid",
    "name",          # Will store 'Thierry Henry ('05)' format dynamically
    "era",           # e.g., 'FIFA 05'
    "season",        # e.g., '04-05'
    "age",           # For future career progression
    "club",          # Real clubs for modern, fallback for retro
    "overall",
    "potential",
    "primary_pos",
    "alt_positions",
    "preferred_foot",
    "PAC",
    "SHO",
    "PAS",
    "DRI",
    "DEF",
    "PHY",
]


def convert_version_to_season(version_int):
    v = int(version_int)
    prev = (v - 1) % 100
    curr = v % 100
    return f"{prev:02d}-{curr:02d}"


def clean_old_era(file_path, era_label, version_num, min_ovr, min_pot, pot_min_ovr, is_fifa_13=False):
    """Processes historical standalone files and cleanly appends short years to names."""
    if not os.path.exists(file_path):
        print(f"⚠️ {file_path} not found. Skipping {era_label}.")
        return None

    df = pd.read_csv(file_path, encoding="utf-8-sig", sep=";")

    df["preferred_positions"] = df["preferred_positions"].fillna("CM").astype(str).str.strip()
    df["Fullname"] = df["Fullname"].fillna("Unknown Player").astype(str)

    # Apply Custom Era Filters
    condition_base = df["current_rating"] >= min_ovr
    condition_pot = (df["potential_rating"] >= min_pot) & (df["current_rating"] >= pot_min_ovr)
    df = df[condition_base | condition_pot].copy()

    df["age"] = df["age"].fillna(25).astype(int) if "age" in df.columns else 25
    df["season"] = convert_version_to_season(version_num)
    df["era"] = era_label
    
    # 🌟 Your Smart Stylistic Fix: Append the short year right to the name string!
    short_year = f"{version_num:02d}"
    df["name"] = df["Fullname"] + f" ('{short_year})"
    
    # Simple, bulletproof fallback for missing club data
    df["club"] = "Retro Class"

    pac_list, sho_list, pas_list, dri_list, def_list, phy_list = [], [], [], [], [], []

    for _, row in df.iterrows():
        if row["preferred_positions"] == "GK":
            div_col = "gk_diving" if "gk_diving" in df.columns else "diving"
            han_col = "gk_handling" if "gk_handling" in df.columns else "handling"
            ref_col = "gk_reflexes" if "gk_reflexes" in df.columns else "reflexes"
            pos_col = "gk_positioning" if "gk_positioning" in df.columns else "gk_position"

            pac_list.append(row[div_col])
            sho_list.append(row[han_col])
            pas_list.append(row["gk_kicking"] if "gk_kicking" in df.columns else row["short_pass"])
            dri_list.append(row[ref_col])
            def_list.append(row[pos_col])
            phy_list.append(row["acceleration"])
        else:
            sprint_col = "sprint_speed" if is_fifa_13 else "spring_speed"
            tackle_col = "stand_tackle" if is_fifa_13 else "tackling"

            pac_list.append((row["acceleration"] + row[sprint_col]) // 2)
            sho_list.append((row["finishing"] + row["shot_power"]) // 2)
            pas_list.append((row["short_pass"] + row["long_pass"]) // 2)
            dri_list.append((row["dribbling"] + row["ball_control"]) // 2)
            def_list.append((row["marking"] + row[tackle_col]) // 2)
            phy_list.append((row["strength"] + row["stamina"]) // 2)

    df["PAC"] = pac_list
    df["SHO"] = sho_list
    df["PAS"] = pas_list
    df["DRI"] = dri_list
    df["DEF"] = def_list
    df["PHY"] = phy_list

    df["primary_pos"] = df["preferred_positions"]
    df["alt_positions"] = "[]"

    df = df.rename(columns={"id": "player_id", "current_rating": "overall", "potential_rating": "potential"})
    return df


def clean_leone_era(file_path, target_version, min_ovr, min_pot, pot_min_ovr):
    """Processes modern files, maps clubs dynamically, and appends the card season year to names."""
    if not os.path.exists(file_path):
        print(f"⚠️ {file_path} not found. Skipping FIFA {target_version}.")
        return None

    df = pd.read_csv(file_path, encoding="utf-8-sig")

    if "fifa_version" in df.columns:
        df = df[df["fifa_version"] == target_version].copy()

    condition_base = df["overall"] >= min_ovr
    condition_pot = (df["potential"] >= min_pot) & (df["overall"] >= pot_min_ovr)
    df = df[condition_base | condition_pot].copy()

    df["era"] = f"FIFA {target_version}"
    df["season"] = convert_version_to_season(target_version)
    df["age"] = df["age"].fillna(24).astype(int)

    # If club_name exists in modern data, use it; otherwise flag as Retro Squad
    if "club_name" in df.columns:
        df["club"] = df["club_name"].fillna("Free Agent").astype(str).str.strip()
    else:
        df["club"] = "Retro Squad"

    # Append short year format to modern files too for structural consistency
    short_year = f"{target_version:02d}"
    df["name"] = df["short_name"].fillna("Unknown Player").astype(str) + f" ('{short_year})"

    df["player_positions"] = df["player_positions"].fillna("CM").astype(str)
    df["primary_pos"] = df["player_positions"].apply(lambda x: x.split(",")[0].strip())
    df["alt_positions"] = df["player_positions"].apply(lambda x: [pos.strip() for pos in x.split(",")[1:]] if "," in x else [])

    # GK mapping
    df.loc[df["primary_pos"] == "GK", "pace"] = df["goalkeeping_diving"]
    df.loc[df["primary_pos"] == "GK", "shooting"] = df["goalkeeping_handling"]
    df.loc[df["primary_pos"] == "GK", "passing"] = df["goalkeeping_kicking"]
    df.loc[df["primary_pos"] == "GK", "dribbling"] = df["goalkeeping_reflexes"]
    df.loc[df["primary_pos"] == "GK", "defending"] = df["goalkeeping_positioning"]
    df.loc[df["primary_pos"] == "GK", "physic"] = df["movement_acceleration"]

    df = df.rename(columns={"pace": "PAC", "shooting": "SHO", "passing": "PAS", "dribbling": "DRI", "defending": "DEF", "physic": "PHY"})
    return df


# ==========================================
# RUN INGESTION PIPELINE
# ==========================================
print("🚀 Rebuilding database with Year-In-Name structure...")
processed_dfs = []

processed_dfs.append(clean_old_era("datasets/fifa05.csv", "FIFA 05", version_num=5, min_ovr=86, min_pot=92, pot_min_ovr=80))
processed_dfs.append(clean_old_era("datasets/fifa10.csv", "FIFA 10", version_num=10, min_ovr=84, min_pot=90, pot_min_ovr=81))
processed_dfs.append(clean_old_era("datasets/fifa13.csv", "FIFA 13", version_num=13, min_ovr=84, min_pot=87, pot_min_ovr=81, is_fifa_13=True))

processed_dfs.append(clean_leone_era("datasets/male_players.csv", target_version=15, min_ovr=85, min_pot=87, pot_min_ovr=78))
processed_dfs.append(clean_leone_era("datasets/male_players.csv", target_version=18, min_ovr=85, min_pot=88, pot_min_ovr=79))
processed_dfs.append(clean_leone_era("datasets/male_players.csv", target_version=21, min_ovr=85, min_pot=87, pot_min_ovr=80))
processed_dfs.append(clean_leone_era("datasets/fifa26.csv", target_version=26, min_ovr=79, min_pot=85, pot_min_ovr=75))

valid_dfs = [d for d in processed_dfs if d is not None]

if valid_dfs:
    master_df = pd.concat(valid_dfs, ignore_index=True)
    master_df["game_uid"] = master_df["player_id"].astype(str) + "_" + master_df["era"].str.replace(" ", "")
    master_df = master_df[FINAL_COLUMNS]
    master_df.to_csv("master_draft_pool.csv", index=False)
    print(f"\n✅ Success! Total Players added: {len(master_df)}, Database successfully compiled into 'master_draft_pool.csv'.")
else:
    print("\n❌ Ingestion workflow failed.")