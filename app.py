import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import math
from models import Node, Member, Truss, Support, Load
from solver import TrussSolver

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

GRID_SIZE = 40
NODE_RADIUS = 5
SNAP_TOLERANCE = 15

class TrussApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Truss Solver")
        self.root.geometry("1100x700")

        self.mode = "SELECT"
        self.nodes = []
        self.members = []
        self.temp_node = None

        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkFrame(root, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.sidebar, text="FERRAMENTAS", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.pack(padx=20, pady=(20, 10))

        self.lbl_status = ctk.CTkLabel(self.sidebar, 
                                       text="Modo: Seleção", 
                                       font=ctk.CTkFont(size=14, weight="bold"),
                                       fg_color="#555555",
                                       text_color="white",
                                       corner_radius=10,
                                       height=35)
        self.lbl_status.pack(padx=20, pady=(0, 20), fill="x")

        self.btn_node = ctk.CTkButton(self.sidebar, text="Adicionar Nó", command=lambda: self.set_mode("NODE"),
                                      fg_color="#3B8ED0", hover_color="#36719F")
        self.btn_node.pack(padx=20, pady=10)

        self.btn_member = ctk.CTkButton(self.sidebar, text="Adicionar Barra", command=lambda: self.set_mode("MEMBER"),
                                        fg_color="#E19600", hover_color="#D08B00")
        self.btn_member.pack(padx=20, pady=10)

        self.btn_support = ctk.CTkButton(self.sidebar, text="Adicionar Apoio", command=lambda: self.set_mode("SUPPORT"),
                                         fg_color="#8D6F64", hover_color="#70554C")
        self.btn_support.pack(padx=20, pady=10)

        self.btn_load = ctk.CTkButton(self.sidebar, text="Adicionar Carga", command=lambda: self.set_mode("LOAD"),
                                      fg_color="#9C27B0", hover_color="#7B1FA2")
        self.btn_load.pack(padx=20, pady=10)

        ctk.CTkLabel(self.sidebar, text="AÇÕES", font=ctk.CTkFont(size=14)).pack(pady=(20, 5))

        self.btn_calc = ctk.CTkButton(self.sidebar, text="CALCULAR", command=self.calculate,
                                      fg_color="#2CC985", hover_color="#229D68",
                                      height=50, font=ctk.CTkFont(size=16, weight="bold"))
        self.btn_calc.pack(padx=20, pady=10)

        self.btn_clear = ctk.CTkButton(self.sidebar, text="Limpar Tudo", command=self.clear_all,
                                       fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"))
        self.btn_clear.pack(padx=20, pady=10)

        self.canvas_frame = ctk.CTkFrame(root)
        self.canvas_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        self.canvas = tk.Canvas(self.canvas_frame, bg="white", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind("<Button-1>", self.on_click)
        self.draw_grid()

    
    def open_support_dialog(self, node):
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Configurar Apoio")
        dialog.geometry("300x200")
        dialog.resizable(False, False)
        
        dialog.transient(self.root)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="Selecione o Tipo de Apoio:", font=("Arial", 14, "bold")).pack(pady=20)

        combo_tipo = ctk.CTkComboBox(dialog, values=["Pino (Fixo X e Y)", "Rolet (Fixo Y)"], width=200)
        combo_tipo.pack(pady=10)
        combo_tipo.set("Pino (Fixo X e Y)")

        def confirm():
            selection = combo_tipo.get()
            if "Pino" in selection:
                node.support = Support(restrain_x=True, restrain_y=True)
            else:
                node.support = Support(restrain_x=False, restrain_y=True)
            
            self.redraw()
            dialog.destroy()

        ctk.CTkButton(dialog, text="Confirmar", command=confirm, fg_color="#2CC985").pack(pady=20)

    def open_load_dialog(self, node):
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Adicionar Carga")
        dialog.geometry("300x320")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="Configurar Força", font=("Arial", 14, "bold")).pack(pady=15)

        ctk.CTkLabel(dialog, text="Magnitude (N):").pack(pady=(5,0))
        entry_mag = ctk.CTkEntry(dialog, placeholder_text="Ex: 1000")
        entry_mag.pack(pady=5)

        ctk.CTkLabel(dialog, text="Ângulo (Graus):").pack(pady=(5,0))
        entry_ang = ctk.CTkEntry(dialog, placeholder_text="Ex: 90 (Cima), 270 (Baixo)")
        entry_ang.pack(pady=5)

        def confirm():
            try:
                mag = float(entry_mag.get())
                ang = float(entry_ang.get())
                node.load = Load(magnitude=mag, angle=ang)
                self.redraw()
                dialog.destroy()
            except ValueError:
                entry_mag.configure(border_color="red")
                entry_ang.configure(border_color="red")

        ctk.CTkButton(dialog, text="Aplicar Carga", command=confirm, 
                      fg_color="#9C27B0", height=40, font=("Arial", 12, "bold")).pack(pady=20)

    def set_mode(self, mode):
        self.mode = mode
        self.temp_node = None
        
        mode_data = {
            "NODE":    ("Adicionar Nó", "#3B8ED0"),
            "MEMBER":  ("Adicionar Barra", "#E19600"), 
            "SUPPORT": ("Adicionar Apoio", "#8D6F64"), 
            "LOAD":    ("Adicionar Carga", "#9C27B0"), 
            "SELECT":  ("Seleção", "#555555")          
        }
        
        text, color = mode_data.get(mode, (mode, "#555555"))
        self.lbl_status.configure(text=text, fg_color=color)
        
        self.redraw()

    def draw_grid(self):
        w, h = 2000, 2000
        for i in range(0, w, GRID_SIZE):
            self.canvas.create_line([(i, 0), (i, h)], tag='grid', fill='#f0f0f0')
        for i in range(0, h, GRID_SIZE):
            self.canvas.create_line([(0, i), (w, i)], tag='grid', fill='#f0f0f0')

    def get_snapped_coords(self, event):
        x = round(event.x / GRID_SIZE) * GRID_SIZE
        y = round(event.y / GRID_SIZE) * GRID_SIZE
        return x, y

    def find_node_at(self, x, y):
        for n in self.nodes:
            dist = math.sqrt((n.x - x) ** 2 + (n.y - y) ** 2)
            if dist < SNAP_TOLERANCE:
                return n
        return None

    def on_click(self, event):
        x, y = self.get_snapped_coords(event)
        clicked_node = self.find_node_at(x, y)

        if self.mode == "NODE":
            if not clicked_node:
                new_id = len(self.nodes) + 1
                self.nodes.append(Node(id=new_id, x=x, y=y))
                self.redraw()

        elif self.mode == "MEMBER":
            if clicked_node:
                if self.temp_node is None:
                    self.temp_node = clicked_node
                    self.redraw()
                else:
                    if clicked_node != self.temp_node:
                        m = Member(id=len(self.members)+1, start_node=self.temp_node, end_node=clicked_node)
                        self.members.append(m)
                        self.temp_node = None
                        self.redraw()

        elif self.mode == "SUPPORT":
            if clicked_node:
                self.open_support_dialog(clicked_node)

        elif self.mode == "LOAD":
            if clicked_node:
                self.open_load_dialog(clicked_node)

    def clear_all(self):
        self.nodes = []
        self.members = []
        self.temp_node = None
        self.set_mode("SELECT")
        self.redraw()

    def calculate(self):
        if not self.nodes or not self.members:
            messagebox.showwarning("Aviso", "Desenhe uma estrutura primeiro!")
            return
        truss = Truss(nodes=self.nodes, members=self.members)
        try:
            TrussSolver.solve(truss)
            self.redraw(show_results=True)
            messagebox.showinfo("Sucesso", "Cálculo realizado com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def redraw(self, show_results=False):
        self.canvas.delete("all")
        self.draw_grid()

        for m in self.members:
            color, width, text = "black", 2, ""
            if show_results:
                if m.force < -1e-5: color, width, text = "#E74C3C", 4, f"{abs(m.force):.1f} N (C)"
                elif m.force > 1e-5: color, width, text = "#3498DB", 4, f"{m.force:.1f} N (T)"
                else: color, text = "#95A5A6", "0"
            
            x1, y1 = m.start_node.x, m.start_node.y
            x2, y2 = m.end_node.x, m.end_node.y
            self.canvas.create_line(x1, y1, x2, y2, fill=color, width=width)
            if show_results:
                mx, my = (x1+x2)/2, (y1+y2)/2
                self.canvas.create_rectangle(mx-30, my-10, mx+30, my+10, fill="white", outline="")
                self.canvas.create_text(mx, my, text=text, fill=color, font=("Arial", 9, "bold"))

        for n in self.nodes:
            fill = "#F1C40F" if n == self.temp_node else "white"
            
            if n.support:
                if n.support.restrain_x:
                    self.canvas.create_polygon(n.x, n.y, n.x-10, n.y+15, n.x+10, n.y+15, fill="#27AE60", outline="black")
                else: 
                    self.canvas.create_oval(n.x-10, n.y+5, n.x+10, n.y+25, outline="#27AE60", width=2)

            self.canvas.create_oval(n.x-NODE_RADIUS, n.y-NODE_RADIUS, n.x+NODE_RADIUS, n.y+NODE_RADIUS, fill=fill, outline="black")
            
            if n.load:
                rad = math.radians(n.load.angle)
                dx = 50 * math.cos(rad)
                dy = -50 * math.sin(rad) 
                self.canvas.create_line(n.x, n.y, n.x+dx, n.y+dy, arrow=tk.LAST, fill="#8E44AD", width=3)
                self.canvas.create_text(n.x+dx+15, n.y+dy, text=f"{n.load.magnitude}N", fill="#8E44AD", font=("Arial", 10, "bold"))

            if show_results and n.support:
                if abs(n.reaction_x) > 0.1: self.canvas.create_text(n.x, n.y+35, text=f"Rx:{n.reaction_x:.1f}", fill="#16A085")
                if abs(n.reaction_y) > 0.1: self.canvas.create_text(n.x, n.y+50, text=f"Ry:{n.reaction_y:.1f}", fill="#16A085")

if __name__ == "__main__":
    app = ctk.CTk()
    gui = TrussApp(app)
    app.mainloop()