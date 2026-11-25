<?php
/**
 * FORMA Fitness — самостоятельная тема (не требует родительской).
 * Может использоваться и как child-тема Astra: см. README.
 *
 * @package forma-fitness
 */

if ( ! defined( 'ABSPATH' ) ) { exit; }

define( 'FORMA_VER', '1.0.0' );

/* ---------- Поддержка возможностей темы ---------- */
add_action( 'after_setup_theme', function () {
	load_theme_textdomain( 'forma', get_stylesheet_directory() . '/languages' );

	add_theme_support( 'title-tag' );
	add_theme_support( 'post-thumbnails' );
	add_theme_support( 'html5', array( 'search-form', 'gallery', 'caption', 'style', 'script' ) );
	add_theme_support( 'custom-logo', array( 'height' => 40, 'width' => 140, 'flex-width' => true ) );
	add_theme_support( 'align-wide' );
	add_theme_support( 'responsive-embeds' );

	register_nav_menus( array(
		'primary' => __( 'Основное меню', 'forma' ),
		'footer'  => __( 'Меню в подвале', 'forma' ),
	) );

	// Размер для карточек тренеров (портрет 3:4)
	add_image_size( 'forma_trainer', 500, 667, true );
} );

/* ---------- Стили и скрипты ---------- */
add_action( 'wp_enqueue_scripts', function () {
	// Google Fonts
	wp_enqueue_style( 'forma-fonts', 'https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap', array(), null );
	// Основной стиль темы
	wp_enqueue_style( 'forma-style', get_stylesheet_uri(), array( 'forma-fonts' ), FORMA_VER );
	// Скрипты (мобильное меню, рендер расписания на клиенте если нужно)
	wp_enqueue_script( 'forma-main', get_stylesheet_directory_uri() . '/assets/js/theme.js', array(), FORMA_VER, true );
} );

/* ---------- Виджеты подвала ---------- */
add_action( 'widgets_init', function () {
	register_sidebar( array(
		'name'          => __( 'Подвал', 'forma' ),
		'id'            => 'footer-1',
		'before_widget' => '<div class="footer-col %2$s">',
		'after_widget'  => '</div>',
		'before_title'  => '<h4>',
		'after_title'   => '</h4>',
	) );
} );

/* ---------- Хелпер: язык для Polylang (RU/EN) ----------
 * Если установлен Polylang, отдаём его текущий язык; иначе локаль сайта. */
function forma_current_lang() {
	if ( function_exists( 'pll_current_language' ) ) {
		return pll_current_language() ?: 'ru';
	}
	return substr( get_locale(), 0, 2 ) ?: 'ru';
}

/* ---------- Регистрируем строки для перевода в Polylang ----------
 * Тексты интерфейса темы можно переводить через «Языки → Переводы строк». */
add_action( 'init', function () {
	if ( function_exists( 'pll_register_string' ) ) {
		pll_register_string( 'forma_cta', 'Пробное занятие', 'FORMA' );
		pll_register_string( 'forma_book', 'Записаться на пробное', 'FORMA' );
		pll_register_string( 'forma_tagline', 'Студия функционального фитнеса', 'FORMA' );
	}
} );

/* Хелпер вывода переводимой строки */
function forma_e( $text ) {
	echo function_exists( 'pll__' ) ? esc_html( pll__( $text ) ) : esc_html( $text );
}
