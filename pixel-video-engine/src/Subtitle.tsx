import React from 'react';
import { AbsoluteFill } from 'remotion';
import { CHANNEL } from './config';
import { FONTS, useFontsReady } from './engine/fonts';
import { ui } from './palette';

// 자막·워터마크는 픽셀 캔버스 바깥 1280x720 레이어에 그려 선명하게 유지한다.

const fontFamily = `${FONTS.subtitle.family}, sans-serif`;

export const Subtitle: React.FC<{ text: string | null }> = ({ text }) => {
  useFontsReady([FONTS.subtitle]);
  if (!text) return null;
  return (
    <AbsoluteFill style={{ justifyContent: 'flex-end', alignItems: 'center', paddingBottom: 44 }}>
      <div
        style={{
          fontFamily,
          fontWeight: 700,
          fontSize: 52,
          lineHeight: 1.25,
          color: ui.subtitleFill,
          WebkitTextStroke: `10px ${ui.subtitleStroke}`,
          paintOrder: 'stroke fill',
          textAlign: 'center',
          maxWidth: 1120,
          wordBreak: 'keep-all',
        }}
      >
        {text}
      </div>
    </AbsoluteFill>
  );
};

export const Watermark: React.FC = () => {
  useFontsReady([FONTS.subtitle]);
  return (
    <div
      style={{
        position: 'absolute',
        top: 20,
        right: 24,
        fontFamily,
        fontWeight: 700,
        fontSize: 20,
        color: ui.watermark,
        opacity: 0.55,
        WebkitTextStroke: `4px ${ui.subtitleStroke}`,
        paintOrder: 'stroke fill',
      }}
    >
      {CHANNEL.watermark}
    </div>
  );
};
