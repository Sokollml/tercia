<?php
/**
 * Архив «Тренеры» — страница /trainers/.
 * @package forma-fitness
 */
if ( ! defined( 'ABSPATH' ) ) { exit; }
get_header(); ?>

<section class="page-hero">
	<div class="wrap">
		<span class="eyebrow"><?php esc_html_e( 'Команда', 'forma' ); ?></span>
		<h1><?php esc_html_e( 'Наши тренеры', 'forma' ); ?></h1>
		<p style="color:#a9a99c;max-width:60ch"><?php esc_html_e( 'Каждый тренер — отдельная запись в админке: имя, фото, специализация и био.', 'forma' ); ?></p>
	</div>
</section>

<section>
	<div class="wrap">
		<div class="forma-trainers">
			<?php while ( have_posts() ) : the_post();
				get_template_part( 'template-parts/trainer', 'card' );
			endwhile; ?>
		</div>
	</div>
</section>

<?php get_footer(); ?>
