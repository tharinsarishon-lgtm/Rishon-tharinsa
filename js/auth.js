// Login / sign-up form behaviour: validation, show/hide password, strength meter.
// NOTE: front-end only. Replace submitToServer() with a call to your real backend
// (e.g. Firebase Auth, Supabase, or your own API). Passwords are never stored here.
(function () {
  const EYE = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/></svg>';
  const EYE_OFF = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.9 17.9A10.4 10.4 0 0 1 12 19c-6.5 0-10-7-10-7a18.5 18.5 0 0 1 5.1-5.9M9.9 5.2A9.1 9.1 0 0 1 12 5c6.5 0 10 7 10 7a18.6 18.6 0 0 1-2.2 3.2M14.1 14.1a3 3 0 1 1-4.2-4.2M2 2l20 20"/></svg>';
  const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

  // Toast
  const toastEl = document.getElementById('toast');
  let toastTimer;
  function toast(message, type = 'success') {
    toastEl.className = `toast ${type}`;
    toastEl.textContent = message;
    requestAnimationFrame(() => toastEl.classList.add('is-show'));
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toastEl.classList.remove('is-show'), 3200);
  }

  // Show / hide password
  document.querySelectorAll('[data-toggle-pass]').forEach((btn) => {
    const input = document.getElementById(btn.dataset.togglePass);
    btn.innerHTML = EYE;
    btn.addEventListener('click', () => {
      const show = input.type === 'password';
      input.type = show ? 'text' : 'password';
      btn.innerHTML = show ? EYE_OFF : EYE;
      btn.setAttribute('aria-label', show ? 'Hide password' : 'Show password');
    });
  });

  // Social buttons (placeholder until OAuth is wired up)
  document.querySelectorAll('[data-social]').forEach((btn) => {
    btn.addEventListener('click', () => toast(`${btn.dataset.social} sign-in will be available once the backend is connected.`, 'success'));
  });
  const forgot = document.getElementById('forgotLink');
  if (forgot) forgot.addEventListener('click', (e) => { e.preventDefault(); toast('Password reset will be available once the backend is connected.'); });

  // Field helpers
  function setError(form, name, message) {
    const field = form.querySelector(`[data-field="${name}"]`);
    if (!field) return;
    field.classList.toggle('has-error', Boolean(message));
    field.classList.toggle('is-valid', !message);
    field.querySelector('.error-msg').textContent = message || '';
    const input = field.querySelector('input');
    if (input) input.setAttribute('aria-invalid', String(Boolean(message)));
  }

  function passwordScore(pw) {
    let score = 0;
    if (pw.length >= 8) score++;
    if (/[a-z]/.test(pw) && /[A-Z]/.test(pw)) score++;
    if (/\d/.test(pw)) score++;
    if (/[^A-Za-z0-9]/.test(pw)) score++;
    if (pw.length < 8) score = Math.min(score, 1);
    return score;
  }

  const validators = {
    firstName: (v) => (v.trim() ? '' : 'Please enter your first name'),
    lastName: (v) => (v.trim() ? '' : 'Please enter your last name'),
    email: (v) => (!v.trim() ? 'Email is required' : EMAIL_RE.test(v.trim()) ? '' : 'Please enter a valid email address'),
    password: (v, form) => {
      if (!v) return 'Password is required';
      if (v.length < 8) return 'Password must be at least 8 characters';
      if (form.id === 'signupForm' && passwordScore(v) < 2) return 'Add uppercase letters, numbers or symbols';
      return '';
    },
    confirm: (v, form) => (!v ? 'Please confirm your password' : v === form.password.value ? '' : 'Passwords do not match'),
    terms: (_, form) => (form.terms.checked ? '' : 'You must accept the terms to continue'),
  };

  function validateField(form, name) {
    const input = form.elements[name];
    const message = validators[name](input.type === 'checkbox' ? input.checked : input.value, form);
    setError(form, name, message);
    return !message;
  }

  // Strength meter
  const bars = document.querySelectorAll('.strength i');
  const strengthLabel = document.getElementById('strengthLabel');
  const LEVELS = [
    { label: 'Use 8+ characters with letters, numbers & symbols', color: '' },
    { label: 'Weak', color: 'var(--danger)' },
    { label: 'Fair', color: 'var(--warning)' },
    { label: 'Good', color: 'var(--cyan)' },
    { label: 'Strong', color: 'var(--success)' },
  ];
  function updateStrength(pw) {
    const score = pw ? Math.max(1, passwordScore(pw)) : 0;
    bars.forEach((bar, i) => { bar.style.background = i < score ? LEVELS[score].color : ''; });
    strengthLabel.textContent = LEVELS[score].label;
    strengthLabel.style.color = LEVELS[score].color || '';
  }

  // Simulated request — swap for fetch('/api/login', …) etc.
  function submitToServer(data) {
    return new Promise((resolve) => setTimeout(() => resolve({ ok: true, data }), 1200));
  }

  function wireForm(form, fields, onSuccess) {
    if (!form) return;
    const touched = new Set();

    fields.forEach((name) => {
      const input = form.elements[name];
      const evt = input.type === 'checkbox' ? 'change' : 'blur';
      input.addEventListener(evt, () => { touched.add(name); validateField(form, name); });
      input.addEventListener('input', () => {
        if (touched.has(name)) validateField(form, name);
        if (name === 'password' && touched.has('confirm')) validateField(form, 'confirm');
      });
    });

    if (strengthLabel && form.password) form.password.addEventListener('input', (e) => updateStrength(e.target.value));

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      fields.forEach((n) => touched.add(n));
      const results = fields.map((n) => validateField(form, n));
      if (results.includes(false)) {
        const firstBad = form.querySelector('.has-error input');
        if (firstBad) firstBad.focus();
        toast('Please fix the highlighted fields.', 'error');
        return;
      }

      const btn = form.querySelector('[type="submit"]');
      const original = btn.innerHTML;
      btn.disabled = true;
      btn.innerHTML = '<span class="spinner"></span> Please wait…';

      // Only non-sensitive fields are passed along; the password never leaves this function in the demo.
      const payload = { email: form.email.value.trim() };
      if (form.firstName) payload.name = `${form.firstName.value.trim()} ${form.lastName.value.trim()}`;
      await submitToServer(payload);

      btn.disabled = false;
      btn.innerHTML = original;
      onSuccess(payload);
    });
  }

  wireForm(document.getElementById('loginForm'), ['email', 'password'], () => {
    toast('Logged in successfully! Redirecting…');
    setTimeout(() => { window.location.href = 'index.html'; }, 1400);
  });

  wireForm(document.getElementById('signupForm'), ['firstName', 'lastName', 'email', 'password', 'confirm', 'terms'], (p) => {
    toast(`Welcome aboard, ${p.name.split(' ')[0]}! Redirecting to log in…`);
    setTimeout(() => { window.location.href = 'login.html'; }, 1600);
  });
})();
