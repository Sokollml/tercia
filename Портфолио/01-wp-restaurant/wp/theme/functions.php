<?php
/**
 * Verano theme functions.
 *
 * @package Verano
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

if ( ! defined( 'VERANO_VERSION' ) ) {
	define( 'VERANO_VERSION', '1.0.0' );
}

/**
 * Поддержка возможностей темы.
 */
function verano_theme_setup() {
	load_theme_textdomain( 'verano', get_template_directory() . '/languages' );

	add_theme_support( 'title-tag' );
	add_theme_support( 'post-thumbnails' );
	add_theme_support( 'automatic-feed-links' );
	add_theme_support( 'html5', array( 'search-form', 'gallery', 'caption', 'style', 'script', 'navigation-widgets' ) );
	add_theme_support( 'responsive-embeds' );
	add_theme_support( 'align-wide' );
	add_theme_support( 'custom-logo', array(
		'height'      => 60,
		'width'       => 200,
		'flex-height' => true,
		'flex-width'  => true,
	) );

	// Размер обрезки для карточек блюд.
	add_image_size( 'verano-dish', 800, 600, true );

	register_nav_menus( array(
		'primary' => __( 'Основное меню (шапка)', 'verano' ),
		'footer'  => __( 'Меню в подвале', 'verano' ),
	) );
}
add_action( 'after_setup_theme', 'verano_theme_setup' );

/**
 * Стили и скрипты.
 */
function verano_enqueue_assets() {
	// Google Fonts.
	wp_enqueue_style(
		'verano-fonts',
		'https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap',
		array(),
		null
	);

	// Основной файл стилей темы.
	wp_enqueue_style(
		'verano-main',
		get_template_directory_uri() . '/assets/css/style.css',
		array( 'verano-fonts' ),
		VERANO_VERSION
	);

	// Скрипты (язык, мобильное меню, лайтбокс, фильтр, форма).
	wp_enqueue_script(
		'verano-main',
		get_template_directory_uri() . '/assets/js/main.js',
		array(),
		VERANO_VERSION,
		true
	);
}
add_action( 'wp_enqueue_scripts', 'verano_enqueue_assets' );

/**
 * Область виджетов в подвале (не обязательна, но удобна владельцу).
 */
function verano_widgets_init() {
	register_sidebar( array(
		'name'          => __( 'Подвал', 'verano' ),
		'id'            => 'footer-1',
		'before_widget' => '<div class="footer-widget">',
		'after_widget'  => '</div>',
		'before_title'  => '<h5>',
		'after_title'   => '</h5>',
	) );
}
add_action( 'widgets_init', 'verano_widgets_init' );

/**
 * Хелпер: вывести метки блюда (веган/остро/шеф) как <span class="tag">.
 *
 * @param int $post_id ID блюда.
 */
function verano_render_dish_tags( $post_id = null ) {
	$post_id = $post_id ? $post_id : get_the_ID();

	$icon_vegan = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M11 20A7 7 0 0 1 4 13c0-5 4-9 9-9 0 5-1 9-2 12M11 20c4 0 7-3 7-7"/></svg>';
	$icon_spicy = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M9 8c3-4 8-4 9 0 0 6-4 11-9 12-3-3-4-7-3-10M9 8c-2 0-3-2-2-4"/></svg>';
	$icon_chef  = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l2.5 5 5.5.8-4 3.9 1 5.5-5-2.7-5 2.7 1-5.5-4-3.9 5.5-.8Z"/></svg>';

	$allowed_svg = array(
		'svg'  => array( 'viewbox' => true, 'fill' => true, 'stroke' => true, 'stroke-width' => true, 'stroke-linecap' => true, 'stroke-linejoin' => true ),
		'path' => array( 'd' => true ),
	);

	echo '<div class="dish__tags">';
	if ( get_post_meta( $post_id, '_verano_vegan', true ) ) {
		echo '<span class="tag tag--vegan">' . wp_kses( $icon_vegan, $allowed_svg ) . '<span>' . esc_html__( 'Веган', 'verano' ) . '</span></span>';
	}
	if ( get_post_meta( $post_id, '_verano_spicy', true ) ) {
		echo '<span class="tag tag--spicy">' . wp_kses( $icon_spicy, $allowed_svg ) . '<span>' . esc_html__( 'Остро', 'verano' ) . '</span></span>';
	}
	if ( get_post_meta( $post_id, '_verano_chef', true ) ) {
		echo '<span class="tag tag--chef">' . wp_kses( $icon_chef, $allowed_svg ) . '<span>' . esc_html__( 'Выбор шефа', 'verano' ) . '</span></span>';
	}
	echo '</div>';
}

/**
 * Fallback-меню, если пользователь ещё не назначил меню в «Внешний вид → Меню».
 */
function verano_primary_menu_fallback() {
	echo '<ul class="nav__links">';
	echo '<li><a href="' . esc_url( home_url( '/' ) ) . '">' . esc_html__( 'Главная', 'verano' ) . '</a></li>';
	echo '<li><a href="' . esc_url( get_post_type_archive_link( 'dish' ) ) . '">' . esc_html__( 'Меню', 'verano' ) . '</a></li>';
	echo '</ul>';
}
