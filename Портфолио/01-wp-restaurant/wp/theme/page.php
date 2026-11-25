<?php
/**
 * Стандартный шаблон страницы (О нас, Контакты, произвольные страницы,
 * в том числе собранные в Elementor — тогда контент рисует Elementor).
 *
 * @package Verano
 */

get_header();

while ( have_posts() ) : the_post();

	// Если страницу верстают в Elementor / Gutenberg full-width, баннер можно
	// не показывать — но для обычных страниц выведем аккуратную шапку.
	if ( ! post_password_required() ) : ?>

		<section class="page-banner">
			<div class="page-banner__inner">
				<div class="wrap">
					<h1><?php the_title(); ?></h1>
				</div>
			</div>
		</section>

		<section class="section section--paper">
			<div class="wrap" style="max-width:820px">
				<div class="entry-content">
					<?php
					the_content();

					wp_link_pages( array(
						'before' => '<div class="page-links">' . esc_html__( 'Страницы:', 'verano' ),
						'after'  => '</div>',
					) );
					?>
				</div>
			</div>
		</section>

	<?php endif;

endwhile;

get_footer();
