import numpy as np
import math
from models import Truss


class TrussSolver:
    @staticmethod
    def solve(truss: Truss):
        nodes = truss.nodes
        members = truss.members
        n_nodes = len(nodes)
        dof = n_nodes * 2  # Graus de liberdade (2 por nó)

        # 1. Inicializa Matriz de Rigidez (K) e Vetor de Forças (F)
        # Equivalente a inicialização em C#
        K = np.zeros((dof, dof))
        F = np.zeros(dof)

        # Mapa para localizar índice do nó rapidamente
        node_index_map = {node.id: i for i, node in enumerate(nodes)}

        # 2. Monta a Matriz de Rigidez Global
        for member in members:
            TrussSolver._add_member_stiffness(K, member, node_index_map)

        # Epsilon para estabilidade numérica (igual ao C#)
        np.fill_diagonal(K, K.diagonal() + 1e-9)

        # 3. Aplica as Cargas (Loads)
        for node in nodes:
            if node.load:
                idx = node_index_map[node.id]
                xi, yi = 2 * idx, 2 * idx + 1

                # Conversão Graus -> Radianos como no C#
                mag = node.load.magnitude
                ang_rad = np.deg2rad(node.load.angle)

                F[xi] += mag * np.cos(ang_rad)
                F[yi] -= mag * np.sin(ang_rad)

        # 4. Identifica Restrições (Supports)
        # Criamos uma máscara booleana: True = Livre, False = Restrito
        free_dofs = np.ones(dof, dtype=bool)

        for node in nodes:
            if node.support:
                idx = node_index_map[node.id]
                xi, yi = 2 * idx, 2 * idx + 1

                if node.support.restrain_x:
                    free_dofs[xi] = False
                if node.support.restrain_y:
                    free_dofs[yi] = False

        # 5. Resolve o Sistema Linear (K * U = F)
        # Particiona as matrizes para pegar apenas os graus livres (Substitui 'SolveWithConstraints' do C#)
        K_free = K[np.ix_(free_dofs, free_dofs)]
        F_free = F[free_dofs]

        try:
            U_free = np.linalg.solve(K_free, F_free)
        except np.linalg.LinAlgError:
            raise Exception("Estrutura instável! Verifique os apoios.")

        # Reconstrói o vetor global de deslocamentos U
        U = np.zeros(dof)
        U[free_dofs] = U_free

        # Armazena deslocamentos nos nós
        for node in nodes:
            idx = node_index_map[node.id]
            node.displacement_x = U[2 * idx]
            node.displacement_y = U[2 * idx + 1]

        # 6. Pós-Processamento: Forças nos Membros e Reações
        TrussSolver._calculate_results(truss, K, U, F, node_index_map)

        return truss

    @staticmethod
    def _add_member_stiffness(K, m, node_map):
        n1, n2 = m.start_node, m.end_node
        i, j = node_map[n1.id], node_map[n2.id]

        dx = n2.x - n1.x
        dy = n2.y - n1.y
        length = math.sqrt(dx ** 2 + dy ** 2)

        if length == 0: return

        c = dx / length
        s = dy / length

        # DIFERENÇA PRINCIPAL VS C#:
        # C# usava rigidez = 1.0. Aqui calculamos EA/L real.
        rigidity = (m.elastic_modulus * m.area) / length

        # Matriz de rigidez local transformada (4x4)
        k_local = np.array([
            [c * c, c * s, -c * c, -c * s],
            [c * s, s * s, -c * s, -s * s],
            [-c * c, -c * s, c * c, c * s],
            [-c * s, -s * s, c * s, s * s]
        ]) * rigidity

        # Índices globais
        indices = [2 * i, 2 * i + 1, 2 * j, 2 * j + 1]

        # Acumula na matriz global K
        for row in range(4):
            for col in range(4):
                K[indices[row], indices[col]] += k_local[row, col]

    @staticmethod
    def _calculate_results(truss, K, U, F_applied, node_map):
        # 1. Calcular Forças Internas
        for m in truss.members:
            n1, n2 = m.start_node, m.end_node
            i, j = node_map[n1.id], node_map[n2.id]

            dx = n2.x - n1.x
            dy = n2.y - n1.y
            length = math.sqrt(dx ** 2 + dy ** 2)
            c, s = dx / length, dy / length

            # Deslocamentos nodais
            u1, v1 = U[2 * i], U[2 * i + 1]
            u2, v2 = U[2 * j], U[2 * j + 1]

            # Deformação (Strain) = (u2-u1)*c + (v2-v1)*s
            deformation = (u2 - u1) * c + (v2 - v1) * s

            # Lei de Hooke: F = (EA/L) * deformação
            k_axial = (m.elastic_modulus * m.area) / length
            m.force = deformation * k_axial
            m.stress = m.force / m.area if m.area > 0 else 0

        # 2. Calcular Reações de Apoio
        # Força Total = K * Deslocamento
        F_total = K @ U

        # Reação = Força Total - Cargas Aplicadas
        Reactions = F_total - F_applied

        for node in truss.nodes:
            if node.support:
                idx = node_map[node.id]
                rx = Reactions[2 * idx]
                ry = Reactions[2 * idx + 1]

                # Limpeza de ruído numérico (igual ao C#)
                if abs(rx) < 1e-5: rx = 0.0
                if abs(ry) < 1e-5: ry = 0.0

                if node.support.restrain_x: node.reaction_x = rx
                if node.support.restrain_y: node.reaction_y = ry