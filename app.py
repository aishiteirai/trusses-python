import tkinter as tk
from tkinter import simpledialog, messagebox
import customtkinter as ctk  # Biblioteca moderna
import math
from models import Node, Member, Truss, Support, Load
from solver import TrussSolver

# --- Configurações Visuais Modernas ---
ctk.set_appearance_mode("System")  # "Light", "Dark" ou "System"
ctk.set_default_color_theme("blue")  # Tema de cores padrão

GRID_SIZE = 40
NODE_RADIUS = 5
SNAP_TOLERANCE = 15

class TrussApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Truss Solver - Modern UI")
        self.root.geometry("1100x700")

        # --- Estado da Aplicação ---
        self.mode = "SELECT"
        self.nodes = []
        self.members = []
        self.temp_node = None

        # --- Layout Principal (Grid) ---
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        # 1. Barra Lateral (Sidebar)
        self.sidebar = ctk.CTkFrame(root, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        # Título da Barra
        self.logo_label = ctk.CTkLabel(self.sidebar, text="FERRAMENTAS", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.pack(padx=20, pady=(20, 10))

        # Botões de Ferramentas
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

        # Separador e Ações
        ctk.CTkLabel(self.sidebar, text="AÇÕES", font=ctk.CTkFont(size=14)).pack(pady=(20, 5))

        self.btn_calc = ctk.CTkButton(self.sidebar, text="CALCULAR", command=self.calculate,
                                      fg_color="#2CC985", hover_color="#229D68",
                                      height=50, font=ctk.CTkFont(size=16, weight="bold"))
        self.btn_calc.pack(padx=20, pady=10)

        self.btn_clear = ctk.CTkButton(self.sidebar, text="Limpar Tudo", command=self.clear_all,
                                       fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"))
        self.btn_clear.pack(padx=20, pady=10)

        # Status Label
        self.lbl_status = ctk.CTkLabel(self.sidebar, text="Modo: Seleção", font=ctk.CTkFont(size=12))
        self.lbl_status.pack(side="bottom", pady=20)

        # 2. Canvas (Área de Desenho)
        # Usamos tk.Canvas normal pois ele é melhor para desenhar linhas/círculos complexos que o CTk
        self.canvas_frame = ctk.CTkFrame(root)
        self.canvas_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        self.canvas = tk.Canvas(self.canvas_frame, bg="white", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Eventos do Mouse
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<Motion>", self.on_mouse_move)

        # Desenhar Grid Inicial
        self.draw_grid()

    def set_mode(self, mode):
        self.mode = mode
        self.temp_node = None
        
        # Tradução simples para exibição
        map_names = {
            "NODE": "Adicionar Nós",
            "MEMBER": "Adicionar Barras",
            "SUPPORT": "Adicionar Apoios",
            "LOAD": "Adicionar Cargas",
            "SELECT": "Seleção"
        }
        display_text = map_names.get(mode, mode)
        self.lbl_status.configure(text=f"Modo Atual: {display_text}")
        self.redraw()

    def draw_grid(self):
        w = 2000
        h = 2000
        # Grid mais suave
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
                new_node = Node(id=new_id, x=x, y=y)
                self.nodes.append(new_node)
                self.redraw()

        elif self.mode == "MEMBER":
            if clicked_node:
                if self.temp_node is None:
                    self.temp_node = clicked_node
                    self.redraw()
                else:
                    if clicked_node != self.temp_node:
                        m = Member(
                            id=len(self.members) + 1,
                            start_node=self.temp_node,
                            end_node=clicked_node,
                            elastic_modulus=200e9,
                            area=0.005
                        )
                        self.members.append(m)
                        self.temp_node = None
                        self.redraw()

        elif self.mode == "SUPPORT":
            if clicked_node:
                tipo = simpledialog.askstring("Apoio", "Digite 'P' para Pino ou 'R' para Rolet:", parent=self.root)
                if tipo:
                    tipo = tipo.upper()
                    if tipo == 'P':
                        clicked_node.support = Support(restrain_x=True, restrain_y=True)
                    elif tipo == 'R':
                        clicked_node.support = Support(restrain_x=False, restrain_y=True)
                    self.redraw()

        elif self.mode == "LOAD":
            if clicked_node:
                mag = simpledialog.askfloat("Carga", "Magnitude da Força (N):", parent=self.root)
                ang = simpledialog.askfloat("Carga", "Ângulo (graus):", parent=self.root)
                if mag is not None and ang is not None:
                    clicked_node.load = Load(magnitude=mag, angle=ang)
                    self.redraw()

    def on_mouse_move(self, event):
        pass

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
            messagebox.showerror("Erro de Cálculo", str(e))

    def redraw(self, show_results=False):
        self.canvas.delete("all")
        self.draw_grid()

        # Desenhar Barras
        for m in self.members:
            color = "black"
            thickness = 2
            text = ""

            if show_results:
                if m.force < -1e-5:
                    color = "#E74C3C"  # Vermelho suave
                    thickness = 4
                    text = f"{abs(m.force):.1f} N (C)"
                elif m.force > 1e-5:
                    color = "#3498DB"  # Azul suave
                    thickness = 4
                    text = f"{m.force:.1f} N (T)"
                else:
                    color = "#95A5A6"
                    text = "0"

            x1, y1 = m.start_node.x, m.start_node.y
            x2, y2 = m.end_node.x, m.end_node.y
            self.canvas.create_line(x1, y1, x2, y2, fill=color, width=thickness, tags="member")

            if show_results:
                mx, my = (x1 + x2) / 2, (y1 + y2) / 2
                # Caixa de fundo para o texto ficar legível
                self.canvas.create_rectangle(mx-30, my-10, mx+30, my+10, fill="white", outline="")
                self.canvas.create_text(mx, my, text=text, fill=color, font=("Arial", 9, "bold"))

        # Desenhar Nós e Elementos
        for n in self.nodes:
            fill_col = "white"
            radius = NODE_RADIUS
            
            if n == self.temp_node: 
                fill_col = "#F1C40F"  # Amarelo destaque
                radius += 2

            # Desenha Apoio
            if n.support:
                sx, sy = n.x, n.y + radius + 5
                if n.support.restrain_x and n.support.restrain_y:
                    self.canvas.create_polygon(n.x, n.y, n.x - 10, n.y + 15, n.x + 10, n.y + 15, fill="#27AE60", outline="black")
                else:
                    self.canvas.create_oval(n.x - 10, n.y + 5, n.x + 10, n.y + 25, outline="#27AE60", width=2)

            # Desenha o Nó
            self.canvas.create_oval(n.x - radius, n.y - radius, n.x + radius, n.y + radius, fill=fill_col, outline="black", width=2)
            self.canvas.create_text(n.x + 15, n.y - 15, text=str(n.id), fill="#7F8C8D", font=("Arial", 8))

            # Desenha Carga
            if n.load:
                rad = math.radians(n.load.angle)
                arrow_len = 50
                dx = arrow_len * math.cos(rad)
                dy = arrow_len * math.sin(rad)
                self.canvas.create_line(n.x, n.y, n.x + dx, n.y + dy, arrow=tk.LAST, fill="#8E44AD", width=3)
                self.canvas.create_text(n.x + dx + 15, n.y + dy, text=f"{n.load.magnitude}N", fill="#8E44AD", font=("Arial", 10, "bold"))

            # Resultados das Reações
            if show_results and n.support:
                rx, ry = n.reaction_x, n.reaction_y
                label_y = n.y + 40
                if abs(rx) > 0.1:
                    self.canvas.create_text(n.x, label_y, text=f"Rx:{rx:.1f}", fill="#16A085", font=("Arial", 9))
                    label_y += 15
                if abs(ry) > 0.1:
                    self.canvas.create_text(n.x, label_y, text=f"Ry:{ry:.1f}", fill="#16A085", font=("Arial", 9))

if __name__ == "__main__":
    app = ctk.CTk()  # Usando CTk em vez de Tk
    gui = TrussApp(app)
    app.mainloop()