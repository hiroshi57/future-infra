#!/usr/bin/env python3
"""
未来の生存圏 × 自動運転モビリティ
Minecraft Schematic Generator v1.0

概念:
  少子高齢化・ドーナッツ化により人口が「生存圏」に集約。
  生存圏間は自動運転専用 3車線×2方向 の高速道路で接続され、
  JR新幹線の3分ダイヤのように常に自動運転車が行き来する。

生成物:
  - 生存圏A（西側・シアン/ブルー系ビル群）
  - 生存圏B（東側・パープル/マゼンタ系ビル群）
  - 3車線×2方向 高速道路（急行=赤 / 通常=灰 / 合乗=水色）
  - 自動運転車オブジェクト（各レーンに配置）
  - 中央分離帯（樹木・ガードレール）
  - 入口ゲート・車線案内サイン

使い方:
  pip install mcschematic
  python gen_mirai_sonken.py
  → mirai_sonken.schem が生成される

Minecraft へのインポート:
  1. .schem を [world]/config/worldedit/schematics/ へコピー
  2. WorldEdit: //schem load mirai_sonken
  3. WorldEdit: //paste -a

ワールドレイアウト (X軸 200ブロック / Z軸 90ブロック):
  X:  0 -  37  生存圏A（密集都市クラスター）
  X: 38 - 161  高速道路（3車線×2方向）
  X:162 - 199  生存圏B（密集都市クラスター）

  道路内 Z レーン配置:
  Z: 22-25  急行（追越）A→B  赤
  Z: 26-29  通常        A→B  灰
  Z: 30-33  合乗        A→B  水色
  Z: 34-55  中央分離帯       緑
  Z: 56-59  合乗        B→A  水色
  Z: 60-63  通常        B→A  灰
  Z: 64-68  急行（追越）B→A  赤
"""

import mcschematic
import random

VERSION = mcschematic.Version.JE_1_21_4
SEED = 2026


# ============================================================
class MiraiSonkenWorld:
    """未来生存圏 Minecraft ワールドジェネレーター"""

    def __init__(self):
        self.schem = mcschematic.MCSchematic()
        self.rng = random.Random(SEED)

    # --------------------------------------------------------
    # 内部ユーティリティ
    # --------------------------------------------------------
    def b(self, x, y, z, block):
        """1ブロック設置"""
        self.schem.setBlock((x, y, z), block)

    def fill(self, x1, y1, z1, x2, y2, z2, block):
        """範囲充填（直方体）"""
        for x in range(min(x1, x2), max(x1, x2) + 1):
            for y in range(min(y1, y2), max(y1, y2) + 1):
                for z in range(min(z1, z2), max(z1, z2) + 1):
                    self.schem.setBlock((x, y, z), block)

    # --------------------------------------------------------
    # 1. 地面
    # --------------------------------------------------------
    def gen_ground(self):
        print("  [1/7] 地面を生成...")
        self.fill(0, 0, 0, 199, 0, 89, "minecraft:grass_block")

    # --------------------------------------------------------
    # 2. 高速道路
    # --------------------------------------------------------
    def gen_highway(self):
        print("  [2/7] 高速道路を生成...")
        B = self.b
        F = self.fill

        # ベース（スムーズストーン）
        F(38, 0, 22, 161, 0, 68, "minecraft:smooth_stone")

        # ── A→B 方向（Z:22-33）──────────────────────────
        # 急行（追越）車線 Z:22-25  赤
        F(38, 0, 22, 161, 0, 25, "minecraft:red_concrete")
        # 通常車線        Z:26-29  灰
        F(38, 0, 26, 161, 0, 29, "minecraft:gray_concrete")
        # 合乗車線        Z:30-33  水色
        F(38, 0, 30, 161, 0, 33, "minecraft:light_blue_concrete")

        # ── 中央分離帯（Z:34-55）──────────────────────────
        F(38, 0, 34, 161, 0, 55, "minecraft:moss_block")

        # 中央分離帯の街路樹（10ブロック間隔）
        for tx in range(42, 162, 10):
            # 幹
            for ty in range(1, 5):
                B(tx, ty, 44, "minecraft:oak_log")
            # 葉（球形ブロック群）
            for dy in range(2, 7):
                for dz in range(-3, 4):
                    for dx in range(-2, 3):
                        if abs(dx) + abs(dz) + abs(dy - 5) <= 4:
                            B(tx + dx, dy, 44 + dz,
                              "minecraft:oak_leaves[persistent=true]")

        # 分離帯ガードレール
        for x in range(38, 162):
            B(x, 1, 34, "minecraft:iron_bars")
            B(x, 1, 55, "minecraft:iron_bars")

        # ── B→A 方向（Z:56-68）──────────────────────────
        # 合乗車線        Z:56-59  水色
        F(38, 0, 56, 161, 0, 59, "minecraft:light_blue_concrete")
        # 通常車線        Z:60-63  灰
        F(38, 0, 60, 161, 0, 63, "minecraft:gray_concrete")
        # 急行（追越）車線 Z:64-68  赤
        F(38, 0, 64, 161, 0, 68, "minecraft:red_concrete")

        # 車線区切り破線（白・4ブロック間隔）
        for x in range(38, 162, 4):
            for z_mark in [25, 29, 33, 55, 59, 63]:
                B(x, 0, z_mark, "minecraft:white_concrete")

        # 道路端ガードレール
        for x in range(38, 162):
            B(x, 1, 22, "minecraft:iron_bars")
            B(x, 1, 68, "minecraft:iron_bars")

        # 街灯（15ブロック間隔）
        for lx in range(45, 162, 15):
            for ly in range(1, 5):
                B(lx, ly, 21, "minecraft:iron_bars")
                B(lx, ly, 69, "minecraft:iron_bars")
            B(lx, 5, 21, "minecraft:sea_lantern")
            B(lx, 5, 69, "minecraft:sea_lantern")

    # --------------------------------------------------------
    # 3. 自動運転車
    # --------------------------------------------------------
    def gen_cars(self):
        print("  [3/7] 自動運転車を配置...")

        # ── A→B 急行（Z:22-25）──
        self._car(50,  22, east=True,  color="red")
        self._car(82,  23, east=True,  color="red")
        self._car(118, 22, east=True,  color="red")

        # ── A→B 通常（Z:26-29）──
        self._car(62,  27, east=True,  color="normal")
        self._car(98,  26, east=True,  color="normal")
        self._car(138, 27, east=True,  color="normal")

        # ── A→B 合乗（Z:30-33）──  ※複数人乗合=多め
        self._car(47,  31, east=True,  color="shared")
        self._car(74,  30, east=True,  color="shared")
        self._car(110, 31, east=True,  color="shared")
        self._car(148, 30, east=True,  color="shared")

        # ── B→A 急行（Z:64-68）──
        self._car(148, 65, east=False, color="red")
        self._car(112, 64, east=False, color="red")
        self._car(76,  65, east=False, color="red")

        # ── B→A 通常（Z:60-63）──
        self._car(132, 61, east=False, color="normal")
        self._car(96,  60, east=False, color="normal")

        # ── B→A 合乗（Z:56-59）──
        self._car(145, 57, east=False, color="shared")
        self._car(108, 56, east=False, color="shared")
        self._car(70,  57, east=False, color="shared")

    def _car(self, cx, cz, east=True, color="normal"):
        """
        4×2×2 ブロックの自動運転車を描画
          cx,cz : 車の左後端（東向きの場合は西端）
          east  : True=A→B方向（東行き）
          color : 'red'=急行 / 'normal'=通常 / 'shared'=合乗
        """
        B = self.b
        F = self.fill

        # 車体（白コンクリート）
        F(cx, 1, cz, cx + 3, 2, cz + 1, "minecraft:white_concrete")

        # フロントガラス（水色ガラス）
        B(cx + 1, 2, cz,     "minecraft:light_blue_stained_glass")
        B(cx + 2, 2, cz,     "minecraft:light_blue_stained_glass")
        B(cx + 1, 2, cz + 1, "minecraft:light_blue_stained_glass")
        B(cx + 2, 2, cz + 1, "minecraft:light_blue_stained_glass")

        # タイヤ（黒コンクリート・四隅）
        B(cx,     1, cz,     "minecraft:black_concrete")
        B(cx + 3, 1, cz,     "minecraft:black_concrete")
        B(cx,     1, cz + 1, "minecraft:black_concrete")
        B(cx + 3, 1, cz + 1, "minecraft:black_concrete")

        # ヘッドライト（進行方向側）
        if east:
            B(cx + 3, 2, cz,     "minecraft:sea_lantern")
            B(cx + 3, 2, cz + 1, "minecraft:sea_lantern")
        else:
            B(cx,     2, cz,     "minecraft:sea_lantern")
            B(cx,     2, cz + 1, "minecraft:sea_lantern")

        # ルーフ上アクセント（車線種別カラー）
        accent = {
            "red":    "minecraft:red_concrete",
            "normal": "minecraft:yellow_concrete",
            "shared": "minecraft:light_blue_concrete",
        }.get(color, "minecraft:white_concrete")
        B(cx + 1, 3, cz,     accent)
        B(cx + 2, 3, cz,     accent)
        B(cx + 1, 3, cz + 1, accent)
        B(cx + 2, 3, cz + 1, accent)

    # --------------------------------------------------------
    # 4 & 5. 生存圏
    # --------------------------------------------------------
    def gen_zones(self):
        print("  [4/7] 生存圏Aを生成...")
        self._gen_zone(0, 37, "A")
        print("  [5/7] 生存圏Bを生成...")
        self._gen_zone(163, 200, "B")

    def _gen_zone(self, x_start, x_end, label):
        """生存圏（未来都市クラスター）を生成"""
        rng = random.Random(SEED + ord(label))
        B = self.b
        F = self.fill

        # 都市地面（コンクリート舗装）
        F(x_start, 0, 0, x_end - 1, 0, 89, "minecraft:light_gray_concrete")

        # 内部グリッド道路（7ブロック間隔）
        for gx in range(x_start + 6, x_end, 7):
            if gx < x_end:
                F(gx, 0, 0, gx, 0, 89, "minecraft:smooth_stone")
        for gz in range(6, 90, 7):
            F(x_start, 0, gz, x_end - 1, 0, gz, "minecraft:smooth_stone")

        # 各ブロックに建物を配置
        for gx_s in range(x_start, x_end, 7):
            for gz_s in range(0, 90, 7):
                bx = gx_s + 1
                bz = gz_s + 1
                bw = min(5, x_end - gx_s - 2)
                bd = 5

                if bw < 2 or bz + bd > 89:
                    continue

                # 高さをランダムに決定（0=広場）
                h_choices = [0, 0, 4, 6, 8, 10, 14, 18, 22]
                h = rng.choice(h_choices)

                if h == 0:
                    # 広場・緑地
                    F(bx, 0, bz, bx + bw - 1, 0, bz + bd - 1,
                      "minecraft:moss_block")
                    if rng.random() > 0.5:
                        # 広場の木
                        tx = bx + bw // 2
                        tz = bz + bd // 2
                        for ty in range(1, 4):
                            B(tx, ty, tz, "minecraft:oak_log")
                        for dy in range(2, 5):
                            for dz in range(-1, 2):
                                for dx in range(-1, 2):
                                    if abs(dx) + abs(dz) + abs(dy - 3) <= 2:
                                        B(tx + dx, dy, tz + dz,
                                          "minecraft:oak_leaves[persistent=true]")
                    continue

                # 外壁カラー（生存圏Aとbで色のテーマを変える）
                if label == "A":
                    wall_colors = [
                        "minecraft:cyan_concrete",
                        "minecraft:blue_concrete",
                        "minecraft:white_concrete",
                        "minecraft:light_gray_concrete",
                        "minecraft:light_blue_concrete",
                    ]
                else:
                    wall_colors = [
                        "minecraft:purple_concrete",
                        "minecraft:magenta_concrete",
                        "minecraft:pink_concrete",
                        "minecraft:white_concrete",
                        "minecraft:light_gray_concrete",
                    ]
                wall = rng.choice(wall_colors)

                # 建物の壁（外周のみ、窓はガラス）
                for y in range(1, h + 1):
                    for xx in range(bx, bx + bw):
                        for zz in range(bz, bz + bd):
                            is_wall = (xx == bx or xx == bx + bw - 1 or
                                       zz == bz or zz == bz + bd - 1)
                            if not is_wall:
                                continue
                            # 窓フロア（3段おきに）・角柱以外はガラス
                            is_z_face = (zz == bz or zz == bz + bd - 1)
                            is_x_edge = (xx == bx or xx == bx + bw - 1)
                            if y % 3 == 2 and is_z_face and not is_x_edge:
                                self.schem.setBlock((xx, y, zz),
                                                    "minecraft:glass")
                            else:
                                self.schem.setBlock((xx, y, zz), wall)

                # 屋上
                F(bx, h + 1, bz, bx + bw - 1, h + 1, bz + bd - 1,
                  "minecraft:dark_prismarine")

                # 高層ビル（h≥14）にはアンテナ
                if h >= 14:
                    ax = bx + bw // 2
                    az = bz + bd // 2
                    for ay in range(h + 2, h + 6):
                        B(ax, ay, az, "minecraft:lightning_rod")
                    B(ax, h + 6, az, "minecraft:sea_lantern")

    # --------------------------------------------------------
    # 6. ゲート（生存圏の入口）
    # --------------------------------------------------------
    def gen_gates(self):
        print("  [6/7] 入口ゲートを生成...")
        B = self.b

        for gate_x in [38, 161]:
            # 縦柱（道路両端）
            for y in range(1, 8):
                B(gate_x, y, 22, "minecraft:iron_block")
                B(gate_x, y, 68, "minecraft:iron_block")
            # 横梁（頭上アーチ）
            for z in range(22, 69):
                B(gate_x, 7, z, "minecraft:iron_block")
            # 横梁のライン発光（3ブロックおき）
            for z in range(22, 69, 3):
                B(gate_x, 7, z, "minecraft:sea_lantern")
            # 中央ビーコン（視認性UP）
            B(gate_x, 8, 44, "minecraft:beacon")
            B(gate_x, 8, 45, "minecraft:beacon")

    # --------------------------------------------------------
    # 7. 車線案内サイン（道路上方・横断看板）
    # --------------------------------------------------------
    def gen_signs(self):
        print("  [7/7] 車線案内サインを生成...")
        B = self.b

        for sx in [55, 100, 145]:
            # 支柱（道路脇）
            for y in range(1, 7):
                B(sx, y, 21, "minecraft:iron_bars")
                B(sx, y, 69, "minecraft:iron_bars")

            # 横断看板（ベース：シアン）
            for z in range(21, 70):
                B(sx, 7, z, "minecraft:cyan_glazed_terracotta")

            # A→B 方向 レーンカラー
            for z in range(22, 26):   # 急行（赤）
                B(sx, 7, z, "minecraft:red_glazed_terracotta")
            for z in range(26, 30):   # 通常（黄）
                B(sx, 7, z, "minecraft:yellow_glazed_terracotta")
            for z in range(30, 34):   # 合乗（青）
                B(sx, 7, z, "minecraft:blue_glazed_terracotta")

            # B→A 方向 レーンカラー
            for z in range(56, 60):   # 合乗（青）
                B(sx, 7, z, "minecraft:blue_glazed_terracotta")
            for z in range(60, 64):   # 通常（黄）
                B(sx, 7, z, "minecraft:yellow_glazed_terracotta")
            for z in range(64, 69):   # 急行（赤）
                B(sx, 7, z, "minecraft:red_glazed_terracotta")

    # --------------------------------------------------------
    # メイン実行
    # --------------------------------------------------------
    def generate(self, output_dir="."):
        print()
        print("=" * 56)
        print("  未来の生存圏 × 自動運転モビリティ")
        print("  Minecraft Schematic Generator v1.0")
        print("=" * 56)
        print()

        self.gen_ground()
        self.gen_highway()
        self.gen_cars()
        self.gen_zones()
        self.gen_gates()
        self.gen_signs()

        print()
        print(f"  [SAVE] 保存中: {output_dir}/mirai_sonken.schem ...")
        self.schem.save(output_dir, "mirai_sonken", VERSION)

        print()
        print("  [OK] mirai_sonken.schem が生成されました！")
        print()
        print("  [Minecraft へのインポート手順]")
        print("    1. .schem を [world]/config/worldedit/schematics/ へコピー")
        print("    2. //schem load mirai_sonken")
        print("    3. //paste -a")
        print()
        print("  [ワールドマップ]")
        print("    X:  0- 37  生存圏A (シアン/ブルー系)")
        print("    X: 38-161  高速道路 (3車線×2方向)")
        print("    X:162-199  生存圏B (パープル/マゼンタ系)")
        print()
        print("  [車線カラーコード]")
        print("    赤 = 急行（追越）車線")
        print("    灰 = 通常車線")
        print("    水 = 合乗（乗り合い）車線")
        print()


# ============================================================
if __name__ == "__main__":
    world = MiraiSonkenWorld()
    world.generate(output_dir=".")
