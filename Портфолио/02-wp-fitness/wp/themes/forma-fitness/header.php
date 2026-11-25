<?php
/**
 * Шапка сайта.
 * @package forma-fitness
 */
if ( ! defined( 'ABSPATH' ) ) { exit; }
?><!doctype html>
<html <?php language_attributes(); ?>>
<head>
	<meta charset="<?php bloginfo( 'charset' ); ?>">
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<link rel="profile" href="https://gmpg.org/xfn/11">
	<?php wp_head(); ?>
</head>
<body <?php body_class(); ?>>
<?php wp_body_open(); ?>

<header class="site-header">
	<div class="wrap nav">
		<?php if ( has_custom_logo() ) : the_custom_logo(); else : ?>
			<a class="brand" href="<?php echo esc_url( home_url( '/' ) ); ?>">
				<svg viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg"><rect width="32" height="32" rx="8" fill="#16160f"/><path d="M10 23V9h12v3.6h-8v2.7h6.6V19H14v4z" fill="#c6ff2e"/></svg>
				<?php bloginfo( 'name' ); ?>
			</a>
		<?php endif; ?>

		<?php
		wp_nav_menu( array(
			'theme_location' => 'primary',
			'container'      => false,
			'menu_class'     => 'nav-links',
			'fallback_cb'    => false,
			'menu_id'        => 'primary-menu',
		) );
		?>

		<div class="nav-actions">
			<?php // Переключатель языка Polylang (если активен)
			if ( function_exists( 'pll_the_languages' ) ) {
				echo '<div class="pll-switcher">';
				pll_the_languages( array( 'display_names_as' => 'slug', 'hide_if_empty' => 0 ) );
				echo '</div>';
			} ?>
			<a class="btn btn--accent" href="<?php echo esc_url( home_url( '/contacts/' ) ); ?>"><?php forma_e( 'Пробное занятие' ); ?></a>
			<button class="burger" aria-label="<?php esc_attr_e( 'Меню', 'forma' ); ?>" id="burger">
				<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 7h16M4 12h16M4 17h16"/></svg>
			</button>
		</div>
	</div>
</header>

<main id="content">
