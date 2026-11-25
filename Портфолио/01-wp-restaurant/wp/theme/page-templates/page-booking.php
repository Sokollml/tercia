<?php
/**
 * Template Name: Бронь стола
 * Description: Страница брони. Слева — форма (вставьте шорткод Contact Form 7 или
 * WPForms в содержимое страницы), справа — контактный блок.
 *
 * @package Verano
 */

get_header();

while ( have_posts() ) : the_post(); ?>

	<section class="page-banner">
		<div class="page-banner__inner">
			<div class="wrap">
				<h1><?php the_title(); ?></h1>
				<p><?php esc_html_e( 'Заполните форму — мы перезвоним и подтвердим бронь в течение часа в рабочее время.', 'verano' ); ?></p>
			</div>
		</div>
	</section>

	<section class="section section--paper">
		<div class="wrap">
			<div class="booking-layout">
				<div class="form-card">
					<?php
					// Содержимое страницы = шорткод формы, например [contact-form-7 id="123" title="Бронь"].
					// Если содержимое пустое, показываем подсказку администратору.
					$content = trim( get_the_content() );
					if ( '' !== $content ) {
						the_content();
					} else {
						echo '<p class="form-note">' . esc_html__( 'Здесь появится форма брони. Установите плагин Contact Form 7 (или WPForms), создайте форму с полями Имя, Телефон, Дата, Время, Гости, Пожелания и вставьте её шорткод в содержимое этой страницы. Настройте письмо формы на адрес ресторана.', 'verano' ) . '</p>';
					}
					?>
				</div>

				<aside class="booking-aside">
					<div class="info-block">
						<h4><?php esc_html_e( 'Часы бронирования', 'verano' ); ?></h4>
						<p><?php esc_html_e( 'Пн–Чт 12:00–23:00 · Пт–Сб 11:00–01:00 · Вс 11:00–22:00', 'verano' ); ?></p>
					</div>
					<div class="info-block">
						<h4><?php esc_html_e( 'Большая компания', 'verano' ); ?></h4>
						<p><?php esc_html_e( 'Для групп от 8 человек позвоните нам — подберём отдельную зону и меню.', 'verano' ); ?></p>
					</div>
					<div class="info-block">
						<h4><?php esc_html_e( 'Телефон', 'verano' ); ?></h4>
						<p><a href="tel:+78120000000">+7 812 000-00-00</a></p>
					</div>
					<div class="info-block">
						<h4><?php esc_html_e( 'Адрес', 'verano' ); ?></h4>
						<p><?php esc_html_e( 'ул. Приморская, 14, 1-й этаж', 'verano' ); ?></p>
					</div>
				</aside>
			</div>
		</div>
	</section>

<?php endwhile;

get_footer();
