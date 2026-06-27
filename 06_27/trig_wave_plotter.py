import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

# 設定中文字型（微軟正黑體，適用於 Windows）
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'Heiti TC', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False  # 解決負號顯示問題

# 定義 x 範圍：0 到 4π
x = np.linspace(0, 4 * np.pi, 1000)

# 建立圖表，並預留下方空間給滑桿
fig, ax = plt.subplots(figsize=(10, 6))
plt.subplots_adjust(bottom=0.25)  # 預留底部空間

# 初始參數
A_init = 1.0
omega_init = 1.0
phi_init = 0.0

# 繪製初始波形
sin_line, = ax.plot(x, A_init * np.sin(omega_init * x + phi_init),
                    label='y = A·sin(ωx + φ)', linewidth=2)
cos_line, = ax.plot(x, A_init * np.cos(omega_init * x + phi_init),
                    label='y = A·cos(ωx + φ)', linewidth=2, linestyle='--')

# 設定圖表外觀
ax.set_xlim(0, 4 * np.pi)
ax.set_ylim(-5.5, 5.5)
ax.set_title('正弦（sin）與餘弦（cos）波形繪圖', fontsize=14)
ax.set_xlabel('x', fontsize=12)
ax.set_ylabel('y', fontsize=12)
ax.grid(True, linestyle=':', alpha=0.7)
ax.legend(loc='upper right')
ax.axhline(0, color='black', linewidth=0.5)  # 水平參考線

# 建立滑桿的座標 [left, bottom, width, height]
slider_color = 'lightgoldenrodyellow'

# 振幅滑桿
ax_amp = plt.axes([0.15, 0.15, 0.7, 0.03], facecolor=slider_color)
slider_amp = Slider(ax_amp, '振幅 (A)', 0.1, 5.0, valinit=A_init)

# 頻率滑桿
ax_freq = plt.axes([0.15, 0.10, 0.7, 0.03], facecolor=slider_color)
slider_freq = Slider(ax_freq, '頻率 (ω)', 0.1, 10.0, valinit=omega_init)

# 相位偏移滑桿
ax_phase = plt.axes([0.15, 0.05, 0.7, 0.03], facecolor=slider_color)
slider_phase = Slider(ax_phase, '相位偏移 (φ)', 0, 2 * np.pi, valinit=phi_init)


def update(val):
    """當滑桿值變動時，更新波形"""
    A = slider_amp.val
    omega = slider_freq.val
    phi = slider_phase.val

    # 更新兩條曲線的資料
    sin_line.set_ydata(A * np.sin(omega * x + phi))
    cos_line.set_ydata(A * np.cos(omega * x + phi))

    # 動態調整 y 軸範圍
    ax.set_ylim(-A * 1.1 - 0.5, A * 1.1 + 0.5)

    fig.canvas.draw_idle()  # 重新繪製


# 綁定滑桿更新事件
slider_amp.on_changed(update)
slider_freq.on_changed(update)
slider_phase.on_changed(update)

plt.show()
