<template>
  <div id="app">
    <!-- Global Navigation Bar -->
    <Navbar />

    <main>
      <router-view />
    </main>
  </div>
</template>

<script>
import Navbar from './components/Navbar.vue'

export default {
  name: 'App',
  components: {
    Navbar
  }
}
</script>

<style>
/* Modern Design System with CSS Custom Properties */
:root {
  /* Color Palette */
  --color-primary: #6366f1;
  --color-primary-hover: #4f46e5;
  --color-primary-light: #a5b4fc;
  --color-primary-dark: #312e81;

  --color-secondary: #06b6d4;
  --color-secondary-hover: #0891b2;
  --color-secondary-light: #67e8f9;
  --color-secondary-dark: #0e7490;

  --color-success: #10b981;
  --color-success-hover: #059669;
  --color-success-light: #6ee7b7;
  --color-success-dark: #047857;

  --color-warning: #f59e0b;
  --color-warning-hover: #d97706;
  --color-warning-light: #fcd34d;
  --color-warning-dark: #92400e;

  --color-error: #ef4444;
  --color-error-hover: #dc2626;
  --color-error-light: #fca5a5;
  --color-error-dark: #b91c1c;

  --color-info: #3b82f6;
  --color-info-hover: #2563eb;
  --color-info-light: #93c5fd;
  --color-info-dark: #1d4ed8;

  /* Neutral Colors */
  --color-white: #ffffff;
  --color-gray-50: #f9fafb;
  --color-gray-100: #f3f4f6;
  --color-gray-200: #e5e7eb;
  --color-gray-300: #d1d5db;
  --color-gray-400: #9ca3af;
  --color-gray-500: #6b7280;
  --color-gray-600: #4b5563;
  --color-gray-700: #374151;
  --color-gray-800: #1f2937;
  --color-gray-900: #111827;

  /* Semantic Colors */
  --color-background: var(--color-gray-50);
  --color-surface: var(--color-white);
  --color-surface-hover: var(--color-gray-50);
  --color-text-primary: var(--color-gray-900);
  --color-text-secondary: var(--color-gray-600);
  --color-text-muted: var(--color-gray-500);
  --color-border: var(--color-gray-200);
  --color-border-hover: var(--color-gray-300);

  /* Spacing System (8px base scale) */
  --spacing-1: 0.25rem;   /* 4px */
  --spacing-2: 0.5rem;    /* 8px */
  --spacing-3: 0.75rem;   /* 12px */
  --spacing-4: 1rem;      /* 16px */
  --spacing-5: 1.25rem;   /* 20px */
  --spacing-6: 1.5rem;    /* 24px */
  --spacing-7: 1.75rem;   /* 28px */
  --spacing-8: 2rem;      /* 32px */
  --spacing-10: 2.5rem;   /* 40px */
  --spacing-12: 3rem;     /* 48px */
  --spacing-16: 4rem;     /* 64px */
  --spacing-20: 5rem;     /* 80px */
  --spacing-24: 6rem;     /* 96px */

  /* Border Radius */
  --radius-none: 0;
  --radius-sm: 0.25rem;   /* 4px */
  --radius-md: 0.5rem;    /* 8px */
  --radius-lg: 0.75rem;   /* 12px */
  --radius-xl: 1rem;      /* 16px */
  --radius-2xl: 1.5rem;   /* 24px */
  --radius-full: 9999px;

  /* Shadows */
  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
  --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);

  /* Typography */
  --font-family-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;

  --font-size-xs: 0.75rem;    /* 12px */
  --font-size-sm: 0.875rem;   /* 14px */
  --font-size-base: 1rem;     /* 16px */
  --font-size-lg: 1.125rem;   /* 18px */
  --font-size-xl: 1.25rem;    /* 20px */
  --font-size-2xl: 1.5rem;    /* 24px */
  --font-size-3xl: 1.875rem;  /* 30px */
  --font-size-4xl: 2.25rem;   /* 36px */
  --font-size-5xl: 3rem;      /* 48px */

  --font-weight-normal: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;

  --line-height-tight: 1.25;
  --line-height-snug: 1.375;
  --line-height-normal: 1.5;
  --line-height-relaxed: 1.625;
  --line-height-loose: 2;

  /* Transitions */
  --transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
  --transition-normal: 300ms cubic-bezier(0.4, 0, 0.2, 1);
  --transition-slow: 500ms cubic-bezier(0.4, 0, 0.2, 1);
}

/* Modern CSS Reset */
*,
*::before,
*::after {
  box-sizing: border-box;
}

* {
  margin: 0;
  padding: 0;
}

html {
  -webkit-text-size-adjust: 100%;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

body {
  font-family: var(--font-family-sans);
  line-height: var(--line-height-normal);
  color: var(--color-text-primary);
  background-color: var(--color-background);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

#app {
  min-height: 100vh;
  /* Focus visible for accessibility */
  :focus-visible {
    outline: 2px solid var(--color-primary);
    outline-offset: 2px;
  }
}

main {
  width: 100%;
  min-height: calc(100vh);
}

/* Basic heading styles */
h1, h2, h3, h4, h5, h6 {
  margin-bottom: 1rem;
  line-height: 1.2;
}

/* Modern Button System */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-2);
  padding: var(--spacing-3) var(--spacing-6);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  line-height: var(--line-height-tight);
  text-decoration: none;
  white-space: nowrap;
  border: 1px solid transparent;
  border-radius: var(--radius-lg);
  background-color: var(--color-primary);
  color: var(--color-white);
  cursor: pointer;
  transition: all var(--transition-fast);
  box-shadow: var(--shadow-sm);
  position: relative;
  overflow: hidden;
}

.btn::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0) 100%);
  opacity: 0;
  transition: opacity var(--transition-fast);
}

.btn:hover:not(:disabled) {
  background-color: var(--color-primary-hover);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.btn:hover:not(:disabled)::before {
  opacity: 1;
}

.btn:active {
  transform: translateY(0);
  box-shadow: var(--shadow-sm);
}

.btn:disabled {
  background-color: var(--color-gray-400);
  color: var(--color-gray-500);
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* Button Variants */
.btn-secondary {
  background-color: var(--color-gray-600);
}

.btn-secondary:hover:not(:disabled) {
  background-color: var(--color-gray-700);
}

.btn-success {
  background-color: var(--color-success);
}

.btn-success:hover:not(:disabled) {
  background-color: var(--color-success-hover);
}

.btn-warning {
  background-color: var(--color-warning);
}

.btn-warning:hover:not(:disabled) {
  background-color: var(--color-warning-hover);
}

.btn-danger {
  background-color: var(--color-error);
  color: var(--color-white);
}

.btn-danger:hover:not(:disabled) {
  background-color: var(--color-error-hover);
}

.btn-info {
  background-color: var(--color-info);
}

.btn-info:hover:not(:disabled) {
  background-color: var(--color-info-hover);
}

/* Button Sizes */
.btn-sm {
  padding: var(--spacing-2) var(--spacing-4);
  font-size: var(--font-size-sm);
  border-radius: var(--radius-md);
}

.btn-lg {
  padding: var(--spacing-4) var(--spacing-8);
  font-size: var(--font-size-lg);
  border-radius: var(--radius-xl);
}

/* Button Styles */
.btn-outline {
  background-color: transparent;
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.btn-outline:hover:not(:disabled) {
  background-color: var(--color-primary);
  color: var(--color-white);
}

.btn-ghost {
  background-color: transparent;
  border-color: transparent;
  color: var(--color-text-primary);
  box-shadow: none;
}

.btn-ghost:hover:not(:disabled) {
  background-color: var(--color-gray-100);
}

/* Modern Form Components */
.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
}

.form-group label {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  line-height: var(--line-height-tight);
}

.form-control {
  padding: var(--spacing-3) var(--spacing-4);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  font-size: var(--font-size-base);
  font-family: var(--font-family-sans);
  background-color: var(--color-surface);
  color: var(--color-text-primary);
  transition: all var(--transition-fast);
  width: 100%;
}

.form-control:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgb(99 102 241 / 0.1);
  background-color: var(--color-white);
}

.form-control::placeholder {
  color: var(--color-text-muted);
}

.form-control:disabled {
  background-color: var(--color-gray-100);
  color: var(--color-text-muted);
  cursor: not-allowed;
}

.form-control[type="password"] {
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  letter-spacing: 0.025em;
}

.form-control[readonly] {
  background-color: var(--color-gray-50);
  cursor: default;
}

/* Form Validation States */
.form-group.has-error .form-control {
  border-color: var(--color-error);
}

.form-group.has-error .form-control:focus {
  border-color: var(--color-error);
  box-shadow: 0 0 0 3px rgb(239 68 68 / 0.1);
}

.form-group.has-success .form-control {
  border-color: var(--color-success);
}

.form-group.has-success .form-control:focus {
  border-color: var(--color-success);
  box-shadow: 0 0 0 3px rgb(16 185 129 / 0.1);
}

/* Form Help Text */
.form-text {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  line-height: var(--line-height-snug);
  margin-top: var(--spacing-1);
}

.form-text.error {
  color: var(--color-error);
}

.form-text.success {
  color: var(--color-success);
}

/* Modern Card Component */
.card {
  background: var(--color-surface);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-md);
  border: 1px solid var(--color-border);
  transition: all var(--transition-normal);
}

.card:hover {
  box-shadow: var(--shadow-lg);
  border-color: var(--color-border-hover);
}

.card-header {
  padding: var(--spacing-6);
  border-bottom: 1px solid var(--color-border);
  background: linear-gradient(135deg, var(--color-surface) 0%, var(--color-surface-hover) 100%);
}

.card-body {
  padding: var(--spacing-6);
}

.card-footer {
  padding: var(--spacing-6);
  border-top: 1px solid var(--color-border);
  background: var(--color-surface-hover);
}

/* Alert Component */
.alert {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-3);
  padding: var(--spacing-4);
  border-radius: var(--radius-lg);
  font-size: var(--font-size-sm);
  line-height: var(--line-height-relaxed);
  border: 1px solid transparent;
}

.alert-info {
  background-color: rgb(239 246 255 / 0.8);
  color: var(--color-info-dark);
  border-color: rgb(191 219 254 / 0.5);
}

.alert-success {
  background-color: rgb(236 253 245 / 0.8);
  color: var(--color-success-dark);
  border-color: rgb(187 247 208 / 0.5);
}

.alert-warning {
  background-color: rgb(255 251 235 / 0.8);
  color: var(--color-warning-dark);
  border-color: rgb(254 240 138 / 0.5);
}

.alert-error {
  background-color: rgb(254 242 242 / 0.8);
  color: var(--color-error-dark);
  border-color: rgb(254 202 202 / 0.5);
}

/* Loading States */
.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-4);
  padding: var(--spacing-12);
  color: var(--color-text-secondary);
  text-align: center;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--color-border);
  border-top: 3px solid var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.skeleton {
  background: linear-gradient(90deg,
    var(--color-gray-100) 25%,
    var(--color-gray-200) 50%,
    var(--color-gray-100) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

.skeleton-text {
  height: var(--font-size-base);
  border-radius: var(--radius-sm);
}

.skeleton-title {
  height: var(--font-size-4xl);
  width: 60%;
  margin: 0 auto var(--spacing-4);
  border-radius: var(--radius-md);
}

.skeleton-card {
  height: 200px;
  border-radius: var(--radius-xl);
}

/* Badge Component */
.badge {
  display: inline-flex;
  align-items: center;
  padding: var(--spacing-1) var(--spacing-3);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  border-radius: var(--radius-full);
  white-space: nowrap;
}

.badge-primary {
  background-color: var(--color-primary-light);
  color: var(--color-primary-dark);
}

.badge-success {
  background-color: var(--color-success-light);
  color: var(--color-success-dark);
}

.badge-warning {
  background-color: var(--color-warning-light);
  color: var(--color-warning-dark);
}

.badge-error {
  background-color: var(--color-error-light);
  color: var(--color-error-dark);
}

/* Empty State Component */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-4);
  padding: var(--spacing-12);
  text-align: center;
  color: var(--color-text-secondary);
}

.empty-state-icon {
  font-size: 4rem;
  opacity: 0.5;
}

.empty-state-title {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.empty-state-description {
  max-width: 400px;
  line-height: var(--line-height-relaxed);
}

/* Modal styles */
.modal-content {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.3);
  max-width: 400px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.auth-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

/* Responsive design */
@media (max-width: 768px) {
  .btn {
    padding: 0.625rem 1.25rem;
    font-size: 0.95rem;
  }

  .modal-content {
    padding: 1.5rem;
    margin: 1rem;
  }
}
</style>
