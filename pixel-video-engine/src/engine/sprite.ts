import type { PaletteColor } from '../palette';

// 스프라이트 = 문자 그리드 + 색 매핑. '.'은 항상 투명.

export type SpriteColors = Record<string, PaletteColor>;

export type SpriteFrame = {
  width: number;
  height: number;
  /** 행 우선, null = 투명 */
  pixels: (PaletteColor | null)[];
};

export type SpriteSheet<A extends string> = {
  width: number;
  height: number;
  anims: Record<A, SpriteFrame[]>;
};

/**
 * 애니메이션별 프레임 그리드를 파싱한다.
 * 모든 프레임은 같은 크기여야 한다(기준점이 흔들리지 않도록). 크기가 다르거나
 * 색 매핑에 없는 문자가 있으면 모듈 로드 시점에 에러를 낸다.
 */
export function defineSprite<A extends string>(
  name: string,
  colors: SpriteColors,
  anims: Record<A, string[][]>,
): SpriteSheet<A> {
  let width = -1;
  let height = -1;
  const parsed = {} as Record<A, SpriteFrame[]>;

  for (const anim of Object.keys(anims) as A[]) {
    parsed[anim] = anims[anim].map((rows, fi) => {
      const where = `sprite "${name}" ${anim}[${fi}]`;
      const h = rows.length;
      const w = rows[0]?.length ?? 0;
      if (width === -1) {
        width = w;
        height = h;
      }
      if (h !== height) throw new Error(`${where}: 높이 ${h} ≠ ${height}`);
      const pixels: (PaletteColor | null)[] = [];
      rows.forEach((row, y) => {
        if (row.length !== width) throw new Error(`${where} row ${y}: 너비 ${row.length} ≠ ${width}`);
        for (const ch of row) {
          if (ch === '.') {
            pixels.push(null);
            continue;
          }
          const c = colors[ch];
          if (!c) throw new Error(`${where} row ${y}: 색 매핑에 없는 문자 "${ch}"`);
          pixels.push(c);
        }
      });
      return { width, height, pixels };
    });
  }
  return { width, height, anims: parsed };
}

export type DrawSpriteOptions = {
  flipX?: boolean;
  /** 정수 배율만 허용 */
  scale?: number;
};

/** 스프라이트 한 프레임을 (x, y) 좌상단 기준으로 그린다. 좌표는 정수로 스냅된다. */
export function drawSprite(
  ctx: CanvasRenderingContext2D,
  sprite: SpriteFrame,
  x: number,
  y: number,
  { flipX = false, scale = 1 }: DrawSpriteOptions = {},
): void {
  if (!Number.isInteger(scale) || scale < 1) throw new Error(`drawSprite: scale은 1 이상의 정수 (받은 값 ${scale})`);
  const ox = Math.round(x);
  const oy = Math.round(y);
  const { width, height, pixels } = sprite;

  for (let row = 0; row < height; row++) {
    // 같은 색이 이어지는 구간은 사각형 하나로 그린다
    let runStart = 0;
    let runColor: PaletteColor | null = null;
    for (let col = 0; col <= width; col++) {
      const src = col < width ? pixels[row * width + (flipX ? width - 1 - col : col)] : null;
      if (src !== runColor || col === width) {
        if (runColor) {
          ctx.fillStyle = runColor;
          ctx.fillRect(ox + runStart * scale, oy + row * scale, (col - runStart) * scale, scale);
        }
        runStart = col;
        runColor = src;
      }
    }
  }
}
