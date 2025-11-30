import tkinter as tk
from tkinter import simpledialog, messagebox
import math
from models import Node, Member, Truss, Support, Load
from solver import TrussSolver

# Configurações Visuais
GRID_SIZE = 40  # Tamanho do quadrado do grid em pixels
NODE_RADIUS = 5
SNAP_TOLERANCE = 15


class TrussApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Truss Solver - Estilo MDSolids")
        self.root.geometry("1000x700")

        # --- Estado da Aplicação ---
        self.mode = "SELECT"  # Modos: SELECT, NODE, MEMBER, SUPPORT, LOAD
        self.nodes = []  # Lista de objetos Node (UI + Model)
        self.members = []  # Lista de objetos Member (UI + Model)

        self.temp_node = None  # Para guardar o primeiro nó ao criar uma barra

        # --- Layout Principal ---
        # Toolbar
        self.toolbar = tk.Frame(root, bg="#ddd", height=40)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

        # Botões
        self.btn_node = tk.Button(self.toolbar, text="Adicionar Nó", command=lambda: self.set_mode("NODE"))
        self.btn_node.pack(side=tk.LEFT, padx=5, pady=5)

        self.btn_member = tk.Button(self.toolbar, text="Adicionar Barra", command=lambda: self.set_mode("MEMBER"))
        self.btn_member.pack(side=tk.LEFT, padx=5, pady=5)

        self.btn_support = tk.Button(self.toolbar, text="Adicionar Apoio", command=lambda: self.set_mode("SUPPORT"))
        self.btn_support.pack(side=tk.LEFT, padx=5, pady=5)

        self.btn_load = tk.Button(self.toolbar, text="Adicionar Carga", command=lambda: self.set_mode("LOAD"))
        self.btn_load.pack(side=tk.LEFT, padx=5, pady=5)

        self.btn_calc = tk.Button(self.toolbar, text="CALCULAR", bg="#4CAF50", fg="white", command=self.calculate)
        self.btn_calc.pack(side=tk.RIGHT, padx=20, pady=5)

        self.btn_clear = tk.Button(self.toolbar, text="Limpar Tudo", command=self.clear_all)
        self.btn_clear.pack(side=tk.RIGHT, padx=5)

        self.lbl_status = tk.Label(self.toolbar, text="Modo: Seleção", bg="#ddd")
        self.lbl_status.pack(side=tk.LEFT, padx=20)

        # Canvas (Área de Desenho)
        self.canvas = tk.Canvas(root, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Eventos do Mouse
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<Motion>", self.on_mouse_move)

        # Desenhar Grid Inicial
        self.draw_grid()

    def set_mode(self, mode):
        self.mode = mode
        self.temp_node = None
        self.lbl_status.config(text=f"Modo: {mode}")
        self.redraw()

    def draw_grid(self):
        w = 2000  # Tamanho arbitrário grande
        h = 2000
        for i in range(0, w, GRID_SIZE):
            self.canvas.create_line([(i, 0), (i, h)], tag='grid', fill='#eee')
        for i in range(0, h, GRID_SIZE):
            self.canvas.create_line([(0, i), (w, i)], tag='grid', fill='#eee')

    def get_snapped_coords(self, event):
        # Arredonda a posição do mouse para o grid mais próximo
        x = round(event.x / GRID_SIZE) * GRID_SIZE
        y = round(event.y / GRID_SIZE) * GRID_SIZE
        return x, y

    def find_node_at(self, x, y):
        # Verifica se clicou perto de um nó existente
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
                # Cria novo nó
                new_id = len(self.nodes) + 1
                # Nota: Na interface Y cresce para baixo, na engenharia para cima.
                # Vamos manter visual por enquanto e tratar Y no solver se necessário.
                new_node = Node(id=new_id, x=x, y=y)
                self.nodes.append(new_node)
                self.redraw()

        elif self.mode == "MEMBER":
            if clicked_node:
                if self.temp_node is None:
                    # Selecionou o primeiro nó
                    self.temp_node = clicked_node
                    self.redraw()  # Para mostrar destaque
                else:
                    # Selecionou o segundo nó -> criar barra
                    if clicked_node != self.temp_node:
                        # Propriedades Padrão (Aço)
                        m = Member(
                            id=len(self.members) + 1,
                            start_node=self.temp_node,
                            end_node=clicked_node,
                            elastic_modulus=200e9,  # 200 GPa
                            area=0.005  # Padrão arbitrário
                        )
                        self.members.append(m)
                        self.temp_node = None
                        self.redraw()

        elif self.mode == "SUPPORT":
            if clicked_node:
                # Pergunta tipo de apoio
                tipo = simpledialog.askstring("Apoio",
                                              "Digite 'P' para Pino (X e Y presos) ou 'R' para Rolet (apenas Y preso):")
                if tipo:
                    tipo = tipo.upper()
                    if tipo == 'P':
                        clicked_node.support = Support(restrain_x=True, restrain_y=True)
                    elif tipo == 'R':
                        clicked_node.support = Support(restrain_x=False, restrain_y=True)
                    self.redraw()

        elif self.mode == "LOAD":
            if clicked_node:
                mag = simpledialog.askfloat("Carga", "Magnitude da Força (N):")
                ang = simpledialog.askfloat("Carga", "Ângulo (graus, 0=Direita, 90=Baixo, 270=Cima):")
                if mag is not None and ang is not None:
                    clicked_node.load = Load(magnitude=mag, angle=ang)
                    self.redraw()

    def on_mouse_move(self, event):
        # Apenas para feedback visual se quisesse desenhar linha "fantasma"
        pass

    def clear_all(self):
        self.nodes = []
        self.members = []
        self.temp_node = None
        self.redraw()

    def calculate(self):
        if not self.nodes or not self.members:
            messagebox.showwarning("Erro", "Desenhe uma estrutura primeiro!")
            return

        # Monta a estrutura
        truss = Truss(nodes=self.nodes, members=self.members)

        try:
            # CHAMA O SOLVER QUE CRIAMOS
            TrussSolver.solve(truss)

            # Atualiza a tela com resultados
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
                # Lógica de Cores MDSolids: Vermelho=Compressão, Azul=Tração
                if m.force < -1e-5:  # Compressão
                    color = "red"
                    thickness = 3
                    text = f"{abs(m.force):.1f} N (C)"
                elif m.force > 1e-5:  # Tração
                    color = "blue"
                    thickness = 3
                    text = f"{m.force:.1f} N (T)"
                else:
                    color = "#555"  # Zero force
                    text = "0"

            # Linha da barra
            x1, y1 = m.start_node.x, m.start_node.y
            x2, y2 = m.end_node.x, m.end_node.y
            self.canvas.create_line(x1, y1, x2, y2, fill=color, width=thickness, tags="member")

            # Texto da força no meio da barra
            if show_results:
                mx, my = (x1 + x2) / 2, (y1 + y2) / 2
                self.canvas.create_text(mx, my - 10, text=text, fill=color, font=("Arial", 10, "bold"))

        # Desenhar Nós e Apoios
        for n in self.nodes:
            # Cor do nó
            fill_col = "white"
            if n == self.temp_node: fill_col = "yellow"

            # Desenha Apoio (Triângulo simples)
            if n.support:
                sx, sy = n.x, n.y + NODE_RADIUS + 5
                if n.support.restrain_x and n.support.restrain_y:  # Pino
                    self.canvas.create_polygon(n.x, n.y, n.x - 8, n.y + 12, n.x + 8, n.y + 12, fill="green",
                                               outline="black")
                else:  # Rolet
                    self.canvas.create_oval(n.x - 8, n.y + 5, n.x + 8, n.y + 21, outline="green", width=2)

            # Desenha o Nó (Círculo)
            self.canvas.create_oval(n.x - NODE_RADIUS, n.y - NODE_RADIUS,
                                    n.x + NODE_RADIUS, n.y + NODE_RADIUS,
                                    fill=fill_col, outline="black")

            # Desenha ID do Nó
            self.canvas.create_text(n.x + 10, n.y + 10, text=str(n.id), fill="#666")

            # Desenha Carga (Seta)
            if n.load:
                # Converter ângulo para coordenadas de tela
                rad = math.radians(n.load.angle)
                arrow_len = 40
                # O vetor força aponta para (dx, dy)
                dx = arrow_len * math.cos(rad)
                dy = arrow_len * math.sin(rad)

                # Desenhamos a seta chegando no nó ou saindo?
                # Visualmente, melhor desenhar a seta 'empurrando' ou 'puxando' o nó.
                # Vamos desenhar uma linha saindo do nó na direção da força
                self.canvas.create_line(n.x, n.y, n.x + dx, n.y + dy, arrow=tk.LAST, fill="purple", width=3)
                self.canvas.create_text(n.x + dx + 10, n.y + dy, text=f"{n.load.magnitude}N", fill="purple")

            # Desenha Reações (após cálculo)
            if show_results and n.support:
                rx, ry = n.reaction_x, n.reaction_y
                if abs(rx) > 0.1:
                    self.canvas.create_text(n.x, n.y - 25, text=f"Rx:{rx:.1f}", fill="darkgreen")
                if abs(ry) > 0.1:
                    self.canvas.create_text(n.x, n.y + 25, text=f"Ry:{ry:.1f}", fill="darkgreen")


if __name__ == "__main__":
    root = tk.Tk()
    app = TrussApp(root)
    root.mainloop()