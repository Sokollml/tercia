<?php
/**
 * Резервный шаблон (блог/поиск/архивы). Основные страницы используют
 * front-page.php, archive-dish.php, page.php и т. д.
 *
 * @package Verano
 */

get_header();
?>

<section class="page-banner">
	<div class="page-banner__inner">
		<div class="wrap">
			<h1><?php
				if ( is_search() ) {
					printf( esc_html__( 'Результаты поиска: %s', 'verano' ), '<span>' . esc_html( get_search_query() ) . '</span>' );
				} elseif ( is_archive() ) {
					the_archive_title();
				} else {
					esc_html_e( 'Записи', 'verano' );
				}
			?></h1>
		</div>
	</div>
</section>

<section class="section section--paper">
	<div class="wrap" style="max-width:820px">
		<?php if ( have_posts() ) : ?>
			<?php while ( have_posts() ) : the_post(); ?>
				<article <?php post_class( 'entry' ); ?> style="margin-bottom:40px; padding-bottom:30px; border-bottom:1px solid var(--line)">
					<h2><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h2>
					<div class="entry-summary"><?php the_excerpt(); ?></div>
				</article>
			<?php endwhile; ?>

			<div class="pagination"><?php the_posts_pagination(); ?></div>
		<?php else : ?>
			<p><?php esc_html_e( 'Ничего не найдено.', 'verano' ); ?></p>
		<?php endif; ?>
	</div>
</section>

<?php
get_footer();
