#!/usr/bin/env python
"""
7TV Paint Applier - DaVinci Resolve / Fusion plugin
=====================================================
A modern, sleek UI plugin to fetch 7TV paints and generate 
Text+ and Background nodes neatly grouped in DaVinci Resolve.

Created by Arsynator
GitHub: https://github.com/Arsynator
Twitch: https://twitch.tv/arsynatorlive

INSTALL:
Windows: %APPDATA%\\Blackmagic Design\\DaVinci Resolve\\Support\\Fusion\\Scripts\\Comp\\
macOS:   ~/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Comp/
Linux:   ~/.local/share/DaVinciResolve/Fusion/Scripts/Comp/
"""

import json
import sys
import math
import urllib.request
import urllib.error
import webbrowser
import tkinter as tk
from tkinter import ttk

# ---------------------------------------------------------------------------
# 7TV GraphQL Configuration
# ---------------------------------------------------------------------------
GQL_ENDPOINT = "https://7tv.io/v3/gql"

QUERY_SEARCH_USERS = """
query SearchUsers($query: String!) {
  users(query: $query) {
    id username display_name
    style { paint { id kind name } }
  }
}"""

QUERY_GET_COSMETICS = """
query GetCosmetics($list: [ObjectID!]) {
  cosmetics(list: $list) {
    paints {
      id kind name function color angle shape image_url repeat
      stops { at color }
      shadows { x_offset y_offset radius color }
    }
  }
}"""

def gql(query, variables=None):
    body = json.dumps({"query": query, "variables": variables or {}}).encode()
    req = urllib.request.Request(
        GQL_ENDPOINT, data=body,
        headers={"Content-Type": "application/json", "User-Agent": "7TVPaintApplier/8.0"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read()).get("data")
    except Exception as e:
        print(f"[7TV] Request failed: {e}")
        return None

# ---------------------------------------------------------------------------
# Data Helpers
# ---------------------------------------------------------------------------
def rgba_ints(n):
    if n is None: return 0, 0, 0, 0
    if n < 0: n += 2 ** 32
    return (n >> 24) & 0xFF, (n >> 16) & 0xFF, (n >> 8) & 0xFF, n & 0xFF

def dominant_hex(p):
    fn = (p.get("function") or "").upper()
    n = 0
    
    if fn in ("LINEAR_GRADIENT", "RADIAL_GRADIENT"):
        stops = p.get("stops") or []
        if stops:
            mid = min(stops, key=lambda s: abs(s.get("at", 0) - 0.5))
            n = mid.get("color") or 0
    else:
        n = p.get("color") or 0
        
    if n < 0: n += 2 ** 32
    r, g, b = (n >> 24) & 0xFF, (n >> 16) & 0xFF, (n >> 8) & 0xFF
    return f"#{r:02X}{g:02X}{b:02X}"

def fetch_paints(query):
    data = gql(QUERY_SEARCH_USERS, {"query": query})
    if not data: return []
    
    paint_ids, user_by_paint = [], {}
    for u in data.get("users") or []:
        pid = ((u.get("style") or {}).get("paint") or {}).get("id")
        if not pid: continue
        display = u.get("display_name") or u.get("username") or "?"
        if pid not in paint_ids: paint_ids.append(pid)
        user_by_paint.setdefault(pid, []).append(display)
        
    if not paint_ids: return []
    
    detail = gql(QUERY_GET_COSMETICS, {"list": paint_ids})
    if not detail: return []
    
    entries = []
    for p in (detail.get("cosmetics") or {}).get("paints") or []:
        for display in user_by_paint.get(p["id"], []):
            entries.append({"user": display, "paint": p})
    return entries

# ---------------------------------------------------------------------------
# Fusion Application Logic - Node Generator Method
# ---------------------------------------------------------------------------
def _get_current_comp():
    g = globals()
    c = g.get("comp") or g.get("composition")
    if c: return c
    try:
        resolve = g.get("resolve")
        if resolve: return resolve.Fusion().GetCurrentComp()
    except: pass
    return None

def apply_paint(entry, custom_message=" : your message here", enable_shadow=True):
    comp_obj = _get_current_comp()
    if not comp_obj:
        return False, "Error: No active Fusion composition found."

    paint = entry["paint"]
    user_name = entry["user"]
    fn = (paint.get("function") or "").upper()
    is_grad = fn in ("LINEAR_GRADIENT", "RADIAL_GRADIENT")
    
    comp_obj.StartUndo("Generate 7TV Paint Nodes")
    
    try:
        comp_obj.Execute("comp:SetActiveTool()")
        
        name_text = comp_obj.AddTool("TextPlus")
        name_text.SetInput("StyledText", user_name)
        
        flow = comp_obj.CurrentFrame.FlowView if hasattr(comp_obj, "CurrentFrame") else None
        bx, by = 0.0, 0.0
        if flow:
            pos = flow.GetPosTable(name_text)
            if pos:
                vals = list(pos.values())
                if len(vals) >= 2:
                    bx = float(vals[0])
                    by = float(vals[1])
        
        # --- PERFECT CENTERING MATH ---
        char_width = 0.026  # Accurately matches Resolve's default Open Sans font width
        name_len = max(len(user_name), 1)
        msg_str = custom_message
        msg_len = len(msg_str)
        
        # Shift Username left by exactly half the message length
        center_x = 0.5 - (msg_len * char_width / 2.0)
        center_y = 0.5
        
        name_text.SetInput("Center", [center_x, center_y])
        
        bg_node = comp_obj.AddTool("Background")
        if flow: flow.SetPos(bg_node, bx, by + 1.0)
        
        if is_grad:
            bg_node.SetInput("Type", "Gradient")
            
            # Gradient bounding box strictly covers the username width
            text_width = min(name_len * char_width, 0.9)
            text_height = 0.08 
            
            if fn == "RADIAL_GRADIENT":
                bg_node.SetInput("GradientType", "Radial")
                bg_node.SetInput("Start", [center_x, center_y])
                bg_node.SetInput("End", [center_x + (text_width / 2.0), center_y])
            else:
                bg_node.SetInput("GradientType", "Linear")
                angle_raw = paint.get("angle")
                angle = float(angle_raw) if angle_raw is not None else 90.0
                rad = math.radians(angle)
                
                dx = math.sin(rad) * (text_width / 2.0)
                dy = math.cos(rad) * (text_height / 2.0)
                
                if abs(dx) < 0.00001: dx = 0.00001
                if abs(dy) < 0.00001: dy = 0.00001
                
                bg_node.SetInput("Start", [center_x - dx, center_y - dy]) 
                bg_node.SetInput("End",   [center_x + dx, center_y + dy]) 
                
            # --- SUPERIOR TILING ENGINE ---
            stops_raw = paint.get("stops") or []
            
            max_seen = -999.0
            for s in stops_raw:
                at_val = float(s.get("at", 0))
                if at_val < max_seen:
                    s["at"] = max_seen
                else:
                    max_seen = at_val
                    s["at"] = at_val
                    
            if paint.get("repeat") and len(stops_raw) > 1:
                min_at = float(stops_raw[0].get("at", 0))
                max_at = float(stops_raw[-1].get("at", 0))
                span = max_at - min_at
                
                if span <= 0.001:
                    span = max_at if max_at > 0.001 else 1.0
                
                tiled = []
                for multiplier in range(-10, 10):
                    offset = multiplier * span
                    for s in stops_raw:
                        new_at = float(s.get("at", 0)) + offset
                        if -2.0 <= new_at <= 3.0:
                            tiled.append({"at": new_at, "color": s.get("color")})
                stops_raw = tiled
                
            stops = sorted(stops_raw, key=lambda s: float(s.get("at", 0)))
            colors_dict = {}
            used_positions = set()
            
            for s in stops:
                at_val = float(s.get("at", 0))
                while at_val in used_positions:
                    at_val += 0.00001
                used_positions.add(at_val)
                
                r, g, b, a = rgba_ints(s.get("color") or 0)
                colors_dict[at_val] = [r / 255.0, g / 255.0, b / 255.0, a / 255.0]

            if colors_dict:
                keys = list(colors_dict.keys())
                if 0.0 not in keys and not any(k < 0.0 for k in keys):
                    colors_dict[0.0] = colors_dict[min(keys)]
                if 1.0 not in keys and not any(k > 1.0 for k in keys):
                    colors_dict[1.0] = colors_dict[max(keys)]

            bg_node.SetInput("Gradient", colors_dict)
            
        else:
            bg_node.SetInput("Type", "Solid Color")
            r, g, b, a = rgba_ints(paint.get("color") or 0)
            bg_node.SetInput("TopLeftRed", r / 255.0)
            bg_node.SetInput("TopLeftGreen", g / 255.0)
            bg_node.SetInput("TopLeftBlue", b / 255.0)
            bg_node.SetInput("TopLeftAlpha", a / 255.0)

        bg_node.ConnectInput("EffectMask", name_text)
        
        msg_text = comp_obj.AddTool("TextPlus")
        msg_text.SetInput("StyledText", msg_str)
        if flow: flow.SetPos(msg_text, bx + 2.0, by)
        
        # Shift Message right by exactly half the username length
        msg_center_x = 0.5 + (name_len * char_width / 2.0)
        msg_text.SetInput("Center", [msg_center_x, center_y])
        
        # --- SHADOW ENGINE ---
        shadows_list = paint.get("shadows")
        merge_node = comp_obj.AddTool("Merge")
        
        if enable_shadow:
            shadow_node = comp_obj.AddTool("Shadow")
            if flow: flow.SetPos(shadow_node, bx, by + 2.0)
            if flow: flow.SetPos(merge_node, bx + 2.0, by + 2.0)
            
            shadow_node.ConnectInput("Input", bg_node)
            merge_node.ConnectInput("Background", msg_text)
            merge_node.ConnectInput("Foreground", shadow_node)
            
            if shadows_list and len(shadows_list) > 0:
                ds = shadows_list[0] 
                sr, sg, sb, sa = rgba_ints(ds.get("color") or 0)
                x_off = float(ds.get("x_offset") or 0) * 0.001
                y_off = float(ds.get("y_offset") or 0) * -0.001
                blur = float(ds.get("radius") or 0) * 0.002
            else:
                # Default drop shadow for readability if the paint doesn't have one
                sr, sg, sb, sa = 0, 0, 0, 255
                x_off, y_off = 0.002, -0.002
                blur = 0.005

            shadow_node.SetInput("Red", sr / 255.0)
            shadow_node.SetInput("Green", sg / 255.0)
            shadow_node.SetInput("Blue", sb / 255.0)
            shadow_node.SetInput("Alpha", sa / 255.0)
            shadow_node.SetInput("ShadowOffset", [0.5 + x_off, 0.5 + y_off])
            shadow_node.SetInput("Softness", blur)
            
            merge_y_offset = 2.0
        else:
            if flow: flow.SetPos(merge_node, bx + 2.0, by + 1.0)
            merge_node.ConnectInput("Background", msg_text)
            merge_node.ConnectInput("Foreground", bg_node)
            merge_y_offset = 1.0
            
        media_out = comp_obj.FindTool("MediaOut1")
        if not media_out:
            tools = comp_obj.GetToolList(False)
            if tools:
                for t in tools.values():
                    if getattr(t, "ID", None) == "MediaOut":
                        media_out = t
                        break
        
        if media_out:
            media_out.ConnectInput("Input", merge_node)
            if flow: flow.SetPos(media_out, bx + 3.0, by + merge_y_offset)
            msg_suffix = "and connected to MediaOut!"
        else:
            msg_suffix = "!"
            
        comp_obj.SetActiveTool(merge_node)
        
        comp_obj.EndUndo(True)
        return True, f"Success: Built grouped setup for '{paint.get('name', 'Unnamed')}' {msg_suffix}"
        
    except Exception as e:
        comp_obj.EndUndo(True)
        return False, f"Error: Failed to build setup ({e})"

# ---------------------------------------------------------------------------
# UI - Floating Dark Cards with Purple/Black Gradient
# ---------------------------------------------------------------------------
class DarkApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("7TV Paint Applier - by Arsynator")
        
        self.geometry("750x680")
        self.minsize(650, 620)
        
        self.bg_canvas = tk.Canvas(self, highlightthickness=0)
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        self.bind("<Configure>", self._draw_gradient)
        
        self.entries = []
        self._setup_styles()
        self._build_ui()

    def _draw_gradient(self, event=None):
        width = self.winfo_width()
        height = self.winfo_height()
        if width <= 1 or height <= 1: return
        self.bg_canvas.delete("gradient")
        
        r1, g1, b1 = 26, 11, 46   # #1A0B2E
        r2, g2, b2 = 5, 5, 5      # #050505
        
        steps = 40
        for i in range(steps):
            nr = int(r1 + (r2 - r1) * i / steps)
            ng = int(g1 + (g2 - g1) * i / steps)
            nb = int(b1 + (b2 - b1) * i / steps)
            color = f"#{nr:02x}{ng:02x}{nb:02x}"
            y0 = int(height * i / steps)
            y1 = int(height * (i + 1) / steps)
            self.bg_canvas.create_rectangle(0, y0, width, y1 + 1, fill=color, outline="", tags="gradient")
        self.bg_canvas.lower("all")

    def _setup_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        
        self.card_bg = "#130C1C" 
        fg_main = "#FAFAFA"
        fg_muted = "#A1A1AA"
        accent = "#9146FF" 
        accent_hover = "#A970FF"
        select_bg = "#3F3F46"
        
        style.configure(".", background=self.card_bg, foreground=fg_main, font=("Segoe UI", 10))
        style.configure("TLabel", background=self.card_bg, foreground=fg_main)
        
        style.configure("Header.TLabel", font=("Segoe UI", 18, "bold"), foreground="#FFFFFF")
        
        style.configure("TEntry", fieldbackground="#1E142B", foreground="#FFFFFF", borderwidth=0, padding=8)
        
        style.configure("TButton", background="#1E142B", foreground="#FFFFFF", borderwidth=0, padding=8, font=("Segoe UI", 10))
        style.map("TButton", background=[("active", select_bg), ("pressed", "#52525B")])
        
        style.configure("Apply.TButton", background=accent, font=("Segoe UI", 10, "bold"))
        style.map("Apply.TButton", background=[("active", accent_hover)])

        style.configure("Treeview", background=self.card_bg, fieldbackground=self.card_bg, foreground=fg_main, borderwidth=0, rowheight=30)
        style.configure("Treeview.Heading", background="#1F1133", foreground="#FFFFFF", borderwidth=0, font=("Segoe UI", 10, "bold"), padding=4)
        style.map("Treeview", background=[("selected", select_bg)], foreground=[("selected", "#FFFFFF")])

    def _build_ui(self):
        head_frame = tk.Frame(self, bg=self.card_bg, bd=0)
        head_frame.pack(fill="x", padx=20, pady=(20, 10))
        ttk.Label(head_frame, text="7TV Paint Applier", style="Header.TLabel").pack(side="left", padx=10, pady=10)

        search_frame = tk.Frame(self, bg=self.card_bg, bd=0)
        search_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        self.search_var = tk.StringVar()
        entry = ttk.Entry(search_frame, textvariable=self.search_var, font=("Segoe UI", 11))
        entry.pack(side="left", fill="x", expand=True, ipady=3, padx=(10, 5), pady=10)
        entry.bind("<Return>", lambda e: self.search())
        entry.focus_set()
        
        ttk.Button(search_frame, text="Search Username", command=self.search).pack(side="left", padx=(0, 10))

        tree_frame = tk.Frame(self, bg=self.card_bg, bd=0)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        self.tree = ttk.Treeview(tree_frame, columns=("user", "paint", "color"), show="headings", selectmode="browse")
        self.tree.heading("user", text="Streamer")
        self.tree.column("user", width=150, anchor="w")
        self.tree.heading("paint", text="Paint Name")
        self.tree.column("paint", width=250, anchor="w")
        self.tree.heading("color", text="Type / ID")
        self.tree.column("color", width=120, anchor="center")
        
        scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        
        self.tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scroll.pack(side="right", fill="y", padx=(0, 10), pady=10)
        
        self.tree.bind("<Double-1>", lambda e: self.handle_action())
        self.tree.bind("<<TreeviewSelect>>", lambda e: self.on_select())

        self.inspector_frame = tk.Frame(self, bg=self.card_bg, bd=0)
        self.inspector_frame.pack(fill="x", padx=20, pady=(0, 10))
        self.info_label = ttk.Label(self.inspector_frame, text="", font=("Segoe UI", 10, "italic"), foreground="#A1A1AA")
        self.info_label.pack(side="left", padx=10, pady=5)

        action_frame = tk.Frame(self, bg=self.card_bg, bd=0)
        action_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self.status_var = tk.StringVar(value="Search a 7TV user to get started.")
        ttk.Label(action_frame, textvariable=self.status_var, foreground="#A1A1AA").pack(side="left", fill="x", expand=True, padx=10, pady=10)
        
        self.apply_btn = ttk.Button(action_frame, text="Customize & Apply", style="Apply.TButton", command=self.handle_action)
        self.apply_btn.pack(side="right", padx=(5, 10), pady=10)
        
        ttk.Button(action_frame, text="Credits", command=self.show_credits).pack(side="right", padx=(10, 0), pady=10)

    def search(self):
        query = self.search_var.get().strip()
        if not query:
            self.status_var.set("Please enter a username.")
            return
            
        self.status_var.set(f"Searching for '{query}'...")
        self.info_label.config(text="")
        
        self.apply_btn.configure(text="Customize & Apply")
        self.update_idletasks()
        
        self.entries = fetch_paints(query)
        self.tree.delete(*self.tree.get_children())
        
        if not self.entries:
            self.status_var.set("No paints found for this user.")
            return
            
        for i, e in enumerate(self.entries):
            p = e["paint"]
            fn = (p.get("function") or "").upper()
            if p.get("image_url"):
                paint_type = "Image/Animated"
            elif fn in ("LINEAR_GRADIENT", "RADIAL_GRADIENT"):
                paint_type = f"Gradient ({dominant_hex(p)})"
            else:
                paint_type = f"Solid ({dominant_hex(p)})"
                
            self.tree.insert("", "end", iid=str(i), values=(e["user"], p.get("name", "Unnamed"), paint_type))
            
        self.status_var.set(f"Found {len(self.entries)} result(s). Select one to view details.")

    def on_select(self):
        sel = self.tree.selection()
        if not sel: return
        
        entry = self.entries[int(sel[0])]
        paint = entry["paint"]
        
        self.info_label.unbind("<Button-1>")
        self.info_label.configure(cursor="")
        
        img_url = paint.get("image_url")
        if img_url:
            self.info_label.configure(text=f"Animated Paint URL (Click to view): {img_url}", foreground="#38BDF8", cursor="hand2")
            self.info_label.bind("<Button-1>", lambda e, url=img_url: webbrowser.open_new(url))
            
            self.apply_btn.configure(text="Open Image")
        else:
            fn = (paint.get("function") or "").upper()
            if fn in ("LINEAR_GRADIENT", "RADIAL_GRADIENT"):
                self.info_label.configure(text=f"Gradient Colors: {dominant_hex(paint)} (Dominant)", foreground="#A1A1AA")
            else:
                self.info_label.configure(text=f"Solid Color Code: {dominant_hex(paint)}", foreground="#A1A1AA")
                
            self.apply_btn.configure(text="Customize & Apply")

    def handle_action(self):
        sel = self.tree.selection()
        if not sel:
            self.status_var.set("Please select a paint from the list first.")
            return
            
        idx = int(sel[0])
        entry = self.entries[idx]
        paint = entry["paint"]
        
        if paint.get("image_url"):
            self.status_var.set(f"Opening animated paint in browser...")
            webbrowser.open_new(paint.get("image_url"))
        else:
            self.show_customization(entry)

    def show_customization(self, entry):
        popup = tk.Toplevel(self)
        popup.title("Customize Layout")
        
        # --- INCREASED POPUP SIZE HERE ---
        popup.geometry("420x320") 
        popup.configure(bg=self.card_bg)
        popup.resizable(False, False)
        popup.grab_set() 
        
        # Keeps it perfectly centered based on the new size
        x = self.winfo_x() + (self.winfo_width() // 2) - 210
        y = self.winfo_y() + (self.winfo_height() // 2) - 160 
        popup.geometry(f"+{x}+{y}")
        
        ttk.Label(popup, text="Customize Layout", font=("Segoe UI", 14, "bold"), background=self.card_bg, foreground="#FFFFFF").pack(pady=(20, 10))
        
        msg_frame = tk.Frame(popup, bg=self.card_bg)
        msg_frame.pack(fill="x", padx=20, pady=10)
        ttk.Label(msg_frame, text="Chat Message:", background=self.card_bg, foreground="#A1A1AA").pack(anchor="w")
        
        msg_var = tk.StringVar(value=" : your message here")
        msg_entry = ttk.Entry(msg_frame, textvariable=msg_var, font=("Segoe UI", 11))
        msg_entry.pack(fill="x", pady=(5,0), ipady=3)
        msg_entry.focus_set()
        
        # Check if 7TV provides a native shadow
        has_shadow = bool(entry["paint"].get("shadows"))
        shadow_var = tk.BooleanVar(value=has_shadow)
        
        shadow_cb = tk.Checkbutton(
            popup, text=" Enable Drop Shadow / Glow", variable=shadow_var,
            bg=self.card_bg, fg="#FAFAFA", selectcolor="#1E142B",
            activebackground=self.card_bg, activeforeground="#FFFFFF",
            font=("Segoe UI", 10), cursor="hand2"
        )
        shadow_cb.pack(anchor="w", padx=20, pady=5)
        
        def on_generate():
            msg = msg_var.get()
            shadow = shadow_var.get()
            popup.destroy()
            self.execute_generation(entry, msg, shadow)
            
        btn_frame = tk.Frame(popup, bg=self.card_bg)
        btn_frame.pack(fill="x", padx=20, pady=(15, 20))
        ttk.Button(btn_frame, text="Generate Nodes", style="Apply.TButton", command=on_generate).pack(side="right")
        ttk.Button(btn_frame, text="Cancel", command=popup.destroy).pack(side="right", padx=10)

    def execute_generation(self, entry, msg, shadow):
        self.status_var.set("Generating nodes...")
        self.update_idletasks()
        
        ok, result_msg = apply_paint(entry, custom_message=msg, enable_shadow=shadow)
        self.status_var.set(result_msg)

    def show_credits(self):
        popup = tk.Toplevel(self)
        popup.title("Credits")
        popup.geometry("320x220")
        popup.configure(bg=self.card_bg)
        popup.resizable(False, False)
        
        x = self.winfo_x() + (self.winfo_width() // 2) - 160
        y = self.winfo_y() + (self.winfo_height() // 2) - 110
        popup.geometry(f"+{x}+{y}")
        
        ttk.Label(popup, text="7TV Paint Applier", font=("Segoe UI", 16, "bold"), background=self.card_bg, foreground="#FFFFFF").pack(pady=(25, 5))
        ttk.Label(popup, text="Created by Arsynator", font=("Segoe UI", 11), background=self.card_bg, foreground="#A1A1AA").pack(pady=(0, 15))
        
        gh_lbl = ttk.Label(popup, text="🔗 GitHub: Arsynator", font=("Segoe UI", 11, "bold"), foreground="#58A6FF", background=self.card_bg, cursor="hand2")
        gh_lbl.pack(pady=5)
        gh_lbl.bind("<Button-1>", lambda e: webbrowser.open_new("https://github.com/Arsynator"))
        
        tw_lbl = ttk.Label(popup, text="📺 Twitch: arsynatorlive", font=("Segoe UI", 11, "bold"), foreground="#9146FF", background=self.card_bg, cursor="hand2")
        tw_lbl.pack(pady=5)
        tw_lbl.bind("<Button-1>", lambda e: webbrowser.open_new("https://twitch.tv/arsynatorlive"))

if __name__ == "__main__":
    app = DarkApp()
    app.mainloop()