import React, { useMemo } from 'react';
import { AbsoluteFill, Sequence, useCurrentFrame, useVideoConfig } from 'remotion';
import type { Script } from './engine/script';
import { buildTimeline, lineAt, sceneStateAt, type SceneSegment } from './engine/timeline';
import { sceneRegistry } from './scenes/registry';
import { Subtitle, Watermark } from './Subtitle';
import { ui } from './palette';

export type MainProps = {
  /** calculateMetadata에서 검증이 끝난 대본 */
  script: Script | null;
};

/** 한 장면 구간. Sequence 안이라 useCurrentFrame()이 구간 로컬 프레임이다. */
const SceneHost: React.FC<{ segment: SceneSegment }> = ({ segment }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const Scene = sceneRegistry[segment.sceneId].component;
  const state = sceneStateAt(segment, frame);
  return <Scene frame={frame} fps={fps} {...state} />;
};

export const Main: React.FC<MainProps> = ({ script }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  if (!script) throw new Error('Main: script가 없음 (calculateMetadata 확인)');
  const timeline = useMemo(() => buildTimeline(script, fps), [script, fps]);
  const line = lineAt(timeline, frame);

  return (
    <AbsoluteFill style={{ backgroundColor: ui.background }}>
      {timeline.segments.map((seg, i) => (
        // 구간 경계 = 하드 컷. 같은 scene이 이어지는 줄들은 한 Sequence 안에서 끊기지 않는다.
        <Sequence key={i} from={seg.from} durationInFrames={seg.durationInFrames} name={`${i}: ${seg.sceneId}`}>
          <SceneHost segment={seg} />
        </Sequence>
      ))}
      <Subtitle text={line?.text ?? null} />
      <Watermark />
    </AbsoluteFill>
  );
};
