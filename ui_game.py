import os
import sys
import tkinter as tk
from tkinter import messagebox

try:
    from engine import DraftSystem, SquadBoard
except ImportError:
    # Safe structural fallback layout if engine imports are processing separately
    pass

class FutDraftApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Custom Club FUT Draft Simulator")
        self.root.state("zoomed")
        self.root.configure(bg="#1e1e1e") 

        try:
            self.system = DraftSystem()
        except Exception:
            messagebox.showerror("Error", "Draft system engine initialization failed! Ensure engine.py exists.")
            sys.exit()

        self.board = None
        self.formation_name = None
        self.current_pick = 1
        self.total_picks = 16
        self.active_options = []
        self.selected_player = None
        self.selected_pitch_slot = None 

        self.tooltip_window = None
        self.tooltip_timer = None
        self.pulse_step = 0

        # Custom user configuration properties
        self.user_team_name = "My Club"
        self.jersey_color = "#0052cc" # Default deep blue

        self.show_club_customization_screen()

    def apply_hover_style(self, button, hover_bg=None, hover_fg=None):
    # If no custom colors are passed, default to the team color
        h_bg = hover_bg if hover_bg else self.jersey_color
        h_fg = hover_fg if hover_fg else "#000000"
    
        button.configure(bg="#2d2d2d", fg="#ffffff", activebackground=h_bg, activeforeground=h_fg, bd=0, cursor="hand2")
        button.bind("<Enter>", lambda e: button.config(bg=h_bg, fg=h_fg))
        button.bind("<Leave>", lambda e: button.config(bg="#2d2d2d", fg="#ffffff"))

    def get_tier_styles(self, ovr):
        if ovr < 70: return "#8c5a3c", False 
        elif ovr <= 74: return "#b0b0b0", False 
        elif ovr <= 79: return "#cfb997", False 
        elif ovr <= 83: return "#ffe17d", False 
        elif ovr <= 85: return "#ff7700", False 
        elif ovr <= 89: return "#d62424", True  
        else: return "#8a2be2", True           

    def show_club_customization_screen(self):
        """Launches a sleek, modern palette creation suite."""
        self.setup_frame = tk.Frame(self.root, bg="#2d2d2d", padx=40, pady=40, bd=1, relief=tk.SOLID)
        self.setup_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        tk.Label(self.setup_frame, text="🛡️ CLUB IDENTITY", font=("Arial", 16, "bold"), bg="#2d2d2d", fg="#ffffff").pack(pady=(0, 20))

        # Club Input
        tk.Label(self.setup_frame, text="CLUB NAME", font=("Arial", 9, "bold"), bg="#2d2d2d", fg="#aaaaaa").pack(anchor="w")
        self.name_entry = tk.Entry(self.setup_frame, font=("Arial", 12), bg="#1e1e1e", fg="#ffffff", insertbackground="white", bd=1, width=25)
        self.name_entry.insert(0, "FC FUT PRO")
        self.name_entry.pack(pady=(5, 20))

        # Modern Color Palette Grid
        tk.Label(self.setup_frame, text="KIT PRIMARY COLOR", font=("Arial", 9, "bold"), bg="#2d2d2d", fg="#aaaaaa").pack(anchor="w")
        palette_frame = tk.Frame(self.setup_frame, bg="#2d2d2d")
        palette_frame.pack(pady=(5, 25))

        self.selected_color_var = tk.StringVar(value="#0052cc")
        colors = ["#d62424", "#0052cc", "#1b5e20", "#cc9900", "#ffffff", "#111111"]

        for color in colors:
            swatch = tk.Button(palette_frame, bg=color, width=4, height=2, bd=0, cursor="hand2",
                               command=lambda c=color: self.set_active_color(c))
            swatch.pack(side=tk.LEFT, padx=5)
            # Add subtle hover highlight to the swatches
            swatch.bind("<Enter>", lambda e, s=swatch: s.config(relief=tk.SOLID, bd=2))
            swatch.bind("<Leave>", lambda e, s=swatch: s.config(relief=tk.FLAT, bd=0))

        # Transition
        next_btn = tk.Button(self.setup_frame, text="CONTINUE TO FORMATIONS", font=("Arial", 10, "bold"), pady=10, command=self.transition_to_formation_step)
        self.apply_hover_style(next_btn, hover_bg="#00ff00", hover_fg="#000000")
        next_btn.pack(fill=tk.X)

    def set_active_color(self, color):
        self.selected_color_var.set(color)
        


    def transition_to_formation_step(self):
        # Save custom choices
        input_name = self.name_entry.get().strip()
        if input_name:
            self.user_team_name = input_name.upper()
        self.jersey_color = self.selected_color_var.get()

        self.setup_frame.destroy()

        # Render Formation selection state
        self.menu_frame = tk.Frame(self.root, bg="#1e1e1e")
        self.menu_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        title = tk.Label(self.menu_frame, text=f"SELECT STRATEGIC FORMATION FOR {self.user_team_name}", font=("Arial", 14, "bold"), bg="#1e1e1e", fg="#ffffff")
        title.pack(pady=25)

        for f_name in self.system.formations.keys():
            btn = tk.Button(self.menu_frame, text=f_name, font=("Arial", 11, "bold"), width=26, pady=10, command=lambda f=f_name: self.initialize_main_game_board(f))
            self.apply_hover_style(btn)
            btn.pack(pady=8)

    def initialize_main_game_board(self, chosen_formation):
        self.formation_name = chosen_formation
        self.board = SquadBoard(chosen_formation, self.system.formations)
        self.menu_frame.destroy()

        self.header_frame = tk.Frame(self.root, bg="#2d2d2d", height=55)
        self.header_frame.pack(fill=tk.X)

        # Custom Team Name embedded directly into top dashboard banner
        self.header_label = tk.Label(self.header_frame, text=f"🛡️ {self.user_team_name} DRAFT  |  PICK {self.current_pick} / {self.total_picks}  |  {self.formation_name}", font=("Arial", 13, "bold"), bg="#2d2d2d", fg="#ffffff")
        self.header_label.pack(side=tk.LEFT, padx=25, pady=15)

        self.workspace = tk.Frame(self.root, bg="#1e1e1e")
        self.workspace.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)

        self.pitch_container = tk.Frame(self.workspace, bg="#1e1e1e", width=620, height=700)
        self.pitch_container.pack(side=tk.LEFT, fill=tk.Y, padx=(10, 20))
        self.pitch_container.pack_propagate(False)

        self.pitch_canvas = tk.Canvas(self.pitch_container, bg="#153e1a", bd=0, highlightthickness=0) 
        self.pitch_canvas.pack(fill=tk.BOTH, expand=True)
        self.pitch_canvas.bind("<Configure>", lambda e: self.draw_stadium_pitch_array())

        self.pack_panel = tk.Frame(self.workspace, bg="#2d2d2d", width=460)
        self.pack_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.pack_panel.pack_propagate(False)

        pack_title = tk.Label(self.pack_panel, text="📦 SELECT PLAYER FROM DRAFT", font=("Arial", 11, "bold"), bg="#2d2d2d", fg="#aaaaaa", pady=15)
        pack_title.pack(fill=tk.X)

        self.pack_rows_container = tk.Frame(self.pack_panel, bg="#2d2d2d")
        self.pack_rows_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        self.action_btn = tk.Button(self.pack_panel, text="CHOOSE A PLAYER TO LOCK IN", font=("Arial", 11, "bold"), bg="#1e1e1e", fg="#555555", bd=0, pady=14, state=tk.DISABLED, command=self.execute_player_submission)
        self.action_btn.pack(fill=tk.X, side=tk.BOTTOM, padx=20, pady=20)

        self.run_canvas_animation_tick()
        self.generate_market_choices_pack()

    def get_formation_coordinates(self, width, height):
        coords = {"GK": (width * 0.5, height * 0.77)}
        def_y = height * 0.59
        mid_y = height * 0.38
        att_y = height * 0.16

        if self.formation_name == "4-3-3":
            coords.update({"LB": (width * 0.14, def_y - 15), "LCB": (width * 0.37, def_y), "RCB": (width * 0.63, def_y), "RB": (width * 0.86, def_y - 15), "LCM": (width * 0.24, mid_y), "CM": (width * 0.50, mid_y + 25), "RCM": (width * 0.76, mid_y), "LW": (width * 0.20, att_y), "ST": (width * 0.50, att_y - 15), "RW": (width * 0.80, att_y)})
        elif self.formation_name == "4-4-2":
            coords.update({"LB": (width * 0.14, def_y - 15), "LCB": (width * 0.37, def_y), "RCB": (width * 0.63, def_y), "RB": (width * 0.86, def_y - 15), "LM": (width * 0.15, mid_y), "LCM": (width * 0.37, mid_y), "RCM": (width * 0.63, mid_y), "RM": (width * 0.85, mid_y), "LS": (width * 0.33, att_y), "RS": (width * 0.67, att_y)})
        elif self.formation_name == "3-5-2":
            coords.update({"LCB": (width * 0.25, def_y), "CB": (width * 0.50, def_y), "RCB": (width * 0.75, def_y), "LM": (width * 0.12, mid_y - 15), "LDM": (width * 0.34, mid_y + 35), "CAM": (width * 0.50, mid_y - 35), "RDM": (width * 0.66, mid_y + 35), "RM": (width * 0.88, mid_y - 15), "LS": (width * 0.33, att_y), "RS": (width * 0.67, att_y)})
        elif self.formation_name == "3-4-3":
            coords.update({"LCB": (width * 0.25, def_y), "CB": (width * 0.50, def_y), "RCB": (width * 0.75, def_y), "LM": (width * 0.13, mid_y), "LCM": (width * 0.38, mid_y + 15), "RCM": (width * 0.62, mid_y + 15), "RM": (width * 0.87, mid_y), "LW": (width * 0.22, att_y), "ST": (width * 0.50, att_y - 15), "RW": (width * 0.78, att_y)})
        elif self.formation_name == "4-5-1 (1)":
            # 2 CDMs, 3 CAMs (LCAM, CAM, RCAM), 1 ST
            coords.update({
                "LB": (width * 0.14, def_y - 15), "LCB": (width * 0.37, def_y), "RCB": (width * 0.63, def_y), "RB": (width * 0.86, def_y - 15),
                "LDM": (width * 0.35, mid_y + 40), "RDM": (width * 0.65, mid_y + 40),
                "LCAM": (width * 0.22, mid_y - 15), "CAM": (width * 0.50, mid_y - 25), "RCAM": (width * 0.78, mid_y - 15),
                "ST": (width * 0.50, att_y - 10)
            })
        elif self.formation_name == "4-5-1 (2)":
            # 2 CDMs, LM, RM, 1 CAM, 1 ST
            coords.update({
                "LB": (width * 0.14, def_y - 15), "LCB": (width * 0.37, def_y), "RCB": (width * 0.63, def_y), "RB": (width * 0.86, def_y - 15),
                "LM": (width * 0.15, mid_y), "LDM": (width * 0.35, mid_y + 35), "CAM": (width * 0.50, mid_y - 15), "RDM": (width * 0.65, mid_y + 35), "RM": (width * 0.85, mid_y),
                "ST": (width * 0.50, att_y)
            })
        elif self.formation_name == "4-4-1-1":
            # 2 CMs, LM, RM, 1 CF, 1 ST
            coords.update({
                "LB": (width * 0.14, def_y - 15), "LCB": (width * 0.37, def_y), "RCB": (width * 0.63, def_y), "RB": (width * 0.86, def_y - 15),
                "LM": (width * 0.15, mid_y), "LCM": (width * 0.37, mid_y + 15), "RCM": (width * 0.63, mid_y + 15), "RM": (width * 0.85, mid_y),
                "CF": (width * 0.50, mid_y - 45), "ST": (width * 0.50, att_y)
            })

        for idx in range(5):
            coords[f"BENCH_{idx}"] = ((width * 0.18) + (idx * (width * 0.16)), height * 0.91)
        return coords

    def draw_stylized_vector_jersey(self, cx, cy, base_scale=1.0):
        """Draws a sharp, geometric shirt outline using the chosen dynamic team colors."""
        s = base_scale
        # Elegant vector coordinates tracking collar, sleeves, and body hem
        jersey_poly_points = [
            cx - (24*s), cy - (22*s),   # Left shoulder joint
            cx - (14*s), cy - (22*s),   # Left collar throat
            cx,          cy - (12*s),   # V-neck front dip center
            cx + (14*s), cy - (22*s),   # Right collar throat
            cx + (24*s), cy - (22*s),   # Right shoulder joint
            cx + (36*s), cy - (10*s),   # Right sleeve top opening
            cx + (26*s), cy + (2*s),    # Right sleeve bottom armpit
            cx + (20*s), cy + (2*s),    # Right torso side top
            cx + (20*s), cy + (24*s),   # Right bottom hem flank
            cx - (20*s), cy + (24*s),   # Left bottom hem flank
            cx - (20*s), cy + (2) * s,  # Left torso side top
            cx - (26*s), cy + (2*s),    # Left sleeve bottom armpit
            cx - (36*s), cy - (10*s)    # Left sleeve top opening
        ]
        
        # Choose trim outline color so white kits remain visibly distinct against green lines
        outline_c = "#ffffff" if self.jersey_color != "#ffffff" else "#cccccc"
        
        # Render the custom colored jersey shape
        self.pitch_canvas.create_polygon(jersey_poly_points, fill=self.jersey_color, outline=outline_c, width=2)
        

    def draw_stadium_pitch_array(self):
        self.pitch_canvas.delete("all")
        w = self.pitch_canvas.winfo_width()
        h = self.pitch_canvas.winfo_height()

        # Strategic Field Linework Paint
        self.pitch_canvas.create_rectangle(15, 15, w - 15, h - 95, outline="#ffffff", width=2)
        self.pitch_canvas.create_line(15, h * 0.43, w - 15, h * 0.43, fill="#ffffff", width=2)
        self.pitch_canvas.create_oval(w * 0.5 - 55, h * 0.43 - 55, w * 0.5 + 55, h * 0.43 + 55, outline="#ffffff", width=2)
        self.pitch_canvas.create_rectangle(w * 0.24, 15, w * 0.76, h * 0.14, outline="#ffffff", width=2)
        self.pitch_canvas.create_rectangle(w * 0.24, h * 0.72, w * 0.76, h - 95, outline="#ffffff", width=2)

        coords = self.get_formation_coordinates(w, h)
        self.jersey_clickable_areas = {}

        for slot_key, (x, y) in coords.items():
            is_bench = slot_key.startswith("BENCH_")
            player = None

            if is_bench:
                b_idx = int(slot_key.split("_")[1])
                if b_idx < len(self.board.bench): player = self.board.bench[b_idx]
                display_label = f"B{b_idx+1}"
            else:
                player = self.board.pitch[slot_key]
                display_label = slot_key

            scale_factor = 0.8 if is_bench else 1.1
            click_radius = 20 if is_bench else 30
            color_tier = "NONE"
            eff_ovr = ""

            if player:
                eff_ovr, color_tier, _ = player.get_effective_rating(slot_key) if not is_bench else (player.base_ovr, "GREEN", 1.0)

            # Chemistry Ring Aura Indicators
            if self.selected_pitch_slot == slot_key:
                self.pitch_canvas.create_oval(x - click_radius - 4, y - click_radius - 4, x + click_radius + 4, y + click_radius + 4, outline="#00bfff", width=3)
            elif player and not is_bench:
                aura = "#00ff00" if color_tier == "GREEN" else "#ffcc00" if color_tier == "YELLOW" else "#ff0000"
                p = self.pulse_step % 5
                self.pitch_canvas.create_oval(x - click_radius - p, y - click_radius - p, x + click_radius + p, y + click_radius + p, outline=aura, width=2)

            # DRAW CUSTOM COLOR KIT
            self.draw_stylized_vector_jersey(x, y, base_scale=scale_factor)

            # Centralized Ratings overlay text numbers inside center of vector model
            main_txt = display_label if not player else f"{eff_ovr}"
            txt_color = "#cccccc" if not player else "#ffe17d" if self.jersey_color in ["#111111", "#0052cc", "#d62424"] else "#ffffff"
            
            # Subtle drop shadow effect for custom white/yellow jerseys
            if self.jersey_color in ["#ffffff", "#cc9900"] and player:
                self.pitch_canvas.create_text(x+1, x+1, text=main_txt, fill="#000000", font=("Arial", 10, "bold"))

            self.pitch_canvas.create_text(x, y, text=main_txt, fill=txt_color, font=("Arial", 10, "bold") if not is_bench else ("Arial", 8, "bold"))

            if player:
                clean_name = player.name.split("(")[0].strip()
                short_name = clean_name.split(" ")[-1] if len(clean_name) > 11 else clean_name
                self.pitch_canvas.create_text(x, y + (28 * scale_factor) + 8, text=short_name, fill="#ffffff", font=("Arial", 9, "bold"))

            self.jersey_clickable_areas[slot_key] = (x, y, click_radius)

        self.pitch_canvas.bind("<Button-1>", self.handle_pitch_canvas_clicks)
        self.pitch_canvas.bind("<Motion>", self.handle_pitch_canvas_hover_events)
        self.pitch_canvas.bind("<Double-Button-1>", self.handle_pitch_canvas_double_clicks)

    def run_canvas_animation_tick(self):
        self.pulse_step += 1
        if self.board: self.draw_stadium_pitch_array()
        self.root.after(140, self.run_canvas_animation_tick)

    def generate_market_choices_pack(self):
        for widget in self.pack_rows_container.winfo_children(): widget.destroy()
        
        self.active_options = self.system.generate_global_chaos_pool(count=5)
        self.selected_player = None

        self.action_btn.configure(text="CHOOSE A PLAYER TO LOCK IN", bg="#1e1e1e", fg="#555555", state=tk.DISABLED)

        for idx, player in enumerate(self.active_options):
            row_frame = tk.Frame(self.pack_rows_container, bg="#383838", height=65, bd=1, relief=tk.FLAT)
            row_frame.pack(fill=tk.X, pady=7)
            row_frame.pack_propagate(False)

            tier_bg, has_glow = self.get_tier_styles(player.base_ovr)
            glow_thickness = 3 if has_glow else 0
            ovr_box = tk.Label(row_frame, text=str(player.base_ovr), font=("Arial", 14, "bold"), bg=tier_bg, fg="#000000", width=4, bd=glow_thickness, relief=tk.SOLID)
            ovr_box.pack(side=tk.LEFT, fill=tk.Y)

            all_positions = [player.primary_pos] + player.alt_positions
            pos_display = ", ".join(all_positions)

            clean_display_name = player.name.split("(")[0].strip()

            info_text = f"  {clean_display_name}\n  Position(s): {pos_display}   |   Age: {player.age}   |   Season: '{player.season[-2:] if len(player.season)>2 else player.season}"
            meta_label = tk.Label(row_frame, text=info_text, font=("Arial", 10, "bold"), bg="#383838", fg="#ffffff", justify=tk.LEFT, anchor="w")
            meta_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

            for component in (row_frame, meta_label, ovr_box):
                component.bind("<Button-1>", lambda e, r=row_frame, p=player: self.select_pack_row(r, p))

    def select_pack_row(self, targeted_frame, player_obj):
        for f in self.pack_rows_container.winfo_children():
            f.config(bg="#383838")
            for sub in f.winfo_children():
                if sub.cget("fg") != "#000000": sub.config(bg="#383838", fg="#ffffff")

        targeted_frame.config(bg="#cc9900")
        for sub in targeted_frame.winfo_children():
            if sub.cget("fg") != "#000000": sub.config(bg="#cc9900", fg="#1e1e1e")

        self.selected_player = player_obj
        self.action_btn.configure(bg="#cc9900", fg="#1e1e1e", state=tk.NORMAL, text="CONFIRM SELECTION")

    def execute_player_submission(self):
        if not self.selected_player: return
        self.board.auto_snap_player(self.selected_player)
        self.draw_stadium_pitch_array()

        if self.current_pick >= self.total_picks:
            self.action_btn.configure(text="FINISH DRAFT SQUAD", bg="#8a2be2", fg="#ffffff", command=self.trigger_completion_sequence)
            for f in self.pack_rows_container.winfo_children():
                for c in f.winfo_children(): c.unbind("<Button-1>")
            return

        self.current_pick += 1
        self.header_label.config(text=f"📊 {self.user_team_name} DRAFT  |  PICK {self.current_pick} / {self.total_picks}  |  {self.formation_name}")
        self.generate_market_choices_pack()

    def handle_pitch_canvas_clicks(self, event):
        clicked_slot = self.find_slot_at_pixel_coordinates(event.x, event.y)
        if not clicked_slot:
            self.selected_pitch_slot = None
            return

        is_bench = clicked_slot.startswith("BENCH_")
        b_idx = int(clicked_slot.split("_")[1]) if is_bench else None

        if self.selected_pitch_slot is None:
            if is_bench and b_idx < len(self.board.bench): self.selected_pitch_slot = clicked_slot
            elif not is_bench and self.board.pitch[clicked_slot] is not None: self.selected_pitch_slot = clicked_slot
        else:
            source_slot = self.selected_pitch_slot
            self.selected_pitch_slot = None
            if source_slot == clicked_slot: return

            src_bench = source_slot.startswith("BENCH_")
            src_idx = int(source_slot.split("_")[1]) if src_bench else None
            src_player = self.board.bench[src_idx] if src_bench else self.board.pitch[source_slot]

            tgt_bench = clicked_slot.startswith("BENCH_")
            tgt_idx = int(clicked_slot.split("_")[1]) if tgt_bench else None
            tgt_player = self.board.bench[tgt_idx] if (tgt_bench and tgt_idx < len(self.board.bench)) else (None if tgt_bench else self.board.pitch[clicked_slot])

            if not src_bench and not tgt_bench:
                self.board.pitch[source_slot] = tgt_player
                self.board.pitch[clicked_slot] = src_player
            elif src_bench and tgt_bench and tgt_idx < len(self.board.bench):
                self.board.bench[src_idx], self.board.bench[tgt_idx] = self.board.bench[tgt_idx], self.board.bench[src_idx]
            elif not src_bench and tgt_bench:
                if tgt_player:
                    self.board.pitch[source_slot] = tgt_player
                    self.board.bench[tgt_idx] = src_player
                else:
                    self.board.pitch[source_slot] = None
                    self.board.bench.append(src_player)
            elif src_bench and not tgt_bench:
                if tgt_player:
                    self.board.pitch[clicked_slot] = src_player
                    self.board.bench[src_idx] = tgt_player
                else:
                    self.board.pitch[clicked_slot] = src_player
                    self.board.bench.pop(src_idx)

            self.draw_stadium_pitch_array()

    def find_slot_at_pixel_coordinates(self, ex, ey):
        if not hasattr(self, "jersey_clickable_areas"): return None
        for slot, (x, y, r) in self.jersey_clickable_areas.items():
            if ((ex - x)**2 + (ey - y)**2) <= (r + 15)**2: return slot
        return None

    def handle_pitch_canvas_hover_events(self, event):
        slot = self.find_slot_at_pixel_coordinates(event.x, event.y)
        player = None
        if slot:
            if slot.startswith("BENCH_"):
                idx = int(slot.split("_")[1])
                if idx < len(self.board.bench): player = self.board.bench[idx]
            else: player = self.board.pitch[slot]

        if not player:
            self.clear_active_tooltip_clocks()
            return

        if self.tooltip_timer is None:
            self.tooltip_timer = self.root.after(1200, lambda: self.render_floating_nuvoletta(event.x_root, event.y_root, player, slot))

    def clear_active_tooltip_clocks(self):
        if self.tooltip_timer: self.root.after_cancel(self.tooltip_timer); self.tooltip_timer = None
        if self.tooltip_window: self.tooltip_window.destroy(); self.tooltip_window = None

    def render_floating_nuvoletta(self, rx, ry, player, slot):
        if self.tooltip_window: self.tooltip_window.destroy()
        self.tooltip_window = tk.Toplevel(self.root)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{rx + 15}+{ry + 10}")
        self.tooltip_window.configure(bg="#2d2d2d", bd=1, relief=tk.SOLID)

        eff_ovr = player.base_ovr if slot.startswith("BENCH_") else player.get_effective_rating(slot)[0]
        bg_c, _ = self.get_tier_styles(eff_ovr)
        lbl = tk.Label(self.tooltip_window, text=str(eff_ovr), font=("Arial", 11, "bold"), bg=bg_c, fg="#000000", padx=5, pady=3)
        lbl.pack(side=tk.LEFT)
        clean_name = player.name.split("(")[0].strip()
        tk.Label(self.tooltip_window, text=f" {clean_name} ", font=("Arial", 10, "bold"), bg="#2d2d2d", fg="#ffffff").pack(side=tk.LEFT)

    def handle_pitch_canvas_double_clicks(self, event):
        slot = self.find_slot_at_pixel_coordinates(event.x, event.y)
        if not slot: return
        player = self.board.bench[int(slot.split("_")[1])] if slot.startswith("BENCH_") and int(slot.split("_")[1]) < len(self.board.bench) else self.board.pitch.get(slot)
        if player: self.clear_active_tooltip_clocks(); self.spawn_properties_inspection_grid(player)

    def spawn_properties_inspection_grid(self, player):
        modal = tk.Toplevel(self.root)
        clean_name = player.name.split("(")[0].strip()
        modal.title(f"Profile: {clean_name}")
        modal.geometry("520x450")
        modal.configure(bg="#1e1e1e")
        modal.transient(self.root)
        modal.grab_set()

        tk.Label(modal, text=clean_name.upper(), font=("Arial", 13, "bold"), bg="#2d2d2d", fg="#ffffff", pady=8).pack(fill=tk.X)
        body = tk.Frame(modal, bg="#1e1e1e", padx=15, pady=15)
        body.pack(fill=tk.BOTH, expand=True)

        sf = tk.Frame(body, bg="#1e1e1e")
        sf.pack(side=tk.LEFT, fill=tk.Y, expand=True)

        meta = f"ERA: {player.era}\nSEASON: {player.season}\nAGE: {player.age}\nNATURAL: {player.primary_pos}\nBASE OVR: {player.base_ovr}\nCLUB: {player.club}\n"
        tk.Label(sf, text=meta, font=("Arial", 10, "bold"), bg="#1e1e1e", fg="#cccccc", justify=tk.LEFT).pack(anchor="w")

        tk.Label(sf, text="\n📊 FACE RATINGS:", font=("Arial", 11, "bold"), bg="#1e1e1e", fg="#ffe17d").pack(anchor="w")
        for s, v in player.stats.items():
            tk.Label(sf, text=f" ➔ {s:<4} : {v}", font=("Courier", 11, "bold"), bg="#1e1e1e", fg="#ffffff").pack(anchor="w")

        mf = tk.LabelFrame(body, text="🗺️ POSITION MAP", font=("Arial", 9, "bold"), bg="#2d2d2d", fg="#ffffff", padx=10, pady=10)
        mf.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        mc = tk.Canvas(mf, bg="#215926", bd=0, highlightthickness=0)
        mc.pack(fill=tk.BOTH, expand=True)

        ms = {"ST": (65, 25), "LW": (20, 30), "RW": (110, 30), "CAM": (65, 65), "LM": (15, 85), "RM": (115, 85), "CM": (65, 100), "CDM": (65, 135), "LB": (15, 165), "RB": (115, 165), "CB": (65, 175)}
        for pk, (mx, my) in ms.items():
            bg_c = "#00ff00" if pk == player.primary_pos else ("#ffcc00" if pk in player.alt_positions else "#404040")
            mc.create_oval(mx-10, my-10, mx+10, my+10, fill=bg_c, outline="#ffffff")
            mc.create_text(mx, my, text=pk, fill="#000000" if bg_c != "#404040" else "#888888", font=("Arial", 7, "bold"))

        tk.Button(modal, text="CLOSE", font=("Arial", 10, "bold"), bg="#2d2d2d", fg="#ffffff", bd=0, pady=6, command=modal.destroy).pack(fill=tk.X, side=tk.BOTTOM)

    def trigger_completion_sequence(self):
        if not messagebox.askyesno("Finish Draft", "Are you sure you have finished?"): return
        self.action_btn.pack_forget()

        active_ratings = [player.get_effective_rating(s)[0] for s, player in self.board.pitch.items() if player is not None]
        final_rating = sum(active_ratings) // len(active_ratings) if active_ratings else 0

        self.header_label.config(text=f"🏁 DRAFT LOCKED! FINAL {self.user_team_name} RATING: ⭐ {final_rating} ⭐", bg="#1b5e20")
        messagebox.showinfo("Draft Finished", f"Roster complete! Final rating: ⭐ {final_rating} ⭐")
        
        self.header_frame.pack_forget()
        self.workspace.pack_forget()
        self.transition_to_dashboard()

    # =========================================================================
    # LEAGUE SYSTEM MODE INTERFACES
    # =========================================================================
    def transition_to_dashboard(self):
        """Initializes the 2-Zone Scrollable League Dashboard."""
        # Initialize the League Manager engine with your dynamic club name
        from engine import LeagueManager, get_premier_league_teams
        self.manager = LeagueManager(self.board, get_premier_league_teams(), user_team_name=self.user_team_name)

        # Main Dashboard Container
        self.dash_frame = tk.Frame(self.root, bg="#1a1a1a")
        self.dash_frame.pack(fill=tk.BOTH, expand=True)

        # ------------------ LEFT ZONE: SCROLLABLE LEAGUE TABLE ------------------
        self.left_zone = tk.Frame(self.dash_frame, bg="#252525", width=550)
        self.left_zone.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=15, pady=15)
        self.left_zone.pack_propagate(False) 

        # Header Columns Label
        header_text = f"{'Pos':<4} {'Team':<20} {'MP':<4} {'W':<3} {'D':<3} {'L':<3} {'GF':<4} {'GA':<4} {'GD':<5} {'PTS'}"
        header_lbl = tk.Label(self.left_zone, text=header_text, font=("Courier", 11, "bold"), 
                              fg="#00ff00", bg="#252525", anchor="w", justify=tk.LEFT)
        header_lbl.pack(fill=tk.X, padx=10, pady=(10, 5))

        # Scrollable Canvas Setup
        self.canvas = tk.Canvas(self.left_zone, bg="#252525", highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.left_zone, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#252525")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=5)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # ------------------ RIGHT ZONE: CONTROLS & OPPONENT ------------------
        self.right_zone = tk.Frame(self.dash_frame, bg="#1a1a1a", width=350)
        self.right_zone.pack(side=tk.RIGHT, fill=tk.BOTH, padx=20, pady=20)
        self.right_zone.pack_propagate(False)

        # Matchday Action Button
        self.play_btn = tk.Button(self.right_zone, text="PLAY NEXT MATCHDAY", font=("Arial", 12, "bold"),
                                  command=self.play_and_refresh, bg="#28a745", fg="white", height=3, relief=tk.FLAT)
        self.play_btn.pack(fill=tk.X, pady=(10, 20))

        # Next Opponent Display Card
        self.opp_card = tk.Frame(self.right_zone, bg="#2d2d2d", bd=2, relief=tk.GROOVE)
        self.opp_card.pack(fill=tk.X, pady=10)
        
        self.opp_heading = tk.Label(self.opp_card, text="NEXT OPPONENT", font=("Arial", 10, "bold"), fg="#888888", bg="#2d2d2d")
        self.opp_heading.pack(pady=(10, 5))
        
        self.opp_label = tk.Label(self.opp_card, text="", font=("Arial", 16, "bold"), fg="white", bg="#2d2d2d")
        self.opp_label.pack(pady=(0, 10))

        # Match Result Ticker Label
        self.ticker_label = tk.Label(self.right_zone, text="Season hasn't started yet.", font=("Arial", 11, "italic"), fg="#aaaaaa", bg="#1a1a1a", wraplength=300)
        self.ticker_label.pack(fill=tk.X, pady=20)

        # Statistics Popup Button
        self.stats_btn = tk.Button(self.right_zone, text="VIEW SQUAD STATS", font=("Arial", 10, "bold"),
                                   command=self.open_stats_popup, bg="#0056b3", fg="white", height=2, relief=tk.FLAT)
        self.stats_btn.pack(fill=tk.X, side=tk.BOTTOM, pady=10)

        # Render initial layout
        self.update_dashboard_view()

    def update_dashboard_view(self):
        """Clears and re-draws the scrollable league table data with professional tactical color zones."""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        sorted_table = self.manager.get_sorted_table()
        user_club = self.manager.user_team_name

        for idx, (team_name, stats) in enumerate(sorted_table):
            pos = idx + 1
            is_user = (team_name == user_club)
            
            # 1. Determine Default Position Row Backgrounds based on your specifications
            if pos == 1:
                bg_color = "#1b5e20"  # Vibrant Green (Champion / Champions League)
            elif 2 <= pos <= 4:
                bg_color = "#0d47a1"  # Deep Blue (Champions League Group Stage)
            elif pos == 5 or pos == 6:
                bg_color = "#b2a100"  # Darker, rich Yellow (Europa League)
            elif pos == 7:
                bg_color = "#fbc02d"  # Standard bright Yellow (Conference League)
            elif pos >= 18:
                bg_color = "#b71c1c"  # Dark Crimson Red (Relegation Zone)
            else:
                bg_color = "#252525"  # Standard dark grey for mid-table safety

            # 2. Text configuration adjustments
            # We use a white/bright setup, but highlight the text if it's the User's team
            fg_color = "#00ff00" if is_user else "white"
            
            # If the user is inside a colored zone, give them a subtle background alternate 
            # or a border indicator so they stand out cleanly without breaking your theme colors
            if is_user:
                display_name = f"⭐ {team_name[:17]}"
            else:
                display_name = team_name[:19]

            # 3. Compile layout character matrix string
            row_str = f"{pos:<4} {display_name:<20} {stats['MP']:<4} {stats['W']:<3} {stats['D']:<3} {stats['L']:<3} {stats['GF']:<4} {stats['GA']:<4} {stats['GD']:+5} {stats['PTS']}"
            
            row_lbl = tk.Label(self.scrollable_frame, text=row_str, font=("Courier", 11), 
                               fg=fg_color, bg=bg_color, anchor="w", justify=tk.LEFT, padx=5, pady=2)
            row_lbl.pack(fill=tk.X, expand=True)

        # 4. Render opponent layout card updates
        if self.manager.current_matchday < self.manager.total_matchdays:
            next_fixtures = self.manager.schedule[self.manager.current_matchday]
            next_opp = ""
            for home, away in next_fixtures:
                if home == user_club: next_opp = away
                elif away == user_club: next_opp = home
            
            self.opp_label.config(text=f"{next_opp}\n(Matchday {self.manager.current_matchday + 1}/38)")
        else:
            self.opp_label.config(text="SEASON COMPLETE")
            self.play_btn.config(state=tk.DISABLED, text="SEASON OVER", bg="#555555")

    def play_and_refresh(self):
        """Simulates the game, flashes ticker update, and refreshes table visuals."""
        result, opp = self.manager.play_next_matchday()
        if result is None:
            self.update_dashboard_view()
            return

        self.ticker_label.config(text=f"Matchday {self.manager.current_matchday} Result:\nvs {opp} -> Finished {result}", fg="white")
        self.update_dashboard_view()

    def open_stats_popup(self):
        """Creates a separate top-level window detailing squad goals and assists."""
        popup = tk.Toplevel(self.root)
        popup.title("Squad Leaderboard & Metrics")
        popup.geometry("500x450")
        popup.configure(bg="#222222")
        popup.grab_set() 

        tk.Label(popup, text="YOUR PLAYER STATS", font=("Arial", 14, "bold"), fg="#00ff00", bg="#222222").pack(pady=10)
        
        # Pull drafted player details directly from your squad object
        pitch_players = [p for p in self.board.pitch.values() if p] + [p for p in self.board.bench if p]
        sorted_squad = sorted(pitch_players, key=lambda p: (p.goals, p.assists), reverse=True)

        stats_box = tk.Frame(popup, bg="#1a1a1a")
        stats_box.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        stat_header = f"{'Player Name':<22} {'OVR':<5} {'Goals':<7} {'Assists'}"
        tk.Label(stats_box, text=stat_header, font=("Courier", 11, "bold"), fg="yellow", bg="#1a1a1a", anchor="w").pack(fill=tk.X, padx=10, pady=5)

        for p in sorted_squad:
            clean_p_name = p.name.split("(")[0].strip()
            p_row = f"{clean_p_name[:20]:<22} {p.base_ovr:<5} {p.goals:<7} {p.assists}"
            tk.Label(stats_box, text=p_row, font=("Courier", 11), fg="white", bg="#1a1a1a", anchor="w").pack(fill=tk.X, padx=10, pady=2)
            
        tk.Button(popup, text="CLOSE WINDOW", command=popup.destroy, bg="#dc3545", fg="white", relief=tk.FLAT).pack(pady=15)
        

if __name__ == "__main__":
    root = tk.Tk()
    app = FutDraftApp(root)
    root.mainloop()