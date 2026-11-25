<?php
/**
 * Карточка тренера. Подключается: get_template_part( 'template-parts/trainer', 'card' ).
 * @package forma-fitness
 */
if ( ! defined( 'ABSPATH' ) ) { exit; }
$spec = get_post_meta( get_the_ID(), '_forma_spec', true );
?>
<article class="forma-trainer">
	<div class="photo">
		<a href="<?php the_permalink(); ?>">
			<?php if ( has_post_thumbnail() ) {
				the_post_thumbnail( 'forma_trainer', array( 'alt' => esc_attr( get_the_title() ) ) );
			} ?>
		</a>
	</div>
	<div class="body">
		<h3><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h3>
		<?php if ( $spec ) : ?><div class="role"><?php echo esc_html( $spec ); ?></div><?php endif; ?>
		<div class="bio"><?php echo wp_kses_post( wpautop( wp_trim_words( get_the_content(), 26 ) ) ); ?></div>
	</div>
</article>
