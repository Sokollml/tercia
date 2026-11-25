<?php
/**
 * Главная страница.
 *
 * Совет владельцу: блоки ниже — «безопасный» вариант на случай, если главную
 * не собирали в Elementor. Если создать страницу и назначить её как «Главную»
 * в «Настройки → Чтение», её можно полностью верстать в Elementor — тогда
 * замените этот файл на front-page, выводящий the_content(), либо соберите
 * страницу и включите её как статическую главную.
 *
 * @package Verano
 */

get_header();
?>

<!-- HERO -->
<section class="hero">
	<div class="hero__media">
		<img src="https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=1600&q=80" alt="<?php esc_attr_e( 'Зал остерии вечером', 'verano' ); ?>">
	</div>
	<div class="wrap">
		<div class="hero__inner">
			<span class="eyebrow"><?php esc_html_e( 'Средиземноморская остерия · с 2012 года', 'verano' ); ?></span>
			<h1><?php esc_html_e( 'Вкус побережья на вашем столе', 'verano' ); ?></h1>
			<p class="hero__lede"><?php esc_html_e( 'Домашняя паста, рыба из утренней поставки и овощи с фермерского рынка. Готовим в дровяной печи и открываем локальные вина.', 'verano' ); ?></p>
			<div class="hero__actions">
				<a href="<?php echo esc_url( home_url( '/booking/' ) ); ?>" class="btn btn--primary"><?php esc_html_e( 'Забронировать стол', 'verano' ); ?></a>
				<a href="<?php echo esc_url( get_post_type_archive_link( 'dish' ) ); ?>" class="btn btn--light"><?php esc_html_e( 'Смотреть меню', 'verano' ); ?></a>
			</div>
		</div>
	</div>
</section>

<!-- SIGNATURE DISHES: «Выбор шефа» из CPT -->
<section class="section section--tint">
	<div class="wrap">
		<div class="section-head center">
			<span class="eyebrow"><?php esc_html_e( 'Гордость кухни', 'verano' ); ?></span>
			<h2><?php esc_html_e( 'Блюда, за которыми возвращаются', 'verano' ); ?></h2>
		</div>

		<?php
		$featured = new WP_Query( array(
			'post_type'      => 'dish',
			'posts_per_page' => 3,
			'meta_query'     => array(
				array(
					'key'   => '_verano_chef',
					'value' => '1',
				),
			),
		) );

		// Если «выбора шефа» ещё нет — берём просто последние 3 блюда.
		if ( ! $featured->have_posts() ) {
			$featured = new WP_Query( array(
				'post_type'      => 'dish',
				'posts_per_page' => 3,
			) );
		}

		if ( $featured->have_posts() ) : ?>
			<div class="dish-grid">
				<?php while ( $featured->have_posts() ) : $featured->the_post();
					get_template_part( 'template-parts/dish-card' );
				endwhile; ?>
			</div>
			<div style="text-align:center; margin-top:44px;">
				<a href="<?php echo esc_url( get_post_type_archive_link( 'dish' ) ); ?>" class="btn btn--ghost"><?php esc_html_e( 'Всё меню', 'verano' ); ?></a>
			</div>
		<?php else : ?>
			<p style="text-align:center"><?php esc_html_e( 'Добавьте блюда в админке (Меню (блюда) → Добавить блюдо), и они появятся здесь.', 'verano' ); ?></p>
		<?php endif;
		wp_reset_postdata();
		?>
	</div>
</section>

<!-- HOURS -->
<section class="section section--paper">
	<div class="wrap">
		<div class="split reverse">
			<div class="split__media">
				<img src="https://images.unsplash.com/photo-1552566626-52f8b828add9?auto=format&fit=crop&w=1000&q=80" alt="<?php esc_attr_e( 'Столик у окна', 'verano' ); ?>">
			</div>
			<div class="split__body">
				<span class="eyebrow"><?php esc_html_e( 'Часы работы', 'verano' ); ?></span>
				<h2><?php esc_html_e( 'Мы открыты для вас', 'verano' ); ?></h2>
				<div class="hours">
					<div class="hours__row"><b><?php esc_html_e( 'Пн — Чт', 'verano' ); ?></b><span>12:00 — 23:00</span></div>
					<div class="hours__row"><b><?php esc_html_e( 'Пт — Сб', 'verano' ); ?></b><span>11:00 — 01:00</span></div>
					<div class="hours__row"><b><?php esc_html_e( 'Воскресенье', 'verano' ); ?></b><span>11:00 — 22:00</span></div>
				</div>
				<div style="margin-top:26px">
					<a href="<?php echo esc_url( home_url( '/contacts/' ) ); ?>" class="btn btn--ghost"><?php esc_html_e( 'Как нас найти', 'verano' ); ?></a>
				</div>
			</div>
		</div>
	</div>
</section>

<!-- VIDEO -->
<section class="section section--tint">
	<div class="wrap">
		<div class="section-head center">
			<span class="eyebrow"><?php esc_html_e( 'Один вечер в Verano', 'verano' ); ?></span>
			<h2><?php esc_html_e( 'Загляните на кухню', 'verano' ); ?></h2>
		</div>
		<div class="video-frame">
			<iframe src="https://www.youtube-nocookie.com/embed/ScMzIvxBSi4" title="Verano" loading="lazy" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
		</div>
	</div>
</section>

<!-- CTA -->
<section class="section cta-band">
	<div class="wrap">
		<h2><?php esc_html_e( 'Готовы к столу у окна?', 'verano' ); ?></h2>
		<p><?php esc_html_e( 'Забронируйте место за пару минут — мы подтвердим по телефону.', 'verano' ); ?></p>
		<a href="<?php echo esc_url( home_url( '/booking/' ) ); ?>" class="btn btn--light"><?php esc_html_e( 'Забронировать стол', 'verano' ); ?></a>
	</div>
</section>

<?php
get_footer();
