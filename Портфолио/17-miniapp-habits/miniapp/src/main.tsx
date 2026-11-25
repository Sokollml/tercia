import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.js';
import { initTelegram } from './lib/telegram.js';
import './styles/index.css';

// Инициализируем Telegram WebApp (тема, expand, ready) до рендера.
initTelegram();

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>
);
