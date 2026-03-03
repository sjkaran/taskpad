"""
╔═══════════════════════════════════════════════════════════════════╗
║              TASKPAD  — Desktop GUI v2.0                          ║
║      Frontend for github.com/sjkaran/taskpad                     ║
║                                                                   ║
║  ► Reads / writes  task_base.json  (same folder as this file)    ║
║  ► Mirrors the original CLI backend schema exactly               ║
║  ► Drop-in GUI replacement — no code changes needed in backend   ║
╚═══════════════════════════════════════════════════════════════════╝

Schema (task_base.json):
    {
      "YYYY-MM-DD": [
        {
          "id":          "<uuid>",
          "title":       "Buy groceries",
          "status":      "pending",
          "remarks":     "Get milk too",
          "date":        "YYYY-MM-DD",
          "created_at":  "YYYY-MM-DD HH:MM"
        }
      ]
    }

Install:  pip install customtkinter
Run:      python taskpad_gui.py
"""

import customtkinter as ctk
import tkinter as tk
import json, datetime, uuid, pathlib, copy

# ════════════════════════════════════════════════════════════════════
#  BACKEND BRIDGE  —  task_base.json read / write
# ════════════════════════════════════════════════════════════════════

DB_PATH = pathlib.Path(__file__).parent / "task_base.json"

TASK_DEFAULTS = {
    "id": "", "title": "", "status": "pending",
    "remarks": "", "date": "", "created_at": "",
}

def _today()    -> str: return datetime.date.today().strftime("%Y-%m-%d")
def _tomorrow() -> str: return (datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")

def _load() -> dict:
    if not DB_PATH.exists():
        DB_PATH.write_text(json.dumps({}, indent=2))
        return {}
    try:
        data = json.loads(DB_PATH.read_text())
        changed = False
        for tasks in data.values():
            for t in tasks:
                if not t.get("id"):
                    t["id"] = str(uuid.uuid4())
                    changed = True
        if changed:
            _save(data)
        return data
    except Exception:
        return {}

def _save(data: dict):
    DB_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False))

def _fmt_date(d: str) -> str:
    try:
        dt   = datetime.date.fromisoformat(d)
        diff = (dt - datetime.date.today()).days
        if diff == 0:  return "Today"
        if diff == 1:  return "Tomorrow"
        if diff == -1: return "Yesterday"
        if diff < 0:   return f"{abs(diff)}d overdue"
        if diff < 7:   return dt.strftime("%A")
        return dt.strftime("%d %b %Y")
    except Exception:
        return d

# ════════════════════════════════════════════════════════════════════
#  DESIGN SYSTEM
# ════════════════════════════════════════════════════════════════════

C = {
    "bg": "#07090F", "surface": "#0C1018", "card": "#101620",
    "card_h": "#151E30", "input": "#090D16", "sidebar": "#080C15",
    "border": "#FFFFFF", "border_a": "#2B78FF", "divider": "#0E1520",
    "accent": "#2B78FF", "accent_h": "#4A90FF", "accent_dim": "#102040",
    "done": "#0FD49A", "done_dim": "#082820",
    "pending": "#FFB020", "pending_dim": "#281C06",
    "overdue": "#FF3D5A", "overdue_dim": "#28080E",
    "tomorrow": "#A855F7", "tomorrow_dim": "#1C0830",
    "t1": "#DDE6F8", "t2": "#FDFDFD", "t3": "#FFFFFF",
}

F = {
    "brand": ("Georgia", 26, "bold"), "h1": ("Georgia", 16, "bold"),
    "h2": ("Georgia", 13, "bold"),    "body": ("Georgia", 12),
    "sm": ("Georgia", 11),            "xs": ("Georgia", 10),
    "mono": ("Courier New", 11),      "mono_s": ("Courier New", 10),
    "badge": ("Georgia", 10, "bold"), "num": ("Georgia", 24, "bold"),
}

# ════════════════════════════════════════════════════════════════════
#  REUSABLE COMPONENTS
# ════════════════════════════════════════════════════════════════════

class PadBtn(ctk.CTkButton):
    _S = {
        "primary": dict(fg_color=C["accent"],     hover_color=C["accent_h"],
                        text_color="#fff",          border_width=0),
        "ghost":   dict(fg_color="transparent",    hover_color=C["card_h"],
                        text_color=C["t2"],         border_width=1,
                        border_color=C["border"]),
        "danger":  dict(fg_color=C["overdue_dim"], hover_color="#380810",
                        text_color=C["overdue"],    border_width=1,
                        border_color=C["overdue"]),
        "success": dict(fg_color=C["done_dim"],    hover_color="#0E3020",
                        text_color=C["done"],       border_width=1,
                        border_color=C["done"]),
        "warn":    dict(fg_color=C["pending_dim"], hover_color="#36240A",
                        text_color=C["pending"],    border_width=1,
                        border_color=C["pending"]),
    }
    def __init__(self, master, variant="primary", **kw):
        merged = {"corner_radius": 7, "font": F["h2"], "cursor": "hand2",
                  **self._S.get(variant, self._S["primary"]), **kw}
        super().__init__(master, **merged)


class Pill(ctk.CTkLabel):
    def __init__(self, master, text, color, **kw):
        super().__init__(master, text=text, text_color=color,
                         fg_color=color + "22", corner_radius=5,
                         font=F["badge"], padx=8, pady=3, **kw)


class Hr(ctk.CTkFrame):
    def __init__(self, master, **kw):
        super().__init__(master, height=1, fg_color=C["divider"], **kw)


class FocusEntry(ctk.CTkEntry):
    def __init__(self, master, **kw):
        base = dict(fg_color=C["input"], border_color=C["border"],
                    text_color=C["t1"], font=F["body"],
                    border_width=1, corner_radius=7,
                    placeholder_text_color=C["t3"])
        base.update(kw)
        super().__init__(master, **base)
        self.bind("<FocusIn>",  lambda _: self.configure(border_color=C["border_a"]))
        self.bind("<FocusOut>", lambda _: self.configure(border_color=C["border"]))


class FocusTextbox(ctk.CTkTextbox):
    def __init__(self, master, **kw):
        base = dict(fg_color=C["input"], border_color=C["border"],
                    text_color=C["t1"], font=F["body"],
                    border_width=1, corner_radius=7)
        base.update(kw)
        super().__init__(master, **base)
        self.bind("<FocusIn>",  lambda _: self.configure(border_color=C["border_a"]))
        self.bind("<FocusOut>", lambda _: self.configure(border_color=C["border"]))


class StatTile(ctk.CTkFrame):
    def __init__(self, master, label, var, color, **kw):
        super().__init__(master, fg_color=C["card"], corner_radius=10,
                         border_width=1, border_color=C["border"], **kw)
        self.columnconfigure(0, weight=1)
        ctk.CTkLabel(self, text=label, text_color=C["t3"],
                     font=F["xs"]).grid(row=0, column=0, padx=14, pady=(12,2), sticky="w")
        ctk.CTkLabel(self, textvariable=var, text_color=color,
                     font=F["num"]).grid(row=1, column=0, padx=14, pady=(0,12), sticky="w")

# ════════════════════════════════════════════════════════════════════
#  TASK FORM DIALOG
# ════════════════════════════════════════════════════════════════════

class TaskDialog(ctk.CTkToplevel):
    def __init__(self, master, task: dict = None, on_save=None):
        super().__init__(master)
        self._task    = task
        self._on_save = on_save
        self._is_edit = task is not None

        self.title("Edit Task" if self._is_edit else "Assign New Task")
        self.geometry("540x510")
        self.resizable(False, False)
        self.configure(fg_color=C["surface"])
        self.grab_set(); self.lift(); self.focus()
        self._build()
        if self._is_edit:
            self._populate()
        self._center()

    def _center(self):
        self.update_idletasks()
        w, h = 540, 510
        px = self.master.winfo_rootx() + self.master.winfo_width()  // 2 - w // 2
        py = self.master.winfo_rooty() + self.master.winfo_height() // 2 - h // 2
        self.geometry(f"{w}x{h}+{px}+{py}")

    def _lbl(self, parent, text, row):
        ctk.CTkLabel(parent, text=text, text_color=C["t3"],
                     font=F["xs"]).grid(row=row, column=0, sticky="w", pady=(12,3))

    def _build(self):
        self.columnconfigure(0, weight=1)

        hdr = ctk.CTkFrame(self, fg_color=C["card"], corner_radius=0, height=68)
        hdr.grid(row=0, column=0, sticky="ew"); hdr.grid_propagate(False)
        hdr.columnconfigure(1, weight=1)
        ctk.CTkLabel(hdr, text="✎" if self._is_edit else "＋",
                     font=("Georgia", 22), text_color=C["accent"]).grid(row=0, column=0, padx=20)
        ctk.CTkLabel(hdr, text="Edit Task" if self._is_edit else "Assign New Task",
                     font=F["h1"], text_color=C["t1"]).grid(row=0, column=1, sticky="w")

        form = ctk.CTkFrame(self, fg_color="transparent")
        form.grid(row=1, column=0, sticky="nsew", padx=26, pady=18)
        form.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self._lbl(form, "TASK TITLE  *", 0)
        self._title_v = tk.StringVar()
        self._title_e = FocusEntry(form, textvariable=self._title_v,
                                    placeholder_text="What needs to be done?", height=44)
        self._title_e.grid(row=1, column=0, sticky="ew")

        self._lbl(form, "SCHEDULE FOR", 2)
        dr = ctk.CTkFrame(form, fg_color="transparent")
        dr.grid(row=3, column=0, sticky="ew"); dr.columnconfigure((0,1,2), weight=1)

        self._date_v    = tk.StringVar(value=_today())
        self._date_btns = []
        for ci, (lbl, val) in enumerate([("Today", _today()),
                                          ("Tomorrow", _tomorrow()),
                                          ("Custom…", "custom")]):
            b = ctk.CTkButton(dr, text=lbl, font=F["sm"], height=36,
                fg_color=C["accent_dim"] if ci==0 else C["card"],
                hover_color=C["accent_dim"],
                text_color=C["accent"] if ci==0 else C["t2"],
                corner_radius=6, cursor="hand2",
                command=lambda v=val, i=ci: self._pick_date(v, i))
            b.grid(row=0, column=ci, padx=3, sticky="ew")
            self._date_btns.append(b)

        self._custom_row = ctk.CTkFrame(form, fg_color="transparent")
        self._custom_e   = FocusEntry(self._custom_row, textvariable=self._date_v,
                                       placeholder_text="YYYY-MM-DD", height=40)
        self._custom_e.pack(fill="x")

        self._lbl(form, "REMARKS / NOTES", 5)
        self._remarks_tb = FocusTextbox(form, height=88)
        self._remarks_tb.grid(row=6, column=0, sticky="ew")

        if self._is_edit:
            self._lbl(form, "STATUS", 7)
            self._status_v = tk.StringVar(value="pending")
            sr = ctk.CTkFrame(form, fg_color="transparent")
            sr.grid(row=8, column=0, sticky="w")
            for s, col in [("pending", C["pending"]), ("completed", C["done"])]:
                ctk.CTkRadioButton(sr, text=s.capitalize(), variable=self._status_v,
                    value=s, font=F["body"], text_color=col,
                    fg_color=col, hover_color=col).pack(side="left", padx=(0,22))

        Hr(form).grid(row=9, column=0, sticky="ew", pady=14)
        br = ctk.CTkFrame(form, fg_color="transparent")
        br.grid(row=10, column=0, sticky="ew"); br.columnconfigure((0,1), weight=1)
        PadBtn(br, text="Cancel", variant="ghost",
               command=self.destroy).grid(row=0, column=0, padx=(0,8), sticky="ew")
        PadBtn(br, text="✓  Save Task", variant="primary",
               command=self._save).grid(row=0, column=1, padx=(8,0), sticky="ew")
        self._title_e.focus()

    def _pick_date(self, val: str, idx: int):
        for i, b in enumerate(self._date_btns):
            b.configure(fg_color=C["accent_dim"] if i==idx else C["card"],
                        text_color=C["accent"] if i==idx else C["t2"])
        if val == "custom":
            self._custom_row.grid(row=4, column=0, sticky="ew",
                                   in_=self._title_e.master, pady=(6,0))
        else:
            self._custom_row.grid_forget()
            self._date_v.set(val)

    def _populate(self):
        self._title_v.set(self._task.get("title",""))
        r = self._task.get("remarks","")
        if r: self._remarks_tb.insert("1.0", r)
        d = self._task.get("date", _today())
        self._date_v.set(d)
        if d == _today():       self._pick_date(_today(), 0)
        elif d == _tomorrow():  self._pick_date(_tomorrow(), 1)
        else:                   self._pick_date("custom", 2); self._date_v.set(d)
        if hasattr(self, "_status_v"):
            self._status_v.set(self._task.get("status","pending"))

    def _save(self):
        title = self._title_v.get().strip()
        if not title:
            self._title_e.configure(border_color=C["overdue"])
            self._title_e.after(1500, lambda: self._title_e.configure(border_color=C["border"]))
            return
        remarks = self._remarks_tb.get("1.0","end").strip()
        date    = self._date_v.get().strip() or _today()
        if self._is_edit:
            updated = copy.deepcopy(self._task)
            updated.update(title=title, remarks=remarks, date=date)
            if hasattr(self, "_status_v"): updated["status"] = self._status_v.get()
            result = updated
        else:
            result = {**TASK_DEFAULTS, "id": str(uuid.uuid4()), "title": title,
                      "remarks": remarks, "date": date, "status": "pending",
                      "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}
        if self._on_save: self._on_save(result)
        self.destroy()

# ════════════════════════════════════════════════════════════════════
#  CONFIRM DIALOG
# ════════════════════════════════════════════════════════════════════

class ConfirmDialog(ctk.CTkToplevel):
    def __init__(self, master, title, message, on_confirm, danger=True):
        super().__init__(master)
        self.title(title); self.geometry("420x205"); self.resizable(False,False)
        self.configure(fg_color=C["surface"]); self.grab_set(); self.lift()
        ctk.CTkLabel(self, text=title, font=F["h1"],
                     text_color=C["overdue"] if danger else C["t1"]).pack(pady=(26,6))
        ctk.CTkLabel(self, text=message, font=F["body"], text_color=C["t2"],
                     wraplength=360, justify="center").pack(pady=(0,18))
        br = ctk.CTkFrame(self, fg_color="transparent"); br.pack(fill="x", padx=30)
        br.columnconfigure((0,1), weight=1)
        PadBtn(br, text="Cancel", variant="ghost",
               command=self.destroy).grid(row=0, column=0, padx=(0,8), sticky="ew")
        PadBtn(br, text="Confirm", variant="danger" if danger else "success",
               command=lambda: [on_confirm(), self.destroy()]
               ).grid(row=0, column=1, padx=(8,0), sticky="ew")
        self.update_idletasks()
        px = master.winfo_rootx() + master.winfo_width()  // 2 - 210
        py = master.winfo_rooty() + master.winfo_height() // 2 - 102
        self.geometry(f"420x205+{px}+{py}")

# ════════════════════════════════════════════════════════════════════
#  TASK CARD
# ════════════════════════════════════════════════════════════════════

class TaskCard(ctk.CTkFrame):
    def __init__(self, master, task, on_toggle, on_edit, on_delete, **kw):
        super().__init__(master, fg_color=C["card"], corner_radius=10,
                         border_width=1, border_color=C["border"], **kw)
        self._task=task; self._on_toggle=on_toggle
        self._on_edit=on_edit; self._on_delete=on_delete
        self.bind("<Enter>", lambda _: self.configure(fg_color=C["card_h"],
                             border_color=C["border_a"]+"66"))
        self.bind("<Leave>", lambda _: self.configure(fg_color=C["card"],
                             border_color=C["border"]))
        self._build()

    def _build(self):
        self.columnconfigure(2, weight=1)
        t=self._task; done=t.get("status")=="completed"; date=t.get("date",_today())
        try: diff=(datetime.date.fromisoformat(date)-datetime.date.today()).days
        except: diff=0

        stripe=(C["done"] if done else C["overdue"] if diff<0
                else C["tomorrow"] if date==_tomorrow() else C["accent"])

        ctk.CTkFrame(self, width=5, corner_radius=3,
                     fg_color=stripe).grid(row=0,column=0,rowspan=3,
                                            padx=(10,0),pady=10,sticky="ns")
        self._chk_v=tk.BooleanVar(value=done)
        ctk.CTkCheckBox(self,text="",variable=self._chk_v,
            command=lambda: self._on_toggle(t["id"]),
            width=28,height=28,checkbox_width=24,checkbox_height=24,
            corner_radius=6,fg_color=C["done"],hover_color="#18C888",
            border_color=C["border_a"],checkmark_color="#fff"
        ).grid(row=0,column=1,rowspan=2,padx=(12,0),pady=14,sticky="w")

        tc=C["t2"] if done else C["t1"]
        tt=("✓  " if done else "")+t.get("title","(no title)")
        ctk.CTkLabel(self,text=tt,text_color=tc,font=F["h2"],anchor="w"
                     ).grid(row=0,column=2,padx=(12,6),pady=(14,2),sticky="ew")

        meta=ctk.CTkFrame(self,fg_color="transparent")
        meta.grid(row=1,column=2,padx=(12,6),pady=(0,10),sticky="w")
        dl=_fmt_date(date)
        dc=(C["done"] if done else C["overdue"] if diff<0
            else C["tomorrow"] if date==_tomorrow() else C["accent"])
        Pill(meta,f" ◷  {dl} ",dc).pack(side="left",padx=(0,6))
        Pill(meta,f" {'✓ Done' if done else '○ Pending'} ",
             C["done"] if done else C["pending"]).pack(side="left",padx=(0,6))
        if t.get("created_at"):
            ctk.CTkLabel(meta,text=f"Added {t['created_at'][:10]}",
                         text_color=C["t3"],font=F["xs"]).pack(side="left")

        if t.get("remarks"):
            r=t["remarks"]; exc=(r[:95]+"…") if len(r)>95 else r
            ctk.CTkLabel(self,text=exc,text_color=C["t2"],font=F["sm"],
                         anchor="w",wraplength=520,justify="left"
                         ).grid(row=2,column=2,padx=(12,6),pady=(0,12),sticky="w")

        acts=ctk.CTkFrame(self,fg_color="transparent")
        acts.grid(row=0,column=3,rowspan=3,padx=(4,14),pady=10,sticky="ne")
        PadBtn(acts,text="✎ Edit",variant="ghost",width=86,height=34,
               command=lambda: self._on_edit(t)).pack(pady=(0,6))
        PadBtn(acts,text="✕ Del", variant="danger",width=86,height=34,
               command=lambda: self._on_delete(t["id"])).pack()

# ════════════════════════════════════════════════════════════════════
#  MAIN APPLICATION
# ════════════════════════════════════════════════════════════════════

class TaskPadApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        self._db=_load(); self._filter="all"; self._search=""
        self._date_frames: dict[str,ctk.CTkFrame]={}
        self._svars={k:tk.StringVar(value="0")
                     for k in ("total","today","tomorrow","pending","done")}
        self._setup_window(); self._build(); self._refresh(); self._tick()

    def _setup_window(self):
        self.title("TaskPad"); self.geometry("1320x820"); self.minsize(1060,640)
        self.configure(fg_color=C["bg"])
        self.columnconfigure(0,weight=0); self.columnconfigure(1,weight=1)
        self.rowconfigure(0,weight=1)

    def _build(self): self._build_sidebar(); self._build_main()

    def _build_sidebar(self):
        sb=ctk.CTkFrame(self,width=278,fg_color=C["sidebar"],corner_radius=0)
        sb.grid(row=0,column=0,sticky="nsew"); sb.grid_propagate(False)
        sb.columnconfigure(0,weight=1); sb.rowconfigure(7,weight=1)

        logo=ctk.CTkFrame(sb,fg_color=C["card"],corner_radius=0,height=88)
        logo.grid(row=0,column=0,sticky="ew"); logo.grid_propagate(False)
        logo.columnconfigure(0,weight=1)
        ctk.CTkLabel(logo,text="🗒  TaskPad",font=F["brand"],text_color=C["accent"]
                     ).place(relx=0.5,rely=0.42,anchor="center")
        ctk.CTkLabel(logo,text="Minimal · Offline · Reliable",font=F["xs"],text_color=C["t3"]
                     ).place(relx=0.5,rely=0.80,anchor="center")
        Hr(sb).grid(row=1,column=0,sticky="ew")

        self._clock_v=tk.StringVar()
        ctk.CTkLabel(sb,textvariable=self._clock_v,font=F["mono_s"],text_color=C["t3"]
                     ).grid(row=2,column=0,padx=20,pady=(12,4),sticky="w")

        sg=ctk.CTkFrame(sb,fg_color="transparent")
        sg.grid(row=3,column=0,sticky="ew",padx=12,pady=(0,8))
        sg.columnconfigure((0,1),weight=1)
        for (lbl,key,col,r,c) in [("TOTAL","total",C["t1"],0,0),
                                    ("TODAY","today",C["accent"],0,1),
                                    ("TOMORROW","tomorrow",C["tomorrow"],1,0),
                                    ("PENDING","pending",C["pending"],1,1)]:
            StatTile(sg,lbl,self._svars[key],col).grid(row=r,column=c,padx=4,pady=4,sticky="ew")

        Hr(sb).grid(row=4,column=0,sticky="ew",pady=6)
        ctk.CTkLabel(sb,text="VIEW",text_color=C["t3"],font=F["xs"]
                     ).grid(row=5,column=0,padx=20,pady=(4,6),sticky="w")

        nav=ctk.CTkFrame(sb,fg_color="transparent")
        nav.grid(row=6,column=0,sticky="ew",padx=10); nav.columnconfigure(0,weight=1)
        self._nav_btns={}
        for key,lbl,col in [("all","⊞  All Tasks",C["t1"]),
                              ("today","◷  Today",C["accent"]),
                              ("tomorrow","◈  Tomorrow",C["tomorrow"]),
                              ("pending","○  Pending",C["pending"]),
                              ("completed","✓  Completed",C["done"])]:
            b=ctk.CTkButton(nav,text=lbl,font=F["body"],height=38,
                fg_color="transparent",hover_color=C["card_h"],
                text_color=col,corner_radius=7,anchor="w",cursor="hand2",
                command=lambda k=key: self._set_filter(k))
            b.grid(row=len(self._nav_btns),column=0,sticky="ew",pady=2)
            self._nav_btns[key]=b
        self._highlight_nav("all")

        sb.rowconfigure(7,weight=1)
        Hr(sb).grid(row=8,column=0,sticky="ew")
        bot=ctk.CTkFrame(sb,fg_color="transparent")
        bot.grid(row=9,column=0,sticky="ew",padx=12,pady=12); bot.columnconfigure(0,weight=1)
        PadBtn(bot,text="⊘  Clear Completed",variant="warn",height=36,font=F["sm"],
               command=self._clear_completed).grid(row=0,column=0,sticky="ew",pady=(0,6))
        PadBtn(bot,text="⚠  Clear All Tasks",variant="danger",height=36,font=F["sm"],
               command=self._clear_all).grid(row=1,column=0,sticky="ew")

    def _build_main(self):
        main=ctk.CTkFrame(self,fg_color="transparent",corner_radius=0)
        main.grid(row=0,column=1,sticky="nsew")
        main.columnconfigure(0,weight=1); main.rowconfigure(3,weight=1)

        tb=ctk.CTkFrame(main,height=86,fg_color=C["card"],corner_radius=0)
        tb.grid(row=0,column=0,sticky="ew"); tb.grid_propagate(False); tb.columnconfigure(1,weight=1)
        ctk.CTkLabel(tb,text="Task Board",font=F["h1"],text_color=C["t1"]
                     ).grid(row=0,column=0,padx=28,pady=28)

        sf=ctk.CTkFrame(tb,fg_color=C["input"],corner_radius=8,border_width=1,border_color=C["border"])
        sf.grid(row=0,column=1,padx=20,pady=22,sticky="ew"); sf.columnconfigure(1,weight=1)
        ctk.CTkLabel(sf,text="⌕",text_color=C["t2"],font=("Georgia",18)
                     ).grid(row=0,column=0,padx=(10,6),pady=6)
        self._search_v=tk.StringVar()
        self._search_v.trace_add("write",lambda *_: self._on_search(self._search_v.get()))
        ctk.CTkEntry(sf,textvariable=self._search_v,placeholder_text="Search tasks…",
                     fg_color="transparent",border_width=0,text_color=C["t1"],font=F["body"]
                     ).grid(row=0,column=1,sticky="ew",padx=(0,10),pady=6)

        PadBtn(tb,text="＋  Assign Task",variant="primary",width=152,height=42,
               command=self._open_assign).grid(row=0,column=2,padx=(0,24))
        Hr(main).grid(row=1,column=0,sticky="ew")

        self._tab_row=ctk.CTkFrame(main,height=50,fg_color=C["surface"],corner_radius=0)
        self._tab_row.grid(row=2,column=0,sticky="ew"); self._tab_row.grid_propagate(False)

        self._scroll=ctk.CTkScrollableFrame(main,fg_color=C["bg"],
            scrollbar_button_color=C["border"],scrollbar_button_hover_color=C["accent"])
        self._scroll.grid(row=3,column=0,sticky="nsew"); self._scroll.columnconfigure(0,weight=1)

        sbar=ctk.CTkFrame(main,height=28,fg_color=C["sidebar"],corner_radius=0)
        sbar.grid(row=4,column=0,sticky="ew"); sbar.grid_propagate(False)
        self._status_v=tk.StringVar(value="Ready")
        self._filter_v=tk.StringVar(value="")
        ctk.CTkLabel(sbar,textvariable=self._status_v,font=F["mono_s"],text_color=C["t3"]
                     ).pack(side="left",padx=16,pady=4)
        ctk.CTkLabel(sbar,textvariable=self._filter_v,font=F["mono_s"],text_color=C["accent"]
                     ).pack(side="right",padx=16,pady=4)

    def _refresh(self):
        tasks=self._filtered_tasks()
        for w in self._scroll.winfo_children(): w.destroy()
        for w in self._tab_row.winfo_children(): w.destroy()
        self._date_frames.clear()

        if not tasks:
            ctk.CTkLabel(self._scroll,
                text="🗒\n\nNo tasks here.\nPress  ＋ Assign Task  to get started.",
                text_color=C["t3"],font=F["body"],justify="center"
            ).pack(expand=True,pady=110)
            self._status_v.set("0 tasks"); self._update_stats(); return

        groups={}
        for t in tasks:
            d=t.get("date",_today()); groups.setdefault(d,[]).append(t)
        sorted_dates=sorted(groups.keys())

        ctk.CTkButton(self._tab_row,text="All Dates",font=F["sm"],height=50,
            fg_color=C["accent_dim"],hover_color=C["accent_dim"],
            text_color=C["accent"],corner_radius=0,border_width=0,
            command=lambda:None).pack(side="left",padx=(4,2))

        for d in sorted_dates:
            try: diff=(datetime.date.fromisoformat(d)-datetime.date.today()).days
            except: diff=0
            col=C["overdue"] if diff<0 else C["tomorrow"] if d==_tomorrow() else C["accent"]
            ctk.CTkButton(self._tab_row,text=f"{_fmt_date(d)}  ·  {len(groups[d])}",
                font=F["sm"],height=50,fg_color="transparent",hover_color=C["card_h"],
                text_color=col,corner_radius=0,border_width=0,
                command=lambda dt=d: self._jump_to_date(dt)).pack(side="left",padx=2)

        row=0
        for date in sorted_dates:
            g=groups[date]; lbl=_fmt_date(date)
            try: diff=(datetime.date.fromisoformat(date)-datetime.date.today()).days
            except: diff=0
            hc=C["overdue"] if diff<0 else C["tomorrow"] if date==_tomorrow() else C["accent"]

            sh=ctk.CTkFrame(self._scroll,fg_color="transparent")
            sh.grid(row=row,column=0,sticky="ew",padx=16,pady=(18,4)); sh.columnconfigure(1,weight=1)
            ctk.CTkLabel(sh,text=lbl,font=F["h1"],text_color=hc).grid(row=0,column=0,padx=(0,10))
            ctk.CTkLabel(sh,text=date,font=F["mono_s"],text_color=C["t3"]).grid(row=0,column=1,sticky="w")
            ctk.CTkLabel(sh,text=f"{len(g)} task{'s' if len(g)!=1 else ''}",
                         text_color=C["t2"],font=F["sm"]).grid(row=0,column=2)
            Hr(self._scroll).grid(row=row+1,column=0,sticky="ew",padx=16,pady=(0,6))
            self._date_frames[date]=sh; row+=2

            for t in g:
                TaskCard(self._scroll,t,
                    on_toggle=self._toggle_task,
                    on_edit=self._open_edit,
                    on_delete=self._delete_task,
                ).grid(row=row,column=0,sticky="ew",padx=16,pady=4); row+=1

        n=len(tasks); self._status_v.set(f"{n} task{'s' if n!=1 else ''} shown")
        self._update_stats()

    def _filtered_tasks(self):
        all_tasks=[{**t,"date":t.get("date",dk)}
                   for dk,tasks in self._db.items() for t in tasks]
        f=self._filter
        if f=="today":     all_tasks=[t for t in all_tasks if t.get("date")==_today()]
        elif f=="tomorrow":all_tasks=[t for t in all_tasks if t.get("date")==_tomorrow()]
        elif f=="pending": all_tasks=[t for t in all_tasks if t.get("status")=="pending"]
        elif f=="completed":all_tasks=[t for t in all_tasks if t.get("status")=="completed"]
        if self._search:
            q=self._search.lower()
            all_tasks=[t for t in all_tasks
                       if q in t.get("title","").lower() or q in t.get("remarks","").lower()]
        all_tasks.sort(key=lambda t:(t.get("date",""),0 if t.get("status")=="pending" else 1))
        return all_tasks

    def _update_stats(self):
        all_tasks=[t for tasks in self._db.values() for t in tasks]
        self._svars["total"].set(str(len(all_tasks)))
        self._svars["today"].set(str(sum(1 for t in all_tasks if t.get("date")==_today())))
        self._svars["tomorrow"].set(str(sum(1 for t in all_tasks if t.get("date")==_tomorrow())))
        self._svars["pending"].set(str(sum(1 for t in all_tasks if t.get("status")=="pending")))
        self._svars["done"].set(str(sum(1 for t in all_tasks if t.get("status")=="completed")))

    def _find_task(self,task_id):
        for dk,tasks in self._db.items():
            for i,t in enumerate(tasks):
                if t.get("id")==task_id: return dk,i,t
        return None,None,None

    def _persist(self): _save(self._db)

    def _toggle_task(self,task_id):
        dk,idx,t=self._find_task(task_id)
        if t is None: return
        t["status"]="completed" if t["status"]=="pending" else "pending"
        if t["status"]=="completed":
            t["completed_at"]=datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        else: t.pop("completed_at",None)
        self._persist(); self._refresh(); self._flash(f"Marked {t['status']}.")

    def _open_assign(self):  TaskDialog(self,on_save=self._save_new_task)
    def _save_new_task(self,task):
        date=task.get("date",_today()); self._db.setdefault(date,[]).append(task)
        self._persist(); self._refresh(); self._flash(f"'{task['title']}' assigned.")

    def _open_edit(self,task): TaskDialog(self,task=task,on_save=self._save_edited_task)
    def _save_edited_task(self,updated):
        dk,idx,_=self._find_task(updated["id"])
        if dk is None: return
        new_date=updated.get("date",dk)
        self._db[dk]=[t for t in self._db[dk] if t.get("id")!=updated["id"]]
        if not self._db[dk]: del self._db[dk]
        self._db.setdefault(new_date,[]).append(updated)
        self._persist(); self._refresh(); self._flash(f"'{updated['title']}' updated.")

    def _delete_task(self,task_id):
        _,_,t=self._find_task(task_id)
        if t is None: return
        ConfirmDialog(self,"Delete Task",
            f"Delete \"{t['title']}\"?\nThis cannot be undone.",
            on_confirm=lambda: self._confirm_delete(task_id))

    def _confirm_delete(self,task_id):
        dk,_,_=self._find_task(task_id)
        if dk is None: return
        self._db[dk]=[t for t in self._db[dk] if t.get("id")!=task_id]
        if not self._db[dk]: del self._db[dk]
        self._persist(); self._refresh(); self._flash("Task deleted.")

    def _clear_completed(self):
        n=sum(1 for tasks in self._db.values() for t in tasks if t.get("status")=="completed")
        if n==0: self._flash("No completed tasks to clear."); return
        ConfirmDialog(self,"Clear Completed",f"Remove all {n} completed task(s)?",
            on_confirm=self._confirm_clear_completed,danger=False)

    def _confirm_clear_completed(self):
        for dk in list(self._db.keys()):
            self._db[dk]=[t for t in self._db[dk] if t.get("status")!="completed"]
            if not self._db[dk]: del self._db[dk]
        self._persist(); self._refresh(); self._flash("Completed tasks cleared.")

    def _clear_all(self):
        total=sum(len(v) for v in self._db.values())
        if total==0: self._flash("Nothing to clear."); return
        ConfirmDialog(self,"⚠  Clear ALL Tasks",
            f"Permanently delete all {total} task(s)?",
            on_confirm=self._confirm_clear_all)

    def _confirm_clear_all(self):
        self._db.clear(); self._persist(); self._refresh(); self._flash("All tasks cleared.")

    def _set_filter(self,key):
        self._filter=key; self._highlight_nav(key)
        names={"all":"All","today":"Today","tomorrow":"Tomorrow",
               "pending":"Pending","completed":"Completed"}
        self._filter_v.set(names.get(key,"")); self._refresh()

    def _on_search(self,q): self._search=q; self._refresh()

    def _jump_to_date(self,date):
        frame=self._date_frames.get(date)
        if frame:
            try:
                canvas=self._scroll._parent_canvas
                canvas.update_idletasks()
                y=frame.winfo_y(); total=self._scroll.winfo_height()
                canvas.yview_moveto(y/max(total*4,1))
            except Exception: pass

    def _highlight_nav(self,active):
        cols={"all":C["t1"],"today":C["accent"],"tomorrow":C["tomorrow"],
              "pending":C["pending"],"completed":C["done"]}
        for k,b in self._nav_btns.items():
            b.configure(fg_color=C["accent_dim"] if k==active else "transparent",
                        text_color=C["accent"] if k==active else cols.get(k,C["t2"]))

    def _tick(self):
        self._clock_v.set(datetime.datetime.now().strftime("%a %d %b %Y     %H:%M:%S"))
        self.after(1000,self._tick)

    def _flash(self,msg,ms=3000):
        self._status_v.set(f"●  {msg}")
        self.after(ms,lambda: self._status_v.set("Ready"))

# ════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    TaskPadApp().mainloop()
