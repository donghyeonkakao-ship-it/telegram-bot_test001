import React from 'react';
import { Composition } from 'remotion';
import rawScript from '../script.json';
import { VIDEO } from './config';
import { validateScript } from './engine/script';
import { buildTimeline } from './engine/timeline';
import { Main, type MainProps } from './Main';
import { sceneRegistry } from './scenes/registry';

export const RemotionRoot: React.FC = () => (
  <Composition
    id="Main"
    component={Main}
    width={VIDEO.width}
    height={VIDEO.height}
    fps={VIDEO.fps}
    durationInFrames={1}
    defaultProps={{ script: null } as MainProps}
    // 렌더 시작 전에 대본을 검증한다. 미등록 scene·잘못된 props면 여기서 에러로 중단.
    calculateMetadata={({ props }) => {
      const script = validateScript(props.script ?? rawScript, sceneRegistry);
      const { durationInFrames } = buildTimeline(script, VIDEO.fps);
      return { durationInFrames, props: { ...props, script } };
    }}
  />
);
