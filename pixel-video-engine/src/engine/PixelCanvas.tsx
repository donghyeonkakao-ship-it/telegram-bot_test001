import React, { useCallback, useLayoutEffect, useRef } from 'react';
import { AbsoluteFill, useVideoConfig } from 'remotion';
import { FONTS, useFontsReady } from './fonts';
import { Painter } from './painter';

/** 모든 장면의 논리 해상도. 출력(1280x720)은 정확히 SCALE배 확대. */
export const LOGICAL_WIDTH = 320;
export const LOGICAL_HEIGHT = 180;
export const SCALE = 4;

export type DrawFn = (p: Painter) => void;

/**
 * 320x180 캔버스에 그리고 CSS로 4배 확대(nearest-neighbor)한다.
 * draw는 "현재 프레임만으로 결정되는 순수 함수"여야 한다. 매 렌더마다 화면 전체를 다시 그린다.
 */
export const PixelCanvas: React.FC<{ draw: DrawFn }> = ({ draw }) => {
  const { width, height } = useVideoConfig();
  if (width !== LOGICAL_WIDTH * SCALE || height !== LOGICAL_HEIGHT * SCALE) {
    throw new Error(`PixelCanvas: 컴포지션은 ${LOGICAL_WIDTH * SCALE}x${LOGICAL_HEIGHT * SCALE}이어야 함 (현재 ${width}x${height})`);
  }

  const canvasRef = useRef<HTMLCanvasElement>(null);
  const drawRef = useRef(draw);
  drawRef.current = draw;

  const paint = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    drawRef.current(new Painter(ctx, LOGICAL_WIDTH, LOGICAL_HEIGHT));
  }, []);

  // 캔버스 라벨용 픽셀 폰트가 로드되기 전에는 그리지 않는다
  const ready = useFontsReady([FONTS.pixel], paint);

  useLayoutEffect(() => {
    if (ready) paint();
  }, [ready, draw, paint]);

  return (
    <AbsoluteFill>
      <canvas
        ref={canvasRef}
        width={LOGICAL_WIDTH}
        height={LOGICAL_HEIGHT}
        style={{
          width: LOGICAL_WIDTH * SCALE,
          height: LOGICAL_HEIGHT * SCALE,
          imageRendering: 'pixelated',
          display: 'block',
        }}
      />
    </AbsoluteFill>
  );
};
