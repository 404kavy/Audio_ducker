import sys
import tkinter as tk
from tkinter import ttk, messagebox
from audio_engine import AudioDuckerEngine

class ADHDDuckerGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Audio Ducker Focus")
        self.root.geometry("380x560")
        self.root.resizable(False, False)

        # Wireframe / Blueprint Parchment & Ink Theme
        self.BG_COLOR = "#F4EFE6"       # Warm parchment paper background
        self.CARD_BG = "#FAF7F0"        # Light off-white card background
        self.BORDER_INK = "#1A1A1A"     # Deep charcoal ink border
        self.TEXT_INK = "#111111"       # Primary ink black text
        self.TEXT_MUTED = "#555555"     # Muted charcoal subtext
        self.ACCENT_FILL = "#1A1A1A"    # Solid ink black fill for active elements
        self.ACCENT_HIGHLIGHT = "#E63946" # Accent pop color
        self.GOLD_INDICATOR = "#D97706" # Warning/threshold marker

        self.root.configure(bg=self.BG_COLOR)

        self.engine = AudioDuckerEngine()
        self.app_list = []

        self._setup_styles()
        self._build_ui()
        self.refresh_audio_sources()

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(".", background=self.BG_COLOR, foreground=self.TEXT_INK, font=("Segoe UI", 9))
        style.configure("TFrame", background=self.BG_COLOR)
        style.configure("TCombobox", fieldbackground=self.CARD_BG, background=self.CARD_BG, foreground=self.TEXT_INK, darkcolor=self.BORDER_INK, lightcolor=self.BORDER_INK)

    def _build_ui(self):
        # 1. Header (Sketch Style)
        header = tk.Frame(self.root, bg=self.BG_COLOR, pady=8, padx=14)
        header.pack(fill="x")

        title_frame = tk.Frame(header, bg=self.BG_COLOR)
        title_frame.pack(side="left")

        title = tk.Label(title_frame, text="AUDIO DUCKER", font=("Segoe UI Bold", 13), bg=self.BG_COLOR, fg=self.TEXT_INK)
        title.pack(anchor="w", side="left")

        sub = tk.Label(title_frame, text=" | FOCUS", font=("Segoe UI", 10), bg=self.BG_COLOR, fg=self.TEXT_MUTED)
        sub.pack(anchor="w", side="left")

        self.badge_status = tk.Label(header, text="IDLE", font=("Segoe UI Bold", 8), bg=self.BORDER_INK, fg="#FFFFFF", padx=6, pady=2)
        self.badge_status.pack(side="right")

        # Divider line
        div = tk.Frame(self.root, bg=self.BORDER_INK, height=2)
        div.pack(fill="x", padx=14, pady=(0, 6))

        # Main Container
        container = tk.Frame(self.root, bg=self.BG_COLOR, padx=14)
        container.pack(fill="both", expand=True)

        # 2. Source Selector Card (Inky Border)
        card_src = tk.Frame(container, bg=self.CARD_BG, highlightbackground=self.BORDER_INK, highlightthickness=2, bd=0)
        card_src.pack(fill="x", pady=4, ipady=4, ipadx=8)

        lbl_src = tk.Label(card_src, text="1. LECTURE SOURCE", font=("Segoe UI Bold", 8), bg=self.CARD_BG, fg=self.TEXT_INK)
        lbl_src.pack(anchor="w", padx=8, pady=(4, 2))

        row_src = tk.Frame(card_src, bg=self.CARD_BG)
        row_src.pack(fill="x", padx=8, pady=(0, 4))

        self.source_combo = ttk.Combobox(row_src, state="readonly", font=("Segoe UI", 9))
        self.source_combo.pack(side="left", fill="x", expand=True)

        btn_ref = tk.Button(row_src, text="🔄", command=self.refresh_audio_sources, bg=self.BG_COLOR, fg=self.TEXT_INK, activebackground=self.CARD_BG, activeforeground=self.TEXT_INK, bd=1, relief="solid", font=("Segoe UI", 8), cursor="hand2", padx=6)
        btn_ref.pack(side="right", padx=(6, 0))

        # 3. Peak Meter & Live Status Card
        card_meter = tk.Frame(container, bg=self.CARD_BG, highlightbackground=self.BORDER_INK, highlightthickness=2, bd=0)
        card_meter.pack(fill="x", pady=4, ipady=4, ipadx=8)

        lbl_m = tk.Label(card_meter, text="2. SPEECH ACTIVITY METER", font=("Segoe UI Bold", 8), bg=self.CARD_BG, fg=self.TEXT_INK)
        lbl_m.pack(anchor="w", padx=8, pady=(4, 2))

        self.canvas_meter = tk.Canvas(card_meter, bg="#E8E2D5", height=16, highlightthickness=1, highlightbackground=self.BORDER_INK)
        self.canvas_meter.pack(fill="x", padx=8, pady=2)

        self.lbl_live_status = tk.Label(card_meter, text="Ready to start session", font=("Segoe UI", 8), bg=self.CARD_BG, fg=self.TEXT_MUTED, anchor="w")
        self.lbl_live_status.pack(fill="x", padx=8, pady=(2, 4))

        # 4. Features Toggles Card
        card_feat = tk.Frame(container, bg=self.CARD_BG, highlightbackground=self.BORDER_INK, highlightthickness=2, bd=0)
        card_feat.pack(fill="x", pady=4, ipady=4, ipadx=8)

        lbl_f = tk.Label(card_feat, text="3. MODES & RAMPING", font=("Segoe UI Bold", 8), bg=self.CARD_BG, fg=self.TEXT_INK)
        lbl_f.pack(anchor="w", padx=8, pady=(4, 2))

        row_spat = tk.Frame(card_feat, bg=self.CARD_BG)
        row_spat.pack(fill="x", padx=8, pady=2)

        self.var_spatial = tk.BooleanVar(value=True)
        chk_spat = tk.Checkbutton(row_spat, text="🦻 Left-Ear Focus (Free Right Ear)", variable=self.var_spatial, command=self._on_slider_change, bg=self.CARD_BG, fg=self.TEXT_INK, selectcolor=self.BG_COLOR, activebackground=self.CARD_BG, font=("Segoe UI Semibold", 8))
        chk_spat.pack(side="left")

        row_ramp = tk.Frame(card_feat, bg=self.CARD_BG)
        row_ramp.pack(fill="x", padx=8, pady=2)

        self.var_ramp = tk.BooleanVar(value=True)
        chk_ramp = tk.Checkbutton(row_ramp, text="⚡ Progressive Focus Ramp (0%)", variable=self.var_ramp, command=self._on_slider_change, bg=self.CARD_BG, fg=self.TEXT_INK, selectcolor=self.BG_COLOR, activebackground=self.CARD_BG, font=("Segoe UI Semibold", 8))
        chk_ramp.pack(side="left")

        self.lbl_ramp_dur = tk.Label(row_ramp, text="45m", font=("Segoe UI Bold", 8), bg=self.CARD_BG, fg=self.TEXT_INK)
        self.lbl_ramp_dur.pack(side="right")

        self.scale_ramp = tk.Scale(card_feat, from_=10, to=90, orient="horizontal", bg=self.CARD_BG, fg=self.TEXT_INK, highlightthickness=0, troughcolor="#DCD4C4", activebackground=self.BORDER_INK, showvalue=0, command=self._on_slider_change)
        self.scale_ramp.set(45)
        self.scale_ramp.pack(fill="x", padx=8, pady=(0, 2))

        # 5. Tuning Controls Card
        card_tune = tk.Frame(container, bg=self.CARD_BG, highlightbackground=self.BORDER_INK, highlightthickness=2, bd=0)
        card_tune.pack(fill="x", pady=4, ipady=4, ipadx=8)

        lbl_t = tk.Label(card_tune, text="4. TUNING CONTROLS", font=("Segoe UI Bold", 8), bg=self.CARD_BG, fg=self.TEXT_INK)
        lbl_t.pack(anchor="w", padx=8, pady=(4, 2))

        # Sensitivity Threshold Slider
        row_t1 = tk.Frame(card_tune, bg=self.CARD_BG)
        row_t1.pack(fill="x", padx=8, pady=(2, 0))
        tk.Label(row_t1, text="Sensitivity Threshold", font=("Segoe UI", 8), bg=self.CARD_BG, fg=self.TEXT_INK).pack(side="left")
        self.lbl_v_thresh = tk.Label(row_t1, text="1.5%", font=("Segoe UI Bold", 8), bg=self.CARD_BG, fg=self.TEXT_INK)
        self.lbl_v_thresh.pack(side="right")
        self.scale_thresh = tk.Scale(card_tune, from_=5, to=200, orient="horizontal", bg=self.CARD_BG, fg=self.TEXT_INK, highlightthickness=0, troughcolor="#DCD4C4", activebackground=self.BORDER_INK, showvalue=0, command=self._on_slider_change)
        self.scale_thresh.set(15)
        self.scale_thresh.pack(fill="x", padx=8, pady=(0, 2))

        # Ducked Volume Slider
        row_t2 = tk.Frame(card_tune, bg=self.CARD_BG)
        row_t2.pack(fill="x", padx=8, pady=(2, 0))
        tk.Label(row_t2, text="Ducked Spotify Volume", font=("Segoe UI", 8), bg=self.CARD_BG, fg=self.TEXT_INK).pack(side="left")
        self.lbl_v_duck = tk.Label(row_t2, text="15%", font=("Segoe UI Bold", 8), bg=self.CARD_BG, fg=self.TEXT_INK)
        self.lbl_v_duck.pack(side="right")
        self.scale_ducked = tk.Scale(card_tune, from_=0, to=50, orient="horizontal", bg=self.CARD_BG, fg=self.TEXT_INK, highlightthickness=0, troughcolor="#DCD4C4", activebackground=self.BORDER_INK, showvalue=0, command=self._on_slider_change)
        self.scale_ducked.set(15)
        self.scale_ducked.pack(fill="x", padx=8, pady=(0, 2))

        # Normal Volume Slider
        row_t3 = tk.Frame(card_tune, bg=self.CARD_BG)
        row_t3.pack(fill="x", padx=8, pady=(2, 0))
        tk.Label(row_t3, text="Normal Spotify Volume", font=("Segoe UI", 8), bg=self.CARD_BG, fg=self.TEXT_INK).pack(side="left")
        self.lbl_v_norm = tk.Label(row_t3, text="85%", font=("Segoe UI Bold", 8), bg=self.CARD_BG, fg=self.TEXT_INK)
        self.lbl_v_norm.pack(side="right")
        self.scale_normal = tk.Scale(card_tune, from_=40, to=100, orient="horizontal", bg=self.CARD_BG, fg=self.TEXT_INK, highlightthickness=0, troughcolor="#DCD4C4", activebackground=self.BORDER_INK, showvalue=0, command=self._on_slider_change)
        self.scale_normal.set(85)
        self.scale_normal.pack(fill="x", padx=8, pady=(0, 2))

        # 6. Action Button (Bold Inky Button)
        btn_box = tk.Frame(container, bg=self.BG_COLOR)
        btn_box.pack(fill="x", pady=6)

        self.btn_toggle = tk.Button(btn_box, text="▶ START FOCUS SESSION", font=("Segoe UI Bold", 10), bg=self.BORDER_INK, fg="#FFFFFF", activebackground="#333333", activeforeground="#FFFFFF", bd=0, cursor="hand2", pady=7, command=self.toggle_engine)
        self.btn_toggle.pack(fill="x")

        self._on_slider_change()

    def refresh_audio_sources(self):
        self.app_list = AudioDuckerEngine.get_audio_sessions_info()
        display_values = [app["display_name"] for app in self.app_list]
        self.source_combo["values"] = display_values
        if display_values:
            selected_idx = 0
            for i, app in enumerate(self.app_list):
                pname = app["name"].lower()
                if any(b in pname for b in ["chrome", "msedge", "firefox", "brave", "vlc"]):
                    selected_idx = i
                    break
            self.source_combo.current(selected_idx)
        else:
            self.source_combo.set("No active audio apps found")

    def _on_slider_change(self, _=None):
        thresh_pct = self.scale_thresh.get() / 10.0
        ducked_pct = self.scale_ducked.get()
        normal_pct = self.scale_normal.get()
        ramp_mins = self.scale_ramp.get()

        self.lbl_v_thresh.config(text=f"{thresh_pct:.1f}%")
        self.lbl_v_duck.config(text=f"{ducked_pct}%")
        self.lbl_v_norm.config(text=f"{normal_pct}%")
        self.lbl_ramp_dur.config(text=f"{ramp_mins}m")

        self.engine.threshold = thresh_pct / 100.0
        self.engine.ducked_volume = ducked_pct / 100.0
        self.engine.normal_volume = normal_pct / 100.0
        self.engine.hold_time = 1.2
        self.engine.left_ear_panning_enabled = self.var_spatial.get()
        self.engine.ramp_enabled = self.var_ramp.get()
        self.engine.ramp_duration_minutes = float(ramp_mins)

    def toggle_engine(self):
        if self.engine.running:
            self.engine.stop()
            self.btn_toggle.config(text="▶ START FOCUS SESSION", bg=self.BORDER_INK, fg="#FFFFFF")
            self.badge_status.config(text="IDLE", bg=self.BORDER_INK, fg="#FFFFFF")
            self.lbl_live_status.config(text="Session stopped", fg=self.TEXT_MUTED)
            self._update_meter(0.0, False)
        else:
            idx = self.source_combo.current()
            if idx < 0 or idx >= len(self.app_list):
                messagebox.showwarning("Select App", "Please select a lecture source application.")
                return

            lecture_app = self.app_list[idx]["name"]
            self._on_slider_change()
            self.engine.start(lecture_app, callback=self._on_engine_update)
            self.btn_toggle.config(text="⏹ STOP FOCUS SESSION", bg=self.ACCENT_HIGHLIGHT, fg="#FFFFFF")
            self.badge_status.config(text="ACTIVE", bg=self.ACCENT_HIGHLIGHT, fg="#FFFFFF")

    def _on_engine_update(self, state: dict):
        self.root.after(0, lambda: self._apply_state_update(state))

    def _apply_state_update(self, state: dict):
        peak = state["peak"]
        is_ducked = state["is_ducked"]
        status = state["status"]
        ramp_mult = state.get("ramp_multiplier", 1.0)
        time_rem = state.get("time_remaining_str", "")

        status_fg = self.TEXT_INK if is_ducked else self.TEXT_MUTED
        
        if self.engine.ramp_enabled and time_rem:
            status_text = f"{status} | Ramp: {time_rem}"
        else:
            status_text = status

        self.lbl_live_status.config(text=status_text, fg=status_fg)
        self._update_meter(peak, is_ducked)

    def _update_meter(self, peak: float, is_ducked: bool):
        self.canvas_meter.delete("all")
        w = self.canvas_meter.winfo_width()
        h = self.canvas_meter.winfo_height()
        if w <= 1:
            w = 340

        self.canvas_meter.create_rectangle(0, 0, w, h, fill="#E8E2D5", outline="")

        bar_w = int(w * min(1.0, peak))
        bar_color = self.BORDER_INK if is_ducked else "#888888"

        if bar_w > 0:
            self.canvas_meter.create_rectangle(0, 0, bar_w, h, fill=bar_color, outline="")

        thresh_x = int(w * self.engine.threshold)
        self.canvas_meter.create_line(thresh_x, 0, thresh_x, h, fill=self.GOLD_INDICATOR, width=2)


def main():
    root = tk.Tk()
    app = ADHDDuckerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
