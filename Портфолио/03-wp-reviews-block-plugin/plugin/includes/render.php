<?php
/**
 * Server-side render for the Reviews (testimonials) dynamic block.
 *
 * @package ReviewsBlock
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Render a row of SVG stars for a rating.
 *
 * @param int $rating Rating 0..5.
 * @return string Escaped HTML.
 */
function reviews_block_render_stars( $rating ) {
	$rating = max( 0, min( 5, (int) $rating ) );
	$out    = '<div class="reviews-block__stars" role="img" aria-label="'
		. esc_attr( sprintf( /* translators: %d: rating value 1-5 */ __( 'Оценка: %d из 5', 'reviews-block' ), $rating ) )
		. '">';

	for ( $i = 1; $i <= 5; $i++ ) {
		$filled = $i <= $rating ? ' is-filled' : '';
		$out   .= '<svg class="reviews-block__star' . esc_attr( $filled ) . '" width="18" height="18" viewBox="0 0 20 20" aria-hidden="true" focusable="false">'
			. '<path d="M10 1.5l2.6 5.27 5.82.85-4.21 4.1.99 5.79L10 14.77 4.8 17.5l.99-5.79-4.21-4.1 5.82-.85z"/>'
			. '</svg>';
	}

	$out .= '</div>';
	return $out;
}

/**
 * Render callback for the reviews-block/testimonials block.
 *
 * @param array $attributes Block attributes from block.json.
 * @return string Rendered HTML.
 */
function reviews_block_render_callback( $attributes ) {
	$defaults = array(
		'count'    => 6,
		'layout'   => 'carousel',
		'autoplay' => true,
		'interval' => 5000,
	);
	$attr = wp_parse_args( is_array( $attributes ) ? $attributes : array(), $defaults );

	$count    = max( 1, min( 24, (int) $attr['count'] ) );
	$layout   = in_array( $attr['layout'], array( 'carousel', 'grid' ), true ) ? $attr['layout'] : 'carousel';
	$autoplay = ! empty( $attr['autoplay'] );
	$interval = max( 2000, min( 15000, (int) $attr['interval'] ) );

	$query = new WP_Query(
		array(
			'post_type'              => Reviews_Block_CPT::POST_TYPE,
			'post_status'            => 'publish',
			'posts_per_page'         => $count,
			'orderby'                => 'date',
			'order'                  => 'DESC',
			'no_found_rows'          => true,
			'update_post_term_cache' => false,
		)
	);

	if ( ! $query->have_posts() ) {
		wp_reset_postdata();
		return '<div class="reviews-block reviews-block--empty"><p>'
			. esc_html__( 'Пока нет отзывов. Добавьте записи типа «Отзыв».', 'reviews-block' )
			. '</p></div>';
	}

	// Wrapper attributes (supports, className, align) from the editor.
	$wrapper_attributes = function_exists( 'get_block_wrapper_attributes' )
		? get_block_wrapper_attributes(
			array(
				'class'                => 'reviews-block reviews-block--' . $layout,
				'data-layout'          => $layout,
				'data-autoplay'        => $autoplay ? 'true' : 'false',
				'data-interval'        => (string) $interval,
			)
		)
		: 'class="reviews-block reviews-block--' . esc_attr( $layout ) . '"';

	ob_start();
	?>
	<div <?php echo $wrapper_attributes; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- get_block_wrapper_attributes escapes. ?>>
		<div class="reviews-block__viewport">
			<div class="reviews-block__track">
				<?php
				while ( $query->have_posts() ) :
					$query->the_post();
					$post_id = get_the_ID();
					$rating  = (int) get_post_meta( $post_id, '_reviews_block_rating', true );
					$company = (string) get_post_meta( $post_id, '_reviews_block_company', true );
					$name    = get_the_title();
					$text    = get_the_content();
					?>
					<article class="reviews-block__card">
						<div class="reviews-block__card-inner">
							<?php echo reviews_block_render_stars( $rating ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- pre-escaped. ?>

							<div class="reviews-block__text">
								<?php
								echo wp_kses_post( wpautop( $text ) );
								?>
							</div>

							<div class="reviews-block__author">
								<?php if ( has_post_thumbnail( $post_id ) ) : ?>
									<div class="reviews-block__avatar">
										<?php
										echo get_the_post_thumbnail(
											$post_id,
											array( 96, 96 ),
											array(
												'class'   => 'reviews-block__avatar-img',
												'loading' => 'lazy',
												'alt'     => esc_attr( $name ),
											)
										);
										?>
									</div>
								<?php else : ?>
									<div class="reviews-block__avatar reviews-block__avatar--placeholder" aria-hidden="true">
										<span><?php echo esc_html( mb_substr( $name, 0, 1 ) ); ?></span>
									</div>
								<?php endif; ?>

								<div class="reviews-block__meta">
									<span class="reviews-block__name"><?php echo esc_html( $name ); ?></span>
									<?php if ( '' !== $company ) : ?>
										<span class="reviews-block__company"><?php echo esc_html( $company ); ?></span>
									<?php endif; ?>
								</div>
							</div>
						</div>
					</article>
				<?php endwhile; ?>
			</div>
		</div>

		<?php if ( 'carousel' === $layout ) : ?>
			<div class="reviews-block__controls">
				<button type="button" class="reviews-block__nav reviews-block__nav--prev" aria-label="<?php esc_attr_e( 'Предыдущий отзыв', 'reviews-block' ); ?>">
					<svg width="20" height="20" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M15 6l-6 6 6 6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
				</button>
				<div class="reviews-block__dots" role="tablist" aria-label="<?php esc_attr_e( 'Навигация по отзывам', 'reviews-block' ); ?>"></div>
				<button type="button" class="reviews-block__nav reviews-block__nav--next" aria-label="<?php esc_attr_e( 'Следующий отзыв', 'reviews-block' ); ?>">
					<svg width="20" height="20" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M9 6l6 6-6 6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
				</button>
			</div>
		<?php endif; ?>
	</div>
	<?php

	wp_reset_postdata();
	return ob_get_clean();
}
