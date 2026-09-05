# 03 · Scrollytelling

**One canvas stays pinned while scrolling changes the picture.** This is where canvas motion
earns its keep: the picture changes on the same coordinate system, so "what is different" is
read with the body, not decoded from a legend.

## Data requirement
**One subject changing in stages.** Four to seven steps must fall out naturally, with each step
shifting emphasis or adding a series on the *same* axis. Five unrelated metrics shown in
sequence is not scrollytelling, it is a slideshow → use 07 Deck.

## Section rhythm

```
masthead      M1, or M5 (vertical label)
intro         two sentences on what they are about to see, plus a scroll cue
story         .layout-scrolly  left: .stick canvas / right: .steps > .step x4-7
resolution    the last step's picture stays; the conclusion sits beside it
methodology
```

## Canvas placement
- **One** canvas. Each step changes `cfg` and repaints. Never create a second canvas.
- **Compute the axis range across all steps and fix it.** If the axis jumps per step, the
  comparison collapses.
- Emphasise with opacity, not colour: drop the non-focused series to `rgba(colour, .22)`.

## Motion

```js
R.scrolly(document.getElementById('story'), function(i, node){
  state.step = i;
  chart.play(420);          // same axis, values interpolate
});
```

- 420ms or less per transition. Longer and it lags behind the scroll.
- Under `prefers-reduced-motion` the shell's `R.scrolly` switches state without animating.
- **The pin turns off on mobile.** Below 940px, `.stick` stops sticking and the canvas is drawn
  once above the steps. Write each step so it reads without the picture.

## Do not
- **Three steps or fewer.** The scroll costs more than the information is worth.
- **A different chart type per step.** The pin then means nothing.
- **A step that says "see the graph above".** Every step carries its own number in its own sentence.
