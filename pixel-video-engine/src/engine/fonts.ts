import { useEffect, useRef, useState } from 'react';
import { cancelRender, continueRender, delayRender, staticFile } from 'remotion';

// 폰트 파일은 npm install 시 public/fonts로 복사된다 (scripts/copy-fonts.mjs).

export const FONTS = {
  /** 캔버스 안 UI 라벨용 한글 픽셀 폰트. 12px(및 정수배)에서 픽셀 그리드에 맞는다. */
  pixel: { family: 'Galmuri11', file: 'fonts/Galmuri11.woff2', weight: '400', size: 12 },
  /** 자막용 (캔버스 바깥 1280x720 레이어) */
  subtitle: { family: 'Pretendard', file: 'fonts/Pretendard-Bold.woff2', weight: '700' },
} as const;

type FontDef = { family: string; file: string; weight: string };

const cache = new Map<string, Promise<void>>();

export function loadFont({ family, file, weight }: FontDef): Promise<void> {
  const key = `${family}/${weight}`;
  let p = cache.get(key);
  if (!p) {
    const face = new FontFace(family, `url(${staticFile(file)}) format('woff2')`, { weight });
    p = face.load().then((loaded) => {
      document.fonts.add(loaded);
    });
    cache.set(key, p);
  }
  return p;
}

/**
 * 폰트가 로드될 때까지 Remotion 렌더를 잡아둔다(delayRender).
 * onReady는 continueRender 직전에 동기로 호출되므로, 그 안에서 그린 결과가 스크린샷에 들어간다.
 */
export function useFontsReady(fonts: FontDef[], onReady?: () => void): boolean {
  const [handle] = useState(() => delayRender(`fonts: ${fonts.map((f) => f.family).join(', ')}`));
  const [ready, setReady] = useState(false);
  const onReadyRef = useRef(onReady);
  onReadyRef.current = onReady;

  useEffect(() => {
    let alive = true;
    Promise.all(fonts.map(loadFont))
      .then(() => {
        if (alive) {
          setReady(true);
          onReadyRef.current?.();
        }
        continueRender(handle);
      })
      .catch((err) => cancelRender(err));
    return () => {
      alive = false;
    };
    // fonts 목록은 컴포넌트 수명 동안 고정
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [handle]);

  return ready;
}
