import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
from scipy.integrate import quad

class SimuladorBoydKleinman:
    def __init__(self):
        # Parâmetros ótimos teóricos (Critério de Boyd-Kleinman)
        self.xi_opt = 2.84
        self.sigma_opt = 0.57
        
        # Malha de cálculo para o eixo X (sigma)
        self.sigma_range = np.linspace(-1.0, 3.0, 200)
        
        # Configuração da Figura e Eixos
        self.fig, self.ax = plt.subplots(figsize=(10, 7))
        plt.subplots_adjust(left=0.1, bottom=0.35, right=0.9, top=0.9)
        
        # Elementos gráficos iniciais
        h_iniciais = self.calcular_curva_h(self.sigma_range, self.xi_opt)
        h_ponto = self.h_integral(self.sigma_opt, self.xi_opt)
        
        self.linha, = self.ax.plot(self.sigma_range, h_iniciais, lw=2.5, color='#2c3e50', label=r'Curva $h(\sigma)$ para o $\xi$ atual')
        self.ponto, = self.ax.plot([self.sigma_opt], [h_ponto], 'ro', markersize=9, label='Posição Atual')
        self.linha_max_teorico = self.ax.axvline(x=self.sigma_opt, color='r', linestyle='--', alpha=0.4, label='Ótimo Teórico ($\sigma=0.57$)')
        
        # Configuração do gráfico principal
        self.ax.set_xlim(-1.0, 3.0)
        self.ax.set_ylim(0, 1.15)
        self.ax.set_xlabel(r'Descasamento de Fase Normalizado $\sigma = \frac{1}{2}b\Delta k$', fontsize=11)
        self.ax.set_ylabel(r'Fator de Eficiência $h(\sigma, \xi)$', fontsize=11)
        self.ax.set_title('Simulador Boyd-Kleinman: Otimização da Geração de Segundo Harmônico', fontweight='bold', pad=15)
        self.ax.grid(True, linestyle=':', alpha=0.7)
        self.ax.legend(loc='upper left')
        
        # Caixa de texto para o painel de dados e física
        props_caixa = dict(boxstyle='round', facecolor='wheat', alpha=0.4)
        self.texto_info = self.ax.text(0.65, 0.95, '', transform=self.ax.transAxes, verticalalignment='top', 
                                       fontsize=10, bbox=props_caixa)
        
        # Criação dos eixos para os widgets (Sliders e Botões)
        cor_eixo = 'lightgoldenrodyellow'
        ax_xi = plt.axes([0.15, 0.20, 0.65, 0.03], facecolor=cor_eixo)
        ax_sigma = plt.axes([0.15, 0.13, 0.65, 0.03], facecolor=cor_eixo)
        ax_reset = plt.axes([0.82, 0.04, 0.12, 0.05])
        
        # Inicialização dos Sliders
        self.slider_xi = Slider(ax_xi, r'Focalização $\xi$', 0.1, 10.0, valinit=self.xi_opt, valstep=0.01)
        self.slider_sigma = Slider(ax_sigma, r'Phase Mismatch $\sigma$', -1.0, 3.0, valinit=self.sigma_opt, valstep=0.01)
        
        # Inicialização do Botão
        self.btn_reset = Button(ax_reset, 'Reset (Ótimo)', color='whitesmoke', hovercolor='0.9')
        
        # Conexão dos eventos
        self.slider_xi.on_changed(self.atualizar)
        self.slider_sigma.on_changed(self.atualizar)
        self.btn_reset.on_clicked(self.resetar)
        
        # Chamada inicial para desenhar o texto
        self.atualizar(None)

    def h_integral(self, sigma, xi):
        """Avalia a integral de sobreposição para um par (sigma, xi)."""
        if xi <= 0: return 0.0
        # Integrando simplificado após a redução por simetria
        def integrando(tau):
            return (np.cos(sigma * tau) + tau * np.sin(sigma * tau)) / (1.0 + tau**2)
        
        valor_integral, _ = quad(integrando, 0, xi)
        return (2.0 / xi) * (valor_integral ** 2)

    def calcular_curva_h(self, vetor_sigma, xi):
        """Vetoriza a função para desenhar a linha do gráfico rapidamente."""
        v_integral = np.vectorize(lambda s: self.h_integral(s, xi))
        return v_integral(vetor_sigma)

    def atualizar(self, val):
        """Função de callback acionada quando os sliders são movidos."""
        xi_atual = self.slider_xi.val
        sigma_atual = self.slider_sigma.val
        
        # Atualiza a curva baseada no novo xi
        novos_h = self.calcular_curva_h(self.sigma_range, xi_atual)
        self.linha.set_ydata(novos_h)
        
        # Atualiza a posição do ponto vermelho
        h_ponto = self.h_integral(sigma_atual, xi_atual)
        self.ponto.set_data([sigma_atual], [h_ponto])
        
        # Atualiza o painel de texto lateral
        texto = (
            f"--- Leituras Atuais ---\n"
            f"Focalização ($\\xi$): {xi_atual:.2f}\n"
            f"Phase Mismatch ($\\sigma$): {sigma_atual:.2f}\n"
            f"Eficiência (h): {h_ponto:.4f}\n\n"
            f"--- Física (Fase de Gouy) ---\n"
            f"A defasagem geométrica do feixe\n"
            f"através do foco força a necessi-\n"
            f"dade de um material com $\\Delta k > 0$\n"
            f"($\\sigma > 0$) para compensar a perda\n"
            f"de coerência macroscópica."
        )
        self.texto_info.set_text(texto)
        
        # Redesenha o canvas
        self.fig.canvas.draw_idle()

    def resetar(self, event):
        """Volta os sliders para o ótimo de Boyd-Kleinman."""
        self.slider_xi.reset()
        self.slider_sigma.reset()

if __name__ == '__main__':
    simulador = SimuladorBoydKleinman()
    plt.show()