import { createCn } from 'cn/config'

const POSTER_TEXT_SIZES = ['eyebrow', 'stat', 'figure', 'figure-lg', 'headline', 'display']

export const cn = createCn({
  extend: { classGroups: { 'font-size': [{ text: POSTER_TEXT_SIZES }] } },
})
