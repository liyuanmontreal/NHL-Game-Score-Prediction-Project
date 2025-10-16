"""
Advanced Shot Map Visualization 
支持三种模式:
  - heatmap: 事件热力图
  - diff: 联盟平均差异热图
  - hockeyviz: KDE 平滑红蓝差异图 (HockeyViz 风格)
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
from scipy.stats import gaussian_kde


# ==================== 核心函数 ====================

def plot_hockeyviz_map_interactive(
    season="20202021",
    team_id=None,
    processed_dir="../data/processed",
    raw_dir="../data/raw",
    rink_path="../src/visualization/advanced_visualization/rink.png",
    mode="diff",
    output_path="figures/",
    cmap="RdBu_r",
):
    """
    Draw shot map for given team and season.

    mode:
        'heatmap'  - basic shot density heatmap
        'diff'     - excess vs league average (rectangular)
        'hockeyviz' - KDE smoothed excess map (HockeyViz style)
    """

    # === 加载数据 ===
    csv = os.path.join(processed_dir, f"tidy_shots_{season}.csv")
    if not os.path.exists(csv):
        print(f"[WARN] Missing file: {csv}")
        return

    df = pd.read_csv(csv)
    if "x" not in df or "y" not in df:
        print("[ERROR] Missing coordinate columns.")
        return

    if team_id is None:
        team_id = int(df["team_id"].mode().iloc[0])

    df_team = df[df["team_id"] == team_id]

   

    # === 坐标限制 (只绘制进攻半场) ===
    df_all = df[(df["x"] >= 0) & (df["x"] <= 100) & (np.abs(df["y"]) <= 42.5)]
    df_team = df_team[(df_team["x"] >= 0) & (df_team["x"] <= 100) & (np.abs(df_team["y"]) <= 42.5)]

    # === 加载背景图 ===
    rink_img = Image.open(rink_path)

    # === 绘图基础设置 ===
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(rink_img, extent=[0, 100, -42.5, 42.5], aspect="auto", alpha=1.0, zorder=0)

    # ----------------------------------------------------------
    # 🔹 Mode 1: Simple heatmap
    # ----------------------------------------------------------
    if mode == "heatmap":
        heatmap, xedges, yedges = np.histogram2d(
            df_team["x"], df_team["y"], bins=(50, 50), range=[[0, 100], [-42.5, 42.5]]
        )
        im = ax.imshow(
            heatmap.T,
            extent=[0, 100, -42.5, 42.5],
            origin="lower",
            cmap="YlOrRd",
            alpha=0.7,
            zorder=1,
        )
        plt.title(f"Shot Density Heatmap — {season}, Team {team_id}")

    # ----------------------------------------------------------
    # 🔹 Mode 2: League difference (rectangular)
    # ----------------------------------------------------------
    elif mode == "diff":
        hist_all, _, _ = np.histogram2d(
            df_all["x"], df_all["y"], bins=(50, 50), range=[[0, 100], [-42.5, 42.5]]
        )
        hist_team, _, _ = np.histogram2d(
            df_team["x"], df_team["y"], bins=(50, 50), range=[[0, 100], [-42.5, 42.5]]
        )

        diff = hist_team / hist_team.max() - hist_all / hist_all.max()
        im = ax.imshow(
            diff.T,
            extent=[0, 100, -42.5, 42.5],
            origin="lower",
            cmap=cmap,
            vmin=-0.3,
            vmax=0.3,
            alpha=0.7,
            zorder=1,
        )
        plt.title(f"Excess Shot Rate (Rectangular) — {season}, Team {team_id}")

    # ----------------------------------------------------------
    # 🔹 Mode 3: HockeyViz-style KDE
    # ----------------------------------------------------------
    elif mode == "hockeyviz":
        if len(df_team) < 50:
            print(f"[WARN] Not enough shots for team {team_id}")
            return

        # KDE 平滑
        kde_all = gaussian_kde(np.vstack([df_all["x"], df_all["y"]]))
        kde_team = gaussian_kde(np.vstack([df_team["x"], df_team["y"]]))

        xi, yi = np.mgrid[0:100:250j, -42.5:42.5:200j]
        zi_all = kde_all(np.vstack([xi.ravel(), yi.ravel()]))
        zi_team = kde_team(np.vstack([xi.ravel(), yi.ravel()]))

        rate_all = zi_all / zi_all.max()
        rate_team = zi_team / zi_team.max()

        diff = (rate_team - rate_all).reshape(xi.shape)

        # 红蓝平滑层
        im = ax.imshow(
            diff.T,
            extent=[0, 100, -42.5, 42.5],
            origin="lower",
            cmap=cmap,
            vmin=-0.3,
            vmax=0.3,
            alpha=0.6,
            zorder=1,
        )

        # ✅ 红蓝双色等高线
        levels_pos = np.linspace(0.05, 0.25, 4)
        levels_neg = np.linspace(-0.25, -0.05, 4)

        ax.contour(
            xi, yi, diff,
            levels=levels_pos,
            colors="darkred",
            linewidths=0.8,
            alpha=0.7,
            zorder=2,
        )
        ax.contour(
            xi, yi, diff,
            levels=levels_neg,
            colors="darkblue",
            linewidths=0.8,
            alpha=0.7,
            zorder=2,
        )
        ax.contour(
            xi, yi, diff,
            levels=[0],
            colors="black",
            linewidths=0.5,
            alpha=0.5,
            zorder=3,
        )

        plt.title(f"HockeyViz-style KDE Map (Contour Enhanced) — {season}, Team {team_id}")

   


    else:
            print(f"[ERROR] Unknown mode '{mode}'")
            return

    # === 统一格式 ===
    ax.set_xlim(0, 100)
    ax.set_ylim(-42.5, 42.5)
    ax.axis("off")

    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("Relative Shot Rate vs League Avg")

    plt.tight_layout()
    output_path="figures/"+season+team_id+mode+".png"
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=300)
        print(f"[INFO] Saved to {output_path}")
    plt.show()

    print(f"[INFO] Shot map rendered: mode={mode}, team={team_id}, season={season}")


