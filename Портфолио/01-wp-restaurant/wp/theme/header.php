<?php
/**
 * Шапка сайта.
 *
 * @package Verano
 */

?><!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
	<meta charset="<?php bloginfo( 'charset' ); ?>">
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<link rel="icon" type="image/svg+xml" href="<?php echo esc_url( get_template_directory_uri() . '/assets/img/favicon.svg' ); ?>">
	<?php wp_head(); ?>
</head>
<body <?php body_class(); ?>>
<?php wp_body_open(); ?>

<header class="site-header">
	<div class="wrap">
		<nav class="nav" aria-label="<?php esc_attr_e( 'Основная навигация', 'verano' ); ?>">
			<a class="brand" href="<?php echo esc_url( home_url( '/' ) ); ?>" aria-label="<?php echo esc_attr( get_bloginfo( 'name' ) ); ?>">
				<span class="brand__mark">
					<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 3v7a2 2 0 0 0 2 2v9M6 3v6M9 3v6M18 3c-1.5 0-2.5 2-2.5 5.5S16 14 18 14v7"/></svg>
					<span class="brand__name"><?php bloginfo( 'name' ); ?></span>
				</span>
			</a>

			<?php
			wp_nav_menu( array(
				'theme_location' => 'primary',
				'container'      => false,
				'menu_class'     => 'nav__links',
				'fallback_cb'    => 'verano_primary_menu_fallback',
				'depth'          => 1,
			) );
			?>

			<div class="nav__right">
				<div class="lang-toggle" role="group" aria-label="<?php esc_attr_e( 'Язык сайта', 'verano' ); ?>">
					<button type="button" data-set-lang="ru" class="is-active">RU</button>
					<button type="button" data-set-lang="en">EN</button>
				</div>
				<a href="<?php echo esc_url( home_url( '/booking/' ) ); ?>" class="btn btn--primary nav__cta-desktop"><?php esc_html_e( 'Забронировать', 'verano' ); ?></a>
				<button class="nav__toggle" aria-label="<?php esc_attr_e( 'Меню', 'verano' ); ?>" aria-expanded="false">
					<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M4 7h16M4 12h16M4 17h16"/></svg>
				</button>
			</div>
		</nav>
	</div>
</header>
