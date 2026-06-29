#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
未来の生存圏 × 自動運転モビリティ
Minecraft Schematic Generator  v2.0  (120% enhanced)

主な改良点 (v1→v2):
  1. 高架ビアダクト構造   : 道路が Y=6 に浮き上がり、8ブロック間隔の
                              支柱群（クロスブレース付き）で支持される
  2. 地下駐車場           : 生存圏A・B の地下 Y=-5〜Y=-1 に駐車構造
  3. 3種類の建物型        : オフィスタワー / 住居タワー / 複合用途
  4. 歩行者デッキ         : Y=10 の空中歩廊で建物間を連絡
  5. 太陽光パネル         : 屋上に daylight_detector で表現
  6. 精細な自動運転車     : ガラス・車体・ライト・ルーフアクセント
  7. インフラ施設         : 交通制御タワー・変電設備
  8. 植生の多様化         : オーク / バーチ / 竹林

使い方:
  pip install mcschematic
  python gen_mirai_sonken.py
  -> mirai_sonken_v2.schem 生成

Minecraft インポート (WorldEdit / FAWE):
  //schem load mirai_sonken_v2
  //paste -a

ワールドレイアウト:
  X:  0- 37  生存圏A  (シアン/ティール系)
  X: 38-161  高架高速道路  (支柱群で Y=6 に浮上)
  X:162-199  生存圏B  (パープル/マゼンタ系)
  Y:  -5〜-1 地下駐車場 (両ゾーン直下)
  Y:   0     地面
  Y:   6     高架道路面
  Y:  10     歩行者デッキ

車線 (Z軸) :
  Z: 22-25  急行(A→B)  赤コンクリート
  Z: 26-29  通常(A→B)  灰コンクリート
  Z: 30-33  合乗(A→B)  水色コンクリート
  Z: 34-55  中央分離帯  苔ブロック + 樹木
  Z: 56-59  合乗(B→A)  水色コンクリート
  Z: 60-63  通常(B→A)  灰コンクリート
  Z: 64-68  急行(B→A)  赤コンクリート
"""

import argparse
import sys

import mcschematic
import random

VERSION = mcschematic.Version.JE_1_21_4
SEED    = 2026

# ================================================================
# 定数
# ================================================================
ROAD_X_START = 38
ROAD_X_END   = 161
ZONE_A_END   = 37
ZONE_B_START = 162
ZONE_B_END   = 199

ROAD_ELEV    = 6    # 高架道路面の Y 座標
DECK_ELEV    = 10   # 歩行者デッキの Y 座標
UG_TOP       = -1   # 地下駐車場の上端
UG_BOT       = -5   # 地下駐車場の下端

PILLAR_INTERVAL = 8  # 支柱間隔 (ブロック)

# ── ワールド境界（座標バリデーション用）──
WORLD_X_MIN, WORLD_X_MAX = 0, 199
WORLD_Y_MIN, WORLD_Y_MAX = -5, 40   # 地下駐車場〜アンテナ頂部
WORLD_Z_MIN, WORLD_Z_MAX = 0, 89

# ── 散在していたマジックナンバーの集約 ──
# ゾーンの Z 方向奥行きはワールド境界 WORLD_Z_MAX (=89) と一致する
MEDIAN_Z     = 44   # 中央分離帯の中心 Z（歩廊・分離帯樹木の基準）
SIGN_X       = [52, 90, 130]   # 車線案内サインを立てる X 位置

# 車線 Z 範囲
LANES = [
    ("express", range(22, 26), "minecraft:red_concrete",        True),
    ("normal",  range(26, 30), "minecraft:gray_concrete",       True),
    ("shared",  range(30, 34), "minecraft:light_blue_concrete", True),
    ("median",  range(34, 56), "minecraft:moss_block",          False),
    ("shared",  range(56, 60), "minecraft:light_blue_concrete", True),
    ("normal",  range(60, 64), "minecraft:gray_concrete",       True),
    ("express", range(64, 69), "minecraft:red_concrete",        True),
]

ROAD_Z_MIN = 22
ROAD_Z_MAX = 68

# ================================================================
# ワールドジェネレーター
# ================================================================
class MiraiSonkenWorld:

    def __init__(self, strict=False):
        self.s   = mcschematic.MCSchematic()
        self.rng = random.Random(SEED)
        self.strict = strict      # True なら範囲外設置で例外を送出
        self.oob_count = 0        # 範囲外として弾いたブロック数

    # ─── 低レベルAPI ────────────────────────────────────────────
    @staticmethod
    def _in_bounds(x, y, z):
        return (WORLD_X_MIN <= x <= WORLD_X_MAX and
                WORLD_Y_MIN <= y <= WORLD_Y_MAX and
                WORLD_Z_MIN <= z <= WORLD_Z_MAX)

    def b(self, x, y, z, block):
        if not self._in_bounds(x, y, z):
            self.oob_count += 1
            msg = (f"範囲外ブロック ({x},{y},{z}) {block} — "
                   f"許容 X:{WORLD_X_MIN}-{WORLD_X_MAX} "
                   f"Y:{WORLD_Y_MIN}-{WORLD_Y_MAX} "
                   f"Z:{WORLD_Z_MIN}-{WORLD_Z_MAX}")
            if self.strict:
                raise ValueError(msg)
            print(f"    [WARN] {msg}")
            return
        self.s.setBlock((x, y, z), block)

    def fill(self, x1, y1, z1, x2, y2, z2, block):
        for x in range(min(x1,x2), max(x1,x2)+1):
            for y in range(min(y1,y2), max(y1,y2)+1):
                for z in range(min(z1,z2), max(z1,z2)+1):
                    self.b(x, y, z, block)

    # ─── 地面 ───────────────────────────────────────────────────
    def gen_ground(self):
        print("  [1/9] 地面を生成...")
        self.fill(0, 0, 0, WORLD_X_MAX, 0, WORLD_Z_MAX, "minecraft:grass_block")
        self.fill(0, -1, 0, WORLD_X_MAX, -1, WORLD_Z_MAX, "minecraft:dirt")

        # 高架下の地面は暗い石畳
        self.fill(ROAD_X_START, 0, ROAD_Z_MIN,
                  ROAD_X_END,  0, ROAD_Z_MAX, "minecraft:deepslate_tiles")

    # ─── 高架ビアダクト ─────────────────────────────────────────
    def gen_elevated_highway(self):
        print("  [2/9] 高架ビアダクトを生成...")

        # ── 支柱基礎（地面 → 高架デッキ下） ──
        for px in range(ROAD_X_START, ROAD_X_END + 1, PILLAR_INTERVAL):
            for pz in [ROAD_Z_MIN, (ROAD_Z_MIN + ROAD_Z_MAX)//2, ROAD_Z_MAX]:
                # 縦柱
                self.fill(px, 1, pz, px, ROAD_ELEV - 1, pz, "minecraft:smooth_stone")
                # 柱キャップ
                self.b(px, ROAD_ELEV, pz, "minecraft:polished_deepslate")

            # 水平クロスブレース（Y=3）
            for z in range(ROAD_Z_MIN, ROAD_Z_MAX + 1):
                self.b(px, 3, z, "minecraft:smooth_stone_slab[type=bottom]")

            # LED 側面灯
            if px % 16 == ROAD_X_START % 16:
                self.b(px, ROAD_ELEV + 1, ROAD_Z_MIN - 1, "minecraft:sea_lantern")
                self.b(px, ROAD_ELEV + 1, ROAD_Z_MAX + 1, "minecraft:sea_lantern")

        # ── デッキ本体（支持スラブ） ──
        self.fill(ROAD_X_START, ROAD_ELEV - 1, ROAD_Z_MIN,
                  ROAD_X_END,   ROAD_ELEV - 1, ROAD_Z_MAX,
                  "minecraft:smooth_stone")

        # ── 車線色 ──
        for _, zrange, block, _ in LANES:
            self.fill(ROAD_X_START, ROAD_ELEV, zrange.start,
                      ROAD_X_END,   ROAD_ELEV, zrange.stop - 1, block)

        # ── 車線境界白線（4ブロック間隔）──
        for wx in range(ROAD_X_START, ROAD_X_END + 1, 4):
            for wz in [25, 29, 33, 55, 59, 63]:
                self.b(wx, ROAD_ELEV, wz, "minecraft:white_concrete")

        # ── 中央分離帯の樹木 ──
        for tx in range(ROAD_X_START + 4, ROAD_X_END, 10):
            self._viaduct_tree(tx, ROAD_ELEV, MEDIAN_Z)

        # ── ガードレール ──
        for rx in range(ROAD_X_START, ROAD_X_END + 1):
            self.b(rx, ROAD_ELEV + 1, ROAD_Z_MIN - 1, "minecraft:iron_bars")
            self.b(rx, ROAD_ELEV + 1, ROAD_Z_MAX + 1, "minecraft:iron_bars")
            self.b(rx, ROAD_ELEV + 1, 33, "minecraft:iron_bars")
            self.b(rx, ROAD_ELEV + 1, 56, "minecraft:iron_bars")

        # ── 道路端 LED 帯 ──
        for rx in range(ROAD_X_START, ROAD_X_END + 1, 2):
            self.b(rx, ROAD_ELEV, ROAD_Z_MIN - 1, "minecraft:sea_lantern")
            self.b(rx, ROAD_ELEV, ROAD_Z_MAX + 1, "minecraft:sea_lantern")

        # ── 進入ランプ (A側: X=38→30 を Y=0→6 へ段階スロープ) ──
        self._entry_ramp(ROAD_X_START, ascending=True)   # A→高架
        self._entry_ramp(ROAD_X_END,   ascending=False)  # 高架→B

    def _viaduct_tree(self, x, base_y, z):
        for dy in range(1, 4):
            self.b(x, base_y + dy, z, "minecraft:oak_log")
        for dy in range(2, 6):
            for dz in range(-2, 3):
                for dx in range(-1, 2):
                    if abs(dx) + abs(dz) + abs(dy - 4) <= 3:
                        self.b(x + dx, base_y + dy, z + dz,
                               "minecraft:oak_leaves[persistent=true]")

    def _entry_ramp(self, gate_x, ascending=True):
        """ランプ: 6段階スラブで Y=0→6 を緩やかに上る"""
        direction = -1 if ascending else 1
        for step in range(ROAD_ELEV):
            rx = gate_x + direction * (ROAD_ELEV - step)
            for z in range(ROAD_Z_MIN, ROAD_Z_MAX + 1):
                self.b(rx, step + 1, z, "minecraft:smooth_stone")
            # ガードレール
            self.b(rx, step + 2, ROAD_Z_MIN - 1, "minecraft:iron_bars")
            self.b(rx, step + 2, ROAD_Z_MAX + 1, "minecraft:iron_bars")

    # ─── 自動運転車 ─────────────────────────────────────────────
    def gen_cars(self):
        print("  [3/9] 自動運転車を配置...")
        RY = ROAD_ELEV + 1  # 車の床面 Y

        # A→B 急行
        for cx, cz in [(52,22),(84,23),(118,22)]:
            self._car(cx, RY, cz, east=True, ctype="express")
        # A→B 通常
        for cx, cz in [(60,27),(95,26),(138,27)]:
            self._car(cx, RY, cz, east=True, ctype="normal")
        # A→B 合乗バス
        for cx, cz in [(47,31),(75,30),(112,31),(148,30)]:
            self._car(cx, RY, cz, east=True, ctype="shared")
        # B→A 急行
        for cx, cz in [(148,65),(112,64),(76,65)]:
            self._car(cx, RY, cz, east=False, ctype="express")
        # B→A 通常
        for cx, cz in [(132,61),(96,60)]:
            self._car(cx, RY, cz, east=False, ctype="normal")
        # B→A 合乗
        for cx, cz in [(145,57),(108,56),(70,57)]:
            self._car(cx, RY, cz, east=False, ctype="shared")

    def _car(self, cx, cy, cz, east=True, ctype="normal"):
        """自動運転車 (4×2×2, 精細版)"""
        # 車体寸法
        big  = ctype == "shared"
        L    = 5 if big else 4
        H    = 2
        W_off= 1   # 幅は z+0 〜 z+1

        body  = "minecraft:white_concrete"
        glass = "minecraft:light_blue_stained_glass"
        roof_map = {"express": "minecraft:red_concrete",
                    "normal":  "minecraft:yellow_concrete",
                    "shared":  "minecraft:light_blue_concrete"}
        roof_color = roof_map[ctype]

        # 車体下部
        self.fill(cx, cy, cz, cx + L - 1, cy, cz + W_off, body)
        # 車体上部
        self.fill(cx, cy + 1, cz, cx + L - 1, cy + 1, cz + W_off, body)
        # フロントガラス
        front_x = cx + (L - 1 if east else 0)
        self.b(front_x, cy + 1, cz,       glass)
        self.b(front_x, cy + 1, cz + W_off, glass)
        # ルーフアクセント
        self.fill(cx + 1, cy + 2, cz, cx + L - 2, cy + 2, cz + W_off, roof_color)
        # タイヤ（黒）
        for tz in [cz, cz + W_off]:
            self.b(cx,         cy, tz, "minecraft:black_concrete")
            self.b(cx + L - 1, cy, tz, "minecraft:black_concrete")
        # ヘッドライト
        head_x = cx + (L - 1 if east else 0)
        self.b(head_x, cy + 1, cz,       "minecraft:sea_lantern")
        self.b(head_x, cy + 1, cz + W_off, "minecraft:sea_lantern")
        # テールランプ（赤：後部）
        tail_x = cx + (0 if east else L - 1)
        self.b(tail_x, cy + 1, cz,       "minecraft:red_stained_glass")
        self.b(tail_x, cy + 1, cz + W_off, "minecraft:red_stained_glass")
        # 合乗バスの側面窓（乗客表現）
        if big:
            side_x = cx + 1
            for wx in range(side_x, cx + L - 1):
                self.b(wx, cy + 1, cz - 0,  glass)

    # ─── 生存圏 ─────────────────────────────────────────────────
    def gen_zones(self):
        print("  [4/9] 生存圏A を生成...")
        self._gen_zone(0, ZONE_A_END, "A")
        print("  [5/9] 生存圏B を生成...")
        self._gen_zone(ZONE_B_START, ZONE_B_END, "B")

    def _gen_zone(self, x_start, x_end, label):
        rng = random.Random(SEED + ord(label))

        # 地面（コンクリート舗装）
        self.fill(x_start, 0, 0, x_end, 0, 89, "minecraft:light_gray_concrete")

        # ── 地下駐車場 ──
        self._underground_parking(x_start, x_end, label)

        # ── 内部グリッド道路 ──
        for gx in range(x_start + 7, x_end, 8):
            if gx <= x_end:
                self.fill(gx, 0, 0, gx, 0, 89, "minecraft:smooth_stone")
        for gz in range(7, 90, 8):
            self.fill(x_start, 0, gz, x_end, 0, gz, "minecraft:smooth_stone")

        # ── 建物配置 ──
        buildings = []
        for gx_s in range(x_start, x_end, 8):
            for gz_s in range(0, 89, 8):
                bx = gx_s + 1
                bz = gz_s + 1
                bw = min(6, x_end - gx_s - 1)
                bd = 6
                if bw < 2 or bz + bd > 89:
                    continue
                h_choice = rng.choice([0, 0, 5, 8, 10, 13, 16, 20, 24, 28])
                if h_choice == 0:
                    # 広場
                    self._plaza(bx, bz, bw, bd, rng)
                else:
                    btype = rng.choice(["office", "residential", "mixed"])
                    self._building(bx, bz, bw, h_choice, bd, label, btype, rng)
                    buildings.append((bx, bz, bw, bd, h_choice))

        # ── 歩行者デッキ（Y=10 空中歩廊） ──
        self._pedestrian_deck(x_start, x_end, label, buildings)

        # ── インフラ施設 ──
        self._infrastructure(x_start, x_end, label, rng)

    def _underground_parking(self, x_start, x_end, label):
        """地下駐車場 Y=-5 〜 Y=-1"""
        # 空間
        self.fill(x_start, UG_BOT, 0, x_end, UG_TOP, 89, "minecraft:air")
        # 床
        self.fill(x_start, UG_BOT, 0, x_end, UG_BOT, 89, "minecraft:smooth_stone")
        # 天井（地面直下）
        self.fill(x_start, -1, 0, x_end, -1, 89, "minecraft:smooth_stone")
        # 照明
        for lx in range(x_start + 4, x_end, 8):
            for lz in range(4, 90, 8):
                self.b(lx, -2, lz, "minecraft:sea_lantern")
        # 駐車スペース境界（白線）
        for lx in range(x_start + 3, x_end, 6):
            self.fill(lx, UG_BOT, 0, lx, UG_BOT, 89, "minecraft:white_concrete")
        # 入口スロープ（端に傾斜）
        ramp_x = x_start + 2 if label == "A" else x_end - 2
        for step in range(5):
            y_pos = -5 + step
            z_pos = step
            self.fill(ramp_x, y_pos, z_pos, ramp_x, y_pos, z_pos + 1, "minecraft:smooth_stone_slab[type=bottom]")

    def _plaza(self, bx, bz, bw, bd, rng):
        """広場・公園エリア"""
        self.fill(bx, 0, bz, bx + bw - 1, 0, bz + bd - 1, "minecraft:moss_block")
        if rng.random() > 0.4:
            tx = bx + bw // 2
            tz = bz + bd // 2
            for ty in range(1, 4):
                self.b(tx, ty, tz, "minecraft:oak_log")
            for dy in range(2, 5):
                for dz in range(-1, 2):
                    for dx in range(-1, 2):
                        if abs(dx)+abs(dz)+abs(dy-3) <= 2:
                            self.b(tx+dx, dy, tz+dz, "minecraft:oak_leaves[persistent=true]")

    def _building(self, bx, bz, bw, bh, bd, label, btype, rng):
        """3種類の建物を生成"""
        is_a = label == "A"
        wall_a = rng.choice(["minecraft:cyan_concrete","minecraft:blue_concrete",
                              "minecraft:light_blue_concrete","minecraft:white_concrete"])
        wall_b = rng.choice(["minecraft:purple_concrete","minecraft:magenta_concrete",
                              "minecraft:pink_concrete","minecraft:white_concrete"])
        wall   = wall_a if is_a else wall_b

        if btype == "office":
            self._build_office(bx, bz, bw, bh, bd, wall, rng)
        elif btype == "residential":
            self._build_residential(bx, bz, bw, bh, bd, wall, rng)
        else:
            self._build_mixed(bx, bz, bw, bh, bd, wall, rng)

    def _build_office(self, bx, bz, bw, bh, bd, wall, rng):
        """オフィスタワー: ガラス多め・縦長"""
        for y in range(1, bh + 1):
            for xx in range(bx, bx + bw):
                for zz in range(bz, bz + bd):
                    on_wall = (xx == bx or xx == bx+bw-1 or
                               zz == bz or zz == bz+bd-1)
                    if not on_wall:
                        continue
                    if y % 3 != 1:  # ガラス多め
                        self.b(xx, y, zz, "minecraft:glass")
                    else:
                        self.b(xx, y, zz, wall)
        self._roof_features(bx, bz, bw, bh, bd, wall, rng, antenna=True, solar=True)

    def _build_residential(self, bx, bz, bw, bh, bd, wall, rng):
        """住居タワー: 低層ポディウム + 上層セットバック"""
        pod_h = min(5, bh // 3)
        # ポディウム（広め）
        for y in range(1, pod_h + 1):
            for xx in range(bx - 1, bx + bw + 1):
                for zz in range(bz - 1, bz + bd + 1):
                    if (0 <= xx <= 199 and 0 <= zz <= 89):
                        on_wall = (xx==bx-1 or xx==bx+bw or zz==bz-1 or zz==bz+bd)
                        self.b(xx, y, zz, wall if on_wall else "minecraft:air")
        # タワー部分（小さめ）
        tw = max(2, bw - 2)
        td = max(2, bd - 2)
        tx, tz = bx + 1, bz + 1
        for y in range(pod_h + 1, bh + 1):
            for xx in range(tx, tx + tw):
                for zz in range(tz, tz + td):
                    on_wall = (xx==tx or xx==tx+tw-1 or zz==tz or zz==tz+td-1)
                    if not on_wall:
                        continue
                    if y % 4 == 2 and xx not in [tx, tx+tw-1]:
                        self.b(xx, y, zz, "minecraft:glass")
                    else:
                        self.b(xx, y, zz, wall)
        self._roof_features(tx, tz, tw, bh, td, wall, rng, antenna=(bh>16), solar=True)

    def _build_mixed(self, bx, bz, bw, bh, bd, wall, rng):
        """複合用途: 地上階グラス商業 + 上層住居"""
        # 1〜3階: ガラス張り商業
        for y in range(1, 4):
            for xx in range(bx, bx + bw):
                for zz in range(bz, bz + bd):
                    on_wall = (xx==bx or xx==bx+bw-1 or zz==bz or zz==bz+bd-1)
                    if on_wall:
                        self.b(xx, y, zz, "minecraft:glass")
        # 4階〜: コンクリート住居
        for y in range(4, bh + 1):
            for xx in range(bx, bx + bw):
                for zz in range(bz, bz + bd):
                    on_wall = (xx==bx or xx==bx+bw-1 or zz==bz or zz==bz+bd-1)
                    if not on_wall:
                        continue
                    if y % 3 == 0 and xx not in [bx, bx+bw-1]:
                        self.b(xx, y, zz, "minecraft:glass")
                    else:
                        self.b(xx, y, zz, wall)
        self._roof_features(bx, bz, bw, bh, bd, wall, rng, antenna=(bh>18), solar=True)

    def _roof_features(self, bx, bz, bw, bh, bd, wall, rng, antenna=False, solar=False):
        """屋上設備"""
        # パラペット
        self.fill(bx, bh+1, bz, bx+bw-1, bh+1, bz+bd-1, "minecraft:dark_prismarine")
        # 太陽光パネル（daylight_detector）
        if solar and bw >= 4 and bd >= 4:
            self.fill(bx+1, bh+2, bz+1, bx+bw-2, bh+2, bz+bd-2,
                      "minecraft:daylight_detector")
        # アンテナ
        if antenna and bh >= 12:
            ax = bx + bw // 2
            az = bz + bd // 2
            for ay in range(bh + 3, bh + 7):
                self.b(ax, ay, az, "minecraft:lightning_rod")
            self.b(ax, bh + 7, az, "minecraft:sea_lantern")

    def _pedestrian_deck(self, x_start, x_end, label, buildings):
        """Y=10 空中歩行者デッキ（建物間の橋）"""
        if len(buildings) < 2:
            return
        DECK_Y = DECK_ELEV
        visited_z = set()
        for (bx, bz, bw, bd, bh) in buildings:
            if bh < DECK_Y:
                continue
            for gz in range(0, 89, 8):
                if abs(bz - gz) > 2 and gz not in visited_z:
                    continue
                deck_z = gz + 3
                # デッキ床
                self.fill(bx, DECK_Y, deck_z, bx + bw - 1, DECK_Y, deck_z + 2,
                          "minecraft:polished_deepslate")
                # 手すり
                for dx in range(bw):
                    self.b(bx + dx, DECK_Y + 1, deck_z,     "minecraft:iron_bars")
                    self.b(bx + dx, DECK_Y + 1, deck_z + 2, "minecraft:iron_bars")
                visited_z.add(gz)

        # ゾーン内の主要歩廊（X方向）
        mid_z = MEDIAN_Z
        for bridge_x in range(x_start + 4, x_end - 4, 8):
            col_h = DECK_Y
            # 支柱
            self.fill(bridge_x, 1, mid_z, bridge_x, col_h - 1, mid_z,
                      "minecraft:iron_bars")
            # 歩廊床
            self.b(bridge_x, col_h, mid_z, "minecraft:polished_deepslate")
            self.b(bridge_x, col_h, mid_z+1, "minecraft:polished_deepslate")

    def _infrastructure(self, x_start, x_end, label, rng):
        """インフラ施設: 交通管制タワー + 変電設備"""
        is_a = label == "A"

        # 交通管制タワー
        ctl_x = x_start + 3 if is_a else x_end - 3
        ctl_z = 4
        self.fill(ctl_x, 1, ctl_z, ctl_x, 12, ctl_z, "minecraft:smooth_quartz")
        self.fill(ctl_x - 1, 10, ctl_z - 1, ctl_x + 1, 12, ctl_z + 1,
                  "minecraft:glass")
        self.b(ctl_x, 13, ctl_z, "minecraft:sea_lantern")

        # 変電所
        sub_x = x_start + 3 if is_a else x_end - 3
        sub_z = 80
        self.fill(sub_x - 1, 1, sub_z - 1, sub_x + 2, 3, sub_z + 2,
                  "minecraft:iron_block")
        self.fill(sub_x, 4, sub_z, sub_x + 1, 4, sub_z + 1, "minecraft:sea_lantern")

    # ─── ゲート ─────────────────────────────────────────────────
    def gen_gates(self):
        print("  [6/9] 入口ゲートを生成...")
        for gate_x in [ROAD_X_START, ROAD_X_END]:
            # 縦柱（高さ 20 ブロック）
            for gz in [ROAD_Z_MIN, ROAD_Z_MAX]:
                self.fill(gate_x, 0, gz, gate_x, 20, gz, "minecraft:polished_deepslate")
            # 横梁
            self.fill(gate_x, 20, ROAD_Z_MIN, gate_x, 20, ROAD_Z_MAX,
                      "minecraft:polished_deepslate")
            # 照明
            for gz in range(ROAD_Z_MIN, ROAD_Z_MAX + 1, 6):
                self.b(gate_x, 20, gz, "minecraft:sea_lantern")
            # 中央ビーコン（ゾーンID）
            for gz in [MEDIAN_Z, MEDIAN_Z + 1]:
                self.b(gate_x, 22, gz, "minecraft:beacon")
            # ゲート下をアーチ状に空ける
            self.fill(gate_x, ROAD_ELEV + 1, ROAD_Z_MIN + 1,
                      gate_x, 18, ROAD_Z_MAX - 1, "minecraft:air")

    # ─── 車線案内サイン ─────────────────────────────────────────
    def gen_signs(self):
        print("  [7/9] 車線案内サインを生成...")
        SIGN_Y = ROAD_ELEV + 8
        for sx in SIGN_X:
            # 支柱
            for sy in range(ROAD_ELEV + 2, SIGN_Y + 1):
                self.b(sx, sy, ROAD_Z_MIN - 2, "minecraft:iron_bars")
                self.b(sx, sy, ROAD_Z_MAX + 2, "minecraft:iron_bars")
            # 横断看板
            for sz in range(ROAD_Z_MIN - 2, ROAD_Z_MAX + 3):
                self.b(sx, SIGN_Y, sz, "minecraft:cyan_glazed_terracotta")
            # 急行ゾーン（赤）
            for sz in range(ROAD_Z_MIN, 26):
                self.b(sx, SIGN_Y, sz, "minecraft:red_glazed_terracotta")
            # 通常ゾーン（黄）
            for sz in range(26, 30):
                self.b(sx, SIGN_Y, sz, "minecraft:yellow_glazed_terracotta")
            # 合乗ゾーン（青）
            for sz in range(30, 34):
                self.b(sx, SIGN_Y, sz, "minecraft:blue_glazed_terracotta")
            # B→A 側
            for sz in range(56, 60):
                self.b(sx, SIGN_Y, sz, "minecraft:blue_glazed_terracotta")
            for sz in range(60, 64):
                self.b(sx, SIGN_Y, sz, "minecraft:yellow_glazed_terracotta")
            for sz in range(64, ROAD_Z_MAX + 1):
                self.b(sx, SIGN_Y, sz, "minecraft:red_glazed_terracotta")

    # ─── 植生 ───────────────────────────────────────────────────
    def gen_vegetation(self):
        print("  [8/9] 植生を配置...")
        rng = random.Random(SEED + 999)
        # ゾーン縁の街路樹
        for zone_x, zone_end in [(0, ZONE_A_END), (ZONE_B_START, ZONE_B_END)]:
            for vx in range(zone_x + 2, zone_end, 5):
                for vz in [2, 87]:
                    tree_type = rng.choice(["oak", "birch", "bamboo"])
                    self._street_tree(vx, 0, vz, tree_type)

    def _street_tree(self, x, y, z, ttype="oak"):
        if ttype == "bamboo":
            for dy in range(1, 6):
                self.b(x, y + dy, z, "minecraft:bamboo[leaves=no_leaves,stage=0]")
            return
        log  = f"minecraft:{ttype}_log"
        leaf = f"minecraft:{ttype}_leaves[persistent=true]"
        for dy in range(1, 5):
            self.b(x, y + dy, z, log)
        for dy in range(3, 6):
            for dz in range(-1, 2):
                for dx in range(-1, 2):
                    if abs(dx) + abs(dz) + abs(dy - 4) <= 2:
                        self.b(x + dx, y + dy, z + dz, leaf)

    # ─── メイン ─────────────────────────────────────────────────
    def generate(self, out=".", name="mirai_sonken_v2"):
        print()
        print("=" * 60)
        print("  未来の生存圏 × 自動運転モビリティ  v2.0  (120%)")
        print("=" * 60)
        print()

        self.gen_ground()
        self.gen_elevated_highway()
        self.gen_cars()
        self.gen_zones()
        self.gen_gates()
        self.gen_signs()
        self.gen_vegetation()

        print(f"  [9/9] .schem を保存中...")
        self.s.save(out, name, VERSION)
        print()
        if self.oob_count:
            print(f"  [WARN] 範囲外として {self.oob_count} ブロックをスキップしました")
            print()
        print(f"  [OK] {name}.schem を生成しました！")
        print()
        print("  [ワールドマップ]")
        print(f"    X:  0- {ZONE_A_END}  生存圏A  (地下駐車 + 歩行者デッキ)")
        print(f"    X: {ROAD_X_START}-{ROAD_X_END}  高架自動運転道路  Y={ROAD_ELEV}  支柱ビアダクト")
        print(f"    X:{ZONE_B_START}-{ZONE_B_END}  生存圏B  (地下駐車 + 歩行者デッキ)")
        print()
        print("  [高架道路構造]")
        print(f"    Y= -5〜-1  地下駐車場")
        print(f"    Y=  0      地面（石畳 / 草地）")
        print(f"    Y=  1〜 5  支柱群（8ブロック間隔）")
        print(f"    Y=  6      高架道路面（3色車線）")
        print(f"    Y= 10      歩行者デッキ")
        print()
        print("  [インポート手順]")
        print("    1. .schem を schematics/ フォルダへコピー")
        print(f"    2. //schem load {name}")
        print("    3. //paste -a")
        print()


def parse_args(argv=None):
    p = argparse.ArgumentParser(
        description="未来の生存圏 × 自動運転モビリティ Minecraft schematic 生成器")
    p.add_argument("--out", default=".",
                   help="出力先ディレクトリ (デフォルト: カレント)")
    p.add_argument("--name", default="mirai_sonken_v2",
                   help="schematic ファイル名 (拡張子なし)")
    p.add_argument("--strict", action="store_true",
                   help="範囲外ブロックを警告でスキップせず例外で停止する")
    return p.parse_args(argv)


if __name__ == "__main__":
    args  = parse_args()
    world = MiraiSonkenWorld(strict=args.strict)
    try:
        world.generate(out=args.out, name=args.name)
    except ValueError as e:
        print(f"  [ERROR] strict モードで停止: {e}", file=sys.stderr)
        sys.exit(1)
