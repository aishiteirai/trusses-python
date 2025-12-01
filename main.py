from models import Node, Member, Truss, Support, Load
from solver import TrussSolver


def main():

    n1 = Node(id=1, x=0, y=0, support=Support(restrain_x=True, restrain_y=True))

    n2 = Node(id=2, x=10, y=0, support=Support(restrain_x=False, restrain_y=True))

    n3 = Node(id=3, x=5, y=5)
    n3.load = Load(magnitude=1000, angle=270)

    E_steel = 200e9  
    Area_bar = 0.01  

    m1 = Member(id=1, start_node=n1, end_node=n2, elastic_modulus=E_steel, area=Area_bar)
    m2 = Member(id=2, start_node=n2, end_node=n3, elastic_modulus=E_steel, area=Area_bar)
    m3 = Member(id=3, start_node=n3, end_node=n1, elastic_modulus=E_steel, area=Area_bar)

    minha_trelica = Truss(nodes=[n1, n2, n3], members=[m1, m2, m3])
    TrussSolver.solve(minha_trelica)

    print("=== RESULTADOS ===")
    print("\n--- Deslocamentos (m) ---")
    for n in minha_trelica.nodes:
        print(f"Nó {n.id}: dx={n.displacement_x:.6f}, dy={n.displacement_y:.6f}")

    print("\n--- Reações de Apoio (N) ---")
    for n in minha_trelica.nodes:
        if n.support:
            print(f"Nó {n.id}: Rx={n.reaction_x:.2f}, Ry={n.reaction_y:.2f}")

    print("\n--- Forças Internas (N) ---")
    for m in minha_trelica.members:
        tipo = "Tração" if m.force > 0 else "Compressão"
        print(f"Membro {m.id}: {abs(m.force):.2f} ({tipo})")


if __name__ == "__main__":
    main()