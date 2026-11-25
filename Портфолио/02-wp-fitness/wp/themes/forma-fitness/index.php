<?php
/**
 * Запасной шаблон (блог / поиск / общий вывод).
 * @package forma-fitness
 */
if ( ! defined( 'ABSPATH' ) ) { exit; }
get_header(); ?>

<section class="page-hero">
	<div class="wrap">
		<h1><?php echo esc_html( get_the_archive_title() ?: get_bloginfo( 'name' ) ); ?></h1>
	</div>
</section>

<div class="wrap entry">
	<?php if ( have_posts() ) : while ( have_posts() ) : the_post(); ?>
		<article <?php post_class(); ?>>
			<h2><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h2>
			<div class="excerpt"><?php the_excerpt(); ?></div>
		</article>
	<?php endwhile; the_posts_pagination(); else : ?>
		<p><?php esc_html_e( 'Записей не найдено.', 'forma' ); ?></p>
	<?php endif; ?>
</div>

<?php get_footer(); ?>
