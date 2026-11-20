import type { Card } from './_card'

const INK = '#f6f7f8'
const MUTED = '#a1a1aa'
const BRAND = '#fdda24'
const TILE = 'rgba(255, 255, 255, 0.04)'
const LINE = 'rgba(255, 255, 255, 0.11)'

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

function stat(item: Card['stats'][number]) {
  return h(
    'div',
    {
      flexDirection: 'column',
      gap: 10,
      padding: '20px 28px',
      borderRadius: 24,
      border: `1px solid ${LINE}`,
      background: TILE,
      flexGrow: 1,
      flexBasis: 0,
      minWidth: 0,
    },
    [
      h(
        'div',
        { fontFamily: 'Instrument Serif', fontSize: 54, lineHeight: 1, color: BRAND },
        item.value,
      ),
      h(
        'div',
        {
          fontFamily: 'Outfit',
          fontWeight: 600,
          fontSize: 15,
          letterSpacing: 2.5,
          textTransform: 'uppercase',
          color: MUTED,
        },
        item.label,
      ),
    ],
  )
}

function titleSize(text: string) {
  if (text.length > 38) return 68
  if (text.length > 26) return 84
  if (text.length > 16) return 104
  return 120
}

export function layout(card: Card, avatar: string | null): Node {
  const size = titleSize(card.title + (card.accent ? ` ${card.accent}` : ''))
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
        'radial-gradient(circle at 0% 0%, rgba(183, 172, 232, 0.2) 0%, rgba(183, 172, 232, 0) 46%)',
        'radial-gradient(circle at 100% 100%, rgba(253, 218, 36, 0.2) 0%, rgba(253, 218, 36, 0) 52%)',
      ].join(', '),
    },
    [
      h('div', { justifyContent: 'space-between', alignItems: 'center' }, [
        h('div', { alignItems: 'center', gap: 20 }, [
          h('div', { fontFamily: 'Instrument Serif', fontSize: 46, lineHeight: 1 }, 'HackProof'),
          card.eyebrow !== 'HackProof'
            ? h(
                'div',
                {
                  fontFamily: 'Outfit',
                  fontWeight: 600,
                  fontSize: 19,
                  letterSpacing: 3,
                  textTransform: 'uppercase',
                  color: MUTED,
                },
                card.eyebrow,
              )
            : null,
        ]),
        avatar
          ? h(
              'div',
              { borderRadius: 999, border: `3px solid ${LINE}`, padding: 6, background: TILE },
              h('img', { width: 112, height: 112, borderRadius: 999 }, undefined, {
                src: avatar,
                width: 112,
                height: 112,
              }),
            )
          : null,
      ]),
      h('div', { flexDirection: 'column', gap: 22 }, [
        h(
          'div',
          {
            fontFamily: 'Instrument Serif',
            fontSize: size,
            lineHeight: 0.98,
            flexWrap: 'wrap',
            letterSpacing: -2,
          },
          [
            h('span', {}, card.title),
            card.accent
              ? h('span', { color: BRAND, fontStyle: 'italic', marginLeft: 22 }, card.accent)
              : null,
          ],
        ),
        card.subtitle
          ? h(
              'div',
              { fontFamily: 'Outfit', fontSize: 28, lineHeight: 1.35, color: MUTED, maxWidth: 940 },
              card.subtitle,
            )
          : null,
      ]),
      h('div', { gap: 20 }, card.stats.map(stat)),
    ],
  )
}
