import type { PaletteColor } from '../palette';
import { FONTS } from './fonts';
import { drawSprite, type DrawSpriteOptions, type SpriteFrame } from './sprite';

// 장면은 ctx 대신 Painter로만 그린다.
// Painter는 모든 좌표·크기를 그리기 직전에 Math.round하고, 색은 PaletteColor만 받는다.
// 원·점선·텍스트도 1px 사각형 단위로 그려 안티앨리어싱이 생기지 않는다.

const r = Math.round;

export type TextAlign = 'left' | 'center' | 'right';

export type TextOptions = {
  color: PaletteColor;
  /** 1px 외곽선 색 (8방향) */
  outline?: PaletteColor;
  align?: TextAlign;
};

type TextMask = { width: number; height: number; on: Uint8Array };

const textMaskCache = new Map<string, TextMask>();

/**
 * 픽셀 폰트를 오프스크린 캔버스에 그린 뒤 알파를 이진화해서 1비트 마스크로 만든다.
 * 폰트가 그리드에 정확히 맞지 않더라도 반투명 픽셀이 화면에 나가지 않는다.
 */
function getTextMask(text: string): TextMask {
  const { family, size } = FONTS.pixel;
  const key = `${family}/${size}/${text}`;
  const hit = textMaskCache.get(key);
  if (hit) return hit;

  const font = `${size}px ${family}`;
  const c = document.createElement('canvas');
  const mctx = c.getContext('2d')!;
  mctx.font = font;
  const width = Math.ceil(mctx.measureText(text).width) + 2;
  const height = size + 4;
  c.width = width;
  c.height = height;
  mctx.font = font;
  mctx.textBaseline = 'top';
  mctx.fillStyle = '#000';
  mctx.fillText(text, 1, 1);

  const data = mctx.getImageData(0, 0, width, height).data;
  const on = new Uint8Array(width * height);
  for (let i = 0; i < on.length; i++) on[i] = data[i * 4 + 3] >= 128 ? 1 : 0;

  const mask = { width, height, on };
  textMaskCache.set(key, mask);
  return mask;
}

export class Painter {
  readonly width: number;
  readonly height: number;
  private ox = 0;
  private oy = 0;

  constructor(
    readonly ctx: CanvasRenderingContext2D,
    width: number,
    height: number,
  ) {
    this.width = width;
    this.height = height;
    ctx.imageSmoothingEnabled = false;
  }

  /** 카메라/레이어 오프셋. 오프셋도 정수로 스냅된다. */
  withOffset(dx: number, dy: number, fn: () => void): void {
    const px = this.ox;
    const py = this.oy;
    this.ox = px + r(dx);
    this.oy = py + r(dy);
    try {
      fn();
    } finally {
      this.ox = px;
      this.oy = py;
    }
  }

  clear(color: PaletteColor): void {
    this.ctx.fillStyle = color;
    this.ctx.fillRect(0, 0, this.width, this.height);
  }

  rect(x: number, y: number, w: number, h: number, color: PaletteColor): void {
    const x0 = r(x) + this.ox;
    const y0 = r(y) + this.oy;
    const rw = r(w);
    const rh = r(h);
    if (rw <= 0 || rh <= 0) return;
    this.ctx.fillStyle = color;
    this.ctx.fillRect(x0, y0, rw, rh);
  }

  pixel(x: number, y: number, color: PaletteColor): void {
    this.rect(x, y, 1, 1, color);
  }

  /** 테두리만 있는 사각형 (1px) */
  frame(x: number, y: number, w: number, h: number, color: PaletteColor): void {
    const [rx, ry, rw, rh] = [r(x), r(y), r(w), r(h)];
    this.rect(rx, ry, rw, 1, color);
    this.rect(rx, ry + rh - 1, rw, 1, color);
    this.rect(rx, ry, 1, rh, color);
    this.rect(rx + rw - 1, ry, 1, rh, color);
  }

  /** 가로 점선. dash px 그리고 gap px 비우기를 반복 */
  dashedHLine(x: number, y: number, w: number, color: PaletteColor, dash = 2, gap = 2): void {
    const rx = r(x);
    const rw = r(w);
    for (let i = 0; i < rw; i += dash + gap) this.rect(rx + i, y, Math.min(dash, rw - i), 1, color);
  }

  /** 픽셀 원(채움): 행마다 정수 폭의 가로줄로 그린다 */
  disc(cx: number, cy: number, radius: number, color: PaletteColor): void {
    const rcx = r(cx);
    const rcy = r(cy);
    const rr = r(radius);
    for (let dy = -rr; dy <= rr; dy++) {
      const half = Math.floor(Math.sqrt(rr * rr - dy * dy + rr * 0.8));
      this.rect(rcx - half, rcy + dy, half * 2 + 1, 1, color);
    }
  }

  sprite(frame: SpriteFrame, x: number, y: number, opts?: DrawSpriteOptions): void {
    drawSprite(this.ctx, frame, r(x) + this.ox, r(y) + this.oy, opts);
  }

  measureText(text: string): { width: number; height: number } {
    const m = getTextMask(text);
    return { width: m.width, height: m.height };
  }

  /** Galmuri11 픽셀 텍스트. (x, y)는 정렬 기준점의 상단. */
  text(text: string, x: number, y: number, { color, outline, align = 'left' }: TextOptions): void {
    const m = getTextMask(text);
    let x0 = r(x);
    if (align === 'center') x0 -= Math.floor(m.width / 2);
    if (align === 'right') x0 -= m.width;
    const y0 = r(y);

    const at = (mx: number, my: number) =>
      mx >= 0 && my >= 0 && mx < m.width && my < m.height ? m.on[my * m.width + mx] : 0;

    if (outline) {
      for (let my = -1; my <= m.height; my++) {
        for (let mx = -1; mx <= m.width; mx++) {
          if (at(mx, my)) continue;
          let near = 0;
          for (let dy = -1; dy <= 1 && !near; dy++) for (let dx = -1; dx <= 1 && !near; dx++) near = at(mx + dx, my + dy);
          if (near) this.rect(x0 + mx, y0 + my, 1, 1, outline);
        }
      }
    }
    for (let my = 0; my < m.height; my++) {
      for (let mx = 0; mx < m.width; mx++) {
        if (at(mx, my)) this.rect(x0 + mx, y0 + my, 1, 1, color);
      }
    }
  }
}
