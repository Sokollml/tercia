<?php
/**
 * Архив блюд = страница «Меню».
 * Выводит блюда, сгруппированные по таксономии «Категория меню»,
 * с кнопками-фильтрами (обрабатываются в assets/js/main.js).
 *
 * @package Verano
 */

get_header();
?>

<section class="page-banner">
	<div class="page-banner__inner">
		<div class="wrap">
			<h1><?php esc_html_e( 'Меню', 'verano' ); ?></h1>
			<p><?php esc_html_e( 'Меню обновляется по сезону. Спросите официанта о блюдах дня и позициях без глютена.', 'verano' ); ?></p>
		</div>
	</div>
</section>

<section class="section section--paper">
	<div class="wrap">

		<?php
		$terms = get_terms( array(
			'taxonomy'   => 'dish_category',
			'hide_empty' => true,
			'orderby'    => 'term_order',
		) );

		if ( ! is_wp_error( $terms ) && ! empty( $terms ) ) : ?>
			<div class="menu-filter" role="group" aria-label="<?php esc_attr_e( 'Фильтр по категориям', 'verano' ); ?>">
				<button type="button" data-filter="all" class="is-active"><?php esc_html_e( 'Всё', 'verano' ); ?></button>
				<?php foreach ( $terms as $term ) : ?>
					<button type="button" data-filter="<?php echo esc_attr( $term->slug ); ?>"><?php echo esc_html( $term->name ); ?></button>
				<?php endforeach; ?>
			</div>

			<?php foreach ( $terms as $term ) :
				$q = new WP_Query( array(
					'post_type'      => 'dish',
					'posts_per_page' => -1,
					'orderby'        => 'menu_order title',
					'order'          => 'ASC',
					'tax_query'      => array(
						array(
							'taxonomy' => 'dish_category',
							'field'    => 'term_id',
							'terms'    => $term->term_id,
						),
					),
				) );
				if ( $q->have_posts() ) : ?>
					<div class="menu-cat" data-cat="<?php echo esc_attr( $term->slug ); ?>">
						<div class="menu-cat__head"><h2><?php echo esc_html( $term->name ); ?></h2></div>
						<div class="dish-grid">
							<?php while ( $q->have_posts() ) : $q->the_post();
								get_template_part( 'template-parts/dish-card' );
							endwhile; ?>
						</div>
					</div>
				<?php endif;
				wp_reset_postdata();
			endforeach; ?>

		<?php else : ?>
			<?php // Категорий нет — выводим все блюда одной сеткой. ?>
			<?php if ( have_posts() ) : ?>
				<div class="dish-grid">
					<?php while ( have_posts() ) : the_post();
						get_template_part( 'template-parts/dish-card' );
					endwhile; ?>
				</div>
			<?php else : ?>
				<p><?php esc_html_e( 'Блюда пока не добавлены. Зайдите в админку → «Меню (блюда)» → «Добавить блюдо».', 'verano' ); ?></p>
			<?php endif; ?>
		<?php endif; ?>

		<p class="form-note" style="text-align:center; margin-top:20px"><?php esc_html_e( 'Цены указаны в рублях. Есть вопросы по аллергенам? Спросите официанта.', 'verano' ); ?></p>
	</div>
</section>

<?php
get_footer();
