<?php
/**
 * Plugin Name:       Reviews Block — Отзывы
 * Plugin URI:        https://example.com/reviews-block
 * Description:       Кастомный тип записи «Отзыв» и Gutenberg-блок для вывода отзывов каруселью или сеткой. Custom post type "Testimonial" and a Gutenberg block that renders reviews as a carousel or grid.
 * Version:           1.0.0
 * Requires at least: 6.1
 * Requires PHP:      7.4
 * Author:            Tercia
 * License:           GPL-2.0-or-later
 * License URI:       https://www.gnu.org/licenses/gpl-2.0.html
 * Text Domain:       reviews-block
 * Domain Path:       /languages
 *
 * @package ReviewsBlock
 */

// No direct access.
if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

define( 'REVIEWS_BLOCK_VERSION', '1.0.0' );
define( 'REVIEWS_BLOCK_FILE', __FILE__ );
define( 'REVIEWS_BLOCK_DIR', plugin_dir_path( __FILE__ ) );
define( 'REVIEWS_BLOCK_URL', plugin_dir_url( __FILE__ ) );

require_once REVIEWS_BLOCK_DIR . 'includes/class-cpt.php';
require_once REVIEWS_BLOCK_DIR . 'includes/render.php';

/**
 * Load translations.
 */
function reviews_block_load_textdomain() {
	load_plugin_textdomain( 'reviews-block', false, dirname( plugin_basename( __FILE__ ) ) . '/languages' );
}
add_action( 'init', 'reviews_block_load_textdomain' );

/**
 * Register the custom post type and its meta on init.
 */
function reviews_block_bootstrap() {
	$cpt = new Reviews_Block_CPT();
	$cpt->register();
}
add_action( 'init', 'reviews_block_bootstrap' );

/**
 * Register the dynamic Gutenberg block from block.json.
 * The PHP render callback lives in includes/render.php.
 */
function reviews_block_register_block() {
	register_block_type(
		REVIEWS_BLOCK_DIR . 'block.json',
		array(
			'render_callback' => 'reviews_block_render_callback',
		)
	);
}
add_action( 'init', 'reviews_block_register_block' );

/**
 * Make the "layout", "count" and "autoplay" strings available for editor JS translations.
 */
function reviews_block_set_script_translations() {
	if ( function_exists( 'wp_set_script_translations' ) ) {
		wp_set_script_translations( 'reviews-block-testimonials-editor-script', 'reviews-block', REVIEWS_BLOCK_DIR . 'languages' );
	}
}
add_action( 'init', 'reviews_block_set_script_translations', 20 );

/**
 * Enqueue the front-end carousel script + styles only when the block is present.
 * WordPress handles this automatically via block.json (script/style/viewScript),
 * but we register handles here so wp_set_script_translations can target them.
 */

/**
 * Flush rewrite rules on activation so the CPT permalinks work immediately.
 */
function reviews_block_activate() {
	require_once REVIEWS_BLOCK_DIR . 'includes/class-cpt.php';
	$cpt = new Reviews_Block_CPT();
	$cpt->register();
	flush_rewrite_rules();
}
register_activation_hook( __FILE__, 'reviews_block_activate' );

/**
 * Clean up rewrite rules on deactivation.
 */
function reviews_block_deactivate() {
	flush_rewrite_rules();
}
register_deactivation_hook( __FILE__, 'reviews_block_deactivate' );
