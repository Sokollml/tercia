// Tercia portfolio showcase — mobile menu + language switcher + cases grid
// Design system reused verbatim from tercia.dev (styles.css).
(function () {
  'use strict';

  /* ============ Portfolio cases (22 works, 7 categories) ============ */
  // demo/repo — заполни ссылками на Vercel / t.me / GitHub (сейчас плейсхолдеры '#').
  var CAT = {
    landing: { ru: 'Лендинги',        en: 'Landing pages',  zh: '落地页' },
    ai:      { ru: 'ИИ-ассистенты',   en: 'AI assistants',  zh: 'AI 助手' },
    bot:     { ru: 'Telegram-боты',   en: 'Telegram bots',  zh: 'Telegram 机器人' },
    comm:    { ru: 'Боты сообществ',  en: 'Community bots', zh: '社群机器人' },
    mini:    { ru: 'Mini-apps',       en: 'Mini-apps',      zh: '小程序' },
    wp:      { ru: 'WordPress',       en: 'WordPress',      zh: 'WordPress' },
    n8n:     { ru: 'Автоматизации',   en: 'Automation',     zh: '自动化' }
  };
  var CAT_ORDER = ['landing', 'ai', 'bot', 'comm', 'mini', 'n8n', 'wp'];

  var CASES = [
    // --- Лендинги ---
    { cat: 'landing', cover: 1, demo: '#', repo: '#',
      title: { ru: 'SaaS-аналитика — Swiss', en: 'SaaS analytics — Swiss', zh: 'SaaS 分析 — Swiss' },
      meta:  { ru: 'Модульная сетка · гротеск', en: 'Grid system · grotesque', zh: '网格系统 · 无衬线' } },
    { cat: 'landing', cover: 2, demo: '#', repo: '#',
      title: { ru: 'Кофейня — Editorial', en: 'Coffee shop — Editorial', zh: '咖啡馆 — Editorial' },
      meta:  { ru: 'Крупный serif · воздух', en: 'Big serif · whitespace', zh: '大衬线 · 留白' } },
    { cat: 'landing', cover: 3, demo: '#', repo: '#',
      title: { ru: 'Моб. приложение — Tactile', en: 'Mobile app — Tactile', zh: '移动应用 — Tactile' },
      meta:  { ru: 'Тёмный премиум · глубина', en: 'Dark premium · depth', zh: '深色高级 · 层次' } },
    { cat: 'landing', cover: 1, demo: '#', repo: '#',
      title: { ru: 'Онлайн-курс — Maximalist', en: 'Online course — Maximalist', zh: '在线课程 — Maximalist' },
      meta:  { ru: 'Смелая типографика · цифры', en: 'Bold type · big numbers', zh: '大胆字体 · 大数字' } },

    // --- ИИ-ассистенты (n8n) ---
    { cat: 'ai', cover: 2, demo: '#', repo: '#',
      title: { ru: 'ИИ-нутрициолог', en: 'AI nutritionist', zh: 'AI 营养师' },
      meta:  { ru: 'n8n · калории и БЖУ', en: 'n8n · calories & macros', zh: 'n8n · 卡路里与营养' } },
    { cat: 'ai', cover: 3, demo: '#', repo: '#',
      title: { ru: 'ИИ-помощник по текстам', en: 'AI writing assistant', zh: 'AI 文案助手' },
      meta:  { ru: 'n8n · письма, посты, ответы', en: 'n8n · emails, posts, replies', zh: 'n8n · 邮件、帖子、回复' } },
    { cat: 'ai', cover: 1, demo: '#', repo: '#',
      title: { ru: 'ИИ FAQ / поддержка', en: 'AI FAQ / support', zh: 'AI 常见问题 / 支持' },
      meta:  { ru: 'n8n · ответы по базе знаний', en: 'n8n · answers from KB', zh: 'n8n · 基于知识库' } },

    // --- Telegram-боты (код) ---
    { cat: 'bot', cover: 3, demo: '#', repo: '#',
      title: { ru: 'Бот записи к мастеру', en: 'Booking bot', zh: '预约机器人' },
      meta:  { ru: 'aiogram · FSM · слоты', en: 'aiogram · FSM · slots', zh: 'aiogram · 状态机 · 时段' } },
    { cat: 'bot', cover: 1, demo: '#', repo: '#',
      title: { ru: 'ИИ-репетитор языка', en: 'AI language tutor', zh: 'AI 语言家教' },
      meta:  { ru: 'aiogram · интервальные повторы', en: 'aiogram · spaced repetition', zh: 'aiogram · 间隔复习' } },

    // --- Боты сообществ ---
    { cat: 'comm', cover: 2, demo: '#', repo: '#',
      title: { ru: 'Бот активности / XP', en: 'Engagement / XP bot', zh: '活跃度 / XP 机器人' },
      meta:  { ru: 'XP · лидерборд · вопрос дня', en: 'XP · leaderboard · daily', zh: 'XP · 排行榜 · 每日' } },
    { cat: 'comm', cover: 3, demo: '#', repo: '#',
      title: { ru: 'Бот викторин', en: 'Quiz bot', zh: '答题机器人' },
      meta:  { ru: 'quiz-опросы · сезоны · очки', en: 'quiz polls · seasons · scores', zh: '答题投票 · 赛季 · 积分' } },
    { cat: 'comm', cover: 1, demo: '#', repo: '#',
      title: { ru: 'Бот розыгрышей + рефералы', en: 'Giveaway + referrals bot', zh: '抽奖 + 推荐机器人' },
      meta:  { ru: 'честный сид · deep-links', en: 'fair seed · deep-links', zh: '公平种子 · 深链' } },
    { cat: 'comm', cover: 2, demo: '#', repo: '#',
      title: { ru: 'Бот модерации + капча', en: 'Moderation + captcha bot', zh: '管理 + 验证机器人' },
      meta:  { ru: 'welcome · антиспам · варны', en: 'welcome · anti-spam · warns', zh: '欢迎 · 反垃圾 · 警告' } },

    // --- Mini-apps ---
    { cat: 'mini', cover: 3, demo: '#', repo: '#',
      title: { ru: 'Трекер привычек', en: 'Habit tracker', zh: '习惯打卡' },
      meta:  { ru: 'React · initData HMAC · стрики', en: 'React · initData HMAC · streaks', zh: 'React · initData 校验 · 连续' } },
    { cat: 'mini', cover: 1, demo: '#', repo: '#',
      title: { ru: 'Карта лояльности кафе', en: 'Cafe loyalty card', zh: '咖啡忠诚卡' },
      meta:  { ru: 'React · QR-штампы · роли', en: 'React · QR stamps · roles', zh: 'React · 二维码印章 · 角色' } },
    { cat: 'mini', cover: 2, demo: '#', repo: '#',
      title: { ru: 'Поиск фриланс-заказов', en: 'Freelance orders finder', zh: '自由职业订单搜索' },
      meta:  { ru: 'React · n8n · Telethon-сборщик', en: 'React · n8n · Telethon collector', zh: 'React · n8n · Telethon 采集' } },

    // --- Автоматизации (n8n) ---
    { cat: 'n8n', cover: 1, demo: '#', repo: '#',
      title: { ru: 'Пайплайн заявок', en: 'Lead pipeline', zh: '线索管道' },
      meta:  { ru: 'webhook · ИИ-класс. · дайджест', en: 'webhook · AI triage · digest', zh: 'webhook · AI 分类 · 摘要' } },
    { cat: 'n8n', cover: 2, demo: '#', repo: '#',
      title: { ru: 'Мониторинг + отчёт', en: 'Monitoring + report', zh: '监控 + 报告' },
      meta:  { ru: 'schedule · детект изменений', en: 'schedule · change detect', zh: '定时 · 变更检测' } },
    { cat: 'n8n', cover: 3, demo: '#', repo: '#',
      title: { ru: 'Кросс-постинг в каналы', en: 'Cross-posting', zh: '跨渠道发布' },
      meta:  { ru: 'очередь · отложенный постинг', en: 'queue · scheduled posting', zh: '队列 · 定时发布' } },

    // --- WordPress ---
    { cat: 'wp', cover: 2, demo: '#', repo: '#',
      title: { ru: 'Сайт ресторана', en: 'Restaurant site', zh: '餐厅网站' },
      meta:  { ru: 'WP · CPT «Блюдо» · бронь', en: 'WP · dish CPT · booking', zh: 'WP · 菜品类型 · 预订' } },
    { cat: 'wp', cover: 3, demo: '#', repo: '#',
      title: { ru: 'Сайт фитнес-студии', en: 'Fitness studio site', zh: '健身工作室网站' },
      meta:  { ru: 'WP · расписание · тренеры', en: 'WP · schedule · trainers', zh: 'WP · 课程表 · 教练' } },
    { cat: 'wp', cover: 1, demo: '#', repo: '#',
      title: { ru: 'Плагин: блок отзывов', en: 'Plugin: reviews block', zh: '插件：评价区块' },
      meta:  { ru: 'Gutenberg · карусель / сетка', en: 'Gutenberg · carousel / grid', zh: 'Gutenberg · 轮播 / 网格' } }
  ];

  var UI = {
    demo:  { ru: 'Живое демо', en: 'Live demo', zh: '在线演示' },
    repo:  { ru: 'GitHub',     en: 'GitHub',    zh: 'GitHub' },
    badge: { ru: '',           en: '',          zh: '' },
    soon:  { ru: 'скоро',      en: 'soon',      zh: '即将' }
  };

  function renderCases(lang) {
    var grid = document.getElementById('cases-grid');
    if (!grid) return;
    var L = (CAT[CAT_ORDER[0]][lang] != null) ? lang : 'ru';
    var html = '';
    CAT_ORDER.forEach(function (key) {
      var items = CASES.filter(function (c) { return c.cat === key; });
      if (!items.length) return;
      html += '<div class="case-group-head"><span class="case-group-dot" aria-hidden="true"></span>' +
              CAT[key][L] + '<span class="case-group-count">' + items.length + '</span></div>';
      items.forEach(function (c) {
        var demoReal = c.demo && c.demo !== '#';
        var repoReal = c.repo && c.repo !== '#';
        html +=
          '<article class="case">' +
            '<div class="case-cover c' + c.cover + '"><svg class="sparkle" viewBox="0 0 120 120" aria-hidden="true"><use href="#spk"/></svg></div>' +
            '<div class="case-body">' +
              '<div class="case-badge">' + UI.badge[L] + '</div>' +
              '<div class="case-title">' + c.title[L] + '</div>' +
              '<div class="case-meta">' + c.meta[L] + '</div>' +
              '<div class="case-actions">' +
                (demoReal
                  ? '<a class="btn btn-acid case-btn" href="' + c.demo + '" target="_blank" rel="noopener">' + UI.demo[L] + ' →</a>'
                  : '<span class="btn btn-acid case-btn is-soon" aria-disabled="true">' + UI.demo[L] + ' · ' + UI.soon[L] + '</span>') +
                (repoReal
                  ? '<a class="btn btn-ghost case-btn" href="' + c.repo + '" target="_blank" rel="noopener"><svg class="case-btn-ic" viewBox="0 0 24 24" aria-hidden="true"><use href="#ic-gh"/></svg>' + UI.repo[L] + '</a>'
                  : '<span class="btn btn-ghost case-btn is-soon" aria-disabled="true"><svg class="case-btn-ic" viewBox="0 0 24 24" aria-hidden="true"><use href="#ic-gh"/></svg>' + UI.repo[L] + '</span>') +
              '</div>' +
            '</div>' +
          '</article>';
      });
    });
    grid.innerHTML = html;
  }

  /* ============ i18n ============ */
  var I18N = {
    ru: {
      'meta.title': 'Tercia — портфолио · цифровые продукты под ключ',
      'brand.tag': 'IT-агентство<br>полного цикла',
      'nav.services': 'Услуги',
      'nav.cases': 'Кейсы',
      'nav.process': 'Процесс',
      'nav.stats': 'Цифры',
      'nav.contacts': 'Контакты',
      'nav.cta': 'Обсудить проект',
      'hero.h1': 'Цифровые<br>продукты <span class="accent">под ключ</span>',
      'hero.sub': 'Сайты, лендинги, Telegram-боты, ИИ-ассистенты, mini-app и автоматизация. Одна команда — от идеи до запуска. Ниже — живые демо наших работ.',
      'hero.cta': 'Смотреть работы →',
      'hero.cases': 'Обсудить проект',
      'hero.stat1': 'проекта в портфолио',
      'hero.stat2num': '7 дней',
      'hero.stat2': 'средний срок старта',
      'hero.stat3': 'боты и поддержка',
      'marquee': 'САЙТЫ  ✦  ЛЕНДИНГИ  ✦  TELEGRAM-БОТЫ  ✦  ИИ-АССИСТЕНТЫ  ✦  MINI-APP  ✦  АВТОМАТИЗАЦИЯ  ✦  ',
      'cases.kicker': 'Кейсы',
      'cases.h2': 'Работы студии',
      'cases.lead': '22 проекта по семи направлениям. У каждого — живое демо и исходники на GitHub.',
      'services.kicker': 'Услуги',
      'services.h2': 'Всё для бизнеса<br>в диджитал',
      'services.lead': 'Шесть направлений и одна команда, которая ведёт проект от старта до результата.',
      'svc.1.t': 'Сайты и лендинги',
      'svc.1.p': 'Продающие сайты от прототипа до запуска — быстро, без воды и на понятной вам логике.',
      'svc.2.t': 'Telegram-боты · mini-app',
      'svc.2.p': 'Боты, воронки и mini-apps — продажи и поддержка 24/7.',
      'svc.3.t': 'ИИ-ассистенты',
      'svc.3.p': 'Боты на LLM: поддержка, консультации, разбор заявок.',
      'svc.4.t': 'Автоматизация',
      'svc.4.p': 'Связываем CRM, чаты и сервисы через n8n.',
      'svc.5.t': 'WordPress',
      'svc.5.p': 'Сайты под управлением владельца.',
      'svc.6.t': 'Mini-apps',
      'svc.6.p': 'Telegram mini-app с реальным бэкендом.',
      'band.1': 'направлений — одна команда',
      'band.2': 'проекта с живыми демо',
      'band.3': 'боты и поддержка',
      'band.4': 'двуязычные интерфейсы',
      'process.kicker': 'Процесс',
      'process.h2': 'Как мы работаем',
      'step.1.t': 'Бриф',
      'step.1.p': 'Разбираем задачу, цели и сроки. Фиксируем результат.',
      'step.2.t': 'Дизайн',
      'step.2.p': 'Прототип и визуал. Согласуем до строчки кода.',
      'step.3.t': 'Сборка',
      'step.3.p': 'Разработка, интеграции и тесты. Прозрачные апдейты.',
      'step.4.t': 'Запуск',
      'step.4.p': 'Публикуем, обучаем команду и остаёмся на поддержке.',
      'cta.h2': 'Запустим ваш проект',
      'cta.sub': 'Бесплатная консультация и план запуска за 24 часа.',
      'cta.btn': 'Обсудить проект →',
      'footer.about': 'IT-агентство полного цикла. Весь диджитал — под одной звездой.',
      'footer.services': 'Направления',
      'footer.sites': 'Лендинги',
      'footer.apps': 'Mini-apps',
      'footer.bots': 'Боты',
      'footer.contacts': 'Контакты',
      'footer.rights': 'Все права защищены.'
    },
    en: {
      'meta.title': 'Tercia — portfolio · turnkey digital products',
      'brand.tag': 'Full-cycle<br>IT agency',
      'nav.services': 'Services',
      'nav.cases': 'Cases',
      'nav.process': 'Process',
      'nav.stats': 'Numbers',
      'nav.contacts': 'Contacts',
      'nav.cta': 'Start a project',
      'hero.h1': 'Turnkey<br>digital <span class="accent">products</span>',
      'hero.sub': 'Websites, landing pages, Telegram bots, AI assistants, mini-apps and automation. One team — from idea to launch. Live demos below.',
      'hero.cta': 'View work →',
      'hero.cases': 'Start a project',
      'hero.stat1': 'projects in portfolio',
      'hero.stat2num': '7 days',
      'hero.stat2': 'average time to start',
      'hero.stat3': 'bots & support',
      'marquee': 'WEBSITES  ✦  LANDING PAGES  ✦  TELEGRAM BOTS  ✦  AI ASSISTANTS  ✦  MINI-APPS  ✦  AUTOMATION  ✦  ',
      'cases.kicker': 'Cases',
      'cases.h2': 'Studio work',
      'cases.lead': '22 projects across seven directions. Each has a live demo and source on GitHub. Demos are labeled as concept / pet-project.',
      'services.kicker': 'Services',
      'services.h2': 'Everything your business<br>needs in digital',
      'services.lead': 'Six directions and one team that drives your project from start to result.',
      'svc.1.t': 'Websites & landing pages',
      'svc.1.p': 'Selling websites from prototype to launch — fast, no fluff, on logic you understand.',
      'svc.2.t': 'Telegram bots · mini-apps',
      'svc.2.p': 'Bots, funnels and mini-apps — sales and support 24/7.',
      'svc.3.t': 'AI assistants',
      'svc.3.p': 'LLM bots: support, consultations, lead triage.',
      'svc.4.t': 'Automation',
      'svc.4.p': 'We connect CRMs, chats and services via n8n.',
      'svc.5.t': 'WordPress',
      'svc.5.p': 'Owner-managed content sites.',
      'svc.6.t': 'Mini-apps',
      'svc.6.p': 'Telegram mini-apps with a real backend.',
      'band.1': 'directions — one team',
      'band.2': 'projects with live demos',
      'band.3': 'bots & support',
      'band.4': 'bilingual interfaces',
      'process.kicker': 'Process',
      'process.h2': 'How we work',
      'step.1.t': 'Brief',
      'step.1.p': 'We clarify the task, goals and deadlines. We fix the outcome.',
      'step.2.t': 'Design',
      'step.2.p': 'Prototype and visuals. Approved before a single line of code.',
      'step.3.t': 'Build',
      'step.3.p': 'Development, integrations and tests. Transparent updates.',
      'step.4.t': 'Launch',
      'step.4.p': 'We publish, train your team and stay for support.',
      'cta.h2': 'Let’s launch your project',
      'cta.sub': 'Free consultation and a launch plan within 24 hours.',
      'cta.btn': 'Start a project →',
      'footer.about': 'Full-cycle IT agency. All your digital — under one star.',
      'footer.services': 'Directions',
      'footer.sites': 'Landing pages',
      'footer.apps': 'Mini-apps',
      'footer.bots': 'Bots',
      'footer.contacts': 'Contacts',
      'footer.rights': 'All rights reserved.'
    },
    zh: {
      'meta.title': 'Tercia — 作品集 · 一站式数字产品',
      'brand.tag': '全流程<br>IT 机构',
      'nav.services': '服务',
      'nav.cases': '案例',
      'nav.process': '流程',
      'nav.stats': '数据',
      'nav.contacts': '联系',
      'nav.cta': '洽谈项目',
      'hero.h1': '一站式<br>数字<span class="accent">产品</span>',
      'hero.sub': '网站、落地页、Telegram 机器人、AI 助手、小程序与自动化。一个团队——从创意到上线。下方为在线演示。',
      'hero.cta': '查看作品 →',
      'hero.cases': '洽谈项目',
      'hero.stat1': '个作品集项目',
      'hero.stat2num': '7 天',
      'hero.stat2': '平均启动周期',
      'hero.stat3': '机器人与支持',
      'marquee': '网站  ✦  落地页  ✦  TELEGRAM 机器人  ✦  AI 助手  ✦  小程序  ✦  自动化  ✦  ',
      'cases.kicker': '案例',
      'cases.h2': '工作室作品',
      'cases.lead': '七个方向共 22 个项目。每个都有在线演示与 GitHub 源码。演示均标注为概念 / 练手项目。',
      'services.kicker': '服务',
      'services.h2': '数字业务<br>一站式解决',
      'services.lead': '六大方向，一个团队，从启动到成果全程负责。',
      'svc.1.t': '网站与落地页',
      'svc.1.p': '从原型到上线的营销型网站——快速、直接、逻辑清晰。',
      'svc.2.t': 'Telegram 机器人 · 小程序',
      'svc.2.p': '机器人、销售漏斗与小程序——全天候销售与支持。',
      'svc.3.t': 'AI 助手',
      'svc.3.p': 'LLM 机器人：支持、咨询、线索分类。',
      'svc.4.t': '自动化',
      'svc.4.p': '通过 n8n 打通 CRM、聊天与各类服务。',
      'svc.5.t': 'WordPress',
      'svc.5.p': '业主自主管理的内容网站。',
      'svc.6.t': '小程序',
      'svc.6.p': '带真实后端的 Telegram 小程序。',
      'band.1': '个方向——一个团队',
      'band.2': '个带在线演示的项目',
      'band.3': '机器人与支持',
      'band.4': '双语界面',
      'process.kicker': '流程',
      'process.h2': '我们如何工作',
      'step.1.t': '需求沟通',
      'step.1.p': '梳理任务、目标与周期，明确成果。',
      'step.2.t': '设计',
      'step.2.p': '原型与视觉，编码前完成确认。',
      'step.3.t': '开发',
      'step.3.p': '开发、集成与测试，进度透明。',
      'step.4.t': '上线',
      'step.4.p': '发布、培训团队并持续提供支持。',
      'cta.h2': '启动您的项目',
      'cta.sub': '免费咨询，24 小时内提供上线方案。',
      'cta.btn': '洽谈项目 →',
      'footer.about': '全流程 IT 机构。所有数字业务，尽在一颗星下。',
      'footer.services': '方向',
      'footer.sites': '落地页',
      'footer.apps': '小程序',
      'footer.bots': '机器人',
      'footer.contacts': '联系方式',
      'footer.rights': '保留所有权利。'
    }
  };

  function applyLang(lang) {
    var dict = I18N[lang] || I18N.ru;
    document.documentElement.lang = lang === 'zh' ? 'zh' : lang;

    document.querySelectorAll('[data-i18n]').forEach(function (el) {
      var v = dict[el.getAttribute('data-i18n')];
      if (v != null) el.textContent = v;
    });
    document.querySelectorAll('[data-i18n-html]').forEach(function (el) {
      var v = dict[el.getAttribute('data-i18n-html')];
      if (v != null) el.innerHTML = v;
    });

    if (dict['meta.title']) document.title = dict['meta.title'];

    renderCases(lang === 'zh' ? 'zh' : lang);

    document.querySelectorAll('.lang-switch button').forEach(function (b) {
      var active = b.getAttribute('data-lang') === lang;
      b.classList.toggle('active', active);
      b.setAttribute('aria-pressed', String(active));
    });

    try { localStorage.setItem('tercia-lang', lang); } catch (e) {}
  }

  function detectLang() {
    var saved;
    try { saved = localStorage.getItem('tercia-lang'); } catch (e) {}
    if (saved && I18N[saved]) return saved;
    var nav = (navigator.language || 'ru').toLowerCase();
    if (nav.indexOf('zh') === 0) return 'zh';
    if (nav.indexOf('en') === 0) return 'en';
    return 'ru';
  }

  document.querySelectorAll('.lang-switch button').forEach(function (b) {
    b.addEventListener('click', function () {
      applyLang(b.getAttribute('data-lang'));
    });
  });

  applyLang(detectLang());

  /* ============ Mobile menu ============ */
  var toggle = document.querySelector('.nav-toggle');
  var menu = document.getElementById('mobile-menu');
  var body = document.body;

  function closeMenu() {
    if (!menu) return;
    menu.classList.remove('open');
    toggle.classList.remove('active');
    toggle.setAttribute('aria-expanded', 'false');
    body.classList.remove('menu-open');
  }

  if (toggle && menu) {
    toggle.addEventListener('click', function () {
      var isOpen = menu.classList.toggle('open');
      toggle.classList.toggle('active', isOpen);
      toggle.setAttribute('aria-expanded', String(isOpen));
      body.classList.toggle('menu-open', isOpen);
    });

    menu.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', closeMenu);
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') closeMenu();
    });
    window.addEventListener('resize', function () {
      if (window.innerWidth > 860) closeMenu();
    });
  }

  // current year in footer
  var yr = document.getElementById('year');
  if (yr) yr.textContent = String(new Date().getFullYear());
})();
