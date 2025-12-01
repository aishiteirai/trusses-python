# 🏗️ Trusses 2D - Análise de Treliças Planas

Um software interativo para análise e cálculo de estruturas de treliças 2D, desenvolvido em Python. O projeto utiliza o **Método da Rigidez Direta** (Direct Stiffness Method) para calcular deslocamentos, reações de apoio e forças internas (tração e compressão) em barras.

<img width="1086" alt="Screenshot do Projeto" src="https://github.com/user-attachments/assets/7eda8eb9-4169-4553-80e9-29fd49da1163" />

## 📖 Sobre o Projeto

Este projeto foi desenvolvido com foco educacional para auxiliar no entendimento de **Mecânica dos Sólidos**. Ele permite que o usuário desenhe livremente uma estrutura, defina condições de contorno (apoios) e aplique carregamentos, visualizando os resultados instantaneamente de forma gráfica e numérica.

### Principais Funcionalidades
* **Interface Gráfica Moderna:** Desenvolvida com `CustomTkinter` para uma aparência limpa e profissional.
* **Sistema de Grid:** Facilita o desenho preciso dos nós e barras com "snap" automático.
* **Configuração de Apoios:** Suporte para Pinos (2º gênero - restrição X/Y) e Roletes (1º gênero - restrição Y).
* **Carregamento Vetorial:** Aplicação de forças com magnitude e ângulo personalizados.
* **Visualização de Resultados:**
    * **Cores:** Azul para Tração, Vermelho para Compressão.
    * **Valores:** Exibição das forças nas barras e reações (Rx, Ry) nos apoios.

---

## 🛠️ Tecnologias e Bibliotecas Utilizadas

O projeto foi escrito inteiramente em **Python 3.13**. Abaixo estão as principais bibliotecas que fazem o sistema funcionar:

### 1. Interface Gráfica (Frontend)
* **[CustomTkinter](https://github.com/TomSchimansky/CustomTkinter):** Uma biblioteca baseada no Tkinter que fornece widgets modernos, arredondados e suporte nativo a temas (Dark/Light mode). Usada para os botões, janelas modais e layout lateral.
* **[Tkinter](https://docs.python.org/3/library/tkinter.html):** A biblioteca padrão de GUI do Python. O componente `Canvas` foi utilizado para a área de desenho (renderização das linhas, círculos e textos da estrutura), pois oferece performance superior para desenho vetorial dinâmico.

### 2. Cálculos Matemáticos (Backend/Solver)
* **[NumPy](https://numpy.org/):** Fundamental para a álgebra linear. O solver utiliza o NumPy para:
    * Montar a **Matriz de Rigidez Global** da estrutura.
    * Resolver o sistema de equações lineares ($F = K \cdot u$).
    * Realizar operações vetoriais de seno e cosseno para decomposição de forças.

---

## 📂 Estrutura do Código

A arquitetura do projeto segue o princípio de separação de responsabilidades:

1.  **`models.py` (Camada de Dados):**
    * Define os objetos físicos utilizando `dataclasses`: `Node` (Nó), `Member` (Barra), `Support` (Apoio) e `Load` (Carga).
    * Define propriedades físicas padrão, como o Módulo de Elasticidade do Aço ($E = 200 GPa$).

2.  **`solver.py` (Camada Lógica - O "Cérebro"):**
    * Implementa a matemática de engenharia.
    * Calcula a rigidez local de cada barra ($k = \frac{EA}{L}$) e monta a matriz global.
    * Resolve os deslocamentos nodais e calcula as reações de apoio.

3.  **`app.py` (Camada de Apresentação):**
    * Gerencia a interação com o usuário (cliques do mouse, botões).
    * Converte as coordenadas da tela (pixels) para o modelo matemático.
    * Desenha a estrutura e os resultados finais na tela.

---

## 🚀 Como Executar

### Pré-requisitos
Certifique-se de ter o Python instalado. Em seguida, instale as dependências necessárias:

```bash
pip install numpy customtkinter

```

---

## 🙋‍♂️ Autores

**Leonardo Rosario Teixeira**  
[GitHub: @leonardorosario](https://github.com/leonardorosario)

**Ryan Corazza Alvarenga**  
[GitHub: @aishiteirai](https://github.com/aishiteirai)
