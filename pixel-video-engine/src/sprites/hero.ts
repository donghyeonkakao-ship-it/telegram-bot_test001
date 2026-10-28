import { blankGrid, defineSprite, flipGridY, rotateCW, stamp, type Grid } from '../engine/sprite';
import { nether } from '../palette';

// 주인공: Minecraft 플레이어 모델 비율(앞모습). 텍셀 1개 = 1px이라 블록(16px)과 크기가 맞는다.
// 머리 8x8, 몸통 8x12, 팔 4x12, 다리 4x12 → 16x32 (블록 2칸 높이). 초록 머리 스킨 + 철 흉갑 + 다이아몬드 검.
// 포즈는 부위 그리드를 찍어서 조립한다.

const COLORS = {
  G: nether.emerald, // 피부
  g: nether.emeraldDark,
  W: nether.white,
  K: nether.black,
  C: nether.diamond, // 검날
  I: nether.stoneLight, // 철 흉갑
  S: nether.stone, // 흉갑 그늘 / 신발
  D: nether.shadow, // 바지 / 검 손잡이 장식
  b: nether.rack, // 검 손잡이(나무)
  L: nether.stoneLight, // 휩쓸기 파티클
};

export const HEAD: Grid = [
  'gggggggg',
  'gGGGGGGg',
  'GGGGGGGG',
  'GWKGGKWG',
  'GGGggGGG',
  'GGgGGgGG',
  'GGGggGGG',
  'gGGGGGGg',
];

/** 철 흉갑을 입은 몸통 (초록 피부 + 청록 셔츠는 Minecraft 좀비와 겹쳐서 피함) */
const TORSO: Grid = [
  'ISIGGISI',
  'IIIIIIII',
  'IIIIIIII',
  'SIIIIIIS',
  'SIISSIIS',
  'SIIIIIIS',
  'SIIIIIIS',
  'SIIIIIIS',
  'SSSSSSSS',
  'DbDDDDbD',
  'DDDDDDDD',
  'DDDDDDDD',
];

const LEGS: Grid = [
  'DDDDDDDD',
  'DDDDDDDD',
  'DDDKKDDD',
  'DDDKKDDD',
  'DDDKKDDD',
  'DDDKKDDD',
  'DDDKKDDD',
  'DDDKKDDD',
  'DDDKKDDD',
  'DDDKKDDD',
  'SSSKKSSS',
  'SSSKKSSS',
];

/** 팔(아래로): 소매 4줄 + 피부 8줄 */
const ARM_DOWN: Grid = ['IIII', 'IIIS', 'IIIS', 'SSSS', 'GGGG', 'GGGG', 'GGGG', 'GGGG', 'GGGG', 'GGGG', 'GGGG', 'gggg'];
const ARM_UP = flipGridY(ARM_DOWN);
/** 팔(오른쪽으로 수평): 어깨 쪽이 왼쪽 */
const ARM_RIGHT: Grid = ['IIIIGGGGGGGg', 'IIIIGGGGGGGg', 'IIISGGGGGGGg', 'SSSSGGGGGGGg'];
/** 팔(오른쪽 아래 대각선): 4x4 덩어리를 대각선으로 이어 붙임 */
const ARM_DIAG = stamp(
  stamp(stamp(blankGrid(10, 10), ['IIII', 'IIIS', 'IIIS', 'SSSS'], 0, 0), ['GGGG', 'GGGG', 'GGGG', 'GGGG'], 3, 3),
  ['GGGG', 'GGGG', 'GGGG', 'gggg'],
  6,
  6,
);

/** 다이아몬드 검 아이템(오른쪽 위를 향함). 손잡이 중심 = (2, 11) */
const SWORD_DIAG: Grid = [
  '...........KKK',
  '..........KWWK',
  '.........KWCK.',
  '........KWCK..',
  '.......KWCK...',
  '......KWCK....',
  '..K..KWCK.....',
  '..KKKWCK......',
  '...KDCK.......',
  '...KbDKK......',
  '..KbK.KDK.....',
  '.KbK...KK.....',
  'KbK...........',
  'KK............',
];
/** 위를 향한 검. 손잡이 = 12~14행, 2~3열 */
const SWORD_UP: Grid = [
  '..KK..',
  '.KWCK.',
  '.KWCK.',
  '.KWCK.',
  '.KWCK.',
  '.KWCK.',
  '.KWCK.',
  '.KWCK.',
  '.KWCK.',
  '.KWCK.',
  '.KWCK.',
  'KDDDDK',
  '..bb..',
  '..bb..',
  '..bb..',
  '..KK..',
];
const SWORD_RIGHT = rotateCW(SWORD_UP); // 손잡이 = 1~3열, 2~3행
const SWORD_DOWN_DIAG = rotateCW(SWORD_DIAG); // 손잡이 중심 = (2, 2)

/** Minecraft 휩쓸기(sweep) 파티클: 앞쪽 초승달 */
const SWEEP: Grid = (() => {
  let g = blankGrid(16, 30);
  for (let a = -70; a <= 70; a += 4) {
    const rad = (a * Math.PI) / 180;
    for (const [rr, ch] of [
      [13, 'L'],
      [12, 'W'],
      [11, 'L'],
    ] as const) {
      const x = Math.round(Math.cos(rad) * rr);
      const y = Math.round(15 + Math.sin(rad) * rr);
      if (Math.abs(a) > 55 && ch === 'W') continue; // 끝은 가늘게
      g = stamp(g, [ch], x + 1, y);
    }
  }
  return g;
})();

// 캔버스 44x48. 몸 왼쪽 끝 x=4, 머리 위 y=16 (위쪽은 검을 치켜드는 공간)
export const HERO_W = 44;
export const HERO_H = 48;
const BX = 4;
const HEAD_Y = 16;
const TORSO_Y = HEAD_Y + 8;
const LEGS_Y = TORSO_Y + 12;
/** 스프라이트 안에서 몸(16px 폭)의 왼쪽 x — 배치할 때 기준 */
export const HERO_BODY_X = BX;

function body(lift = 0, rightArm?: (g: Grid) => Grid): Grid {
  let g = blankGrid(HERO_W, HERO_H);
  g = stamp(g, LEGS, BX + 4, LEGS_Y);
  g = stamp(g, TORSO, BX + 4, TORSO_Y + lift);
  g = stamp(g, HEAD, BX + 4, HEAD_Y + lift);
  g = stamp(g, ARM_DOWN, BX, TORSO_Y + lift);
  return rightArm ? rightArm(g) : g;
}

const RX = BX + 12; // 오른팔 x

const idle = (lift: number) =>
  body(lift, (g) => stamp(stamp(g, SWORD_DIAG, RX - 1, TORSO_Y + lift - 2), ARM_DOWN, RX, TORSO_Y + lift));

export const hero = defineSprite('hero', COLORS, {
  idle: [idle(0), idle(1)],
  attack: [
    // 0: 팔을 들어 검을 치켜듦
    body(0, (g) => stamp(stamp(g, SWORD_UP, RX - 1, TORSO_Y - 24), ARM_UP, RX, TORSO_Y - 12)),
    // 1: 수평으로 휘두름 + 휩쓸기 파티클
    body(0, (g) => stamp(stamp(stamp(g, SWEEP, RX + 13, TORSO_Y - 14), SWORD_RIGHT, RX + 8, TORSO_Y - 1), ARM_RIGHT, RX, TORSO_Y)),
    // 2: 오른쪽 아래로 내려벰
    body(0, (g) => stamp(stamp(g, SWORD_DOWN_DIAG, RX + 5, TORSO_Y + 5), ARM_DIAG, RX, TORSO_Y)),
  ],
});

/** 막대 위 아이콘: 주인공 머리(플레이어 헤드) + 1px 외곽선 */
export const heroHead = defineSprite('heroHead', COLORS, {
  icon: [stamp(['KKKKKKKKKK', ...Array.from({ length: 8 }, () => 'K........K'), 'KKKKKKKKKK'], HEAD, 1, 1)],
});
