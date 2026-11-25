<?php
/**
 * Карточка блюда. Ожидает, что глобальный $post — это запись типа dish.
 *
 * @package Verano
 */

$price = get_post_meta( get_the_ID(), '_verano_price', true );
?>
<article <?php post_class( 'dish' ); ?>>
	<a class="dish__media" href="<?php the_permalink(); ?>" aria-hidden="true" tabindex="-1">
		<?php
		if ( has_post_thumbnail() ) {
			the_post_thumbnail( 'verano-dish', array( 'alt' => the_title_attribute( array( 'echo' => false ) ) ) );
		} else {
			echo '<img src="' . esc_url( get_template_directory_uri() . '/assets/img/placeholder.svg' ) . '" alt="">';
		}
		?>
	</a>
	<div class="dish__body">
		<div class="dish__top">
			<h3 class="dish__name"><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h3>
			<?php if ( $price ) : ?>
				<span class="dish__price"><?php echo esc_html( $price ); ?></span>
			<?php endif; ?>
		</div>
		<?php if ( has_excerpt() ) : ?>
			<p class="dish__desc"><?php echo esc_html( get_the_excerpt() ); ?></p>
		<?php endif; ?>
		<?php verano_render_dish_tags( get_the_ID() ); ?>
	</div>
</article>
