import type { SceneDef } from '../engine/scene';
import { netherBar } from './nether_bar';

// 새 장면은 scenes/<id>.tsx에서 defineScene으로 만들고 여기 배열에 추가한다.
const scenes = [netherBar];

export const sceneRegistry: Record<string, SceneDef<unknown>> = Object.fromEntries(
  scenes.map((s) => [s.id, s as unknown as SceneDef<unknown>]),
);

if (Object.keys(sceneRegistry).length !== scenes.length) {
  throw new Error('scenes/registry.ts: 중복된 scene id가 있음');
}
