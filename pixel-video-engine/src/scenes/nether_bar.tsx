import React from 'react';
import { z } from 'zod';
import { animStep, easing, loopFrame, onceFrame } from '../engine/anim';
import type { Painter } from '../engine/painter';
import { LOGICAL_HEIGHT, LOGICAL_WIDTH, PixelCanvas } from '../engine/PixelCanvas';
import { defineScene, type SceneProps } from '../engine/scene';
import { hash01, randInt, seededList } from '../engine/seededRandom';
import { chainTween } from '../engine/tween';
import { nether as C, type PaletteColor } from '../palette';
import { blaze } from '../sprites/blaze';
import { HERO_BODY_X, HERO_H, hero, heroHead } from '../sprites/hero';
import { BLOCK, cobblestone, darkenRack, emeraldBlock, glowstone, lavaAt, netherrack } from '../textures/blocks';

// 장면: Minecraft 네더. "정상 확률" 조약돌 기둥과 "실제 결과" 에메랄드 블록 기둥을 비교한다.
// 월드는 1블록 = 16px 격자. 기둥은 반블록(슬랩, 8px) = 10% 단위.

const propsSchema = z.object({
  /** 왼쪽 조약돌 기둥(기준 확률) % */
  left: z.number().min(0).max(100),
  /** 오른쪽 에메랄드 기둥(실제 값) % — 줄이 바뀌면 이전 값에서 이어서 쌓인다 */
  right: z.number().min(0).max(100),
});

type Props = z.output<typeof propsSchema>;

// ── 레이아웃 (논리 좌표 320x180) ──────────────────────────
const H = LOGICAL_HEIGHT;
const CEIL_Y = BLOCK; // 천장 블록 한 줄
const FLOOR_Y = 120; // 바닥(네더랙 한 줄) 윗면 = 기둥 바닥
const LAVA_Y = FLOOR_Y + BLOCK; // 136, 하단 약 1/4이 용암 바다
const CAMERA_MAX = 32;
const WORLD_W = LOGICAL_WIDTH + CAMERA_MAX;
const COLS = Math.ceil(WORLD_W / BLOCK);

const SLAB = 8; // 반블록 = 10%
const PX_PER_PERCENT = SLAB / 10;
const LEFT_BAR = { x: 20, w: BLOCK * 2 };
const RIGHT_BAR = { x: 250, w: BLOCK * 2 };
const FILL_FRAMES = 24; // 쌓이기 약 1초
const HERO_X = 128; // 몸 왼쪽 끝(월드)

// 천장: 열마다 아래로 매달린 네더랙 블록 수, 그 아래 발광석
const CEIL_DEPTH = [1, 2, 1, 1, 1, 0, 0, 0, 1, 2, 1, 0, 1, 0, 0, 0, 1, 2, 1, 0, 1, 2];
const GLOWSTONE = new Set([3, 9, 13, 19, 20]);
// 용암폭포 열 (천장 구멍에서 쏟아짐). 카메라 팬 중에도 기둥·라벨 영역을 가로지르지 않는 위치
const LAVA_FALL_COLS = [6, 11, 14];

const EMBERS = seededList(0xe1b3, 26, (rng) => ({
  x: Math.floor(rng() * WORLD_W),
  phase: Math.floor(rng() * 200),
  speed: 0.5 + rng() * 0.7,
  sway: rng() * 5,
  hot: rng() < 0.4,
}));

const BLAZES = seededList(0xb1a2e, 6, (rng, i) => ({
  // 월드 폭을 6칸으로 나눠 한 칸에 하나씩
  x: Math.floor((i * WORLD_W) / 6 + rng() * (WORLD_W / 6 - blaze.width)),
  y: randInt(rng, 40, FLOOR_Y - blaze.height - 10),
  phase: randInt(rng, 0, 31),
  drift: randInt(rng, 2, 6),
}));

// ── 월드 레이어 ───────────────────────────────────────────

function drawCave(p: Painter, step: number) {
  // 먼 벽: 한 단계 어두운 네더랙
  p.texture(netherrack, 0, CEIL_Y, WORLD_W, FLOOR_Y - CEIL_Y, { map: darkenRack });

  // 용암폭포 (천장 구멍 → 바닥 뒤 용암 바다)
  for (const col of LAVA_FALL_COLS) {
    p.pattern(col * BLOCK, 0, BLOCK, LAVA_Y, (wx, wy) => lavaAt(wx, wy, step, 3));
  }

  // 천장 + 매달린 블록 + 발광석
  for (let col = 0; col < COLS; col++) {
    const x = col * BLOCK;
    if (!LAVA_FALL_COLS.includes(col)) p.texture(netherrack, x, 0, BLOCK, CEIL_Y);
    const depth = CEIL_DEPTH[col] ?? 0;
    if (depth > 0) p.texture(netherrack, x, CEIL_Y, BLOCK, depth * BLOCK);
    if (GLOWSTONE.has(col)) p.texture(glowstone, x, CEIL_Y + depth * BLOCK, BLOCK, BLOCK);
  }
}

function drawGround(p: Painter, step: number) {
  p.texture(netherrack, 0, FLOOR_Y, WORLD_W, BLOCK);
  p.pattern(0, LAVA_Y, WORLD_W, H - LAVA_Y, (wx, wy) => lavaAt(wx, wy, step));
}

function drawEmbers(p: Painter, step: number) {
  EMBERS.forEach((e, i) => {
    const rise = (e.phase + step * e.speed) % (LAVA_Y - CEIL_Y);
    const y = LAVA_Y - 2 - rise;
    const x = e.x + Math.sin((step + e.phase) * 0.15) * e.sway;
    if (hash01(i, step >> 1, 3) < 0.25) return; // 깜빡임
    p.pixel(x, y, e.hot ? C.lavaHot : C.lavaLight);
  });
}

function drawBlazes(p: Painter, step: number) {
  const BOB = [0, -1, -2, -1];
  BLAZES.forEach((b, i) => {
    const t = step + b.phase;
    const bob = BOB[Math.floor(t / 2) % 4];
    const x = Math.round(b.x + Math.sin(t / 14) * b.drift);
    const y = b.y + bob;
    p.sprite(blaze.anims.spin[t % 4], x, y);
    // 머리 위로 피어오르는 연기
    for (let k = 0; k < 3; k++) {
      const age = (t + k * 3) % 9;
      if (hash01(i, k, Math.floor((t + k * 3) / 9)) < 0.3) continue;
      p.pixel(x + 7 + Math.floor(hash01(i, k, 7) * 6), y - 1 - age, age < 4 ? C.stone : C.shadow);
    }
  });
}

function drawHero(p: Painter, frame: number, lineStartFrame: number) {
  // 줄이 바뀔 때마다 한 번 휘두르고(휩쓸기 공격), 나머지는 숨쉬기 idle
  const atk = onceFrame(frame, lineStartFrame, 3, 2);
  const sprite = atk !== null ? hero.anims.attack[atk] : hero.anims.idle[loopFrame(frame, 2, 3)];
  p.sprite(sprite, HERO_X - HERO_BODY_X, FLOOR_Y - HERO_H);
}

// ── 기둥 UI (화면 고정) ───────────────────────────────────

/** Minecraft 이름표: 검은 판 + 글씨. bottom = 판 아래쪽 y */
function nameTag(p: Painter, text: string, cx: number, bottom: number, color: PaletteColor = C.white) {
  const { width, height } = p.measureText(text);
  const x = Math.round(cx - width / 2);
  const y = bottom - height;
  p.rect(x - 1, y - 1, width + 1, height, C.black);
  p.text(text, x, y - 1, { color });
}

function drawStonePillar(p: Painter, percent: number) {
  const { x, w } = LEFT_BAR;
  const h = Math.round(percent * PX_PER_PERCENT);
  const top = FLOOR_Y - h;
  if (h > 0) {
    p.frame(x - 1, top - 1, w + 2, h + 1, C.black);
    p.texture(cobblestone, x, top, w, h, { originX: x, originY: FLOOR_Y });
  }
  nameTag(p, `정상 ${Math.round(percent)}%`, x + w / 2, top - 4);
}

function drawEmeraldPillar(p: Painter, value: number, target: number, compareTo: number, step: number) {
  const { x, w } = RIGHT_BAR;
  const cx = x + w / 2;

  // 반블록(슬랩) 단위로 쌓기
  const slabs = Math.round(value / 10);
  const h = slabs * SLAB;
  const top = FLOOR_Y - h;
  if (h > 0) {
    p.frame(x - 1, top - 1, w + 2, h + 1, C.black);
    p.texture(emeraldBlock, x, top, w, h, { originX: x, originY: FLOOR_Y });
    p.rect(x, top, w, 1, C.emeraldLight); // 맨 위 슬랩 윗면
  }

  // 50% 기준 점선 + 라벨
  const midY = FLOOR_Y - 50 * PX_PER_PERCENT;
  p.dashedHLine(x - 4, midY, w + 8, C.white, 2, 2);
  p.text('50%', x + w + 5, midY - 6, { color: C.white, shadow: C.shadow });

  // 플레이어 머리 아이콘 + 기준보다 높으면 행복 파티클(초록 반짝이)
  const head = heroHead.anims.icon[0];
  const headX = Math.round(cx - head.width / 2);
  const headY = top - head.height - 2;
  p.sprite(head, headX, headY);
  if (value > compareTo + 5) {
    for (let k = 0; k < 4; k++) {
      if (hash01(k, step >> 1, 11) < 0.45) continue;
      const sx = headX - 6 + Math.floor(hash01(k, step >> 1, 12) * (head.width + 12));
      const sy = headY - 4 + Math.floor(hash01(k, step >> 1, 13) * (head.height + 4));
      p.rect(sx - 1, sy, 3, 1, C.emerald);
      p.rect(sx, sy - 1, 1, 3, C.emerald);
      p.pixel(sx, sy, C.emeraldLight);
    }
  }

  // 쌓이는 중에는 슬랩 수와 같은 값, 도착하면 정확한 목표값
  const shown = Math.abs(value - target) < 0.5 ? Math.round(target) : slabs * 10;
  nameTag(p, `${shown}%`, cx, headY - 3, C.emeraldLight);
}

// ── 장면 ─────────────────────────────────────────────────

function drawScene(p: Painter, s: SceneProps<Props>) {
  const { frame, props, history, lineStartFrame } = s;
  const step = animStep(frame);

  // 카메라: 장면 시작부터 8프레임에 1px씩 오른쪽으로 (UI 모션이라 매 프레임 계산, 정수 스냅)
  const camX = Math.min(CAMERA_MAX, Math.floor(frame / 8));

  p.withOffset(-camX, 0, () => {
    drawCave(p, step);
    drawBlazes(p, step);
    drawGround(p, step);
    drawHero(p, frame, lineStartFrame);
    drawEmbers(p, step);
  });

  const right = chainTween(history, frame, (h) => h.right, { duration: FILL_FRAMES, easing: easing.easeOutCubic, initial: 0 });
  drawStonePillar(p, props.left);
  drawEmeraldPillar(p, right, props.right, props.left, step);
}

const NetherBar: React.FC<SceneProps<Props>> = (s) => <PixelCanvas draw={(p) => drawScene(p, s)} />;

export const netherBar = defineScene({
  id: 'nether_bar',
  propsSchema,
  component: NetherBar,
});
