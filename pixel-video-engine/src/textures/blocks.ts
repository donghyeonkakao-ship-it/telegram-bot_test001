import { defineTexture, type Grid } from '../engine/sprite';
import { hash01 } from '../engine/seededRandom';
import { nether } from '../palette';

// Minecraft 스타일 16x16 블록 텍스처 (1블록 = 16px, 텍셀 1개 = 1px). 원본 파일을 쓰지 않고 코드로 다시 그렸다.

export const BLOCK = 16;

/** 네더랙: 붉은 바탕에 어둡고 밝은 얼룩. 시드 노이즈로 만든 뒤 고정 — 모든 블록이 같은 무늬로 반복된다. */
const netherrackRows: Grid = Array.from({ length: BLOCK }, (_, y) =>
  Array.from({ length: BLOCK }, (_, x) => {
    const n = (dx: number, dy: number) => hash01((x + dx) & 15, (y + dy) & 15, 0x4e7);
    const v = (n(0, 0) * 3 + n(1, 0) + n(-1, 0) + n(0, 1) + n(0, -1)) / 7;
    if (n(0, 0) > 0.94 || v < 0.37) return 'd';
    if (v > 0.6) return 'l';
    return 'm';
  }).join(''),
);

export const netherrack = defineTexture('netherrack', { d: nether.rackDark, m: nether.rack, l: nether.rackLight }, netherrackRows);

/** 먼 벽용: 네더랙을 한 단계씩 어둡게 */
export const darkenRack = (c: string) =>
  c === nether.rackLight ? nether.rack : c === nether.rack ? nether.rackDark : nether.black;

export const cobblestone = defineTexture(
  'cobblestone',
  { L: nether.stoneLight, S: nether.stone, D: nether.shadow, K: nether.black },
  [
    'LLSSDKSLLLSSDKLS',
    'LSSSDKSLSSSSDKSS',
    'SSSDDKSSSSSDDKSD',
    'DDDKKDDSSSDDKKDD',
    'SLLSSDKDDDKLLSSD',
    'LSSSSSDKSLSLSSSD',
    'SSSSSDDKLSSSSSDD',
    'DSSSDDKKSSSSDDKS',
    'KDDDKKLLSDDDKKLL',
    'SLLSDKSSSSDKLSSS',
    'LSSSDKSSSDDKSSSS',
    'SSSDDKDDDDKKSSSD',
    'DDDKKLLSSDKSSDDK',
    'LLSDKSSSSDKDDKKS',
    'SSSDKSSSDDKLSSSS',
    'SDDKKDDDDKKSSSSD',
  ],
);

/** 에메랄드 블록: 밝은 테두리 + 가운데 마름모 보석 (왼쪽 위 밝음, 오른쪽 아래 어두움) */
export const emeraldBlock = defineTexture(
  'emeraldBlock',
  { A: nether.emeraldLight, E: nether.emerald, d: nether.emeraldDark },
  [
    'AAAAAAAAAAAAAAAE',
    'AEEEEEEEEEEEEEEd',
    'AEAAEEEEEEEEAAEd',
    'AEAEEEEAAEEEEdEd',
    'AEEEEEAEEdEEEEEd',
    'AEEEEAEEEEdEEEEd',
    'AEEEAEEEEEEdEEEd',
    'AEEAEEEEEEEEdEEd',
    'AEEdEEEEEEEEAEEd',
    'AEEEdEEEEEEAEEEd',
    'AEEEEdEEEEAEEEEd',
    'AEEEEEdEEAEEEEEd',
    'AEAEEEEddEEEEAEd',
    'AEddEEEEEEEEddEd',
    'AEEEEEEEEEEEEEEd',
    'Eddddddddddddddd',
  ],
);

export const glowstone = defineTexture(
  'glowstone',
  { Y: nether.lavaHot, y: nether.lavaLight, b: nether.rack },
  [
    'bYYybyYYYbyyYYby',
    'yYYYyyYYYyYYYyyb',
    'YYyYbyYyybYYYYyb',
    'ybbyyYYbbYyyYybb',
    'byYYYybyYYYybyYY',
    'yYYYYYyyYYyYyYYY',
    'YYyYYybbyYYYbyYy',
    'ybbyybYyybyybbyb',
    'YYYybyYYYyYYYbyY',
    'YyYYyYYyYYYyYyYY',
    'bYYYbyYYbyyYYYyb',
    'ybyyyYYYYbbyyybb',
    'YYYbyYyYYyYYbyYY',
    'YyYYbyyyYYYYyYYy',
    'yYYyybYYbyYyyYyb',
    'bbyybyyybbybbybb',
  ],
);

/** 16px 주기로 반복되는 값 노이즈 (격자 4칸, smoothstep 보간). x, y는 실수 허용. */
function tileNoise(x: number, y: number, seed: number): number {
  const CELL = 4;
  const N = BLOCK / CELL;
  const gx = x / CELL;
  const gy = y / CELL;
  const x0 = Math.floor(gx);
  const y0 = Math.floor(gy);
  const fx = gx - x0;
  const fy = gy - y0;
  const s = (t: number) => t * t * (3 - 2 * t);
  const at = (i: number, j: number) => hash01(((i % N) + N) % N, ((j % N) + N) % N, seed);
  const top = at(x0, y0) + (at(x0 + 1, y0) - at(x0, y0)) * s(fx);
  const bottom = at(x0, y0 + 1) + (at(x0 + 1, y0 + 1) - at(x0, y0 + 1)) * s(fx);
  return top + (bottom - top) * s(fy);
}

/**
 * 용암: 주황 바탕에 붉은 얼룩과 노란 줄기가 천천히 뒤섞이는 무늬(16px 반복).
 * step(4프레임 단위)마다 바뀐다. flowY > 0이면 아래로 흐른다(용암폭포).
 */
export function lavaAt(wx: number, wy: number, step: number, flowY = 0) {
  const tx = ((wx % BLOCK) + BLOCK) % BLOCK;
  const ty = wy - step * flowY;
  const v =
    tileNoise(tx + step * 0.5, ty, 0x1a7a) * 0.6 +
    tileNoise(tx, ty + step * 0.35, 0x2b8b) * 0.4 +
    (hash01(tx, ((ty % BLOCK) + BLOCK) % BLOCK, 0x3c9c) - 0.5) * 0.12;
  // 분포 기준(실측 분위수): 최고온 ~10%, 밝은 줄 ~20%, 기본 주황 ~50%, 붉은 얼룩 ~20%
  if (v > 0.81) return nether.lavaHot;
  if (v > 0.7) return nether.lavaLight;
  if (v > 0.48) return nether.lava;
  return nether.lavaDark;
}
