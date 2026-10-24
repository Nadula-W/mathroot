# globals.css — code explained

**Source:** [frontend/app/globals.css](../../../frontend/app/globals.css) · [All frontend explanations](../SOURCE_INDEX.md)

**What and how:** Shared colours, layout, spacing, typography and responsive rules. React className values select these rules; CSS does not change grades or permissions.

Read the code blocks in order. Each block contains the actual source and an explanation immediately below it. Line numbers match the source snapshot used here. Closing brackets and repeated markup are explained with their surrounding block.

## Lines 1–12: Code section

```css
:root {
  --bg: #f6f7f3;
  --ink: #172826;
  --muted: #667771;
  --line: #e0e6df;
  --card: #fff;
  --green: #226b55;
  --green-dark: #174a3c;
  --green-pale: #eaf5ed;
  --orange-pale: #fff5e5;
  --orange: #a05f13;
}
```

**Explanation:**

- Selectors `:root` choose the elements/className values to style.
- -- variables define shared design colours; var(--name) reuses them.

## Lines 13–13: Code section

```css
* { box-sizing: border-box; }
```

**Explanation:**

- Selectors `*` choose the elements/className values to style.
- Borders, radius and shadows style outlines and rounded panels.

## Lines 14–14: Code section

```css
html, body { margin: 0; min-height: 100%; }
```

**Explanation:**

- Selectors `html, body` choose the elements/className values to style.

## Lines 15–15: Code section

```css
body { font-family: Arial, Helvetica, sans-serif; color: var(--ink); background: var(--bg); line-height: 1.55; }
```

**Explanation:**

- Selectors `body` choose the elements/className values to style.
- Font declarations set typeface/size/weight; clamp supplies a bounded responsive size.

## Lines 16–16: Code section

```css
a { color: inherit; text-decoration: none; }
```

**Explanation:**

- Selectors `a` choose the elements/className values to style.

## Lines 17–17: Code section

```css
button, input { font: inherit; }
```

**Explanation:**

- Selectors `button, input` choose the elements/className values to style.
- Font declarations set typeface/size/weight; clamp supplies a bounded responsive size.

## Lines 18–18: Code section

```css
button { cursor: pointer; }
```

**Explanation:**

- Selectors `button` choose the elements/className values to style.

## Lines 19–19: Code section

```css
button:disabled { opacity: .55; cursor: not-allowed; }
```

**Explanation:**

- Selectors `button:disabled` choose the elements/className values to style.
- Disabled controls get a distinct appearance; actual interaction is disabled in JSX.

## Lines 20–20: Code section

```css
button:focus-visible, input:focus-visible, a:focus-visible { outline: 3px solid #68b493; outline-offset: 3px; }
```

**Explanation:**

- Selectors `button:focus-visible, input:focus-visible, a:focus-visible` choose the elements/className values to style.
- The focus outline makes keyboard navigation visible.

## Lines 21–21: Code section

```css
.shell { max-width: 1100px; margin: 0 auto; padding: 0 24px; }
```

**Explanation:**

- Selectors `.shell` choose the elements/className values to style.
- padding adds inside space; margin adds outside space.

## Lines 22–22: Code section

```css
.topbar { display: flex; align-items: center; justify-content: space-between; min-height: 96px; border-bottom: 1px solid var(--line); gap: 16px; }
```

**Explanation:**

- Selectors `.topbar` choose the elements/className values to style.
- display selects flex/grid/block layout; gap sets spacing between layout items.
- Borders, radius and shadows style outlines and rounded panels.

## Lines 23–23: Code section

```css
.logo { font-weight: 800; font-size: 23px; letter-spacing: -.8px; display: inline-flex; align-items: center; gap: 7px; }
```

**Explanation:**

- Selectors `.logo` choose the elements/className values to style.
- display selects flex/grid/block layout; gap sets spacing between layout items.
- Font declarations set typeface/size/weight; clamp supplies a bounded responsive size.

## Lines 24–24: Code section

```css
.logo > span:last-child { color: var(--green); }
```

**Explanation:**

- Selectors `.logo > span:last-child` choose the elements/className values to style.

## Lines 25–25: Code section

```css
.logo-icon { display: inline-flex; justify-content: center; align-items: center; width: 40px; height: 40px; background: var(--green); color: white; border-radius: 11px; font: bold 26px Georgia, serif; margin-right: 4px; }
```

**Explanation:**

- Selectors `.logo-icon` choose the elements/className values to style.
- display selects flex/grid/block layout; gap sets spacing between layout items.
- Font declarations set typeface/size/weight; clamp supplies a bounded responsive size.
- Borders, radius and shadows style outlines and rounded panels.

## Lines 26–26: Code section

```css
.topbar-tag, .text-link { color: var(--muted); font-size: 13px; }
```

**Explanation:**

- Selectors `.topbar-tag, .text-link` choose the elements/className values to style.
- Font declarations set typeface/size/weight; clamp supplies a bounded responsive size.

## Lines 27–27: Code section

```css
.text-link:hover { color: var(--green); }
```

**Explanation:**

- Selectors `.text-link:hover` choose the elements/className values to style.
- The hover rule gives pointer feedback.

## Lines 28–28: Code section

```css
.hero { padding: 96px 0 68px; max-width: 830px; }
```

**Explanation:**

- Selectors `.hero` choose the elements/className values to style.
- padding adds inside space; margin adds outside space.

## Lines 29–29: Code section

```css
.eyebrow, .panel-kicker, .question-label { text-transform: uppercase; letter-spacing: 1.6px; font-size: 11px; font-weight: 800; color: var(--green); }
```

**Explanation:**

- Selectors `.eyebrow, .panel-kicker, .question-label` choose the elements/className values to style.
- Font declarations set typeface/size/weight; clamp supplies a bounded responsive size.

## Lines 30–30: Code section

```css
h1,h2,p { margin-top: 0; }
```

**Explanation:**

- Selectors `h1,h2,p` choose the elements/className values to style.

## Lines 31–31: Code section

```css
h1 { font-size: clamp(34px,5.5vw,61px); letter-spacing: -2.3px; font-weight: 800; line-height: 1.11; margin: 20px 0; }
```

**Explanation:**

- Selectors `h1` choose the elements/className values to style.
- Font declarations set typeface/size/weight; clamp supplies a bounded responsive size.

## Lines 32–32: Code section

```css
h1 em { color: var(--green); font-style: normal; }
```

**Explanation:**

- Selectors `h1 em` choose the elements/className values to style.
- Font declarations set typeface/size/weight; clamp supplies a bounded responsive size.

## Lines 33–33: Code section

```css
h2 { font-size: 23px; letter-spacing: -.6px; line-height: 1.3; }
```

**Explanation:**

- Selectors `h2` choose the elements/className values to style.
- Font declarations set typeface/size/weight; clamp supplies a bounded responsive size.

## Lines 34–34: Code section

```css
.lead { color: var(--muted); font-size: 19px; max-width: 700px; }
```

**Explanation:**

- Selectors `.lead` choose the elements/className values to style.
- Font declarations set typeface/size/weight; clamp supplies a bounded responsive size.

## Lines 35–35: Code section

```css
.choice-grid { display: grid; grid-template-columns: repeat(2,minmax(0,1fr)); gap: 20px; }
```

**Explanation:**

- Selectors `.choice-grid` choose the elements/className values to style.
- display selects flex/grid/block layout; gap sets spacing between layout items.

## Lines 36–36: Code section

```css
.choice-card { min-height: 236px; border: 1px solid var(--line); background: var(--card); border-radius: 20px; padding: 27px; display: flex; flex-direction: column; position: relative; box-shadow: 0 5px 20px #16372a07; transition: transform .18s, border-color .18s; }
```

**Explanation:**

- Selectors `.choice-card` choose the elements/className values to style.
- display selects flex/grid/block layout; gap sets spacing between layout items.
- padding adds inside space; margin adds outside space.
- Borders, radius and shadows style outlines and rounded panels.

## Lines 37–37: Code section

```css
.choice-card:hover { transform: translateY(-3px); border-color: #74a690; }
```

**Explanation:**

- Selectors `.choice-card:hover` choose the elements/className values to style.
- Borders, radius and shadows style outlines and rounded panels.
- The hover rule gives pointer feedback.

## Lines 38–38: Code section

```css
.choice-card h2 { margin: 30px 0 8px; }
```

**Explanation:**

- Selectors `.choice-card h2` choose the elements/className values to style.

## Lines 39–39: Code section

```css
.choice-card p { color: var(--muted); font-size: 15px; margin: 0; max-width: 370px; }
```

**Explanation:**

- Selectors `.choice-card p` choose the elements/className values to style.
- Font declarations set typeface/size/weight; clamp supplies a bounded responsive size.

## Lines 40–40: Code section

```css
.choice-symbol { font-size: 13px; color: var(--green); font-weight: 800; }
```

**Explanation:**

- Selectors `.choice-symbol` choose the elements/className values to style.
- Font declarations set typeface/size/weight; clamp supplies a bounded responsive size.

## Lines 41–41: Code section

```css
.choice-arrow { font-size: 26px; position: absolute; right: 27px; top: 21px; color: var(--green); }
```

**Explanation:**

- Selectors `.choice-arrow` choose the elements/className values to style.
- Font declarations set typeface/size/weight; clamp supplies a bounded responsive size.

## Lines 42–42: Code section

```css
.note { font-size: 13px; background: #edf2eb; padding: 18px 22px; margin: 30px 0; border-radius: 12px; color: #4a6256; }
```

**Explanation:**

- Selectors `.note` choose the elements/className values to style.
- padding adds inside space; margin adds outside space.
- Font declarations set typeface/size/weight; clamp supplies a bounded responsive size.
- Borders, radius and shadows style outlines and rounded panels.

## Lines 43–43: Code section

```css
.footer { color: #89978e; font-size: 12px; border-top: 1px solid var(--line); margin-top: 52px; padding: 22px 0 34px; }
```

**Explanation:**

- Selectors `.footer` choose the elements/className values to style.
- padding adds inside space; margin adds outside space.
- Font declarations set typeface/size/weight; clamp supplies a bounded responsive size.
- Borders, radius and shadows style outlines and rounded panels.

## Lines 44–44: Code section

```css
.section-head { padding: 47px 0 29px; }
```

**Explanation:**

- Selectors `.section-head` choose the elements/className values to style.
- padding adds inside space; margin adds outside space.

## Lines 45–45: Code section

```css
.section-head h1 { font-size: clamp(29px, 4vw, 42px); letter-spacing: -1.4px; margin: 12px 0; }
```

**Explanation:**

- Selectors `.section-head h1` choose the elements/className values to style.
- Font declarations set typeface/size/weight; clamp supplies a bounded responsive size.

## Lines 46–46: Code section

```css
.section-head p { color: var(--muted); margin-bottom: 0; }
```

**Explanation:**

- Selectors `.section-head p` choose the elements/className values to style.

## Lines 47–47: Code section

```css
.panel { background: var(--card); border: 1px solid var(--line); border-radius: 19px; padding: 30px; box-shadow: 0 4px 20px #16372a06; }
```

**Explanation:**

- Selectors `.panel` choose the elements/className values to style.
- padding adds inside space; margin adds outside space.
- Borders, radius and shadows style outlines and rounded panels.

## Lines 48–48: Code section

```css
.panel h2 { margin: 7px 0 10px; }
```

**Explanation:**

- Selectors `.panel h2` choose the elements/className values to style.

## Lines 49–49: Code section

```css
.panel.narrow { max-width: 640px; margin: 8px auto; }
```

**Explanation:**

- Selectors `.panel.narrow` choose the elements/className values to style.

## Lines 50–50: Code section

```css
.muted { color: var(--muted); font-size: 14px; }
```

**Explanation:**

- Selectors `.muted` choose the elements/className values to style.
- Font declarations set typeface/size/weight; clamp supplies a bounded responsive size.

## Lines 51–51: Code section

```css
.form-grid { display: grid; grid-template-columns: repeat(2, minmax(0,1fr)); gap: 16px; margin: 24px 0; }
```

**Explanation:**

- Selectors `.form-grid` choose the elements/className values to style.
- display selects flex/grid/block layout; gap sets spacing between layout items.

## Lines 52–52: Code section

```css
.field { display: flex; flex-direction: column; gap: 7px; }
```

**Explanation:**

- Selectors `.field` choose the elements/className values to style.
- display selects flex/grid/block layout; gap sets spacing between layout items.

## Lines 53–53: Code section

```css
.field > span { font-size: 13px; font-weight: 700; color: #425851; }
```

**Explanation:**

- Selectors `.field > span` choose the elements/className values to style.
- Font declarations set typeface/size/weight; clamp supplies a bounded responsive size.

## Lines 54–54: Code section

```css
.field input { height: 46px; width: 100%; border: 1px solid #d3ddd4; background: white; border-radius: 10px; padding: 0 13px; color: var(--ink); }
```

**Explanation:**

- Selectors `.field input` choose the elements/className values to style.
- padding adds inside space; margin adds outside space.
- Borders, radius and shadows style outlines and rounded panels.

## Lines 55–55: Code section

```css
.field input:focus { border-color: var(--green); }
```

**Explanation:**

- Selectors `.field input:focus` choose the elements/className values to style.
- Borders, radius and shadows style outlines and rounded panels.

## Lines 56–56: Code section

```css
.button { border: 0; border-radius: 11px; padding: 12px 22px; text-align: center; font-weight: 700; font-size: 14px; display: inline-flex; justify-content: center; align-items: center; min-height: 47px; }
```

**Explanation:**

- Selectors `.button` choose the elements/className values to style.
- display selects flex/grid/block layout; gap sets spacing between layout items.
- padding adds inside space; margin adds outside space.
- Font declarations set typeface/size/weight; clamp supplies a bounded responsive size.
- Borders, radius and shadows style outlines and rounded panels.

## Lines 57–57: Code section

```css
.button.primary { background: var(--green); color: white; }
```

**Explanation:**

- Selectors `.button.primary` choose the elements/className values to style.

## Lines 58–58: Code section

```css
.button.primary:hover:not(:disabled) { background: var(--green-dark); }
```

**Explanation:**

- Selectors `.button.primary:hover:not(:disabled)` choose the elements/className values to style.
- Disabled controls get a distinct appearance; actual interaction is disabled in JSX.
- The hover rule gives pointer feedback.

## Lines 59–59: Code section

```css
.button.ghost { background: #eef4ef; color: var(--green); }
```

**Explanation:**

- Selectors `.button.ghost` choose the elements/className values to style.

## Lines 60–60: Code section

```css
.button.full { display: flex; width: 100%; margin-top: 18px; }
```

**Explanation:**

- Selectors `.button.full` choose the elements/className values to style.
- display selects flex/grid/block layout; gap sets spacing between layout items.

## Lines 61–61: Code section

```css
.helper { color: var(--muted); font-size: 12px; margin: 16px 0 0; }
```

**Explanation:**

- Selectors `.helper` choose the elements/className values to style.
- Font declarations set typeface/size/weight; clamp supplies a bounded responsive size.

## Lines 62–62: Code section

```css
.alert { background: #fff0e6; border: 1px solid #f2c39f; color: #7b401b; border-radius: 11px; padding: 13px 17px; margin: 0 0 20px; font-size: 14px; }
```

**Explanation:**

- Selectors `.alert` choose the elements/className values to style.
- padding adds inside space; margin adds outside space.
- Font declarations set typeface/size/weight; clamp supplies a bounded responsive size.
- Borders, radius and shadows style outlines and rounded panels.

## Lines 63–63: Code section

```css
.alert.soft { background: #eef3ec; border-color: #d6e6d9; color: #416353; }
```

**Explanation:**

- Selectors `.alert.soft` choose the elements/className values to style.
- Borders, radius and shadows style outlines and rounded panels.

## Lines 64–64: Code section

```css
.progress-row { display: flex; justify-content: space-between; gap: 12px; align-items: center; }
```

**Explanation:**

- Selectors `.progress-row` choose the elements/className values to style.
- display selects flex/grid/block layout; gap sets spacing between layout items.

## Lines 65–65: Code section

```css
.difficulty { background: #edf3ee; color: #476858; border-radius: 100px; font-size: 12px; font-weight: 700; text-transform: capitalize; padding: 5px 12px; }
```

**Explanation:**

- Selectors `.difficulty` choose the elements/className values to style.
- padding adds inside space; margin adds outside space.
- Font declarations set typeface/size/weight; clamp supplies a bounded responsive size.
- Borders, radius and shadows style outlines and rounded panels.

## Lines 66–66: Code section

```css
.progress { height: 6px; border-radius: 8px; background: #e9eee7; overflow: hidden; margin: 15px 0 28px; }
```

**Explanation:**

- Selectors `.progress` choose the elements/className values to style.
- Borders, radius and shadows style outlines and rounded panels.

## Lines 67–67: Code section

```css
.progress span { display: block; height: 100%; background: var(--green); border-radius: inherit; transition: width .2s ease; }
```

**Explanation:**

- Selectors `.progress span` choose the elements/className values to style.
- display selects flex/grid/block layout; gap sets spacing between layout items.
- Borders, radius and shadows style outlines and rounded panels.

## Lines 68–68: Code section

```css
.assessment-panel { max-width: 770px; margin: 0 auto; }
```

**Explanation:**

- Selectors `.assessment-panel` choose the elements/className values to style.

## Lines 69–69: Code section

```css
.question-area { padding: 5px 0 15px; }
```

**Explanation:**

- Selectors `.question-area` choose the elements/className values to style.
- padding adds inside space; margin adds outside space.

## Lines 70–70: Code section

```css
.question-area h2 { font-size: clamp(24px,4vw,32px); margin: 10px 0; }
```

**Explanation:**

- Selectors `.question-area h2` choose the elements/className values to style.
- Font declarations set typeface/size/weight; clamp supplies a bounded responsive size.

## Lines 71–71: Code section

```css
.options { display: grid; gap: 12px; }
```

**Explanation:**

- Selectors `.options` choose the elements/className values to style.
- display selects flex/grid/block layout; gap sets spacing between layout items.

## Lines 72–72: Code section

```css
.option { display: flex; align-items: center; width: 100%; gap: 15px; background: white; padding: 14px; min-height: 62px; border: 1.5px solid #dce5db; border-radius: 12px; text-align: left; color: var(--ink); }
```

**Explanation:**

- Selectors `.option` choose the elements/className values to style.
- display selects flex/grid/block layout; gap sets spacing between layout items.
- padding adds inside space; margin adds outside space.
- Borders, radius and shadows style outlines and rounded panels.

## Lines 73–73: Code section

```css
.option:hover:not(:disabled) { border-color: var(--green); }
```

**Explanation:**

- Selectors `.option:hover:not(:disabled)` choose the elements/className values to style.
- Borders, radius and shadows style outlines and rounded panels.
- Disabled controls get a distinct appearance; actual interaction is disabled in JSX.
- The hover rule gives pointer feedback.

## Lines 74–74: Code section

```css
.option.selected { border-color: var(--green); background: #f2f8f4; }
```

**Explanation:**

- Selectors `.option.selected` choose the elements/className values to style.
- Borders, radius and shadows style outlines and rounded panels.

## Lines 75–75: Code section

```css
.option.is-correct { background: #e9f6eb; border-color: #63a97d; }
```

**Explanation:**

- Selectors `.option.is-correct` choose the elements/className values to style.
- Borders, radius and shadows style outlines and rounded panels.

## Lines 76–76: Code section

```css
.option-index { background: #edf0ed; color: #617066; display: inline-flex; width: 34px; height: 34px; border-radius: 8px; align-items: center; justify-content: center; font-size: 13px; font-weight: 800; flex-shrink: 0; }
```

**Explanation:**

- Selectors `.option-index` choose the elements/className values to style.
- display selects flex/grid/block layout; gap sets spacing between layout items.
- Font declarations set typeface/size/weight; clamp supplies a bounded responsive size.
- Borders, radius and shadows style outlines and rounded panels.

## Lines 77–77: Code section

```css
.option-text { font-size: 20px; font-weight: 600; letter-spacing: -.5px; flex: 1; }
```

**Explanation:**

- Selectors `.option-text` choose the elements/className values to style.
- Font declarations set typeface/size/weight; clamp supplies a bounded responsive size.

## Lines 78–78: Code section

```css
.option-status { color: var(--green); font-weight: 800; }
```

**Explanation:**

- Selectors `.option-status` choose the elements/className values to style.
- Font declarations set typeface/size/weight; clamp supplies a bounded responsive size.

## Lines 79–79: Code section

```css
.feedback-box { margin-top: 21px; padding: 20px; border-radius: 12px; font-size: 14px; }
```

**Explanation:**

- Selectors `.feedback-box` choose the elements/className values to style.
- padding adds inside space; margin adds outside space.
- Font declarations set typeface/size/weight; clamp supplies a bounded responsive size.
- Borders, radius and shadows style outlines and rounded panels.

## Lines 80–80: Code section

```css
.feedback-box.good { background: var(--green-pale); border: 1px solid #cae7d2; }
```

**Explanation:**

- Selectors `.feedback-box.good` choose the elements/className values to style.
- Borders, radius and shadows style outlines and rounded panels.

## Lines 81–81: Code section

```css
.feedback-box.review { background: var(--orange-pale); border: 1px solid #f1dfbe; }
```

**Explanation:**

- Selectors `.feedback-box.review` choose the elements/className values to style.
- Borders, radius and shadows style outlines and rounded panels.

## Lines 82–82: Code section

```css
.feedback-box p { margin: 10px 0; }
```

**Explanation:**

- Selectors `.feedback-box p` choose the elements/className values to style.

## Lines 83–83: Code section

```css
.feedback-title { font-weight: 800; font-size: 17px; }
```

**Explanation:**

- Selectors `.feedback-title` choose the elements/className values to style.
- Font declarations set typeface/size/weight; clamp supplies a bounded responsive size.

## Lines 84–84: Code section

```css
.tag { font-size: 11px; font-weight: 700; display: inline-block; padding: 5px 9px; background: #fff8ed; border-radius: 7px; color: var(--orange); }
```

**Explanation:**

- Selectors `.tag` choose the elements/className values to style.
- display selects flex/grid/block layout; gap sets spacing between layout items.
- padding adds inside space; margin adds outside space.
- Font declarations set typeface/size/weight; clamp supplies a bounded responsive size.
- Borders, radius and shadows style outlines and rounded panels.

## Lines 85–85: Code section

```css
.finished { text-align: center; padding: 55px 36px; }
```

**Explanation:**

- Selectors `.finished` choose the elements/className values to style.
- padding adds inside space; margin adds outside space.

## Lines 86–86: Code section

```css
.finish-icon { margin: 0 auto 16px; display: grid; place-items: center; width: 60px; height: 60px; background: #e4f4e8; color: var(--green); font-size: 33px; border-radius: 50%; }
```

**Explanation:**

- Selectors `.finish-icon` choose the elements/className values to style.
- display selects flex/grid/block layout; gap sets spacing between layout items.
- Font declarations set typeface/size/weight; clamp supplies a bounded responsive size.
- Borders, radius and shadows style outlines and rounded panels.

## Lines 87–87: Code section

```css
.control-panel { display: flex; justify-content: space-between; align-items: end; gap: 25px; margin-bottom: 23px; }
```

**Explanation:**

- Selectors `.control-panel` choose the elements/className values to style.
- display selects flex/grid/block layout; gap sets spacing between layout items.

## Lines 88–88: Code section

```css
.control-panel h2 { margin-bottom: 0; }
```

**Explanation:**

- Selectors `.control-panel h2` choose the elements/className values to style.

## Lines 89–89: Code section

```css
.class-controls { display: flex; align-items: end; gap: 12px; }
```

**Explanation:**

- Selectors `.class-controls` choose the elements/className values to style.
- display selects flex/grid/block layout; gap sets spacing between layout items.

## Lines 90–90: Code section

```css
.class-controls .field { min-width: 240px; }
```

**Explanation:**

- Selectors `.class-controls .field` choose the elements/className values to style.

## Lines 91–91: Code section

```css
.stats-grid { display: grid; grid-template-columns: repeat(3, minmax(0,1fr)); gap: 18px; margin: 0 0 20px; }
```

**Explanation:**

- Selectors `.stats-grid` choose the elements/className values to style.
- display selects flex/grid/block layout; gap sets spacing between layout items.

## Lines 92–92: Code section

```css
.stat { background: white; border: 1px solid var(--line); border-radius: 16px; padding: 23px; display: flex; flex-direction: column; }
```

**Explanation:**

- Selectors `.stat` choose the elements/className values to style.
- display selects flex/grid/block layout; gap sets spacing between layout items.
- padding adds inside space; margin adds outside space.
- Borders, radius and shadows style outlines and rounded panels.

## Lines 93–93: Code section

```css
.stat span { font-size: 13px; color: var(--muted); }
```

**Explanation:**

- Selectors `.stat span` choose the elements/className values to style.
- Font declarations set typeface/size/weight; clamp supplies a bounded responsive size.

## Lines 94–94: Code section

```css
.stat strong { font-size: 39px; letter-spacing: -1px; margin: 4px 0; }
```

**Explanation:**

- Selectors `.stat strong` choose the elements/className values to style.
- Font declarations set typeface/size/weight; clamp supplies a bounded responsive size.

## Lines 95–95: Code section

```css
.stat small { color: #87958c; font-size: 12px; }
```

**Explanation:**

- Selectors `.stat small` choose the elements/className values to style.
- Font declarations set typeface/size/weight; clamp supplies a bounded responsive size.

## Lines 96–96: Code section

```css
.teacher-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 19px; align-items: start; }
```

**Explanation:**

- Selectors `.teacher-grid` choose the elements/className values to style.
- display selects flex/grid/block layout; gap sets spacing between layout items.

## Lines 97–97: Code section

```css
.teacher-grid .panel { min-height: 315px; }
```

**Explanation:**

- Selectors `.teacher-grid .panel` choose the elements/className values to style.

## Lines 98–98: Code section

```css
.misconceptions { margin-top: 26px; display: grid; gap: 23px; }
```

**Explanation:**

- Selectors `.misconceptions` choose the elements/className values to style.
- display selects flex/grid/block layout; gap sets spacing between layout items.

## Lines 99–99: Code section

```css
.misconception-row { display: flex; justify-content: space-between; gap: 12px; font-size: 13px; }
```

**Explanation:**

- Selectors `.misconception-row` choose the elements/className values to style.
- display selects flex/grid/block layout; gap sets spacing between layout items.
- Font declarations set typeface/size/weight; clamp supplies a bounded responsive size.

## Lines 100–100: Code section

```css
.misconception-row strong { font-size: 14px; }
```

**Explanation:**

- Selectors `.misconception-row strong` choose the elements/className values to style.
- Font declarations set typeface/size/weight; clamp supplies a bounded responsive size.

## Lines 101–101: Code section

```css
.bar-track { height: 8px; border-radius: 10px; background: #e7eee8; margin-top: 8px; overflow: hidden; }
```

**Explanation:**

- Selectors `.bar-track` choose the elements/className values to style.
- Borders, radius and shadows style outlines and rounded panels.

## Lines 102–102: Code section

```css
.bar-track div { background: var(--green); height: 100%; border-radius: 10px; }
```

**Explanation:**

- Selectors `.bar-track div` choose the elements/className values to style.
- Borders, radius and shadows style outlines and rounded panels.

## Lines 103–103: Code section

```css
.recommendations { display: grid; gap: 17px; margin-top: 24px; }
```

**Explanation:**

- Selectors `.recommendations` choose the elements/className values to style.
- display selects flex/grid/block layout; gap sets spacing between layout items.

## Lines 104–104: Code section

```css
.recommendation { display: flex; gap: 13px; padding-bottom: 14px; border-bottom: 1px solid var(--line); }
```

**Explanation:**

- Selectors `.recommendation` choose the elements/className values to style.
- display selects flex/grid/block layout; gap sets spacing between layout items.
- Borders, radius and shadows style outlines and rounded panels.

## Lines 105–105: Code section

```css
.rec-no { color: var(--green); font-size: 13px; font-weight: 800; }
```

**Explanation:**

- Selectors `.rec-no` choose the elements/className values to style.
- Font declarations set typeface/size/weight; clamp supplies a bounded responsive size.

## Lines 106–106: Code section

```css
.recommendation p { margin: 0; font-size: 14px; }
```

**Explanation:**

- Selectors `.recommendation p` choose the elements/className values to style.
- Font declarations set typeface/size/weight; clamp supplies a bounded responsive size.

## Lines 107–107: Code section

```css
.empty-inline { margin: 28px 0 0; color: var(--muted); font-size: 14px; }
```

**Explanation:**

- Selectors `.empty-inline` choose the elements/className values to style.
- Font declarations set typeface/size/weight; clamp supplies a bounded responsive size.

## Lines 108–108: Code section

```css
.empty-state { max-width: 640px; margin: 45px auto 120px; padding: 28px; text-align: center; color: var(--muted); }
```

**Explanation:**

- Selectors `.empty-state` choose the elements/className values to style.
- padding adds inside space; margin adds outside space.

## Lines 109–109: Code section

```css
.empty-state > span { font-size: 45px; color: #7ca18a; }
```

**Explanation:**

- Selectors `.empty-state > span` choose the elements/className values to style.
- Font declarations set typeface/size/weight; clamp supplies a bounded responsive size.

## Lines 110–110: Code section

```css
.empty-state h2 { color: var(--ink); margin: 8px 0; }
```

**Explanation:**

- Selectors `.empty-state h2` choose the elements/className values to style.

## Lines 111–121: Code section

```css
@media (max-width: 780px) {
  .hero { padding: 65px 0 35px; }
  .choice-grid, .teacher-grid { grid-template-columns: 1fr; }
  .control-panel { align-items: stretch; flex-direction: column; }
  .class-controls { flex-direction: column; align-items: stretch; }
  .class-controls .field { min-width: 0; }
  .stats-grid { gap: 9px; }
  .stat { padding: 15px; }
  .stat strong { font-size: 30px; }
  .stat span, .stat small { font-size: 11px; }
}
```

**Explanation:**

- Selectors `.hero`, `.choice-grid, .teacher-grid`, `.control-panel`, `.class-controls` choose the elements/className values to style.
- The media condition applies these overrides only at the stated screen width.
- padding adds inside space; margin adds outside space.
- Font declarations set typeface/size/weight; clamp supplies a bounded responsive size.

## Lines 122–136: Code section

```css
@media (max-width: 540px) {
  .shell { padding: 0 15px; }
  .topbar { min-height: 75px; }
  .topbar-tag { font-size: 10px; text-align: right; }
  .logo { font-size: 19px; }
  .logo-icon { width: 33px; height: 33px; font-size: 23px; }
  h1 { letter-spacing: -1.2px; }
  .section-head { padding: 32px 0 25px; }
  .panel { padding: 20px 16px; }
  .form-grid { grid-template-columns: 1fr; }
  .stats-grid { grid-template-columns: 1fr 1fr 1fr; }
  .option-text { font-size: 17px; }
  .question-area h2 { font-size: 23px; }
  .choice-card { min-height: 210px; }
}
```

**Explanation:**

- Selectors `.shell`, `.topbar`, `.topbar-tag`, `.logo` choose the elements/className values to style.
- The media condition applies these overrides only at the stated screen width.
- padding adds inside space; margin adds outside space.
- Font declarations set typeface/size/weight; clamp supplies a bounded responsive size.

## Lines 138–143: Code section

```css
.topic-choices {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  margin: 12px 0 20px;
}
```

**Explanation:**

- Selectors `.topic-choices` choose the elements/className values to style.
- display selects flex/grid/block layout; gap sets spacing between layout items.

## Lines 145–152: Code section

```css
.topic-choice {
  display: flex;
  gap: 9px;
  padding: 13px;
  border: 1px solid var(--line);
  border-radius: 10px;
  align-items: center;
}
```

**Explanation:**

- Selectors `.topic-choice` choose the elements/className values to style.
- display selects flex/grid/block layout; gap sets spacing between layout items.
- padding adds inside space; margin adds outside space.
- Borders, radius and shadows style outlines and rounded panels.

## Lines 154–156: Code section

```css
.topic-choice small {
  color: var(--muted);
}
```

**Explanation:**

- Selectors `.topic-choice small` choose the elements/className values to style.

## Lines 158–164: Code section

```css
.field select {
  height: 46px;
  border: 1px solid var(--line);
  border-radius: 10px;
  padding: 0 10px;
  background: white;
}
```

**Explanation:**

- Selectors `.field select` choose the elements/className values to style.
- padding adds inside space; margin adds outside space.
- Borders, radius and shadows style outlines and rounded panels.

## Lines 166–173: Code section

```css
.test-entry {
  border-top: 1px solid var(--line);
  padding: 14px 0;
  display: flex;
  justify-content: space-between;
  gap: 15px;
  align-items: center;
}
```

**Explanation:**

- Selectors `.test-entry` choose the elements/className values to style.
- display selects flex/grid/block layout; gap sets spacing between layout items.
- padding adds inside space; margin adds outside space.
- Borders, radius and shadows style outlines and rounded panels.

## Lines 175–181: Code section

```css
.test-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.test-buttons button,
```

**Explanation:**

- Selectors `.test-buttons` choose the elements/className values to style.
- display selects flex/grid/block layout; gap sets spacing between layout items.

## Lines 182–189: Code section

```css
.test-buttons a {
  padding: 8px 12px;
  background: #edf3ee;
  border: 0;
  border-radius: 8px;
  color: var(--ink);
  font-size: 13px;
}
```

**Explanation:**

- Selectors `.test-buttons a` choose the elements/className values to style.
- padding adds inside space; margin adds outside space.
- Font declarations set typeface/size/weight; clamp supplies a bounded responsive size.
- Borders, radius and shadows style outlines and rounded panels.

## Lines 191–195: Code section

```css
.results-area {
  margin-top: 25px;
  border-top: 2px solid var(--line);
  padding-top: 20px;
}
```

**Explanation:**

- Selectors `.results-area` choose the elements/className values to style.
- Borders, radius and shadows style outlines and rounded panels.

## Lines 197–208: Code section

```css
@media (max-width: 720px) {
  .topic-choices {
    grid-template-columns: 1fr;
  }

  .test-entry {
    align-items: flex-start;
    flex-direction: column;
  }
}

/* MathRoot authenticated account header */
```

**Explanation:**

- Selectors `.topic-choices`, `.test-entry` choose the elements/className values to style.
- The media condition applies these overrides only at the stated screen width.

## Lines 210–220: Code section

```css
.mr-account-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
  padding: 15px 5%;
  background: #0f172a;
  color: #ffffff;
  border-bottom: 1px solid #334155;
}
```

**Explanation:**

- Selectors `.mr-account-header` choose the elements/className values to style.
- display selects flex/grid/block layout; gap sets spacing between layout items.
- padding adds inside space; margin adds outside space.
- Borders, radius and shadows style outlines and rounded panels.

## Lines 222–227: Code section

```css
.mr-account-brand {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 15px;
}
```

**Explanation:**

- Selectors `.mr-account-brand` choose the elements/className values to style.
- display selects flex/grid/block layout; gap sets spacing between layout items.

## Lines 229–234: Code section

```css
.mr-account-brand a {
  font-size: 19px;
  font-weight: 800;
  color: #ffffff;
  text-decoration: none;
}
```

**Explanation:**

- Selectors `.mr-account-brand a` choose the elements/className values to style.
- Font declarations set typeface/size/weight; clamp supplies a bounded responsive size.

## Lines 236–239: Code section

```css
.mr-account-section {
  font-size: 12px;
  color: #cbd5e1;
}
```

**Explanation:**

- Selectors `.mr-account-section` choose the elements/className values to style.
- Font declarations set typeface/size/weight; clamp supplies a bounded responsive size.

## Lines 241–245: Code section

```css
.mr-account-right {
  display: flex;
  align-items: center;
  gap: 18px;
}
```

**Explanation:**

- Selectors `.mr-account-right` choose the elements/className values to style.
- display selects flex/grid/block layout; gap sets spacing between layout items.

## Lines 247–252: Code section

```css
.mr-account-user {
  display: flex;
  flex-direction: column;
  text-align: right;
  gap: 3px;
}
```

**Explanation:**

- Selectors `.mr-account-user` choose the elements/className values to style.
- display selects flex/grid/block layout; gap sets spacing between layout items.

## Lines 254–258: Code section

```css
.mr-account-greeting {
  font-size: 14px;
  font-weight: 700;
  color: #ffffff;
}
```

**Explanation:**

- Selectors `.mr-account-greeting` choose the elements/className values to style.
- Font declarations set typeface/size/weight; clamp supplies a bounded responsive size.

## Lines 260–263: Code section

```css
.mr-account-role {
  font-size: 11px;
  color: #94a3b8;
}
```

**Explanation:**

- Selectors `.mr-account-role` choose the elements/className values to style.
- Font declarations set typeface/size/weight; clamp supplies a bounded responsive size.

## Lines 265–274: Code section

```css
.mr-account-logout {
  cursor: pointer;
  border: 1px solid #64748b;
  border-radius: 9px;
  padding: 9px 15px;
  background: transparent;
  color: #ffffff;
  font-size: 13px;
  font-weight: 600;
}
```

**Explanation:**

- Selectors `.mr-account-logout` choose the elements/className values to style.
- padding adds inside space; margin adds outside space.
- Font declarations set typeface/size/weight; clamp supplies a bounded responsive size.
- Borders, radius and shadows style outlines and rounded panels.

## Lines 276–278: Code section

```css
.mr-account-logout:hover {
  background: #334155;
}
```

**Explanation:**

- Selectors `.mr-account-logout:hover` choose the elements/className values to style.
- The hover rule gives pointer feedback.

## Lines 280–283: Code section

```css
.mr-account-logout:disabled {
  opacity: 0.6;
  cursor: wait;
}
```

**Explanation:**

- Selectors `.mr-account-logout:disabled` choose the elements/className values to style.
- Disabled controls get a distinct appearance; actual interaction is disabled in JSX.

## Lines 285–289: Code section

```css
.mr-account-error {
  color: #fca5a5;
  font-size: 12px;
  width: 100%;
}
```

**Explanation:**

- Selectors `.mr-account-error` choose the elements/className values to style.
- Font declarations set typeface/size/weight; clamp supplies a bounded responsive size.

## Lines 291–308: Code section

```css
@media (max-width: 600px) {
  .mr-account-header {
    padding: 14px 18px;
  }

  .mr-account-section {
    display: none;
  }

  .mr-account-right {
    width: 100%;
    justify-content: space-between;
  }

  .mr-account-user {
    text-align: left;
  }
}
```

**Explanation:**

- Selectors `.mr-account-header`, `.mr-account-section`, `.mr-account-right`, `.mr-account-user` choose the elements/className values to style.
- The media condition applies these overrides only at the stated screen width.
- display selects flex/grid/block layout; gap sets spacing between layout items.
- padding adds inside space; margin adds outside space.

## How to explain this file in the viva

“Shared colours, layout, spacing, typography and responsive rules. React className values select these rules; CSS does not change grades or permissions.”
