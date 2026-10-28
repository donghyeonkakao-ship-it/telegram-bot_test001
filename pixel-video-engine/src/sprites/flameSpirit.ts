import { defineSprite } from '../engine/sprite';
import { nether } from '../palette';

// 불꽃 머리 정령(오리지널): 물방울 몸통 위에 불꽃이 타오르는 작은 정령. 11x14
// f 바깥 불꽃, y 안쪽 불꽃, c 심지, o 몸통, K 외곽선, w 눈 흰자, m 입

export const flameSpirit = defineSprite(
  'flameSpirit',
  {
    f: nether.lavaMid,
    y: nether.lavaLight,
    c: nether.lavaHot,
    o: nether.lavaDark,
    K: nether.void,
    w: nether.white,
    m: nether.brickDark,
  },
  {
    float: [
      [
        '.....f.....',
        '....ff..f..',
        '..f.fyf.f..',
        '..ffyyfff..',
        '.ffyycyyff.',
        '.fyyccccyf.',
        '..KKKKKKK..',
        '.KoooooooK.',
        'KoowKoowKoK',
        'KoowKoowKoK',
        'KoooooooooK',
        '.KoooommoK.',
        '..KKoooKK..',
        '....KKK....',
      ],
      [
        '...f.......',
        '...ff..f...',
        '..fyf.ff...',
        '..fyyffyf..',
        '.ffycyyyff.',
        '.fyyccccyf.',
        '..KKKKKKK..',
        '.KoooooooK.',
        'KoowKoowKoK',
        'KoowKoowKoK',
        'KoooooooooK',
        '.KoooommoK.',
        '..KKoooKK..',
        '....KKK....',
      ],
    ],
  },
);
