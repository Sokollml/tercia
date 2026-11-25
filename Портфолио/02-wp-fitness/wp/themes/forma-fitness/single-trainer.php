<?php
/**
 * Отдельная страница тренера.
 * @package forma-fitness
 */
if ( ! defined( 'ABSPATH' ) ) { exit; }
get_header();

while ( have_posts() ) : the_post();
	$spec = get_post_meta( get_the_ID(), '_forma_spec', true ); ?>

	<section class="page-hero">
		<div class="wrap">
			<?php if ( $spec ) : ?><span class="eyebrow"><?php echo esc_html( $spec ); ?></span><?php endif; ?>
			<h1><?php the_title(); ?></h1>
		</div>
	</section>

	<div class="wrap entry">
		<div class="forma-trainer" style="max-width:820px">
			<?php if ( has_post_thumbnail() ) : ?>
				<div class="photo" style="aspect-ratio:16/9"><?php the_post_thumbnail( 'large' ); ?></div>
			<?php endif; ?>
			<div class="body">
				<div class="bio"><?php the_content(); ?></div>
				<p><a class="btn btn--accent" href="<?php echo esc_url( home_url( '/contacts/' ) ); ?>"><?php forma_e( 'Записаться на пробное' ); ?></a></p>
			</div>
		</div>
	</div>

<?php endwhile;

get_footer();
