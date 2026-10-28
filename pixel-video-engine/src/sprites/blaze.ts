import { blankGrid, defineSprite, stamp, type Grid } from '../engine/sprite';
import { nether } from '../palette';

// 블레이즈(Minecraft 네더 몹): 8x8 노란 머리 + 아래에서 세 층으로 회전하는 막대(2x6) 12개.
// 회전은 4장 스프라이트로 미리 조립한다 (막대 4개씩이라 90°마다 같은 모양 → 22.5°씩 4프레임).

const COLORS = {
  Y: nether.lavaHot,
  y: nether.lavaLight,
  o: nether.lava,
  r: nether.lavaDark,
  K: nether.black,
};

const HEAD: Grid = [
  'YyYYYyYY',
  'yYYyYYYy',
  'YYyYYyYY',
  'ooorrooo',
  'KKKYYKKK',
  'YyYYYYyY',
  'YYrrrrYY',
  'yYYyyYYy',
];

const W = 20;
const H = 32;
const CX = 10;

function frame(i: number): Grid {
  const back: [number, number][] = [];
  const front: [number, number][] = [];
  const rings = [
    { y: 9, r: 8, dir: 1 },
    { y: 17, r: 7, dir: -1 },
    { y: 25, r: 4, dir: 1 },
  ];
  rings.forEach(({ y, r, dir }, ri) => {
    for (let k = 0; k < 4; k++) {
      const a = dir * i * (Math.PI / 8) + (k * Math.PI) / 2 + ri * 0.4;
      const x = Math.round(CX + Math.cos(a) * r) - 1;
      (Math.sin(a) < 0 ? back : front).push([x, y]);
    }
  });
  const rod = (c: string): Grid => Array.from({ length: 6 }, () => c + c);
  let g = blankGrid(W, H);
  for (const [x, y] of back) g = stamp(g, rod('o'), x, y); // 머리 뒤쪽 막대는 어둡게
  g = stamp(g, HEAD, CX - 4, 0);
  for (const [x, y] of front) g = stamp(g, ['yY', 'yY', 'yY', 'yy', 'yo', 'oo'], x, y);
  return g;
}

export const blaze = defineSprite('blaze', COLORS, {
  spin: [frame(0), frame(1), frame(2), frame(3)],
});
