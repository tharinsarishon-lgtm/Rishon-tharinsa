# Nexora — 3D responsive website

A modern 3D landing page with Login and Sign-up pages. Built with plain HTML, CSS and JavaScript plus [Three.js](https://threejs.org/) for the 3D scenes. It works on phone, tablet and laptop screens.

## Pages
| File | What it is |
|------|------------|
| `index.html` | Home page: interactive 3D hero, features (3D tilt cards), stats, steps, pricing, CTA, footer |
| `login.html` | Login page with a 3D background, validation and show/hide password |
| `signup.html` | Sign-up page with a password strength meter, confirm password and terms checkbox |

## 3D and animation
- **Three.js scene** (`js/scene.js`): a glowing crystal (home) or torus knot (login and sign-up) with a wireframe shell, orbit rings, moving satellites and a star field.
- It follows the mouse and rotates as you scroll.
- **3D tilt cards** with a cursor spotlight (only on devices with a mouse).
- **Scroll reveal** animations, animated counters and a logo marquee.
- **Performance:** fewer particles on phones, pixel ratio capped at 2, and animation pauses when the tab is hidden or the canvas is off screen.
- **Accessibility:** respects `prefers-reduced-motion`, falls back to a CSS gradient when WebGL is not available, keeps touch targets at 44px or more and supports the keyboard.

## Responsive layout
- **Phone (< 600px):** the 3D object sits above the text, the menu becomes a hamburger drawer, and the auth card floats over a full-screen 3D background.
- **Tablet (600–959px):** two-column grids and a centred hero.
- **Laptop (≥ 960px):** the text sits on the left with the 3D object on the right, and the auth pages split into a 3D panel and a form panel.

## Run locally
The pages use ES modules, so open them through a local server rather than by double-clicking the file:
```bash
python3 -m http.server 8000
# open http://localhost:8000
```
Three.js is bundled in `js/vendor/`, so no CDN is needed. The site can be deployed as-is to GitHub Pages, Netlify or Vercel.

## Connecting a real backend
The login and sign-up forms only run in the browser for now. To add real accounts, replace `submitToServer()` in `js/auth.js` with Firebase Auth, Supabase or your own API. Do this over HTTPS, and never store passwords in the browser.
