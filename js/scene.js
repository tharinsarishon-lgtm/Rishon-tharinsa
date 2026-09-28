// Shared Three.js background scene used by the home page and the auth pages.
// Handles resize, pointer/scroll interaction, reduced motion and pausing when hidden.
import * as THREE from 'three';

const COLORS = { violet: 0x8b5cf6, cyan: 0x22d3ee, pink: 0xec4899 };

// Soft round sprite so particles render as glowing dots instead of squares
function dotTexture() {
  const c = document.createElement('canvas');
  c.width = c.height = 64;
  const ctx = c.getContext('2d');
  const g = ctx.createRadialGradient(32, 32, 0, 32, 32, 32);
  g.addColorStop(0, 'rgba(255,255,255,1)');
  g.addColorStop(0.35, 'rgba(255,255,255,0.6)');
  g.addColorStop(1, 'rgba(255,255,255,0)');
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, 64, 64);
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}

export function createScene(canvas, { variant = 'hero' } = {}) {
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, powerPreference: 'high-performance' });
  } catch (err) {
    // No WebGL: the CSS gradient behind the canvas stays visible.
    canvas.classList.add('no-webgl');
    return null;
  }
  renderer.setClearColor(0x000000, 0);

  const scene = new THREE.Scene();
  scene.fog = new THREE.FogExp2(0x07060f, 0.045);
  const camera = new THREE.PerspectiveCamera(45, 1, 0.1, 100);
  camera.position.set(0, 0, 8);

  // Lights
  scene.add(new THREE.AmbientLight(0xffffff, 0.35));
  const lightA = new THREE.PointLight(COLORS.violet, 60, 30);
  lightA.position.set(4, 3, 5);
  const lightB = new THREE.PointLight(COLORS.cyan, 50, 30);
  lightB.position.set(-5, -2, 4);
  const lightC = new THREE.PointLight(COLORS.pink, 30, 30);
  lightC.position.set(0, -4, -3);
  scene.add(lightA, lightB, lightC);

  // Main object group
  const group = new THREE.Group();
  scene.add(group);

  const coreGeo = variant === 'auth'
    ? new THREE.TorusKnotGeometry(1.1, 0.34, 180, 24)
    : new THREE.IcosahedronGeometry(1.5, 1);
  const core = new THREE.Mesh(coreGeo, new THREE.MeshStandardMaterial({
    color: 0x1a1333, metalness: 0.75, roughness: 0.22, flatShading: variant !== 'auth',
    emissive: 0x2a1060, emissiveIntensity: 0.35,
  }));
  group.add(core);

  const wire = new THREE.Mesh(
    variant === 'auth' ? new THREE.IcosahedronGeometry(2.3, 1) : new THREE.IcosahedronGeometry(2.05, 1),
    new THREE.MeshBasicMaterial({ color: COLORS.cyan, wireframe: true, transparent: true, opacity: 0.18 }),
  );
  group.add(wire);

  const ringMat = new THREE.MeshBasicMaterial({ color: COLORS.violet, transparent: true, opacity: 0.55 });
  const ring1 = new THREE.Mesh(new THREE.TorusGeometry(2.8, 0.012, 8, 160), ringMat);
  ring1.rotation.x = Math.PI / 2.3;
  const ring2 = new THREE.Mesh(new THREE.TorusGeometry(3.3, 0.008, 8, 160), ringMat.clone());
  ring2.material.color.setHex(COLORS.cyan);
  ring2.material.opacity = 0.35;
  ring2.rotation.x = Math.PI / 1.7;
  ring2.rotation.y = 0.4;
  group.add(ring1, ring2);

  // Small orbiting satellites
  const satellites = [];
  const satGeo = new THREE.SphereGeometry(0.07, 16, 16);
  [COLORS.cyan, COLORS.pink, COLORS.violet].forEach((color, i) => {
    const sat = new THREE.Mesh(satGeo, new THREE.MeshBasicMaterial({ color }));
    sat.userData = { radius: 2.8 + i * 0.25, speed: 0.4 + i * 0.18, offset: i * 2.1, tilt: 0.3 + i * 0.35 };
    satellites.push(sat);
    group.add(sat);
  });

  // Star / particle field — fewer particles on small screens
  const isSmall = window.innerWidth < 768;
  const count = isSmall ? 700 : 1600;
  const positions = new Float32Array(count * 3);
  const colors = new Float32Array(count * 3);
  const palette = [new THREE.Color(COLORS.violet), new THREE.Color(COLORS.cyan), new THREE.Color(0xffffff)];
  for (let i = 0; i < count; i++) {
    const r = 6 + Math.random() * 18;
    const theta = Math.random() * Math.PI * 2;
    const phi = Math.acos(2 * Math.random() - 1);
    positions[i * 3] = r * Math.sin(phi) * Math.cos(theta);
    positions[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
    positions[i * 3 + 2] = Math.min(r * Math.cos(phi) - 6, 1); // keep clear of the camera
    const c = palette[i % palette.length];
    colors.set([c.r, c.g, c.b], i * 3);
  }
  const starsGeo = new THREE.BufferGeometry();
  starsGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  starsGeo.setAttribute('color', new THREE.BufferAttribute(colors, 3));
  const stars = new THREE.Points(starsGeo, new THREE.PointsMaterial({
    size: 0.08, map: dotTexture(), vertexColors: true, transparent: true, opacity: 0.9,
    depthWrite: false, blending: THREE.AdditiveBlending,
  }));
  scene.add(stars);

  // Layout: object sits to the side on wide screens, centred and smaller on phones
  function layout() {
    const w = canvas.clientWidth || window.innerWidth;
    const h = canvas.clientHeight || window.innerHeight;
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();

    const wide = w >= 960;
    if (variant === 'hero') {
      group.position.x = wide ? 2.9 : 0;
      group.userData.baseY = wide ? 0 : 1.2;
      group.scale.setScalar(wide ? 1 : w < 480 ? 0.62 : 0.78);
    } else {
      group.position.x = 0;
      group.userData.baseY = 0;
      group.scale.setScalar(w < 480 ? 0.7 : 0.9);
    }
  }
  layout();
  new ResizeObserver(layout).observe(canvas);

  // Interaction
  const pointer = { x: 0, y: 0 };
  const eased = { x: 0, y: 0 };
  window.addEventListener('pointermove', (e) => {
    pointer.x = (e.clientX / window.innerWidth) * 2 - 1;
    pointer.y = (e.clientY / window.innerHeight) * 2 - 1;
  }, { passive: true });

  let scrollProgress = 0;
  window.addEventListener('scroll', () => {
    scrollProgress = window.scrollY / Math.max(1, window.innerHeight);
  }, { passive: true });

  // Loop — paused while the tab is hidden or the canvas is offscreen
  const clock = new THREE.Clock();
  let running = true;
  let visible = true;
  let frame = 0;

  function render() {
    const t = clock.getElapsedTime();

    eased.x += (pointer.x - eased.x) * 0.05;
    eased.y += (pointer.y - eased.y) * 0.05;

    core.rotation.x = t * 0.18 + scrollProgress * 0.8;
    core.rotation.y = t * 0.25 + scrollProgress * 1.2;
    wire.rotation.x = -t * 0.08;
    wire.rotation.y = -t * 0.12;
    ring1.rotation.z = t * 0.15;
    ring2.rotation.z = -t * 0.1;

    group.rotation.y = eased.x * 0.45;
    group.rotation.x = eased.y * 0.3;
    group.position.y = group.userData.baseY + Math.sin(t * 0.8) * 0.12;

    satellites.forEach(({ userData: d, position }) => {
      const a = t * d.speed + d.offset;
      position.set(Math.cos(a) * d.radius, Math.sin(a) * d.radius * Math.sin(d.tilt), Math.sin(a) * d.radius * Math.cos(d.tilt));
    });

    stars.rotation.y = t * 0.012 + eased.x * 0.05;
    stars.rotation.x = eased.y * 0.03;
    camera.position.z = 8 + Math.min(scrollProgress, 1.5) * 1.2;

    renderer.render(scene, camera);
  }

  function tick() {
    if (!running || !visible) { frame = 0; return; }
    render();
    frame = requestAnimationFrame(tick);
  }
  function start() { if (!frame && running && visible && !reduceMotion) frame = requestAnimationFrame(tick); }

  document.addEventListener('visibilitychange', () => { running = !document.hidden; start(); });
  new IntersectionObserver(([entry]) => { visible = entry.isIntersecting; start(); }).observe(canvas);

  if (reduceMotion) {
    // Single static frame, re-rendered on resize
    render();
    new ResizeObserver(render).observe(canvas);
  } else {
    start();
  }

  canvas.classList.add('is-ready');
  return { renderer, scene, camera };
}
