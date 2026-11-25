<?php
/**
 * Отдельная страница блюда.
 *
 * @package Verano
 */

get_header();

while ( have_posts() ) : the_post();
	$price = get_post_meta( get_the_ID(), '_verano_price', true );
	?>

	<section class="page-banner">
		<div class="page-banner__inner">
			<div class="wrap">
				<p class="crumbs"><a href="<?php echo esc_url( get_post_type_archive_link( 'dish' ) ); ?>"><?php esc_html_e( 'Меню', 'verano' ); ?></a></p>
				<h1><?php the_title(); ?></h1>
			</div>
		</div>
	</section>

	<section class="section section--paper">
		<div class="wrap">
			<div class="split">
				<div class="split__media">
					<?php
					if ( has_post_thumbnail() ) {
						the_post_thumbnail( 'large' );
					} else {
						echo '<img src="' . esc_url( get_template_directory_uri() . '/assets/img/placeholder.svg' ) . '" alt="">';
					}
					?>
				</div>
				<div class="split__body">
					<?php if ( $price ) : ?>
						<p class="dish__price" style="font-size:2rem"><?php echo esc_html( $price ); ?></p>
					<?php endif; ?>

					<?php verano_render_dish_tags( get_the_ID() ); ?>

					<div style="margin-top:20px">
						<?php the_content(); ?>
					</div>

					<?php
					$cats = get_the_term_list( get_the_ID(), 'dish_category', '<p class="form-note">' . esc_html__( 'Категория: ', 'verano' ), ', ', '</p>' );
					if ( $cats ) {
						echo wp_kses_post( $cats );
					}
					?>

					<div style="margin-top:26px">
						<a href="<?php echo esc_url( home_url( '/booking/' ) ); ?>" class="btn btn--primary"><?php esc_html_e( 'Забронировать стол', 'verano' ); ?></a>
						<a href="<?php echo esc_url( get_post_type_archive_link( 'dish' ) ); ?>" class="btn btn--ghost"><?php esc_html_e( 'Ко всему меню', 'verano' ); ?></a>
					</div>
				</div>
			</div>
		</div>
	</section>

	<?php
endwhile;

get_footer();
