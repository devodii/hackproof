import type { Card } from './_card'

const INK = '#f6f7f8'
const MUTED = '#a1a1aa'
const BRAND = '#fdda24'
const TILE = 'rgba(255, 255, 255, 0.045)'
const LINE = 'rgba(255, 255, 255, 0.12)'
const DIM = 'rgba(255, 255, 255, 0.075)'

const COLUMNS = 10
const ROWS = 5
const CELL = 34
const GAP = 8

type Node = {
  type: string
  props: { style?: Record<string, unknown>; children?: unknown; [key: string]: unknown }
}

function h(
  type: string,
  style: Record<string, unknown>,
  children?: unknown,
  extra: Record<string, unknown> = {},
): Node {
  return { type, props: { style: { display: 'flex', ...style }, children, ...extra } }
}

const eyebrow = (text: string, size = 17) =>
  h(
    'div',
    {
      fontFamily: 'Outfit',
      fontWeight: 600,
      fontSize: size,
      letterSpacing: 3,
      textTransform: 'uppercase',
      color: MUTED,
    },
    text,
  )

function waffle(lit: number, caption: string) {
  const total = COLUMNS * ROWS
  const on = Math.round(lit * total)
  const cells = Array.from({ length: total }, (_, index) =>
    h('div', {
      width: CELL,
      height: CELL,
      borderRadius: 9,
      background: index < on ? BRAND : DIM,
      opacity: index < on ? 1 - (index % 7) * 0.035 : 1,
      boxShadow: index < on ? '0 0 22px rgba(253, 218, 36, 0.22)' : 'none',
    }),
  )
  return h('div', { flexDirection: 'column', alignItems: 'flex-end', gap: 18 }, [
    h(
      'div',
      {
        flexWrap: 'wrap',
        gap: GAP,
        width: COLUMNS * CELL + (COLUMNS - 1) * GAP,
        padding: 22,
        borderRadius: 30,
        border: `1px solid ${LINE}`,
        background: TILE,
        boxSizing: 'content-box',
      },
      cells,
    ),
    h(
      'div',
      { fontFamily: 'Outfit', fontSize: 21, color: MUTED, justifyContent: 'flex-end' },
      caption,
    ),
  ])
}

function portrait(avatar: string) {
  return h(
    'div',
    {
      padding: 14,
      borderRadius: 999,
      border: `1px solid ${LINE}`,
      background: TILE,
      boxShadow: '0 0 90px rgba(253, 218, 36, 0.18)',
    },
    h('img', { width: 300, height: 300, borderRadius: 999 }, undefined, {
      src: avatar,
      width: 300,
      height: 300,
    }),
  )
}

function stats(items: Card['stats']) {
  return h(
    'div',
    { borderTop: `1px solid ${LINE}`, paddingTop: 24 },
    items.map((item, index) =>
      h(
        'div',
        {
          flexDirection: 'column',
          gap: 8,
          paddingLeft: index === 0 ? 0 : 40,
          marginLeft: index === 0 ? 0 : 40,
          borderLeft: index === 0 ? 'none' : `1px solid ${LINE}`,
        },
        [
          h(
            'div',
            { fontFamily: 'Instrument Serif', fontSize: 54, lineHeight: 1, color: BRAND },
            item.value,
          ),
          eyebrow(item.label, 15),
        ],
      ),
    ),
  )
}

function titleSize(text: string, narrow: boolean) {
  const length = text.length
  if (narrow) {
    if (length > 30) return 58
    if (length > 22) return 68
    if (length > 14) return 80
    return 108
  }
  if (length > 38) return 70
  if (length > 26) return 88
  if (length > 16) return 108
  return 128
}

export function layout(card: Card, avatar: string | null): Node {
  const visual = avatar
    ? portrait(avatar)
    : card.meter
      ? waffle(card.meter.lit, card.meter.caption)
      : null
  const size = titleSize(card.title + (card.accent ? ` ${card.accent}` : ''), visual !== null)

  return h(
    'div',
    {
      width: '100%',
      height: '100%',
      flexDirection: 'column',
      justifyContent: 'space-between',
      boxSizing: 'border-box',
      padding: '52px 72px',
      color: INK,
      backgroundColor: '#0f0f0f',
      backgroundImage: [
        'radial-gradient(circle at 0% 0%, rgba(183, 172, 232, 0.22) 0%, rgba(183, 172, 232, 0) 44%)',
        'radial-gradient(circle at 100% 100%, rgba(253, 218, 36, 0.2) 0%, rgba(253, 218, 36, 0) 50%)',
      ].join(', '),
    },
    [
      h('div', { justifyContent: 'space-between', alignItems: 'center' }, [
        h('div', { fontFamily: 'Instrument Serif', fontSize: 46, lineHeight: 1 }, 'HackProof'),
        card.eyebrow !== 'HackProof'
          ? h(
              'div',
              {
                padding: '10px 22px',
                borderRadius: 999,
                border: `1px solid ${LINE}`,
                background: TILE,
              },
              eyebrow(card.eyebrow, 16),
            )
          : null,
      ]),
      h('div', { alignItems: 'center', justifyContent: 'space-between', gap: 56 }, [
        h('div', { flexDirection: 'column', gap: 24, flex: 1 }, [
          h(
            'div',
            {
              fontFamily: 'Instrument Serif',
              fontSize: size,
              lineHeight: 1,
              flexWrap: 'wrap',
              columnGap: 20,
              letterSpacing: -2,
            },
            [
              h('span', {}, card.title),
              card.accent ? h('span', { color: BRAND, fontStyle: 'italic' }, card.accent) : null,
            ],
          ),
          card.subtitle
            ? h(
                'div',
                {
                  fontFamily: 'Outfit',
                  fontSize: 27,
                  lineHeight: 1.4,
                  color: MUTED,
                  maxWidth: 700,
                },
                card.subtitle,
              )
            : null,
        ]),
        visual,
      ]),
      card.stats.length > 0 ? stats(card.stats) : h('div', {}, null),
    ],
  )
}
