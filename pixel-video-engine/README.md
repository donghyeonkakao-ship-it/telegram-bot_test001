# pixel-video-engine

`script.json`만 바꾸면 나레이션 기반 2D 픽셀아트 해설 영상(1280x720, 24fps, H.264)이 나오는 Remotion 엔진.
현재 장면은 Minecraft 스타일(1블록 = 16px, 텍셀 1개 = 1px). 블록·몹 텍스처는 원본 파일을 쓰지 않고 코드로 다시 그렸다.

## 실행

```bash
npm install          # postinstall이 폰트(Pretendard Bold, Galmuri11)를 public/fonts로 복사
npm run dev          # Remotion Studio (미리보기)
npm run render       # out/video.mp4
npm run still -- out/x.png --frame=72   # 특정 프레임 스틸
./scripts/stills.sh  # 검증용 0/3/6/9초 스틸 → out/stills/
npm run typecheck
```

대본 검증(zod 구조, 시간 겹침, 미등록 scene, 장면별 props)은 `calculateMetadata`에서 렌더 전에 실행되어 실패하면 렌더가 시작되지 않는다.

## 구조

```
script.json            영상 전체 정의 (줄 단위: text, start, end, scene, props)
src/
  engine/
    PixelCanvas.tsx    320x180 캔버스 → CSS 4배 확대(pixelated). 폰트 로드 전엔 delayRender로 대기
    painter.ts         장면이 쓰는 유일한 그리기 API. 모든 좌표 Math.round, PaletteColor만 허용,
                       반복 텍스처(texture)·픽셀 함수(pattern)·디더링, 텍스트는 Galmuri11을
                       1비트 마스크로 이진화해서 그림(안티앨리어싱 없음, 외곽선/그림자 옵션)
    sprite.ts          defineSprite(문자 그리드 + 색 매핑), drawSprite(ctx, frame, x, y, {flipX, scale}),
                       부위 조립 도구(stamp, rotateCW, flipGridY), defineTexture
    seededRandom.ts    createRng / hash01 / seededList (Math.random 금지)
    anim.ts            ANIM_STEP=4, animStep / loopFrame / onceFrame, easing
    tween.ts           chainTween: 같은 장면에서 줄이 바뀔 때 이전 값에서 이어서 보간
    timeline.ts        script → 장면 구간(같은 scene 연속 줄은 한 구간), 현재 줄/props 이력
    script.ts          zod 스키마 + validateScript
    scene.ts           SceneProps / defineScene
    fonts.ts           FontFace 로딩 + useFontsReady(delayRender)
  scenes/
    nether_bar.tsx     Minecraft 네더: 조약돌 기둥(left) vs 에메랄드 블록 기둥(right, 슬랩=10% 단위)
    registry.ts        장면 등록
  sprites/             hero(플레이어 모델 비율, 철 흉갑, 다이아몬드 검, 휩쓸기 공격), heroHead, blaze
  textures/blocks.ts   16x16 블록 텍스처: 네더랙, 조약돌, 에메랄드 블록, 발광석, 용암(애니메이션)
  palette.ts           장면별 팔레트(8~16색, 개수·hex 검증), 자막용 ui 팔레트
  Subtitle.tsx         자막 + 워터마크 (1280x720 레이어, Pretendard Bold)
  config.ts            채널 워터마크 텍스트, 출력 크기/fps
```

## 렌더링 규칙 (엔진이 강제)

- 논리 해상도 320x180, 출력은 정확히 4배. 장면은 `Painter`로만 그린다 → 좌표 정수 스냅, 팔레트 색만 사용.
- 캐릭터·오브젝트 애니메이션은 `animStep(frame)`(4프레임 단위). 카메라·막대 같은 UI 모션만 매 프레임.
- 랜덤은 `seededRandom`만. 모든 그림은 frame만으로 결정되는 순수 함수.

## 새 장면 추가하는 법

1. `src/palette.ts`에 `definePalette('<id>', {...})`로 8~16색 팔레트를 추가한다.
2. 필요한 스프라이트는 `src/sprites/<name>.ts`에 `defineSprite`(문자 그리드)로, 블록은
   `src/textures/`에 `defineTexture`(16x16)로 만든다. 월드는 16px 블록 격자에 맞춘다.
3. `src/scenes/<id>.tsx`에 zod `propsSchema`와 `drawScene(p: Painter, s: SceneProps)`를 작성하고
   `defineScene({ id, propsSchema, component: (s) => <PixelCanvas draw={(p) => drawScene(p, s)} /> })`로 내보낸다.
   줄 사이 값 전환은 `chainTween(s.history, s.frame, (pr) => pr.값, {...})`.
4. `src/scenes/registry.ts`의 `scenes` 배열에 추가한다.
5. `script.json`에서 `"scene": "<id>"`로 사용한다.

## TODO (이번 범위 밖)

- TTS 연동: 나레이션 음성 생성 + 단어/문장 타임스탬프로 `start`/`end` 자동 생성, 오디오 트랙 삽입
- 장면 전환 효과 (현재는 하드 컷)
- 추가 장면들
- 긴 자막 자동 줄바꿈/분할 규칙, 자막 등장 애니메이션
- 폰트 서브셋(현재 Pretendard 전체 woff2 로드)
- Minecraft 폰트 느낌의 라벨용 픽셀 폰트 검토 (현재 Galmuri11)
