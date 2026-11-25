<?php
/**
 * Шаблон страницы. Контент редактируется в админке или Elementor.
 * @package forma-fitness
 */
if ( ! defined( 'ABSPATH' ) ) { exit; }
get_header();

while ( have_posts() ) : the_post(); ?>
	<?php if ( ! function_exists( 'elementor_theme_do_location' ) || ! elementor_theme_do_location( 'single' ) ) : ?>
		<section class="page-hero">
			<div class="wrap"><h1><?php the_title(); ?></h1></div>
		</section>
		<div class="wrap entry">
			<?php the_content(); // шорткоды [forma_schedule] / [forma_trainers] работают здесь ?>
		</div>
	<?php endif; ?>
<?php endwhile;

get_footer();
