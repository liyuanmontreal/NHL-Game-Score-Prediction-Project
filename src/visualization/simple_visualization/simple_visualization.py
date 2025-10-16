"""
src/visualization/simple_visualization.py
-----------------------------------------
Simple visualization module for NHL shot data.
NHL 射门数据的基础可视化模块。
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os


# ========== Helper Functions / 辅助函数 ==========

def compute_shot_distance(df: pd.DataFrame) -> pd.DataFrame:
    """计算射门到球门的距离。
    假设球门位于 x=89(进攻方向右侧)，并使用勾股定理计算距离。
    """
    df = df.copy()
    df["distance"] = np.sqrt((89 - np.abs(df["x"]))**2 + (df["y"]**2))
    return df


# ========== Visualization 1 / 射门类型分布 ==========
def plot_shot_type_distribution( season: str):
    """Plot total shots and goals by shot type.
    按射门类型统计射门与进球数量并绘图。
    """

    df = pd.read_csv("../data/processed/tidy_shots_"+season+".csv")

    if df.empty:
        print(f"[WARN] No data found for season {season}")
        print("[INFO] Available seasons:", df["season"].unique()[:10])
        return pd.DataFrame()

    print(f"[INFO] Plotting for season {season} — {len(df)} events found")

    # 聚合射门类型
    agg = (
        df.groupby("shot_type")["is_goal"]
        .agg(["count", "sum"])
        .rename(columns={"count": "num_shots", "sum": "num_goals"})
        .sort_values("num_shots", ascending=False)
    )
    agg["goal_pct"] = agg["num_goals"] / agg["num_shots"] * 100
  

    # 绘图
    plt.figure(figsize=(10, 6))
    sns.barplot(x=agg.index, y=agg["num_shots"], color="lightblue", label="Shots")
    sns.barplot(x=agg.index, y=agg["num_goals"], color="red", alpha=0.7, label="Goals")

    plt.title(f"Shot Type Distribution — Season {season}")
    plt.xlabel("Shot Type")
    plt.ylabel("Count")
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    # 输出统计结果
    print("Most common shot type:", agg.index[0])
    print("Most dangerous shot type:", agg["goal_pct"].idxmax())
    return agg



# ========== Visualization 2 / 距离与进球概率关系 ==========
def plot_distance_vs_goal_probability(season_list=None):
    """
    Plot goal probability vs shot distance for multiple seasons.
    从多个赛季的 CSV 文件加载数据并绘制射门距离与进球率关系。
    """
    import os
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import seaborn as sns

    #plt.rcParams['font.family'] = ['SimHei']  #  支持中文（Windows）
    #plt.rcParams['axes.unicode_minus'] = False

    if season_list is None:
        season_list = []

    all_data = []

    # === 🔹 读取各赛季 CSV 文件 ===
    for season in season_list:
        csv_path = os.path.join("../data/processed", f"tidy_shots_{season}.csv")   
        if not os.path.exists(csv_path):
            print(f"[WARN] Missing file: {csv_path}")
            continue

        df = pd.read_csv(csv_path)
        df["season"] = str(season)
        all_data.append(df)
        print(f"[INFO] Loaded {csv_path} ({len(df)} rows)")

    if not all_data:
        print("[ERROR] No data loaded. Please check season_list or file paths.")
        return

    # === 🔹 合并所有赛季数据 ===
    df_all = pd.concat(all_data, ignore_index=True)
    df_all["distance"] = np.sqrt((89 - np.abs(df_all["x"]))**2 + (df_all["y"]**2))

    # === 🔹 计算每个赛季的进球率 ===
    plt.figure(figsize=(9, 6))
    for season in season_list:
        df = df_all[df_all["season"] == str(season)].copy()  #  避免 SettingWithCopyWarning
        df["dist_bin"] = pd.cut(df["distance"], bins=np.arange(0, 90, 5))
        agg = df.groupby("dist_bin", observed=False)["is_goal"].mean().reset_index()
        centers = [b.mid for b in agg["dist_bin"]]
        plt.plot(centers, agg["is_goal"], marker="o", label=season)

    # === 🔹 绘图样式 ===
    plt.title("Goal Probability vs Shot Distance")
    plt.xlabel("Distance from Net (ft)")
    plt.ylabel("Goal Probability")
    plt.legend(title="Season")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    print("[INFO] Plot completed successfully.")


# ========== Visualization 3 / 距离 × 射门类型 热力图 ==========
def plot_goal_percentage_by_distance_and_type(season="20222023"):
    """Plot 2D heatmap of goal percentage by shot distance and shot type.
    按距离与射门类型绘制进球率热力图。
    """
    import os
    import pandas as pd
    import numpy as np
    import seaborn as sns
    import matplotlib.pyplot as plt

    csv_path = os.path.join("../data/processed", f"tidy_shots_{season}.csv")   
    if not os.path.exists(csv_path):
        print(f"[WARN] Missing file: {csv_path}")
        return

    df = pd.read_csv(csv_path)
    if df.empty:
        print(f"[WARN] Empty dataset for {season}.")
        return

    # 计算距离
    df = compute_shot_distance(df)
    df = df[df["shot_type"].notna()]  #  过滤空类型
    df = df[df["is_goal"].isin([0, 1])]  # 只保留有效进球标志

    if df.empty:
        print(f"[WARN] No valid shot_type or is_goal values for {season}.")
        return

    # 自动调整距离范围
    max_dist = min(150, int(df["distance"].max()) + 5)
    df["dist_bin"] = pd.cut(df["distance"], bins=np.arange(0, max_dist, 5))

    # 分组聚合
    pivot = (
        df.groupby(["shot_type", "dist_bin"], observed=True)["is_goal"]  
        .mean()
        .reset_index()
        .pivot(index="shot_type", columns="dist_bin", values="is_goal")
    )

    # 如果仍然为空
    if pivot.empty or pivot.isna().all().all():
        print(f"[WARN] No valid goal probability data for {season}.")
        print("Try checking your tidy_shots CSV for missing columns or zero goals.")
        return

    # 格式化数值（显示百分比）
    pivot_display = pivot * 100

    #  绘制热力图（添加数字标签 annot=True）
    plt.figure(figsize=(12, 6))
    sns.heatmap(
        pivot_display,
        cmap="YlOrRd",
        cbar_kws={"label": "Goal Probability (%)"},
        linewidths=0.5,
        annot=True,             # 显示数字
        fmt=".1f",              # 一位小数
        annot_kws={"size": 8}   # 字体大小
    )

    plt.title(f"Goal % by Distance and Shot Type — {season}")
    plt.xlabel("Distance Bin (ft)")
    plt.ylabel("Shot Type")
    plt.tight_layout()
    plt.show()

    print(f"[INFO] Heatmap ready for {season}: shows how distance & shot type affect scoring chance.")




if __name__ == "__main__":
    # Example: load tidy dataset
    df = pd.read_csv("data/processed/tidy_shots_20222023.csv")
    plot_shot_type_distribution(season="20222023")
    plot_distance_vs_goal_probability( season_list=["20182019", "20192020", "20202021"])
    plot_goal_percentage_by_distance_and_type(season="20222023")
