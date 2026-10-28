import { defineSprite } from '../engine/sprite';
import { nether } from '../palette';

// 막대 위 작은 얼굴 아이콘. 9x9, neutral / happy

export const faceIcon = defineSprite(
  'faceIcon',
  {
    K: nether.void,
    Y: nether.lavaHot,
    y: nether.lavaLight,
  },
  {
    neutral: [
      [
        '..KKKKK..',
        '.KYYYYYK.',
        'KYYKYKYYK',
        'KYYKYKYYK',
        'KYYYYYYYK',
        'KYYYYYYYK',
        'KyYKKKYyK',
        '.KyyyyyK.',
        '..KKKKK..',
      ],
    ],
    happy: [
      [
        '..KKKKK..',
        '.KYYYYYK.',
        'KYYKYKYYK',
        'KYYKYKYYK',
        'KYYYYYYYK',
        'KyKYYYKyK',
        'KYYKKKYYK',
        '.KyyyyyK.',
        '..KKKKK..',
      ],
    ],
  },
);
