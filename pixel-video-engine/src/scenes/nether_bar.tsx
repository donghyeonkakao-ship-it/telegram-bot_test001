import React from 'react';
import { z } from 'zod';
import { animStep, easing, loopFrame, onceFrame } from '../engine/anim';
import type { Painter } from '../engine/painter';
import { LOGICAL_HEIGHT, LOGICAL_WIDTH, PixelCanvas } from '../engine/PixelCanvas';
import { defineScene, type SceneProps } from '../engine/scene';
import { hash01, randInt, seededList } from '../engine/seededRandom';
import { chainTween } from '../engine/tween';
import { nether as C } from '../palette';
import { faceIcon } from '../sprites/faceIcon';
import { flameSpirit } from '../sprites/flameSpirit';
import { hero } from '../sprites/hero';

// 장면: 용암 동굴에서 "정상 확률" 돌 막대와 "실제 결과" 초록 블록 막대를 비교한다.

const propsSchema = z.object({
  /** 왼쪽 회색 돌 막대(기준 확률) % */
  left: z.number().min(0).max(100),
  /** 오른쪽 초록 블록 막대(실제 값) % — 줄이 바뀌면 이전 값에서 이어서 차오른다 */
  right: z.number().min(0).max(100),
});

type Props = z.output<typeof propsSchema>;

// ── 레이아웃 (논리 좌표 320x180) ──────────────────────────
const W = LOGICAL_WIDTH;
const H = LOGICAL_HEIGHT;
const LAVA_Y = 135; // 하단 1/4
const FLOOR_Y = 128; // 바닥 윗면 = 막대 바닥
const PX_PER_PERCENT = 1; // 100% = 100px
const CAMERA_MAX = 32;
const WORLD_W = W + CAMERA_MAX;

const LEFT_BAR = { x: 30, w: 22 };
const RIGHT_BAR = { x: 258, w: 22 };
const BLOCK = 5; // 초록 막대 블록 1칸 = 5%
const FILL_FRAMES = 24; // 차오르기 약 1초
const HERO_X = 128;
const HERO_SCALE = 2;

// 카메라 팬(최대 32px) 동안에도 막대·라벨 영역(화면 x 18~64, 250~320)을 가로지르지 않는 위치
const LAVA_FALLS = [
  { x: 12, w: 5 },
  { x: 100, w: 5 },
  { x: 180, w: 4 },
  { x: 236, w: 6 },
];

const EMBERS = seededList(0xe1b3, 26, (rng) => ({
  x: Math.floor(rng() * WORLD_W),
  phase: Math.floor(rng() * 200),
  speed: 0.5 + rng() * 0.7,
  sway: rng() * 6,
  hot: rng() < 0.4,
}));

const SPIRITS = seededList(0x5b17, 7, (rng, i) => ({
  // 화면 폭을 7칸으로 나눠 한 칸에 하나씩, 칸 안에서 위치는 랜덤
  x: Math.floor((i * WORLD_W) / 7 + rng() * (WORLD_W / 7 - 12)),
  y: randInt(rng, 14, 84),
  phase: randInt(rng, 0, 31),
  drift: randInt(rng, 3, 8),
}));

// ── 배경 레이어 ────────────────────────────────────────────

function drawBricks(p: Painter) {
  const BW = 16;
  const BH = 8;
  p.rect(0, 0, WORLD_W, FLOOR_Y, C.mortar);
  for (let row = 0; row * BH < FLOOR_Y; row++) {
    const offset = row % 2 === 0 ? 0 : BW / 2;
    for (let col = -1; col * BW < WORLD_W; col++) {
      const x = col * BW + offset;
      const y = row * BH;
      const n = hash01(col, row, 7);
      // 아래쪽(용암 가까이)일수록 밝은 벽돌이 많다
      const glow = row / (FLOOR_Y / BH);
      const fill = n < 0.15 + glow * 0.35 ? C.brickLight : n < 0.75 ? C.brickMid : C.brickDark;
      p.rect(x, y, BW - 1, BH - 1, fill);
      p.rect(x, y, BW - 1, 1, fill === C.brickLight ? C.lavaDark : C.brickLight);
      if (n > 0.85) p.rect(x + 3 + Math.floor(n * 40) % 8, y + 3, 2, 1, C.brickDark); // 금
    }
  }
  // 천장 쪽 어둠 (디더링)
  for (let y = 0; y < 14; y++) {
    for (let x = 0; x < WORLD_W; x++) {
      const density = 1 - y / 14;
      if (((x + y) % 2 === 0 && density > 0.3) || density > 0.85) p.pixel(x, y, C.void);
    }
  }
}

function drawLavaFalls(p: Painter, step: number) {
  for (const f of LAVA_FALLS) {
    for (let y = 0; y < FLOOR_Y + 2; y++) {
      const t = (((y - step * 3) % 10) + 10) % 10;
      const core = t < 2 ? C.lavaHot : t < 6 ? C.lavaLight : C.lavaMid;
      p.rect(f.x - 1, y, 1, 1, C.lavaDark);
      p.rect(f.x, y, 1, 1, C.lavaMid);
      p.rect(f.x + 1, y, f.w - 2, 1, core);
      p.rect(f.x + f.w - 1, y, 1, 1, C.lavaMid);
      p.rect(f.x + f.w, y, 1, 1, C.lavaDark);
    }
  }
}

function drawFloor(p: Painter) {
  p.rect(0, FLOOR_Y, WORLD_W, LAVA_Y - FLOOR_Y + 2, C.brickDark);
  p.rect(0, FLOOR_Y, WORLD_W, 1, C.stoneMid);
  p.rect(0, FLOOR_Y + 1, WORLD_W, 1, C.stoneDark);
  for (let x = 0; x < WORLD_W; x += 6) {
    const n = hash01(x, 91);
    p.rect(x, FLOOR_Y + 3 + Math.floor(n * 3), 3, 1, C.void);
  }
}

function drawLava(p: Painter, step: number) {
  const CELL = 2;
  for (let y = LAVA_Y - 2; y < H; y += CELL) {
    for (let x = 0; x < WORLD_W; x += CELL) {
      // 표면은 1px 단위로 출렁인다
      const surface = LAVA_Y + Math.round(Math.sin(x * 0.18 + step * 0.9));
      if (y + CELL <= surface) continue;
      const v =
        Math.sin(x * 0.11 + step * 0.6) + Math.sin(y * 0.45 - step * 0.8 + x * 0.03) + hash01(x, y, step >> 1) * 0.9;
      const color = v > 2.0 ? C.lavaHot : v > 1.2 ? C.lavaLight : v > -0.2 ? C.lavaMid : C.lavaDark;
      const top = Math.max(y, surface);
      p.rect(x, top, CELL, y + CELL - top, y < surface + 2 ? C.lavaLight : color);
    }
  }
}

function drawEmbers(p: Painter, step: number) {
  EMBERS.forEach((e, i) => {
    const rise = (e.phase + step * e.speed) % (LAVA_Y - 4);
    const y = LAVA_Y - 2 - rise;
    const x = e.x + Math.sin((step + e.phase) * 0.15) * e.sway;
    if (hash01(i, step >> 1, 3) < 0.25) return; // 깜빡임
    p.pixel(x, y, e.hot ? C.lavaHot : C.lavaLight);
    if (rise < 30) p.pixel(x, y + 1, C.lavaMid); // 막 튀어오른 불씨는 꼬리가 있다
  });
}

function drawSpirits(p: Painter, step: number) {
  const BOB = [0, -1, -2, -1];
  for (const s of SPIRITS) {
    const t = step + s.phase;
    const bob = BOB[Math.floor(t / 2) % 4];
    const dx = Math.sin(t / 14) * s.drift;
    const facingLeft = Math.cos(t / 14) < 0;
    const frame = flameSpirit.anims.float[t % 2];
    p.sprite(frame, s.x + dx, s.y + bob, { flipX: facingLeft });
  }
}

function drawHero(p: Painter, frame: number, lineStartFrame: number) {
  // 줄이 바뀔 때마다 한 번 휘두르고, 나머지는 숨쉬기 idle
  const atk = onceFrame(frame, lineStartFrame, 3, 2);
  const sprite = atk !== null ? hero.anims.attack[atk] : hero.anims.idle[loopFrame(frame, 2, 3)];
  p.sprite(sprite, HERO_X, FLOOR_Y - hero.height * HERO_SCALE, { scale: HERO_SCALE });
}

// ── 막대 UI (화면 고정) ───────────────────────────────────

function drawStoneBar(p: Painter, percent: number) {
  const { x, w } = LEFT_BAR;
  const h = Math.round(percent * PX_PER_PERCENT);
  const top = FLOOR_Y - h;
  if (h > 0) {
    p.rect(x - 1, top - 1, w + 2, h + 1, C.void);
    p.rect(x, top, w, h, C.stoneMid);
    p.rect(x, top, 2, h, C.stoneLight);
    p.rect(x + w - 2, top, 2, h, C.stoneDark);
    p.rect(x, top, w, 1, C.stoneLight);
    // 돌 블록 이음매 (바닥 기준 10px마다, 엇갈린 세로 이음)
    for (let k = 1; k * 10 < h; k++) {
      const sy = FLOOR_Y - k * 10;
      p.rect(x + 2, sy, w - 4, 1, C.stoneDark);
      p.rect(x + (k % 2 === 0 ? 8 : 14), sy + 1, 1, 9, C.stoneDark);
    }
  }
  p.text(`정상 ${Math.round(percent)}%`, x + w / 2, top - 16, { color: C.white, outline: C.void, align: 'center' });
}

function drawBlockBar(p: Painter, value: number, target: number, compareTo: number) {
  const { x, w } = RIGHT_BAR;
  const cx = x + Math.floor(w / 2);

  // 빈 트랙 (100%)
  const trackH = 100 * PX_PER_PERCENT;
  p.rect(x - 1, FLOOR_Y - trackH - 1, w + 2, trackH + 1, C.void);
  p.rect(x, FLOOR_Y - trackH, w, trackH, C.mortar);

  // 블록 단위로 채우기
  const blocks = Math.round(value / BLOCK);
  const bh = BLOCK * PX_PER_PERCENT;
  for (let b = 0; b < blocks; b++) {
    const by = FLOOR_Y - (b + 1) * bh;
    p.rect(x, by, w, bh, C.green);
    p.rect(x, by, w, 1, C.greenLight);
    p.rect(x, by, 1, bh, C.greenLight);
    p.rect(x + w - 1, by, 1, bh, C.greenDark);
    p.rect(x, by + bh - 1, w, 1, C.greenDark);
  }
  const fillTop = FLOOR_Y - blocks * bh;

  // 50% 기준 점선 + 라벨
  const midY = FLOOR_Y - 50 * PX_PER_PERCENT;
  p.dashedHLine(x - 6, midY, w + 12, C.white, 2, 2);
  p.text('50%', x + w + 9, midY - 6, { color: C.white, outline: C.void });

  // 얼굴 아이콘 + 현재 값
  const face = value > compareTo + 5 ? faceIcon.anims.happy[0] : faceIcon.anims.neutral[0];
  p.sprite(face, cx - Math.floor(face.width / 2), fillTop - face.height - 2);
  // 차오르는 중에는 블록 수와 같은 값, 도착하면 정확한 목표값
  const shown = Math.abs(value - target) < 0.5 ? Math.round(target) : blocks * BLOCK;
  p.text(`${shown}%`, cx, fillTop - face.height - 17, { color: C.greenLight, outline: C.void, align: 'center' });
}

// ── 장면 ─────────────────────────────────────────────────

function drawScene(p: Painter, s: SceneProps<Props>) {
  const { frame, props, history, lineStartFrame } = s;
  const step = animStep(frame);

  // 카메라: 장면 시작부터 8프레임에 1px씩 오른쪽으로 (UI 모션이라 매 프레임 계산, 정수 스냅)
  const camX = Math.min(CAMERA_MAX, Math.floor(frame / 8));

  p.withOffset(-camX, 0, () => {
    drawBricks(p);
    drawLavaFalls(p, step);
    drawSpirits(p, step);
    drawFloor(p);
    drawLava(p, step);
    drawHero(p, frame, lineStartFrame);
    drawEmbers(p, step);
  });

  const right = chainTween(history, frame, (h) => h.right, { duration: FILL_FRAMES, easing: easing.easeOutCubic, initial: 0 });
  drawStoneBar(p, props.left);
  drawBlockBar(p, right, props.right, props.left);
}

const NetherBar: React.FC<SceneProps<Props>> = (s) => <PixelCanvas draw={(p) => drawScene(p, s)} />;

export const netherBar = defineScene({
  id: 'nether_bar',
  propsSchema,
  component: NetherBar,
});
