// Tercia landing — mobile menu + language switcher
(function () {
  'use strict';

  /* ============ i18n ============ */
  var I18N = {
    ru: {
      'meta.title': 'Tercia — цифровые продукты под ключ',
      'brand.tag': 'IT-агентство<br>полного цикла',
      'nav.services': 'Услуги',
      'nav.cases': 'Кейсы',
      'nav.process': 'Процесс',
      'nav.stats': 'Цифры',
      'nav.contacts': 'Контакты',
      'nav.cta': 'Обсудить проект',
      'hero.h1': 'Цифровые<br>продукты <span class="accent">под ключ</span>',
      'hero.sub': 'Сайты, приложения, Telegram-боты, автоматизация и контент. Одна команда — от идеи до запуска.',
      'hero.cta': 'Обсудить проект →',
      'hero.cases': 'Смотреть кейсы',
      'hero.stat1': 'проектов запущено',
      'hero.stat2num': '7 дней',
      'hero.stat2': 'средний срок старта',
      'hero.stat3': 'боты и поддержка',
      'marquee': 'САЙТЫ  ✦  ПРИЛОЖЕНИЯ  ✦  TELEGRAM-БОТЫ  ✦  MINI-APP  ✦  АВТОМАТИЗАЦИЯ  ✦  SHOPIFY  ✦  КОНТЕНТ  ✦  ',
      'services.kicker': 'Услуги',
      'services.h2': 'Всё для бизнеса<br>в диджитал',
      'services.lead': 'Шесть направлений и одна команда, которая ведёт проект от старта до результата.',
      'svc.1.t': 'Сайты и лендинги',
      'svc.1.p': 'Продающие сайты от прототипа до запуска — быстро, без воды и на понятной вам логике.',
      'svc.2.t': 'Telegram-боты · mini-app',
      'svc.2.p': 'Боты, воронки и mini-apps — продажи и поддержка 24/7.',
      'svc.3.t': 'Приложения',
      'svc.3.p': 'iOS, Android и веб — от прототипа до релиза в сторах.',
      'svc.4.t': 'Автоматизация',
      'svc.4.p': 'Связываем CRM, чаты и сервисы.',
      'svc.5.t': 'Shopify',
      'svc.5.p': 'Магазины: дизайн, товары, оплаты.',
      'svc.6.t': 'Контент и рилсы',
      'svc.6.p': 'Сценарий, съёмка, монтаж — пачками.',
      'band.1': 'услуг — одна команда',
      'band.2num': '7 дней',
      'band.2': 'до запуска проекта',
      'band.3': 'боты и поддержка',
      'band.4': 'рост заявок в среднем',
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
      'cases.kicker': 'Кейсы',
      'cases.h2': 'Избранные проекты',
      'cases.all': 'Все проекты →',
      'case.1.t': 'Магазин косметики',
      'case.1.m': 'Shopify + контент каталога',
      'case.2.t': 'Бот-воронка школы',
      'case.2.m': 'Mini-app + автопродажи',
      'case.3.t': 'Сервис доставки',
      'case.3.m': 'Приложение iOS + Android',
      'quote.text': '«Запустили сайт, бота и автоматизацию за две недели. Заявки выросли вдвое, а рутину с менеджеров сняли полностью.»',
      'quote.name': 'Анна Кот',
      'quote.role': 'Основатель, cosmetics-бренд',
      'cta.h2': 'Запустим ваш проект',
      'cta.sub': 'Бесплатная консультация и план запуска за 24 часа.',
      'cta.btn': 'Обсудить проект →',
      'footer.about': 'IT-агентство полного цикла. Весь диджитал — под одной звездой.',
      'footer.services': 'Услуги',
      'footer.sites': 'Сайты',
      'footer.apps': 'Приложения',
      'footer.bots': 'Боты',
      'footer.contacts': 'Контакты',
      'footer.rights': 'Все права защищены.'
    },
    en: {
      'meta.title': 'Tercia — turnkey digital products',
      'brand.tag': 'Full-cycle<br>IT agency',
      'nav.services': 'Services',
      'nav.cases': 'Cases',
      'nav.process': 'Process',
      'nav.stats': 'Numbers',
      'nav.contacts': 'Contacts',
      'nav.cta': 'Start a project',
      'hero.h1': 'Turnkey<br>digital <span class="accent">products</span>',
      'hero.sub': 'Websites, apps, Telegram bots, automation and content. One team — from idea to launch.',
      'hero.cta': 'Start a project →',
      'hero.cases': 'View cases',
      'hero.stat1': 'projects launched',
      'hero.stat2num': '7 days',
      'hero.stat2': 'average time to start',
      'hero.stat3': 'bots & support',
      'marquee': 'WEBSITES  ✦  APPS  ✦  TELEGRAM BOTS  ✦  MINI-APPS  ✦  AUTOMATION  ✦  SHOPIFY  ✦  CONTENT  ✦  ',
      'services.kicker': 'Services',
      'services.h2': 'Everything your business<br>needs in digital',
      'services.lead': 'Six directions and one team that drives your project from start to result.',
      'svc.1.t': 'Websites & landing pages',
      'svc.1.p': 'Selling websites from prototype to launch — fast, no fluff, on logic you understand.',
      'svc.2.t': 'Telegram bots · mini-apps',
      'svc.2.p': 'Bots, funnels and mini-apps — sales and support 24/7.',
      'svc.3.t': 'Apps',
      'svc.3.p': 'iOS, Android and web — from prototype to store release.',
      'svc.4.t': 'Automation',
      'svc.4.p': 'We connect CRMs, chats and services.',
      'svc.5.t': 'Shopify',
      'svc.5.p': 'Stores: design, products, payments.',
      'svc.6.t': 'Content & reels',
      'svc.6.p': 'Script, shooting, editing — in batches.',
      'band.1': 'services — one team',
      'band.2num': '7 days',
      'band.2': 'to project launch',
      'band.3': 'bots & support',
      'band.4': 'average leads growth',
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
      'cases.kicker': 'Cases',
      'cases.h2': 'Selected projects',
      'cases.all': 'All projects →',
      'case.1.t': 'Cosmetics store',
      'case.1.m': 'Shopify + catalog content',
      'case.2.t': 'School bot funnel',
      'case.2.m': 'Mini-app + auto-sales',
      'case.3.t': 'Delivery service',
      'case.3.m': 'iOS + Android app',
      'quote.text': '“We launched a website, a bot and automation in two weeks. Leads doubled, and the routine was fully taken off the managers.”',
      'quote.name': 'Anna Kot',
      'quote.role': 'Founder, cosmetics brand',
      'cta.h2': 'Let’s launch your project',
      'cta.sub': 'Free consultation and a launch plan within 24 hours.',
      'cta.btn': 'Start a project →',
      'footer.about': 'Full-cycle IT agency. All your digital — under one star.',
      'footer.services': 'Services',
      'footer.sites': 'Websites',
      'footer.apps': 'Apps',
      'footer.bots': 'Bots',
      'footer.contacts': 'Contacts',
      'footer.rights': 'All rights reserved.'
    },
    zh: {
      'meta.title': 'Tercia — 一站式数字产品',
      'brand.tag': '全流程<br>IT 机构',
      'nav.services': '服务',
      'nav.cases': '案例',
      'nav.process': '流程',
      'nav.stats': '数据',
      'nav.contacts': '联系',
      'nav.cta': '洽谈项目',
      'hero.h1': '一站式<br>数字<span class="accent">产品</span>',
      'hero.sub': '网站、应用、Telegram 机器人、自动化与内容。一个团队——从创意到上线。',
      'hero.cta': '洽谈项目 →',
      'hero.cases': '查看案例',
      'hero.stat1': '个已上线项目',
      'hero.stat2num': '7 天',
      'hero.stat2': '平均启动周期',
      'hero.stat3': '机器人与支持',
      'marquee': '网站  ✦  应用  ✦  TELEGRAM 机器人  ✦  小程序  ✦  自动化  ✦  SHOPIFY  ✦  内容  ✦  ',
      'services.kicker': '服务',
      'services.h2': '数字业务<br>一站式解决',
      'services.lead': '六大方向，一个团队，从启动到成果全程负责。',
      'svc.1.t': '网站与落地页',
      'svc.1.p': '从原型到上线的营销型网站——快速、直接、逻辑清晰。',
      'svc.2.t': 'Telegram 机器人 · 小程序',
      'svc.2.p': '机器人、销售漏斗与小程序——全天候销售与支持。',
      'svc.3.t': '应用程序',
      'svc.3.p': 'iOS、Android 与网页端——从原型到应用商店发布。',
      'svc.4.t': '自动化',
      'svc.4.p': '打通 CRM、聊天与各类服务。',
      'svc.5.t': 'Shopify',
      'svc.5.p': '商店：设计、商品、支付。',
      'svc.6.t': '内容与短视频',
      'svc.6.p': '脚本、拍摄、剪辑——批量产出。',
      'band.1': '项服务——一个团队',
      'band.2num': '7 天',
      'band.2': '项目上线周期',
      'band.3': '机器人与支持',
      'band.4': '平均询盘增长',
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
      'cases.kicker': '案例',
      'cases.h2': '精选项目',
      'cases.all': '全部项目 →',
      'case.1.t': '美妆商城',
      'case.1.m': 'Shopify + 商品内容',
      'case.2.t': '学校机器人漏斗',
      'case.2.m': '小程序 + 自动销售',
      'case.3.t': '配送服务',
      'case.3.m': 'iOS + Android 应用',
      'quote.text': '“两周内上线了网站、机器人和自动化。询盘翻倍，销售完全摆脱了繁琐的日常工作。”',
      'quote.name': '安娜·科特',
      'quote.role': '创始人，美妆品牌',
      'cta.h2': '启动您的项目',
      'cta.sub': '免费咨询，24 小时内提供上线方案。',
      'cta.btn': '洽谈项目 →',
      'footer.about': '全流程 IT 机构。所有数字业务，尽在一颗星下。',
      'footer.services': '服务',
      'footer.sites': '网站',
      'footer.apps': '应用',
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

    // close after tapping a link
    menu.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', closeMenu);
    });

    // close on escape / when resizing to desktop
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
